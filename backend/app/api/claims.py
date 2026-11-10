from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user
from app.core.dlp import redact_claim_if_restricted, mask_sensitive_tokens
from app.models.models import Claim, ClaimVersion, Source, User, AuditLog, AccessRequest
from app.schemas.schemas import ClaimCreate, ClaimUpdate, ClaimResponse, ClaimVersionResponse

router = APIRouter(prefix="/claims", tags=["Claims & Evidence"])

@router.get("/")
def list_claims(
    project_id: Optional[int] = None,
    evidence_status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Claim)
    if project_id:
        query = query.filter(Claim.project_id == project_id)
    if evidence_status and evidence_status.upper() != "ALL":
        query = query.filter(Claim.evidence_status == evidence_status.upper())
    if category:
        query = query.filter(Claim.category == category)
        
    claims = query.order_by(Claim.id.desc()).all()
    
    # Get approved claim IDs for the user
    approved_claim_ids = set()
    user_role = current_user.role if current_user else "Incoming"
    user_id = current_user.id if current_user else None
    
    if user_id:
        approved_reqs = db.query(AccessRequest).filter(
            AccessRequest.user_id == user_id,
            AccessRequest.status == "Approved",
            AccessRequest.resource_type == "Claim"
        ).all()
        approved_claim_ids = {req.resource_id for req in approved_reqs}
        
    results = []
    hidden_count = 0
    
    for c in claims:
        # Build dictionary
        c_dict = {
            "id": c.id,
            "claim_code": c.claim_code,
            "project_id": c.project_id,
            "handover_case_id": c.handover_case_id,
            "title": c.title,
            "description": c.description,
            "category": c.category,
            "evidence_status": c.evidence_status,
            "confidence_score": c.confidence_score,
            "verification_method": c.verification_method,
            "source_id": c.source_id,
            "secondary_source_id": c.secondary_source_id,
            "exact_quote": c.exact_quote,
            "line_span": c.line_span,
            "primary_code_diff": c.primary_code_diff,
            "cryptographic_root": c.cryptographic_root,
            "golden_ref": c.golden_ref,
            "related_person": c.related_person,
            "author_id": c.author_id,
            "signoff_reviewer_id": c.signoff_reviewer_id,
            "access_classification": c.access_classification,
            "is_approved": c.is_approved,
            "source_name": c.source.name if c.source else None,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        }
        
        redacted = redact_claim_if_restricted(c_dict, user_role, user_id, approved_claim_ids)
        if redacted.get("is_redacted"):
            hidden_count += 1
        results.append(redacted)
        
    return {
        "claims": results,
        "total_count": len(results),
        "hidden_count": hidden_count
    }

@router.get("/{claim_id}")
def get_claim(
    claim_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    user_role = current_user.role if current_user else "Incoming"
    user_id = current_user.id if current_user else None
    
    approved_claim_ids = set()
    if user_id:
        approved_reqs = db.query(AccessRequest).filter(
            AccessRequest.user_id == user_id,
            AccessRequest.status == "Approved"
        ).all()
        approved_claim_ids = {req.resource_id for req in approved_reqs}
        
    c_dict = {
        "id": claim.id,
        "claim_code": claim.claim_code,
        "project_id": claim.project_id,
        "handover_case_id": claim.handover_case_id,
        "title": claim.title,
        "description": claim.description,
        "category": claim.category,
        "evidence_status": claim.evidence_status,
        "confidence_score": claim.confidence_score,
        "verification_method": claim.verification_method,
        "source_id": claim.source_id,
        "secondary_source_id": claim.secondary_source_id,
        "exact_quote": claim.exact_quote,
        "line_span": claim.line_span,
        "primary_code_diff": claim.primary_code_diff,
        "cryptographic_root": claim.cryptographic_root,
        "golden_ref": claim.golden_ref,
        "related_person": claim.related_person,
        "author_id": claim.author_id,
        "signoff_reviewer_id": claim.signoff_reviewer_id,
        "access_classification": claim.access_classification,
        "is_approved": claim.is_approved,
        "source_name": claim.source.name if claim.source else None,
        "created_at": claim.created_at,
        "updated_at": claim.updated_at
    }
    
    redacted = redact_claim_if_restricted(c_dict, user_role, user_id, approved_claim_ids)
    
    # Fetch version history
    versions = db.query(ClaimVersion).filter(ClaimVersion.claim_id == claim_id).order_by(ClaimVersion.version_num.desc()).all()
    version_list = []
    for v in versions:
        u = db.query(User).filter(User.id == v.changed_by_user_id).first()
        version_list.append({
            "version_num": v.version_num,
            "previous_value": v.previous_value,
            "updated_value": v.updated_value,
            "change_reason": v.change_reason,
            "changed_by": u.full_name if u else "System",
            "timestamp": v.timestamp
        })
        
    return {
        "claim": redacted,
        "versions": version_list
    }

@router.put("/{claim_id}")
def update_claim(
    claim_id: int,
    claim_in: ClaimUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    prev_val = claim.description
    
    if claim_in.title:
        claim.title = claim_in.title
    if claim_in.description:
        claim.description = claim_in.description
    if claim_in.evidence_status:
        claim.evidence_status = claim_in.evidence_status
    if claim_in.confidence_score is not None:
        claim.confidence_score = claim_in.confidence_score
    if claim_in.is_approved is not None:
        claim.is_approved = claim_in.is_approved
        
    # Add version record
    curr_version_count = db.query(ClaimVersion).filter(ClaimVersion.claim_id == claim_id).count()
    ver = ClaimVersion(
        claim_id=claim.id,
        version_num=curr_version_count + 1,
        previous_value=prev_val,
        updated_value=claim.description,
        change_reason=claim_in.change_reason or "Review Board Modification",
        changed_by_user_id=current_user.id
    )
    db.add(ver)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CLAIM_UPDATE",
        entity_type="Claim",
        entity_id=claim.claim_code,
        details_json={"status": claim.evidence_status, "reason": claim_in.change_reason}
    )
    db.add(audit)
    db.commit()
    db.refresh(claim)
    
    return {"status": "success", "claim": claim}

@router.post("/{claim_id}/confirm")
def confirm_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Allows departing staff or manager to confirm an Inferred claim into Verified status."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    prev_status = claim.evidence_status
    claim.evidence_status = "VERIFIED"
    claim.confidence_score = 1.0
    claim.verification_method = "Exact Match"
    
    ver = ClaimVersion(
        claim_id=claim.id,
        version_num=db.query(ClaimVersion).filter(ClaimVersion.claim_id == claim_id).count() + 1,
        previous_value=f"Status: {prev_status}",
        updated_value="Status: VERIFIED (Human Confirmed)",
        change_reason="Confirmed during Review Board triage",
        changed_by_user_id=current_user.id
    )
    db.add(ver)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="CLAIM_CONFIRM",
        entity_type="Claim",
        entity_id=claim.claim_code,
        details_json={"previous_status": prev_status, "new_status": "VERIFIED"}
    )
    db.add(audit)
    db.commit()
    return {"status": "success", "claim": claim}
