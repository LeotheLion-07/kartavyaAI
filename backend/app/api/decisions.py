from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Decision, User, AuditLog
from app.schemas.schemas import DecisionCreate, DecisionResponse

router = APIRouter(prefix="/decisions", tags=["Decisions Timeline"])

@router.get("/", response_model=List[DecisionResponse])
def list_decisions(
    project_id: Optional[int] = None,
    person: Optional[str] = None,
    evidence_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Decision)
    if project_id:
        query = query.filter(Decision.project_id == project_id)
    if person:
        query = query.filter(Decision.person_responsible.ilike(f"%{person}%"))
    if evidence_status and evidence_status.upper() != "ALL":
        query = query.filter(Decision.evidence_status == evidence_status.upper())
    return query.order_by(Decision.date.desc()).all()

@router.post("/", response_model=DecisionResponse)
def create_decision(
    decision_in: DecisionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dec = Decision(
        decision_code=decision_in.decision_code,
        project_id=decision_in.project_id,
        title=decision_in.title,
        date=decision_in.date,
        person_responsible=decision_in.person_responsible or current_user.full_name,
        rationale=decision_in.rationale,
        alternatives_evaluated=decision_in.alternatives_evaluated,
        supporting_evidence=decision_in.supporting_evidence,
        is_reversed=decision_in.is_reversed,
        is_unresolved=decision_in.is_unresolved,
        evidence_status=decision_in.evidence_status,
        tags=decision_in.tags
    )
    db.add(dec)
    db.commit()
    db.refresh(dec)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="DECISION_CREATE",
        entity_type="Decision",
        entity_id=dec.decision_code,
        details_json={"title": dec.title}
    )
    db.add(audit)
    db.commit()
    return dec
