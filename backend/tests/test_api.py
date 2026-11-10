import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["platform"] == "Kartavya AI"
    assert data["tagline"] == "Pass on what matters, with proof."

def test_login_demo_user():
    res = client.post("/api/v1/auth/login", json={
        "email": "alex.morgan@company.internal",
        "password": "password123"
    })
    assert res.status_code == 200
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["user"]["role"] == "Manager"

def test_projects_list():
    res = client.get("/api/v1/projects/")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) >= 2
    slugs = [p["slug"] for p in projects]
    assert "core-platform-payments" in slugs
    assert "campus-management-system" in slugs

def test_claims_dlp_and_permissions():
    # Incoming user without explicit confidential approval
    res = client.get("/api/v1/claims/?project_id=1")
    assert res.status_code == 200
    data = res.json()
    assert "claims" in data
    assert data["hidden_count"] >= 1
    # Check that confidential claim description is redacted
    redacted_items = [c for c in data["claims"] if c.get("is_redacted") is True]
    assert len(redacted_items) >= 1
    assert "hidden. Request access." in redacted_items[0]["description"]

def test_conflict_resolution():
    res = client.get("/api/v1/conflicts/")
    assert res.status_code == 200
    conflicts = res.json()
    assert len(conflicts) >= 1
    conf_id = conflicts[0]["id"]
    
    # Login as Alex Morgan (Manager)
    login_res = client.post("/api/v1/auth/login", json={
        "email": "alex.morgan@company.internal",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    
    # Resolve conflict
    res_resolve = client.post(
        f"/api/v1/conflicts/{conf_id}/resolve",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "resolution_notes": "Accepted fix: Payments Pod holds L2 triage; SRE automated restart only.",
            "accepted_fix": "Payments Pod L2 triage"
        }
    )
    assert res_resolve.status_code == 200
    assert res_resolve.json()["conflict"]["resolution_status"] == "Resolved"

def test_grounded_chat_zero_hallucination():
    # Query with matching evidence
    res = client.post("/api/v1/chat/query", json={
        "project_id": 1,
        "query": "What is the database pool setup?"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["is_grounded"] is True
    assert len(data["citations"]) > 0
    assert "SQLAlchemy" in data["answer"] or "pool_size" in data["answer"]

    # Query with no matching evidence (must reject and admit lack of proof)
    res_unknown = client.post("/api/v1/chat/query", json={
        "project_id": 1,
        "query": "What is the secret recipe for cafeteria chocolate brownies?"
    })
    assert res_unknown.status_code == 200
    data_unknown = res_unknown.json()
    assert data_unknown["is_grounded"] is False
    assert "No evidence found in the approved project sources." in data_unknown["answer"]

def test_successor_acknowledgement():
    # Login as Marcus Vance (Successor)
    login_res = client.post("/api/v1/auth/login", json={
        "email": "marcus.vance@company.internal",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    
    res = client.post(
        "/api/v1/handovers/case/1/acknowledge",
        headers={"Authorization": f"Bearer {token}"},
        json={"notes": "Successfully assumed on-call rotation and verified AWS cluster access."}
    )
    assert res.status_code == 200
    ack = res.json()["acknowledgement"]
    assert "sha256:" in ack["signature_token"]
