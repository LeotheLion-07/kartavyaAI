from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Set
from app.core.database import get_db
from app.core.security import (
    get_optional_current_user, verify_project_membership, log_audit_event
)
from app.models.models import Claim, User, AccessRequest, Project
from app.schemas.schemas import GroundedChatRequest, GroundedChatResponse
from app.services.grounded_chat import answer_grounded_query

router = APIRouter(prefix="/chat", tags=["Grounded AI Chat"])

@router.post("/query", response_model=GroundedChatResponse)
def query_grounded_assistant(
    payload: GroundedChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user and not verify_project_membership(payload.project_id, current_user, db):
        log_audit_event(
            db=db,
            user_id=current_user.id,
            user_name=current_user.full_name,
            user_role=current_user.role,
            action="RESTRICTED_ACCESS_DENIED",
            entity_type="ChatQuery",
            entity_id=str(payload.project_id),
            details_json={"reason": "User not a member of project"}
        )
        raise HTTPException(status_code=403, detail="Access denied: User is not a member of this project")

    claims = db.query(Claim).filter(Claim.project_id == payload.project_id).all()
    user_role = current_user.role if current_user else "Incoming"
    user_id = current_user.id if current_user else None
    
    approved_claim_ids: Set[int] = set()
    approved_source_ids: Set[int] = set()
    if user_id:
        approved_reqs = db.query(AccessRequest).filter(
            AccessRequest.user_id == user_id,
            AccessRequest.status == "Approved"
        ).all()
        for r in approved_reqs:
            if r.resource_type == "Claim":
                approved_claim_ids.add(r.resource_id)
            elif r.resource_type == "Source":
                approved_source_ids.add(r.resource_id)
        
    response = answer_grounded_query(
        query=payload.query,
        claims=claims,
        user_role=user_role,
        user_id=user_id,
        approved_claim_ids=approved_claim_ids,
        approved_source_ids=approved_source_ids
    )

    log_audit_event(
        db=db,
        user_id=user_id,
        user_name=current_user.full_name if current_user else "Anonymous",
        user_role=user_role,
        action="CHAT_QUERY",
        entity_type="Project",
        entity_id=str(payload.project_id),
        details_json={
            "query": payload.query,
            "is_grounded": response["is_grounded"],
            "evidence_count": response["evidence_count"],
            "redacted_items": response.get("redacted_items_count", 0)
        }
    )

    return response
