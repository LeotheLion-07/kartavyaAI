from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import (
    get_current_user, get_optional_current_user,
    is_manager_or_admin, verify_project_membership, log_audit_event
)
from app.core.dlp import redact_conflict_if_restricted
from app.models.models import Conflict, Claim, User, AuditLog, HandoverReport, AccessRequest
from app.schemas.schemas import ConflictCreate, ConflictResolve, ConflictResponse
from app.services.conflict_detector import detect_and_persist_conflicts

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])

@router.get("/", response_model=List[ConflictResponse])
def list_conflicts(
    project_id: Optional[int] = None,
    resolution_status: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Conflict)
    if project_id:
        if current_user and not verify_project_membership(project_id, current_user, db):
            log_audit_event(
                db=db,
                user_id=current_user.id,
                user_name=current_user.full_name,
                user_role=current_user.role,
                action="RESTRICTED_ACCESS_DENIED",
                entity_type="Project",
                entity_id=str(project_id),
                details_json={"reason": "User not a member of project"}
            )
            raise HTTPException(status_code=403, detail="Access denied: User is not a member of this project")
        query = query.filter(Conflict.project_id == project_id)
        
    if resolution_status and resolution_status.upper() != "ALL":
        query = query.filter(Conflict.resolution_status == resolution_status)
        
    conflicts = query.order_by(Conflict.id.desc()).all()
    
    # Resolve approved access requests for the user
    user_role = current_user.role if current_user else "Incoming"
    user_id = current_user.id if current_user else None
    approved_ids = set()
    if user_id:
        approved_reqs = db.query(AccessRequest).filter(
            AccessRequest.user_id == user_id,
            AccessRequest.status == "Approved"
        ).all()
        approved_ids = {r.resource_id for r in approved_reqs}

    results = []
    for c in conflicts:
        c_dict = {
            "id": c.id,
            "conflict_code": c.conflict_code,
            "project_id": c.project_id,
            "handover_case_id": c.handover_case_id,
            "title": c.title,
            "description": c.description,
            "category": c.category or "Ownership",
            "entity_or_subject": c.entity_or_subject,
            "detection_reason": c.detection_reason,
            "claim_a_id": c.claim_a_id,
            "claim_b_id": c.claim_b_id,
            "source_a_label": c.source_a_label,
            "source_a_quote": c.source_a_quote,
            "source_a_claim": c.source_a_claim,
            "source_a_value": c.source_a_value,
            "source_b_label": c.source_b_label,
            "source_b_quote": c.source_b_quote,
            "source_b_claim": c.source_b_claim,
            "source_b_value": c.source_b_value,
            "recommended_fix": c.recommended_fix,
            "resolution_status": c.resolution_status,
            "resolution_notes": c.resolution_notes,
            "resolved_by_id": c.resolved_by_id,
            "resolved_at": c.resolved_at,
            "access_classification": c.access_classification or "Team",
            "created_at": c.created_at
        }
        redacted = redact_conflict_if_restricted(c_dict, user_role, user_id, approved_ids)
        results.append(redacted)

    return results

@router.post("/detect")
def trigger_conflict_detection(
    project_id: int,
    handover_case_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Triggers automated cross-source conflict detection on project claims."""
    if not verify_project_membership(project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Forbidden: User is not a member of this project")

    created = detect_and_persist_conflicts(project_id, db, handover_case_id)
    return {
        "status": "success",
        "conflicts_detected": len(created),
        "conflicts": [c.conflict_code for c in created]
    }

@router.post("/{conflict_id}/resolve")
def resolve_conflict(
    conflict_id: int,
    payload: ConflictResolve,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Authoritative conflict resolution. Only authorized managers, admins, or owners can resolve."""
    conf = db.query(Conflict).filter(Conflict.id == conflict_id).first()
    if not conf:
        raise HTTPException(status_code=404, detail="Conflict not found")

    # Security check: only managers or admins can resolve
    if not is_manager_or_admin(current_user):
        log_audit_event(
            db=db,
            user_id=current_user.id,
            user_name=current_user.full_name,
            user_role=current_user.role,
            action="RESTRICTED_ACCESS_DENIED",
            entity_type="Conflict",
            entity_id=conf.conflict_code,
            details_json={"reason": "Unauthorized conflict resolution attempt"}
        )
        raise HTTPException(status_code=403, detail="Forbidden: Only authorized managers or administrators can resolve conflicts.")

    new_status = payload.resolution_status or "Resolved"
    conf.resolution_status = new_status
    conf.resolution_notes = payload.resolution_notes or payload.accepted_fix
    conf.resolved_by_id = current_user.id
    conf.resolved_at = datetime.now(timezone.utc)
    
    # Update claim status without deleting or overwriting original evidence
    if conf.claim_a_id:
        claim_a = db.query(Claim).filter(Claim.id == conf.claim_a_id).first()
        if claim_a:
            claim_a.evidence_status = "VERIFIED" if new_status == "Resolved" else "CONFLICTING"
    if conf.claim_b_id:
        claim_b = db.query(Claim).filter(Claim.id == conf.claim_b_id).first()
        if claim_b:
            claim_b.evidence_status = "VERIFIED" if new_status == "Resolved" else "CONFLICTING"
            
    # Update HandoverReport Manager Checklist if any
    reports = db.query(HandoverReport).all()
    for r in reports:
        if r.manager_checklist_json:
            updated_list = []
            for item in r.manager_checklist_json:
                if item.get("id") == "conflicts":
                    item["ready"] = (new_status == "Resolved")
                    item["detail"] = f"Conflict {conf.conflict_code} resolved by {current_user.full_name}"
                updated_list.append(item)
            r.manager_checklist_json = updated_list
            
    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CONFLICT_RESOLVE",
        entity_type="Conflict",
        entity_id=conf.conflict_code,
        details_json={
            "status": new_status,
            "notes": conf.resolution_notes,
            "resolver": current_user.full_name
        }
    )
    db.commit()
    db.refresh(conf)
    
    return {
        "status": "success",
        "message": f"Conflict {conf.conflict_code} updated to {new_status}",
        "conflict": conf
    }
