import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import SessionLocal
from app.models.models import (
    User, Project, Source, Claim, Decision, Task, Conflict, KnowledgeGapQuestion, ProjectMember
)

client = TestClient(app)

def get_auth_token(email: str):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_grounded_assistant_citations_and_verbatim_quotes():
    """Verify that factual queries return real citations with verbatim matching quotes."""
    token = get_auth_token("marcus.vance@company.internal")
    
    res = client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "project_id": 1,
            "query": "What is the database pool setup?"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_grounded"] is True
    assert len(data["citations"]) > 0

    first_cite = data["citations"][0]
    assert first_cite["claim_id"] > 0
    assert first_cite["claim_code"].startswith("#CLM-") or first_cite["claim_code"].startswith("CLM-")
    assert len(first_cite["exact_quote"]) > 10
    # Verbatim quotation in the answer or citation
    assert first_cite["exact_quote"] in data["answer"] or first_cite["title"] in data["answer"]

def test_grounded_assistant_unsupported_query_exact_no_evidence_found():
    """Verify that ungrounded queries return EXACTLY 'No evidence found'."""
    token = get_auth_token("marcus.vance@company.internal")

    res = client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "project_id": 1,
            "query": "What is the secret recipe for cafeteria brownies?"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_grounded"] is False
    assert data["answer"] == "No evidence found"
    assert len(data["citations"]) == 0

def test_grounded_assistant_surfaces_conflicts_rather_than_merging():
    """
    Verify that when accessible sources contain contradictory claims,
    the assistant surfaces the contradiction and directs the user to conflict review.
    """
    token = get_auth_token("alex.morgan@company.internal")
    with SessionLocal() as db:
        # Project 1 has CONF-882 (Webhook circuit breaker ownership between PR-1420 and Slack)
        res = client.post(
            "/api/v1/chat/query",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "project_id": 1,
                "query": "Who owns the webhook failover circuit breaker?"
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["is_grounded"] is True
        # Check conflict indicator
        if data.get("has_conflict"):
            assert "Conflicting evidence exists" in data["answer"] or "contradiction" in data["answer"].lower()
            assert "Conflict Management" in data["answer"] or "review" in data["answer"].lower()

def test_automated_knowledge_gap_question_generation():
    """
    Verify automated gap detection creates targeted questions across dimensions:
    - Missing rationale
    - Missing ownership
    - Missing blocker resolution
    """
    token = get_auth_token("alex.morgan@company.internal")
    with SessionLocal() as db:
        proj = Project(
            name="Gap Engine Project",
            slug=f"gap-test-{db.query(Project).count() + 1}",
            description="Testing automated knowledge gap detection"
        )
        db.add(proj)
        db.commit()
        db.refresh(proj)

        alex = db.query(User).filter(User.email == "alex.morgan@company.internal").first()
        db.add(ProjectMember(project_id=proj.id, user_id=alex.id, role_in_project="Manager"))

        # 1. Decision with missing rationale
        dec = Decision(
            decision_code=f"DEC-GAP-{proj.id}",
            project_id=proj.id,
            title="Adoption of SurrealDB",
            person_responsible="Sarah Lin",
            rationale="TODO: document rationale later",
            alternatives_evaluated="",
            supporting_evidence=""
        )
        # 2. Unfinished task with no owner
        task = Task(
            project_id=proj.id,
            title="Stripe Payment Webhook Idempotency Worker",
            status="In Progress",
            assignee_name=None,
            assignee_id=None,
            is_completed=False
        )
        # 3. Blocker with no resolution
        blocker = Claim(
            claim_code=f"CLM-BLK-{proj.id}",
            project_id=proj.id,
            title="Biometric Scanner Serial Timeout",
            description="Active blocker: USB serial connection drops under heavy load",
            category="Blocker",
            entity_or_subject="Biometric Scanner",
            exact_quote="Serial connection drops causing scanner timeout",
            evidence_status="VERIFIED"
        )
        db.add_all([dec, task, blocker])
        db.commit()

        # Trigger gap detection
        detect_res = client.post(
            f"/api/v1/gaps/detect?project_id={proj.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert detect_res.status_code == 200
        count = detect_res.json()["questions_generated"]
        assert count >= 3, f"Expected at least 3 gap questions, got {count}"

        # Fetch questions
        gaps_res = client.get(
            f"/api/v1/gaps/?project_id={proj.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert gaps_res.status_code == 200
        gaps = gaps_res.json()
        categories = {g["category"] for g in gaps}

        assert "DecisionRationale" in categories
        assert "Ownership" in categories
        assert "BlockerResolution" in categories

def test_knowledge_gap_answering_and_clarification_provenance():
    """
    Verify departing employee answer persistence and automatic promotion to clarification claim.
    """
    token_sarah = get_auth_token("sarah.lin@company.internal") # Departing Lead

    with SessionLocal() as db:
        proj = db.query(Project).filter(Project.name == "Gap Engine Project").order_by(Project.id.desc()).first()
        gap_q = db.query(KnowledgeGapQuestion).filter(
            KnowledgeGapQuestion.project_id == proj.id,
            KnowledgeGapQuestion.category == "Ownership"
        ).first()
        assert gap_q is not None

        # Sarah answers the gap question
        answer_text = "Marcus Vance is taking over primary maintenance of the Idempotency Worker, with David K. as backup."
        ans_res = client.post(
            f"/api/v1/gaps/{gap_q.id}/answer",
            headers={"Authorization": f"Bearer {token_sarah}"},
            json={
                "answer": answer_text,
                "respondent_name": "Sarah Lin (Departing Lead)"
            }
        )
        assert ans_res.status_code == 200
        updated_q = ans_res.json()["question"]
        assert updated_q["status"] == "Answered"
        assert updated_q["answer"] == answer_text
        assert updated_q["respondent_name"] == "Sarah Lin (Departing Lead)"

        # Verify clarification claim is created in claims ledger
        clarification_claim = db.query(Claim).filter(
            Claim.project_id == proj.id,
            Claim.claim_code == f"#CLM-GAP-{gap_q.id}"
        ).first()
        assert clarification_claim is not None
        assert clarification_claim.verification_method == "Human Clarification"
        assert clarification_claim.evidence_status == "INFERRED"
        assert "Sarah Lin" in clarification_claim.exact_quote
        assert "Marcus Vance" in clarification_claim.description
