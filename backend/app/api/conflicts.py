from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Conflict, Claim, User, AuditLog, HandoverReport
from app.schemas.schemas import ConflictCreate, ConflictResolve, ConflictResponse

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])

@router.get("/", response_model=List[ConflictResponse])
def list_conflicts(
    project_id: Optional[int] = None,
    resolution_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Conflict)
    if project_id:
        query = query.filter(Conflict.project_id == project_id)
    if resolution_status and resolution_status.upper() != "ALL":
        query = query.filter(Conflict.resolution_status == resolution_status)
    return query.order_by(Conflict.id.desc()).all()

@router.post("/{conflict_id}/resolve")
def resolve_conflict(
    conflict_id: int,
    payload: ConflictResolve,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conf = db.query(Conflict).filter(Conflict.id == conflict_id).first()
    if not conf:
        raise HTTPException(status_code=404, detail="Conflict not found")
        
    conf.resolution_status = "Resolved"
    conf.resolution_notes = payload.resolution_notes or payload.accepted_fix
    conf.resolved_by_id = current_user.id
    conf.resolved_at = datetime.now(timezone.utc)
    
    # If there is an associated claim marked CONFLICTING, update it
    if conf.claim_a_id:
        claim_a = db.query(Claim).filter(Claim.id == conf.claim_a_id).first()
        if claim_a:
            claim_a.evidence_status = "VERIFIED"
            claim_a.description = f"{claim_a.description} [Resolved by {current_user.full_name}: {payload.resolution_notes}]"
            
    # Update HandoverReport Manager Checklist if any
    reports = db.query(HandoverReport).all()
    for r in reports:
        if r.manager_checklist_json:
            updated_list = []
            for item in r.manager_checklist_json:
                if item.get("id") == "conflicts":
                    item["ready"] = True
                    item["detail"] = f"Conflict {conf.conflict_code} resolved by {current_user.full_name}"
                updated_list.append(item)
            r.manager_checklist_json = updated_list
            
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CONFLICT_RESOLVE",
        entity_type="Conflict",
        entity_id=conf.conflict_code,
        details_json={"notes": conf.resolution_notes, "resolver": current_user.full_name}
    )
    db.add(audit)
    db.commit()
    db.refresh(conf)
    
    return {
        "status": "success",
        "message": f"Conflict {conf.conflict_code} successfully resolved",
        "conflict": conf
    }
