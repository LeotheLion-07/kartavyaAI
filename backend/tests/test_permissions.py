import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import SessionLocal
from app.models.models import User, Project, Source, SourceChunk, Claim, AccessRequest, HandoverCase, AuditLog, ProjectMember

client = TestClient(app)

def get_auth_token(email: str):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_unauthenticated_access_denied():
    """Verify that unauthenticated users cannot access protected endpoints."""
    # Attempting to upload source without token
    res = client.post("/api/v1/sources/upload", data={"project_id": 1, "name": "Hack"})
    assert res.status_code == 401

    # Attempting to approve handover without token
    res_appr = client.post("/api/v1/handovers/case/1/approve")
    assert res_appr.status_code == 401

def test_non_member_access_denied():
    """Verify that users cannot access projects they do not belong to."""
    token_marcus = get_auth_token("marcus.vance@company.internal")
    with SessionLocal() as db:
        # Create an isolated project where Marcus is NOT a member
        secret_proj = Project(
            name="Top Secret Admin Project",
            slug=f"secret-proj-{db.query(Project).count() + 100}",
            description="Highly confidential R&D project"
        )
        db.add(secret_proj)
        db.commit()
        db.refresh(secret_proj)

        # Marcus attempts to list sources of this project
        res = client.get(
            f"/api/v1/sources/?project_id={secret_proj.id}",
            headers={"Authorization": f"Bearer {token_marcus}"}
        )
        assert res.status_code == 403
        assert "Access denied" in res.json()["detail"]

        # Marcus attempts to list claims of this project
        res_claims = client.get(
            f"/api/v1/claims/?project_id={secret_proj.id}",
            headers={"Authorization": f"Bearer {token_marcus}"}
        )
        assert res_claims.status_code == 403

        # Verify audit log records access denial
        denial_audit = db.query(AuditLog).filter(
            AuditLog.action == "RESTRICTED_ACCESS_DENIED",
            AuditLog.entity_id == str(secret_proj.id)
        ).first()
        assert denial_audit is not None

