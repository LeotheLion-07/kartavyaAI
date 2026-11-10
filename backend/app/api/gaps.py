from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import KnowledgeGapQuestion, User, AuditLog
from app.schemas.schemas import KnowledgeGapCreate, KnowledgeGapAnswer, KnowledgeGapResponse

router = APIRouter(prefix="/gaps", tags=["Knowledge Gap Questions"])

@router.get("/", response_model=List[KnowledgeGapResponse])
def list_gap_questions(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeGapQuestion)
    if project_id:
        query = query.filter(KnowledgeGapQuestion.project_id == project_id)
    if status and status.upper() != "ALL":
        query = query.filter(KnowledgeGapQuestion.status == status)
    return query.order_by(KnowledgeGapQuestion.id.asc()).all()

@router.post("/", response_model=KnowledgeGapResponse)
def create_gap_question(
    question_in: KnowledgeGapCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = KnowledgeGapQuestion(
        project_id=question_in.project_id,
        handover_case_id=question_in.handover_case_id,
        question=question_in.question,
        rationale=question_in.rationale,
        target_user_name=question_in.target_user_name or "Sarah Lin (Departing Lead)",
        status="Open",
        is_clarification=True
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="GAP_QUESTION_CREATE",
        entity_type="KnowledgeGap",
        entity_id=str(q.id),
        details_json={"question": q.question}
    )
    db.add(audit)
    db.commit()
    return q

@router.post("/{question_id}/answer")
def answer_gap_question(
    question_id: int,
    payload: KnowledgeGapAnswer,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(KnowledgeGapQuestion).filter(KnowledgeGapQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
        
    q.answer = payload.answer
    q.status = "Answered"
    q.answered_at = datetime.now(timezone.utc)
    q.respondent_name = payload.respondent_name or current_user.full_name
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="GAP_QUESTION_ANSWER",
        entity_type="KnowledgeGap",
        entity_id=str(q.id),
        details_json={"respondent": q.respondent_name, "clarification": True}
    )
    db.add(audit)
    db.commit()
    db.refresh(q)
    return {"status": "success", "question": q}
