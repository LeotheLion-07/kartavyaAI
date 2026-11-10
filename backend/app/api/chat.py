from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_optional_current_user
from app.models.models import Claim, User, AccessRequest
from app.schemas.schemas import GroundedChatRequest, GroundedChatResponse
from app.services.grounded_chat import answer_grounded_query

router = APIRouter(prefix="/chat", tags=["Grounded AI Chat"])

@router.post("/query", response_model=GroundedChatResponse)
def query_grounded_assistant(
    payload: GroundedChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    claims = db.query(Claim).filter(Claim.project_id == payload.project_id).all()
    user_role = current_user.role if current_user else "Incoming"
    
    approved_claim_ids = set()
    if current_user:
        approved_reqs = db.query(AccessRequest).filter(
            AccessRequest.user_id == current_user.id,
            AccessRequest.status == "Approved"
        ).all()
        approved_claim_ids = {r.resource_id for r in approved_reqs}
        
    response = answer_grounded_query(
        query=payload.query,
        claims=claims,
        user_role=user_role,
        approved_claim_ids=approved_claim_ids
    )
    return response
