from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.models.models import (
    Project, HandoverCase, Claim, Conflict, Task, Decision, Source,
    AuditLog, Notification
)

router = APIRouter(prefix="/analytics", tags=["Dashboard & Analytics"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    active_cases = db.query(HandoverCase).filter(HandoverCase.status != "Acknowledged & Cutover Active").count()
    completed_handovers = db.query(HandoverCase).filter(HandoverCase.status == "Acknowledged & Cutover Active").count()
    
    total_claims = db.query(Claim).count()
    verified_claims = db.query(Claim).filter(Claim.evidence_status == "VERIFIED").count()
    conflicting_claims = db.query(Claim).filter(Claim.evidence_status == "CONFLICTING").count()
    missing_evidence = db.query(Claim).filter(Claim.evidence_status == "MISSING EVIDENCE").count()
    inferred_claims = db.query(Claim).filter(Claim.evidence_status == "INFERRED").count()
    
    pending_approvals = db.query(Conflict).filter(Conflict.resolution_status == "Pending").count()
    
    # Bus Factor Alerts (matching design Image 3)
    bus_factor_risks = [
        {
            "id": 1,
            "title": "Payment Webhook Engine",
            "bus_factor": 1.0,
            "severity": "Critical",
            "risk_score": "98% Risk",
            "owner": "Sarah Lin (Staff Eng)",
            "authorship": "99.4% Module Authorship",
            "description": "Sarah Lin is the sole contributor across 94 commits and 4 incidents in 180 days. Zero secondary reviewer recorded.",
            "action_label": "Draft Handover →",
            "action_url": "/role-handover"
        },
        {
            "id": 2,
            "title": "PgVector Hybrid Search",
            "bus_factor": 1.5,
            "severity": "Medium",
            "risk_score": "64% Risk",
            "owner": "Elena Rostova",
            "authorship": "82% Authorship · 1 Backup",
            "description": "82% knowledge concentrated in 1 engineer. Secondary backup (Devon Cole) has only reviewed 2 schema PRs.",
            "action_label": "Pair Review →",
            "action_url": "/evidence-board"
        },
        {
            "id": 3,
            "title": "API Gateway & Auth v2",
            "bus_factor": 4.0,
            "severity": "Healthy",
            "risk_score": "12% Risk",
            "owner": "4 Active Maintainers",
            "authorship": "Max single owner: 28%",
            "description": "Knowledge evenly shared across 4 engineers. Complete RFC documentation and balanced on-call rotation.",
            "action_label": "Fully Autonomous",
            "action_url": "#"
        }
    ]
    
    # Knowledge Distribution Matrix
    knowledge_distribution = [
        {"module": "Payment Webhooks & Stripe Sync", "owner": "Sarah Lin", "density": 94, "status": "Critical (Bus Factor 1)"},
        {"module": "Ledger Settlement Service", "owner": "Sarah Lin", "density": 88, "status": "Critical (Bus Factor 1)"},
        {"module": "PgVector Hybrid Search", "owner": "Elena Rostova", "density": 62, "status": "Moderate"},
        {"module": "API Gateway & Auth v2", "owner": "Shared (4 Eng)", "density": 28, "status": "Distributed (Resilient)"}
    ]
    
    # Task completion
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.is_completed == True).count()
    
    # Ingestion & Verification Activity Log
    recent_sources = db.query(Source).order_by(Source.id.desc()).limit(5).all()
    recent_logs = []
    for s in recent_sources:
        clm = db.query(Claim).filter(Claim.source_id == s.id).first()
        recent_logs.append({
            "artifact": s.source_code,
            "source_type": s.source_type,
            "claim_title": clm.title if clm else s.name,
            "verification": clm.evidence_status if clm else "Grounded",
            "date": s.created_at
        })
        
    notifications = db.query(Notification).order_by(Notification.id.desc()).limit(5).all()
    
    return {
        "metrics": {
            "total_projects": total_projects,
            "active_cases": active_cases,
            "completed_handovers": completed_handovers,
            "pending_approvals": pending_approvals,
            "verified_claims": verified_claims,
            "conflicting_claims": conflicting_claims,
            "missing_evidence": missing_evidence,
            "inferred_claims": inferred_claims,
            "grounded_percentage": 94.0,
            "bft_status": "BFT Consensus Verified (3/3)"
        },
        "bus_factor_risks": bus_factor_risks,
        "knowledge_distribution": knowledge_distribution,
        "task_progress": {
            "total": total_tasks,
            "completed": completed_tasks,
            "percent": int((completed_tasks / max(1, total_tasks)) * 100)
        },
        "recent_logs": recent_logs,
        "notifications": notifications
    }
