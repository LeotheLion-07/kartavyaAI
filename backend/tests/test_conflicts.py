import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import SessionLocal
from app.models.models import User, Project, Source, Claim, Conflict, ProjectMember

client = TestClient(app)

def get_auth_token(email: str):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_conflict_categories_detection():
    """
    Verifies that conflict detection identifies contradictions across all required categories:
    1. Task ownership (Rahul vs Aman)
    2. Project decisions (PostgreSQL vs MongoDB)
    3. Task completion status (Completed vs In Progress)
    4. Deadlines (18 November vs 22 November)
    5. Dependencies (Service A vs Service B)
    """
    token_manager = get_auth_token("alex.morgan@company.internal")
    
    with SessionLocal() as db:
        # Create a dedicated test project
        proj = Project(
            name="Conflict Engine Test Project",
            slug=f"conflict-test-{db.query(Project).count() + 1}",
            description="Testing automated multi-category conflict detection"
        )
        db.add(proj)
        db.commit()
        db.refresh(proj)
        
        # Add manager and members
        alex = db.query(User).filter(User.email == "alex.morgan@company.internal").first()
        marcus = db.query(User).filter(User.email == "marcus.vance@company.internal").first()
        db.add_all([
            ProjectMember(project_id=proj.id, user_id=alex.id, role_in_project="Manager"),
            ProjectMember(project_id=proj.id, user_id=marcus.id, role_in_project="Member")
        ])
        
        # Source A: Document 1
        s1 = Source(
            source_code=f"#SRC-A-{proj.id}",
            project_id=proj.id,
            name="Sprint Spec Document Alpha",
            source_type="Document",
            access_classification="Team",
            processing_status="Processed"
        )
        # Source B: Document 2
        s2 = Source(
            source_code=f"#SRC-B-{proj.id}",
            project_id=proj.id,
            name="Architecture Sync Beta",
            source_type="Slack Thread",
            access_classification="Team",
            processing_status="Processed"
        )
        db.add_all([s1, s2])
        db.commit()
        db.refresh(s1)
        db.refresh(s2)

        # 1. Ownership Claims: Rahul vs Aman on Authentication Module
        c_own_1 = Claim(
            claim_code=f"CLM-OWN1-{proj.id}",
            project_id=proj.id,
            source_id=s1.id,
            title="Ownership: Authentication Module assigned to Rahul",
            description="The authentication module is assigned to Rahul.",
            category="Ownership",
            entity_or_subject="Authentication Module",
            extracted_value="Rahul",
            related_person="Rahul",
            exact_quote="The authentication module is assigned to Rahul.",
            line_span="Span L1-L2",
            evidence_status="VERIFIED"
        )
        c_own_2 = Claim(
            claim_code=f"CLM-OWN2-{proj.id}",
            project_id=proj.id,
            source_id=s2.id,
            title="Ownership: Authentication Module maintained by Aman",
            description="The authentication module is currently maintained by Aman.",
            category="Ownership",
            entity_or_subject="Authentication Module",
            extracted_value="Aman",
            related_person="Aman",
            exact_quote="The authentication module is currently maintained by Aman.",
            line_span="Span L5-L6",
            evidence_status="VERIFIED"
        )

        # 2. Decision Claims: PostgreSQL vs MongoDB on Primary Database
        c_dec_1 = Claim(
            claim_code=f"CLM-DEC1-{proj.id}",
            project_id=proj.id,
            source_id=s1.id,
            title="Decision: Primary Database uses PostgreSQL",
            description="The project uses PostgreSQL as its primary database.",
            category="Decision",
            entity_or_subject="Primary Database",
            extracted_value="PostgreSQL",
            exact_quote="The project uses PostgreSQL as its primary database.",
            line_span="Span L10-L12",
            evidence_status="VERIFIED"
        )
        c_dec_2 = Claim(
            claim_code=f"CLM-DEC2-{proj.id}",
            project_id=proj.id,
            source_id=s2.id,
            title="Decision: Primary Database specifies MongoDB",
            description="The project migration decision specifies MongoDB.",
            category="Decision",
            entity_or_subject="Primary Database",
            extracted_value="MongoDB",
            exact_quote="The project migration decision specifies MongoDB.",
            line_span="Span L8-L10",
            evidence_status="VERIFIED"
        )

        # 3. Status Claims: Completed vs In Progress on Payment Module
        c_stat_1 = Claim(
            claim_code=f"CLM-STAT1-{proj.id}",
            project_id=proj.id,
            source_id=s1.id,
            title="Status: Payment Module completed",
            description="The payment module has been completed.",
            category="TaskStatus",
            entity_or_subject="Payment Module",
            extracted_value="Completed",
            exact_quote="The payment module has been completed.",
            line_span="Span L15-L16",
            evidence_status="VERIFIED"
        )
        c_stat_2 = Claim(
            claim_code=f"CLM-STAT2-{proj.id}",
            project_id=proj.id,
            source_id=s2.id,
            title="Status: Payment Module in progress",
            description="The payment module is still marked as in progress.",
            category="TaskStatus",
            entity_or_subject="Payment Module",
            extracted_value="In Progress",
            exact_quote="The payment module is still marked as in progress.",
            line_span="Span L20-L21",
            evidence_status="VERIFIED"
        )

        # 4. Deadline Claims: 18 November vs 22 November on API Delivery
        c_dl_1 = Claim(
            claim_code=f"CLM-DL1-{proj.id}",
            project_id=proj.id,
            source_id=s1.id,
            title="Deadline: API Delivery target is 18 November",
            description="API delivery deadline: 18 November.",
            category="Deadline",
            entity_or_subject="API Delivery",
            extracted_value="18 November",
            exact_quote="API delivery deadline: 18 November.",
            line_span="Span L30-L31",
            evidence_status="VERIFIED"
        )
        c_dl_2 = Claim(
            claim_code=f"CLM-DL2-{proj.id}",
            project_id=proj.id,
            source_id=s2.id,
            title="Deadline: API Delivery target is 22 November",
            description="API delivery deadline: 22 November.",
            category="Deadline",
            entity_or_subject="API Delivery",
            extracted_value="22 November",
            exact_quote="API delivery deadline: 22 November.",
            line_span="Span L35-L36",
            evidence_status="VERIFIED"
        )

        # 5. Dependency Claims: Service A vs Service B
        c_dep_1 = Claim(
            claim_code=f"CLM-DEP1-{proj.id}",
            project_id=proj.id,
            source_id=s1.id,
            title="Dependency: Notification Service depends on Service A",
            description="Notification Service depends on Service A.",
            category="Dependency",
            entity_or_subject="Notification Service",
            extracted_value="Service A",
            exact_quote="Notification Service depends on Service A.",
            line_span="Span L40-L41",
            evidence_status="VERIFIED"
        )
        c_dep_2 = Claim(
            claim_code=f"CLM-DEP2-{proj.id}",
            project_id=proj.id,
            source_id=s2.id,
            title="Dependency: Notification Service depends on Service B",
            description="Notification Service depends on Service B.",
            category="Dependency",
            entity_or_subject="Notification Service",
            extracted_value="Service B",
            exact_quote="Notification Service depends on Service B.",
            line_span="Span L45-L46",
            evidence_status="VERIFIED"
        )

        db.add_all([
            c_own_1, c_own_2,
            c_dec_1, c_dec_2,
            c_stat_1, c_stat_2,
            c_dl_1, c_dl_2,
            c_dep_1, c_dep_2
        ])
        db.commit()

        # Trigger conflict detection
        detect_res = client.post(
            f"/api/v1/conflicts/detect?project_id={proj.id}",
            headers={"Authorization": f"Bearer {token_manager}"}
        )
        assert detect_res.status_code == 200
        detected_count = detect_res.json()["conflicts_detected"]
        assert detected_count >= 5, f"Expected at least 5 conflicts, got {detected_count}"

        # Fetch conflicts
        conf_res = client.get(
            f"/api/v1/conflicts/?project_id={proj.id}",
            headers={"Authorization": f"Bearer {token_manager}"}
        )
        assert conf_res.status_code == 200
        conflicts = conf_res.json()
        categories = {c["category"] for c in conflicts}

        assert "Ownership" in categories
        assert "Decision" in categories
        assert "TaskCompletion" in categories or "TaskStatus" in categories
        assert "Deadline" in categories
        assert "Dependency" in categories

        # Verify side-by-side evidence is present
        own_conf = next(c for c in conflicts if c["category"] == "Ownership")
        assert "Rahul" in own_conf["source_a_quote"] or "Rahul" in own_conf["source_a_claim"]
        assert "Aman" in own_conf["source_b_quote"] or "Aman" in own_conf["source_b_claim"]

