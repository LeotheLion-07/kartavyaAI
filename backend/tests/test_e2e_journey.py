import io
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

def test_full_e2e_hackathon_journey():
    """
    Executes the mandatory 21-step end-to-end integration scenario (Section 11.E).
    """
    token_manager = get_auth_token("alex.morgan@company.internal")
    token_successor = get_auth_token("marcus.vance@company.internal")
    token_departing = get_auth_token("sarah.lin@company.internal")

    # Step 1: Create a project with authorized users
    with SessionLocal() as db:
        alex = db.query(User).filter(User.email == "alex.morgan@company.internal").first()
        marcus = db.query(User).filter(User.email == "marcus.vance@company.internal").first()
        sarah = db.query(User).filter(User.email == "sarah.lin@company.internal").first()

        proj = Project(
            name="E2E Real Handover Project",
            slug=f"e2e-project-{db.query(Project).count() + 100}",
            description="End-to-End verified project for hackathon evaluation"
        )
        db.add(proj)
        db.commit()
        db.refresh(proj)

        db.add_all([
            ProjectMember(project_id=proj.id, user_id=alex.id, role_in_project="Manager"),
            ProjectMember(project_id=proj.id, user_id=marcus.id, role_in_project="Successor"),
            ProjectMember(project_id=proj.id, user_id=sarah.id, role_in_project="Departing Lead"),
        ])
        db.commit()
        proj_id = proj.id

    # Step 2: Upload two documents with conflicting task ownership
    # Doc 1: Authentication module assigned to Rahul
    doc1_content = b"Engineering Sprint Plan 2026\nThe authentication module is assigned to Rahul for maintenance.\nAll JWT tokens use RS256."
    res_up1 = client.post(
        "/api/v1/sources/upload",
        headers={"Authorization": f"Bearer {token_manager}"},
        data={
            "project_id": proj_id,
            "name": "Sprint Plan Spec",
            "source_type": "Document",
            "access_classification": "Team"
        },
        files={"file": ("sprint_plan.txt", io.BytesIO(doc1_content), "text/plain")}
    )
    assert res_up1.status_code == 200

    # Doc 2: Authentication module maintained by Aman
    doc2_content = b"Tech Lead Handover Notes\nThe authentication module is currently maintained by Aman.\nAutomated rate limiting is enabled."
    res_up2 = client.post(
        "/api/v1/sources/upload",
        headers={"Authorization": f"Bearer {token_manager}"},
        data={
            "project_id": proj_id,
            "name": "Handover Notes",
            "source_type": "Document",
            "access_classification": "Team"
        },
        files={"file": ("handover_notes.txt", io.BytesIO(doc2_content), "text/plain")}
    )
    assert res_up2.status_code == 200

    # Step 3: Upload a third document with an incomplete technical decision
    doc3_content = b"Architecture RFC 092\nThe project decided to adopt SurrealDB as its secondary store.\nPending team review."
    res_up3 = client.post(
        "/api/v1/sources/upload",
        headers={"Authorization": f"Bearer {token_manager}"},
        data={
            "project_id": proj_id,
            "name": "RFC 092 SurrealDB",
            "source_type": "Architecture RFC",
            "access_classification": "Team"
        },
        files={"file": ("rfc_092.txt", io.BytesIO(doc3_content), "text/plain")}
    )
    assert res_up3.status_code == 200

    # Step 4: Add a task record showing an unfinished task
    with SessionLocal() as db:
        t = Task(
            project_id=proj_id,
            title="Idempotency Deduplication Engine",
            description="Zero duplicate settlement guarantee for high throughput queue",
            status="In Progress",
            assignee_name=None,
            assignee_id=None,
            is_completed=False
        )
        db.add(t)
        db.commit()

    # Step 5: Create a restricted source containing a unique secret marker
    unique_secret = "SECRET_MARKER_E2E_VAULT_PASS_XYZ8819"
    restricted_doc = f"Production Vault HSM Specification\nRoot Access Token: {unique_secret}\nStrictly for SecOps.".encode("utf-8")
    res_up_restr = client.post(
        "/api/v1/sources/upload",
        headers={"Authorization": f"Bearer {token_manager}"},
        data={
            "project_id": proj_id,
            "name": "Confidential Vault Specification",
            "source_type": "Document",
            "access_classification": "Restricted"
        },
        files={"file": ("restricted_vault.txt", io.BytesIO(restricted_doc), "text/plain")}
    )
    assert res_up_restr.status_code == 200

    # Step 6, 7 & 8: Verify automated extraction and conflict detection
    conf_res = client.get(
        f"/api/v1/conflicts/?project_id={proj_id}",
        headers={"Authorization": f"Bearer {token_manager}"}
    )
    assert conf_res.status_code == 200
    conflicts = conf_res.json()
    assert len(conflicts) >= 1, "Expected ownership conflict to be automatically detected"
    target_conflict = next(c for c in conflicts if "Authentication" in c["title"] or "Ownership" in c["category"])
    assert "Rahul" in target_conflict["source_a_quote"] or "Rahul" in target_conflict["source_a_claim"]
    assert "Aman" in target_conflict["source_b_quote"] or "Aman" in target_conflict["source_b_claim"]

    # Step 9: Verify targeted knowledge-gap generation
    gaps_res = client.get(
        f"/api/v1/gaps/?project_id={proj_id}",
        headers={"Authorization": f"Bearer {token_manager}"}
    )
    assert gaps_res.status_code == 200
    gaps = gaps_res.json()
    assert len(gaps) >= 1, "Expected automated knowledge gaps to be generated"

    # Step 10 & 11: Log in as incoming successor and ask question supported by permitted evidence
    chat_perm_res = client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_successor}"},
        json={"project_id": proj_id, "query": "What signing algorithm is used for JWT tokens?"}
    )
    assert chat_perm_res.status_code == 200
    chat_perm_data = chat_perm_res.json()
    assert chat_perm_data["is_grounded"] is True
    assert "RS256" in chat_perm_data["answer"]

    # Step 12: Verify accurate citations
    assert len(chat_perm_data["citations"]) > 0
    first_citation = chat_perm_data["citations"][0]
    assert "Sprint Plan" in first_citation["source_name"]
    assert "RS256" in first_citation["exact_quote"]

    # Step 13 & 14: Ask question about restricted content & verify marker is absent
    chat_restr_res = client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_successor}"},
        json={"project_id": proj_id, "query": f"What is the token {unique_secret}?"}
    )
    assert chat_restr_res.status_code == 200
    restr_data = chat_restr_res.json()
    assert unique_secret not in restr_data["answer"]
    assert unique_secret not in str(restr_data["citations"])
    assert "No evidence found" in restr_data["answer"]

    # Step 15 & 16: Ask unsupported question -> verify exact response "No evidence found"
    chat_fake_res = client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_successor}"},
        json={"project_id": proj_id, "query": "What is the cafeteria chocolate chip cookie recipe?"}
    )
    assert chat_fake_res.status_code == 200
    fake_data = chat_fake_res.json()
    assert fake_data["is_grounded"] is False
    assert fake_data["answer"] == "No evidence found"

    # Step 17 & 18: Log in as authorized manager and resolve conflict
    resolve_res = client.post(
        f"/api/v1/conflicts/{target_conflict['id']}/resolve",
        headers={"Authorization": f"Bearer {token_manager}"},
        json={
            "resolution_notes": "Aman is confirmed as primary maintainer; Rahul shifted to payments module.",
            "resolution_status": "Resolved"
        }
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["conflict"]["resolution_status"] == "Resolved"

    # Step 19: Submit missing information through departing employee workflow
    gap_to_answer = gaps[0]
    ans_res = client.post(
        f"/api/v1/gaps/{gap_to_answer['id']}/answer",
        headers={"Authorization": f"Bearer {token_departing}"},
        json={
            "answer": "SurrealDB was selected for graph edge traversals in secondary indexing.",
            "respondent_name": "Sarah Lin (Departing Lead)"
        }
    )
    assert ans_res.status_code == 200
    assert ans_res.json()["question"]["status"] == "Answered"

    # Step 20: Verify new clarification is available to authorized retrieval
    chat_clarify_res = client.post(
        "/api/v1/chat/query",
        headers={"Authorization": f"Bearer {token_successor}"},
        json={"project_id": proj_id, "query": "Why was SurrealDB selected?"}
    )
    assert chat_clarify_res.status_code == 200
    clarify_data = chat_clarify_res.json()
    assert clarify_data["is_grounded"] is True
    assert "SurrealDB" in clarify_data["answer"]
    assert "Sarah Lin" in clarify_data["answer"] or any("Sarah Lin" in c["exact_quote"] for c in clarify_data["citations"])

    # Step 21: Reload and confirm that all relevant changes persist
    with SessionLocal() as db:
        persisted_conf = db.query(Conflict).filter(Conflict.id == target_conflict["id"]).first()
        assert persisted_conf.resolution_status == "Resolved"

        persisted_gap = db.query(KnowledgeGapQuestion).filter(KnowledgeGapQuestion.id == gap_to_answer["id"]).first()
        assert persisted_gap.status == "Answered"

        persisted_claim = db.query(Claim).filter(Claim.claim_code == f"#CLM-GAP-{gap_to_answer['id']}").first()
        assert persisted_claim is not None
        assert "SurrealDB" in persisted_claim.description
