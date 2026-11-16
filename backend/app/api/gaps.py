from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import hashlib
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user, verify_project_membership, log_audit_event
from app.models.models import KnowledgeGapQuestion, Claim, User, AuditLog
from app.schemas.schemas import KnowledgeGapCreate, KnowledgeGapAnswer, KnowledgeGapResponse
from app.services.gap_detector import detect_and_generate_gap_questions

router = APIRouter(prefix="/gaps", tags=["Knowledge Gap Questions"])

@router.get("/", response_model=List[KnowledgeGapResponse])
def list_gap_questions(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeGapQuestion)
    if project_id:
        if current_user and not verify_project_membership(project_id, current_user, db):
            raise HTTPException(status_code=403, detail="Access denied: User is not a member of this project")
        query = query.filter(KnowledgeGapQuestion.project_id == project_id)
    if status and status.upper() != "ALL":
        query = query.filter(KnowledgeGapQuestion.status == status)
    return query.order_by(KnowledgeGapQuestion.id.asc()).all()

@router.post("/detect")
def trigger_gap_detection(
    project_id: int,
    handover_case_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Triggers automated scan across 10 knowledge dimensions to generate targeted questions."""
    if not verify_project_membership(project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Forbidden: User is not a member of this project")

    created = detect_and_generate_gap_questions(
        project_id=project_id,
        db=db,
        handover_case_id=handover_case_id
    )
    return {
        "status": "success",
        "questions_generated": len(created),
        "questions": [{"id": q.id, "question": q.question, "priority": q.priority} for q in created]
    }

@router.post("/", response_model=KnowledgeGapResponse)
def create_gap_question(
    question_in: KnowledgeGapCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = KnowledgeGapQuestion(
        project_id=question_in.project_id,
        handover_case_id=question_in.handover_case_id,
        category=question_in.category or "DecisionRationale",
        entity_or_subject=question_in.entity_or_subject,
        priority=question_in.priority or "High",
        question=question_in.question,
        rationale=question_in.rationale,
        target_user_name=question_in.target_user_name or "Sarah Lin (Departing Lead)",
        status="Open",
        is_clarification=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    
    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="GAP_QUESTION_CREATE",
        entity_type="KnowledgeGap",
        entity_id=str(q.id),
        details_json={"question": q.question}
    )
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
    
    # Store clarification as a distinct claim with explicit human clarification provenance
    # so that subsequent assistant retrieval can use it
    sig = hashlib.sha256(f"CLARIFY:{q.id}:{payload.answer}".encode("utf-8")).hexdigest()
    claim_code = f"#CLM-GAP-{q.id}"
    
    existing_claim = db.query(Claim).filter(Claim.claim_code == claim_code).first()
    if not existing_claim:
        clarification_claim = Claim(
            claim_code=claim_code,
            project_id=q.project_id,
            handover_case_id=q.handover_case_id,
            title=f"Clarification: {q.question[:65]}",
            description=f"Human clarification provided by {q.respondent_name}: {payload.answer}",
            category=q.category or "Clarification",
            entity_or_subject=q.entity_or_subject or q.question[:40],
            extracted_value=payload.answer[:80],
            evidence_status="INFERRED",
            confidence_score=0.90,
            verification_method="Human Clarification",
            exact_quote=f"Human Clarification by {q.respondent_name}: \"{payload.answer}\"",
            line_span="Recorded Clarification",
            cryptographic_root=f"sha256:{sig[:8]}...{sig[-6:]}",
            golden_ref=False,
            related_person=q.respondent_name,
            author_id=current_user.id,
            access_classification="Team",
            is_approved=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(clarification_claim)
    else:
        existing_claim.description = f"Human clarification provided by {q.respondent_name}: {payload.answer}"
        existing_claim.exact_quote = f"Human Clarification by {q.respondent_name}: \"{payload.answer}\""
        existing_claim.updated_at = datetime.now(timezone.utc)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="GAP_QUESTION_ANSWER",
        entity_type="KnowledgeGap",
        entity_id=str(q.id),
        details_json={
            "respondent": q.respondent_name,
            "clarification": True,
            "question": q.question
        }
    )
    db.commit()
    db.refresh(q)
    return {"status": "success", "question": q}