def test_unauthorized_approvals_blocked():
    """
    Verify:
    1. Unauthorized users cannot approve access requests (only Manager or Admin).
    2. Unauthorized users cannot approve handovers (only Manager or Admin).
    3. Non-assigned successors cannot acknowledge handovers.
    """
    token_marcus = get_auth_token("marcus.vance@company.internal") # Role: Incoming
    token_alex = get_auth_token("alex.morgan@company.internal")     # Role: Manager

    with SessionLocal() as db:
        marcus = db.query(User).filter(User.email == "marcus.vance@company.internal").first()
        # Create a pending access request
        req = AccessRequest(
            user_id=marcus.id,
            resource_type="Claim",
            resource_id=1,
            resource_name="Confidential HSM Key Vault",
            status="Pending"
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        # Marcus (Incoming) attempts to approve his own request -> MUST BE 403
        res_marcus_approve = client.post(
            f"/api/v1/permissions/requests/{req.id}/review",
            headers={"Authorization": f"Bearer {token_marcus}"},
            json={"status": "Approved", "review_comment": "Self-approved"}
        )
        assert res_marcus_approve.status_code == 403
        assert "Only authorized managers or administrators" in res_marcus_approve.json()["detail"]

        # Alex (Manager) approves the request -> MUST BE 200
        res_alex_approve = client.post(
            f"/api/v1/permissions/requests/{req.id}/review",
            headers={"Authorization": f"Bearer {token_alex}"},
            json={"status": "Approved", "review_comment": "Approved by engineering manager"}
        )
        assert res_alex_approve.status_code == 200
        assert res_alex_approve.json()["request"]["status"] == "Approved"

        # Unauthorized handover approval test:
        # Marcus (Incoming) attempts to approve manager gate on Case 1 -> MUST BE 403
        res_marcus_gate = client.post(
            "/api/v1/handovers/case/1/approve",
            headers={"Authorization": f"Bearer {token_marcus}"}
        )
        assert res_marcus_gate.status_code == 403

def test_successor_only_acknowledgement():
    """Verify that only the assigned successor can acknowledge and sign a handover."""
    token_alex = get_auth_token("alex.morgan@company.internal") # Alex is Manager, NOT successor of Case 1

    # Alex attempts to sign successor receipt for Case 1
    res_alex_ack = client.post(
        "/api/v1/handovers/case/1/acknowledge",
        headers={"Authorization": f"Bearer {token_alex}"},
        json={"notes": "Manager signing as successor illegally"}
    )
    assert res_alex_ack.status_code == 403
    assert "Only the assigned successor can acknowledge" in res_alex_ack.json()["detail"]

def test_mandatory_negative_security_test_restricted_secret_marker():
    """
    MANDATORY NEGATIVE TEST (Section 5.8):
    Add a restricted source containing a unique secret marker.
    Ask the incoming successor a question specifically designed to retrieve that marker.
    Verify that the marker is absent from:
    1. The model context / retrieval set
    2. The API response
    3. The citations
    4. Error messages / UI
    """
    token_marcus = get_auth_token("marcus.vance@company.internal")
    secret_marker = "SECRET_MARKER_KARTAVYA_VAULT_99482X"

    with SessionLocal() as db:
        # 1. Add restricted source to Project 1 with the secret marker
        restricted_source = Source(
            source_code=f"#RESTRICTED-VAULT-{db.query(Source).count() + 1}",
            project_id=1,
            name="Confidential HSM Key Vault Specification",
            source_type="Document",
            access_classification="Restricted", # RESTRICTED
            raw_content=f"Primary encryption master key for payments vault: {secret_marker} (HSM Slot 4).",
            processing_status="Processed"
        )
        db.add(restricted_source)
        db.commit()
        db.refresh(restricted_source)

        restricted_claim = Claim(
            claim_code=f"CLM-RESTRICTED-{restricted_source.id}",
            project_id=1,
            source_id=restricted_source.id,
            title="Confidential HSM Master Key Storage",
            description=f"Vault encryption uses {secret_marker} in production.",
            category="Decision",
            access_classification="Restricted",
            exact_quote=f"Primary encryption master key for payments vault: {secret_marker}",
            evidence_status="VERIFIED",
            is_approved=True
        )
        db.add(restricted_claim)
        db.commit()

        # 2. Marcus (Incoming Successor) queries the Grounded Assistant specifically for the secret marker
        chat_res = client.post(
            "/api/v1/chat/query",
            headers={"Authorization": f"Bearer {token_marcus}"},
            json={
                "project_id": 1,
                "query": f"What is the secret marker {secret_marker}?"
            }
        )
        assert chat_res.status_code == 200
        chat_data = chat_res.json()

        # 3. VERIFY ABSENCE OF SECRET MARKER
        # Marker must NOT be in the answer
        assert secret_marker not in chat_data["answer"]
        # Marker must NOT be in any citations
        for cite in chat_data["citations"]:
            assert secret_marker not in cite["exact_quote"]
            assert secret_marker not in cite["title"]
        # In fact, since no permitted source contains this, it must return "No evidence found"
        assert "No evidence found" in chat_data["answer"]

        # 4. Verify restricted source cannot be directly fetched by successor
        src_res = client.get(
            f"/api/v1/sources/{restricted_source.id}",
            headers={"Authorization": f"Bearer {token_marcus}"}
        )
        assert src_res.status_code == 403
        assert secret_marker not in str(src_res.json())

        # 5. Verify claim listing masks restricted claim
        claims_res = client.get(
            f"/api/v1/claims/?project_id=1",
            headers={"Authorization": f"Bearer {token_marcus}"}
        )
        assert claims_res.status_code == 200
        claims_list = claims_res.json()["claims"]
        target_claim = next(c for c in claims_list if c["id"] == restricted_claim.id)
        assert target_claim["is_redacted"] is True
        assert secret_marker not in str(target_claim)
        assert "1 related item hidden. Request access." in target_claim["description"]
