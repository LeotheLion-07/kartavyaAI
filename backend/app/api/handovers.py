from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import hashlib
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user
from app.core.dlp import mask_sensitive_tokens
from app.models.models import (
    HandoverCase, HandoverReport, HandoverAcknowledgement,
    Claim, Conflict, Task, Decision, KnowledgeGapQuestion, User, AuditLog
)
from app.schemas.schemas import HandoverReportResponse, AcknowledgeRequest
from app.services.handover_generator import generate_handover_report_payload

router = APIRouter(prefix="/handovers", tags=["Handovers & Role Views"])

@router.get("/cases")
def list_handover_cases(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(HandoverCase)
    if project_id:
        query = query.filter(HandoverCase.project_id == project_id)
    cases = query.all()
    results = []
    for c in cases:
        dep = db.query(User).filter(User.id == c.departing_user_id).first()
        succ = db.query(User).filter(User.id == c.successor_user_id).first()
        appr = db.query(User).filter(User.id == c.approver_user_id).first()
        ack = db.query(HandoverAcknowledgement).filter(HandoverAcknowledgement.handover_case_id == c.id).first()
        results.append({
            "id": c.id,
            "case_number": c.case_number,
            "project_id": c.project_id,
            "project_name": c.project.name if c.project else "Project",
            "title": c.title,
            "stage": c.stage,
            "status": c.status,
            "target_cutover_date": c.target_cutover_date,
            "grounded_pct": c.grounded_pct,
            "consensus_status": c.consensus_status,
            "departing_user": {"name": dep.full_name, "title": dep.title, "email": dep.email, "avatar": dep.avatar_url} if dep else None,
            "successor_user": {"name": succ.full_name, "title": succ.title, "email": succ.email, "avatar": succ.avatar_url} if succ else None,
            "approver_user": {"name": appr.full_name, "title": appr.title, "email": appr.email, "avatar": appr.avatar_url} if appr else None,
            "is_acknowledged": ack is not None,
            "acknowledged_at": ack.acknowledged_at if ack else None
        })
    return results

@router.get("/case/{case_id}")
def get_handover_case_full(
    case_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    case = db.query(HandoverCase).filter(HandoverCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Handover case not found")
        
    report = db.query(HandoverReport).filter(HandoverReport.handover_case_id == case_id).order_by(HandoverReport.id.desc()).first()
    ack = db.query(HandoverAcknowledgement).filter(HandoverAcknowledgement.handover_case_id == case_id).first()
    tasks = db.query(Task).filter(Task.handover_case_id == case_id).all()
    conflicts = db.query(Conflict).filter(Conflict.handover_case_id == case_id).all()
    gaps = db.query(KnowledgeGapQuestion).filter(KnowledgeGapQuestion.handover_case_id == case_id).all()
    
    dep = db.query(User).filter(User.id == case.departing_user_id).first()
    succ = db.query(User).filter(User.id == case.successor_user_id).first()
    appr = db.query(User).filter(User.id == case.approver_user_id).first()
    
    return {
        "case": {
            "id": case.id,
            "case_number": case.case_number,
            "project_id": case.project_id,
            "project_name": case.project.name if case.project else "",
            "title": case.title,
            "stage": case.stage,
            "status": case.status,
            "target_cutover_date": case.target_cutover_date,
            "grounded_pct": case.grounded_pct,
            "consensus_status": case.consensus_status,
            "departing_user": {"id": dep.id, "name": dep.full_name, "title": dep.title, "email": dep.email, "avatar": dep.avatar_url} if dep else None,
            "successor_user": {"id": succ.id, "name": succ.full_name, "title": succ.title, "email": succ.email, "avatar": succ.avatar_url} if succ else None,
            "approver_user": {"id": appr.id, "name": appr.full_name, "title": appr.title, "email": appr.email, "avatar": appr.avatar_url} if appr else None,
        },
        "report": report,
        "acknowledgement": ack,
        "tasks": tasks,
        "conflicts": conflicts,
        "gaps": gaps
    }

@router.get("/role-view/{role_type}")
def get_role_view(
    role_type: str, # developer, manager, coordinator
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns curated view filtered specifically for:
    - DEVELOPER VIEW (Architecture, code decisions, PRs, bugs, dependencies, pending technical tasks)
    - MANAGER VIEW (Project progress, team responsibilities, risks, deadlines, approvals)
    - COORDINATOR VIEW (Activity, task ownership, communications, upcoming deadlines)
    """
    role = role_type.lower()
    claims = db.query(Claim).filter(Claim.project_id == project_id, Claim.is_approved == True).all()
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    decisions = db.query(Decision).filter(Decision.project_id == project_id).all()
    
    if role == "developer":
        dev_claims = [c for c in claims if c.category in ["Decision", "Blocker", "Dependency", "NextAction"]]
        return {
            "role": "Developer View",
            "critical_systems": [
                {
                    "title": "Payment Settlement Worker",
                    "stack": "FastAPI · RQ Celery · Redis Cluster",
                    "status": "Stable in Prod",
                    "throughput": "4,500 req/s",
                    "p99_latency": "84ms (<150ms SLA)",
                    "infrastructure": "12 EKS Pods",
                    "active_blocker": "Stripe webhook timeout bug during traffic bursts exceeding 4,200 rps batch payouts.",
                    "immediate_action": "Increase async timeout in worker.py: line 84 to 15s and configure exponential backoff in Redis broker."
                },
                {
                    "title": "PostgreSQL 16 + pgvector",
                    "stack": "OLTP Primary · Semantic Vector Embeddings (HNSW)",
                    "status": "Migrated Sprint 41",
                    "description": "Main transaction storage & RAG index with HNSW (m=16, ef_construction=64). Houses all user vectors and contextual decision history.",
                    "scaling_imperative": "Monitor memory footprint as index crosses 800k vectors. Provisioning upgrade to 32GB RAM recommended before reaching 1,000,000 threshold."
                }
            ],
            "technical_decisions": decisions,
            "tasks": tasks,
            "claims": dev_claims
        }
    elif role == "manager":
        mgr_claims = [c for c in claims if c.category in ["Risk", "Owner", "Deadline", "Decision"]]
        return {
            "role": "Manager View",
            "progress_pct": 82,
            "risks_summary": [
                {"title": "Bus Factor 1 on Payment Webhook Engine", "severity": "Critical", "score": "98% Risk", "owner": "Sarah Lin (99.4% module authorship)"},
                {"title": "PgVector Hybrid Search Concentration", "severity": "Medium", "score": "64% Risk", "owner": "Elena Rostova (82% authorship)"}
            ],
            "responsibilities": [
                {"person": "Sarah Lin", "role": "Outgoing Core Lead", "status": "Exit Oct 28"},
                {"person": "Marcus Vance", "role": "Incoming Core Lead", "status": "Ramping Week 2"},
                {"person": "Alex Morgan", "role": "Engineering Manager", "status": "Gate Sign-off"}
            ],
            "claims": mgr_claims,
            "tasks": tasks
        }
    else: # coordinator
        return {
            "role": "Coordinator View",
            "milestones": [
                {"date": "Oct 14", "label": "Pgvector Migration Merged", "status": "Completed"},
                {"date": "Oct 21", "label": "15-Min Knowledge Gap Exit Sync", "status": "Completed"},
                {"date": "Oct 28", "label": "Final Cutover & Access Key Rollover", "status": "Scheduled"}
            ],
            "task_ownership": [t for t in tasks],
            "communications": [
                {"channel": "#eng-payments", "note": "Weekly payments triage notes logged and anchored to PR-1420"}
            ]
        }

@router.post("/case/{case_id}/acknowledge")
def acknowledge_handover_receipt(
    case_id: int,
    payload: AcknowledgeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Allows the successor to sign and acknowledge receipt of the handover package."""
    case = db.query(HandoverCase).filter(HandoverCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    sig = hashlib.sha256(f"ACK:{current_user.email}:{datetime.now(timezone.utc).isoformat()}".encode("utf-8")).hexdigest()
    sig_token = f"sha256:{sig[:8]}...{sig[-6:]}"
    
    ack = HandoverAcknowledgement(
        handover_case_id=case_id,
        successor_user_id=current_user.id,
        signature_token=sig_token,
        notes=payload.notes,
        acknowledged_at=datetime.now(timezone.utc)
    )
    db.add(ack)
    
    case.status = "Acknowledged & Cutover Active"
    case.completed_at = datetime.now(timezone.utc)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="HANDOVER_ACKNOWLEDGED",
        entity_type="HandoverCase",
        entity_id=case.case_number,
        details_json={"signature": sig_token, "notes": payload.notes}
    )
    db.add(audit)
    db.commit()
    db.refresh(ack)
    
    return {
        "status": "success",
        "message": "Handover receipt successfully signed and cryptographically recorded.",
        "acknowledgement": {
            "id": ack.id,
            "signature_token": ack.signature_token,
            "acknowledged_at": ack.acknowledged_at,
            "successor_name": current_user.full_name,
            "notes": ack.notes
        }
    }

@router.post("/case/{case_id}/approve")
def approve_handover_by_manager(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manager Gate sign-off to authorize cutover."""
    case = db.query(HandoverCase).filter(HandoverCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    report = db.query(HandoverReport).filter(HandoverReport.handover_case_id == case_id).first()
    if report:
        report.status = "Published"
        report.approved_by_id = current_user.id
        report.published_at = datetime.now(timezone.utc)
        
    case.status = "Cutover Authorized · Ready for Sign-off"
    case.stage = "Stage 5 of 5 · Final Cutover Execution"
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="HANDOVER_PUBLISH",
        entity_type="HandoverCase",
        entity_id=case.case_number,
        details_json={"authorized_by": current_user.full_name}
    )
    db.add(audit)
    db.commit()
    
    return {"status": "success", "message": "Handover authorized and transition package published."}

@router.put("/tasks/{task_id}/toggle")
def toggle_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggles completion state of onboarding plan task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.is_completed = not task.is_completed
    task.status = "Completed" if task.is_completed else "In Progress"
    db.commit()
    return {"status": "success", "task_id": task.id, "is_completed": task.is_completed}