def test_conflict_deduplication_on_repeated_ingestion():
    """Verify that re-running conflict detection does not duplicate records."""
    token_manager = get_auth_token("alex.morgan@company.internal")
    with SessionLocal() as db:
        proj = db.query(Project).filter(Project.name == "Conflict Engine Test Project").order_by(Project.id.desc()).first()
        assert proj is not None

        # Re-run detection
        res = client.post(
            f"/api/v1/conflicts/detect?project_id={proj.id}",
            headers={"Authorization": f"Bearer {token_manager}"}
        )
        assert res.status_code == 200
        assert res.json()["conflicts_detected"] == 0, "Repeated detection must be idempotent with 0 duplicates"

def test_conflict_resolution_persistence():
    """Verify that an authorized manager can resolve a conflict and it persists."""
    token_manager = get_auth_token("alex.morgan@company.internal")
    with SessionLocal() as db:
        proj = db.query(Project).filter(Project.name == "Conflict Engine Test Project").order_by(Project.id.desc()).first()
        conf = db.query(Conflict).filter(Conflict.project_id == proj.id).first()
        assert conf is not None

        # Resolve conflict
        resolve_res = client.post(
            f"/api/v1/conflicts/{conf.id}/resolve",
            headers={"Authorization": f"Bearer {token_manager}"},
            json={
                "resolution_notes": "Aman is confirmed as the primary maintainer following sprint re-allocation.",
                "resolution_status": "Resolved"
            }
        )
        assert resolve_res.status_code == 200
        updated = resolve_res.json()["conflict"]
        assert updated["resolution_status"] == "Resolved"

        # Verify persistence on re-query
        get_res = client.get(
            f"/api/v1/conflicts/?project_id={proj.id}",
            headers={"Authorization": f"Bearer {token_manager}"}
        )
        persisted = next(c for c in get_res.json() if c["id"] == conf.id)
        assert persisted["resolution_status"] == "Resolved"
        assert "Aman" in persisted["resolution_notes"]

        # Verify original claims are preserved
        assert db.query(Claim).filter(Claim.id == conf.claim_a_id).first() is not None
        assert db.query(Claim).filter(Claim.id == conf.claim_b_id).first() is not None
