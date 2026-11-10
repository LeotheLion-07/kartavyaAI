from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.models import AccessRequest, User, AuditLog
from app.schemas.schemas import AccessRequestCreate, AccessRequestReview, AccessRequestResponse

router = APIRouter(prefix="/permissions", tags=["Permissions & Access Requests"])

@router.get("/requests", response_model=List[AccessRequestResponse])
def list_access_requests(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AccessRequest)
    # If user is not manager/admin, show only their own requests
    if "admin" not in current_user.role.lower() and "manager" not in current_user.role.lower():
        query = query.filter(AccessRequest.user_id == current_user.id)
    if status and status.upper() != "ALL":
        query = query.filter(AccessRequest.status == status)
        
    requests = query.order_by(AccessRequest.requested_at.desc()).all()
    results = []
    for r in requests:
        u = db.query(User).filter(User.id == r.user_id).first()
        results.append({
            "id": r.id,
            "user_id": r.user_id,
            "user_name": u.full_name if u else "User",
            "resource_type": r.resource_type,
            "resource_id": r.resource_id,
            "resource_name": r.resource_name,
            "reason": r.reason,
            "status": r.status,
            "reviewed_by_id": r.reviewed_by_id,
            "review_comment": r.review_comment,
            "requested_at": r.requested_at,
            "reviewed_at": r.reviewed_at
        })
    return results

@router.post("/request", response_model=AccessRequestResponse)
def create_access_request(
    req_in: AccessRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_req = AccessRequest(
        user_id=current_user.id,
        resource_type=req_in.resource_type,
        resource_id=req_in.resource_id,
        resource_name=req_in.resource_name,
        reason=req_in.reason,
        status="Pending",
        requested_at=datetime.now(timezone.utc)
    )
    db.add(new_req)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="ACCESS_REQUEST",
        entity_type=req_in.resource_type,
        entity_id=str(req_in.resource_id),
        details_json={"resource": req_in.resource_name, "reason": req_in.reason}
    )
    db.add(audit)
    db.commit()
    db.refresh(new_req)
    
    return {
        "id": new_req.id,
        "user_id": new_req.user_id,
        "user_name": current_user.full_name,
        "resource_type": new_req.resource_type,
        "resource_id": new_req.resource_id,
        "resource_name": new_req.resource_name,
        "reason": new_req.reason,
        "status": new_req.status,
        "reviewed_by_id": None,
        "review_comment": None,
        "requested_at": new_req.requested_at,
        "reviewed_at": None
    }

@router.post("/requests/{request_id}/review")
def review_access_request(
    request_id: int,
    review_in: AccessRequestReview,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    req.status = review_in.status
    req.review_comment = review_in.review_comment
    req.reviewed_by_id = current_user.id
    req.reviewed_at = datetime.now(timezone.utc)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action=f"ACCESS_{review_in.status.upper()}",
        entity_type="AccessRequest",
        entity_id=str(req.id),
        details_json={"resource": req.resource_name, "status": req.status, "reviewer": current_user.full_name}
    )
    db.add(audit)
    db.commit()
    db.refresh(req)
    
    return {"status": "success", "message": f"Access request marked as {req.status}", "request": req}
