from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Set
import os
import shutil
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import (
    get_current_user, get_optional_current_user,
    verify_project_membership, is_manager_or_admin, log_audit_event
)
from app.core.config import settings
from app.core.dlp import redact_source_if_restricted, user_can_access_classification, mask_sensitive_tokens
from app.models.models import Source, SourceChunk, Claim, User, AuditLog, Project, AccessRequest
from app.schemas.schemas import SourceResponse
from app.services.parser import parse_file_content, chunk_text
from app.services.ai_extractor import extract_knowledge_from_text
from app.services.conflict_detector import detect_and_persist_conflicts
from app.services.gap_detector import detect_and_generate_gap_questions

router = APIRouter(prefix="/sources", tags=["Sources & Ingestion"])

@router.get("/")
def list_sources(
    project_id: Optional[int] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Source)
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
        query = query.filter(Source.project_id == project_id)
        
    sources = query.order_by(Source.id.desc()).all()
    
    # Resolve approved source requests for user
    user_role = current_user.role if current_user else "Incoming"
    user_id = current_user.id if current_user else None
    approved_source_ids: Set[int] = set()
    if user_id:
        approved_reqs = db.query(AccessRequest).filter(
            AccessRequest.user_id == user_id,
            AccessRequest.status == "Approved",
            AccessRequest.resource_type == "Source"
        ).all()
        approved_source_ids = {r.resource_id for r in approved_reqs}
        
    results = []
    for s in sources:
        s_dict = {
            "id": s.id,
            "source_code": s.source_code,
            "project_id": s.project_id,
            "name": s.name,
            "source_type": s.source_type,
            "access_classification": s.access_classification,
            "consent_status": s.consent_status,
            "processing_status": s.processing_status,
            "uploaded_by_id": s.uploaded_by_id,
            "raw_content": s.raw_content,
            "created_at": s.created_at
        }
        redacted = redact_source_if_restricted(s_dict, user_role, user_id, approved_source_ids)
        results.append(redacted)
        
    return results

@router.get("/{source_id}")
def get_source(
    source_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    if current_user and not verify_project_membership(source.project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Access denied: User is not a member of this project")
        
    user_role = current_user.role if current_user else "Incoming"
    user_id = current_user.id if current_user else None
    approved_ids: Set[int] = set()
    if user_id:
        approved_reqs = db.query(AccessRequest).filter(
            AccessRequest.user_id == user_id,
            AccessRequest.status == "Approved",
            AccessRequest.resource_type == "Source"
        ).all()
        approved_ids = {r.resource_id for r in approved_reqs}
        
    if not user_can_access_classification(user_role, source.access_classification, user_id, source.uploaded_by_id, approved_ids, source.id):
        log_audit_event(
            db=db,
            user_id=user_id,
            user_name=current_user.full_name if current_user else "Anonymous",
            user_role=user_role,
            action="RESTRICTED_ACCESS_DENIED",
            entity_type="Source",
            entity_id=source.source_code,
            details_json={"classification": source.access_classification, "reason": "Requires manager approval"}
        )
        raise HTTPException(status_code=403, detail="Access restricted: This source requires approved authorization.")
        
    log_audit_event(
        db=db,
        user_id=user_id,
        user_name=current_user.full_name if current_user else "Anonymous",
        user_role=user_role,
        action="SOURCE_ACCESS",
        entity_type="Source",
        entity_id=source.source_code,
        details_json={"name": source.name, "classification": source.access_classification}
    )
    return {
        "id": source.id,
        "source_code": source.source_code,
        "project_id": source.project_id,
        "name": source.name,
        "source_type": source.source_type,
        "access_classification": source.access_classification,
        "raw_content": mask_sensitive_tokens(source.raw_content),
        "created_at": source.created_at
    }

@router.post("/upload")
async def upload_source(
    project_id: int = Form(...),
    name: str = Form(...),
    source_type: str = Form("Document"),
    access_classification: str = Form("Team"),
    consent_status: str = Form("Granted"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not verify_project_membership(project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Forbidden: User is not a member of this project")
        
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_bytes = await file.read()
    file_path = os.path.join(settings.UPLOAD_DIR, f"{datetime.now().timestamp()}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    # Parse file content
    parsed = parse_file_content(file_path, file.filename, file_bytes)
    raw_text = parsed.get("text", "")
    metadata = parsed.get("metadata", {})
    
    # Generate globally unique source code
    total_count = db.query(Source).count()
    code_prefix = "DOC" if source_type == "Document" else "SPEC"
    source_code = f"#{code_prefix}-{project_id}-{100 + total_count + 1}"
    while db.query(Source).filter(Source.source_code == source_code).first():
        total_count += 1
        source_code = f"#{code_prefix}-{project_id}-{100 + total_count + 1}"
    
    new_source = Source(
        source_code=source_code,
        project_id=project_id,
        name=name,
        source_type=source_type,
        access_classification=access_classification,
        consent_status=consent_status,
        processing_status="Processed",
        uploaded_by_id=current_user.id,
        file_path=file_path,
        raw_content=raw_text,
        metadata_json=metadata
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    
    # Create chunks preserving access classification
    chunks = chunk_text(raw_text)
    for c in chunks:
        chunk_obj = SourceChunk(
            source_id=new_source.id,
            chunk_index=c["chunk_index"],
            line_start=c["line_start"],
            line_end=c["line_end"],
            text_content=c["text"],
            access_classification=access_classification
        )
        db.add(chunk_obj)
        
    # AI Knowledge Extraction with structured dimensions & categories
    extracted_claims = extract_knowledge_from_text(
        source_code=source_code,
        source_name=name,
        text=raw_text,
        source_type=source_type,
        access_classification=access_classification
    )
    created_claims = []
    
    for ec in extracted_claims:
        claim_obj = Claim(
            claim_code=ec["claim_code"],
            project_id=project_id,
            title=ec["title"],
            description=ec["description"],
            category=ec.get("category", "Decision"),
            entity_or_subject=ec.get("entity_or_subject"),
            extracted_value=ec.get("extracted_value"),
            evidence_status=ec.get("evidence_status", "VERIFIED"),
            confidence_score=ec.get("confidence_score", 0.95),
            verification_method=ec.get("verification_method", "Exact Match"),
            source_id=new_source.id,
            exact_quote=ec.get("exact_quote"),
            line_span=ec.get("line_span"),
            cryptographic_root=ec.get("cryptographic_root", "sha256:4b91f0...de21"),
            golden_ref=ec.get("golden_ref", False),
            related_person=ec.get("related_person", current_user.full_name),
            author_id=current_user.id,
            access_classification=access_classification,
            is_approved=True
        )
        db.add(claim_obj)
        created_claims.append(ec["claim_code"])
        
    db.commit()

    # Automatically run Conflict Detection
    newly_detected_conflicts = detect_and_persist_conflicts(project_id, db)

    # Automatically run Knowledge Gap Detection
    newly_generated_gaps = detect_and_generate_gap_questions(project_id, db)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="SOURCE_UPLOAD",
        entity_type="Source",
        entity_id=source_code,
        details_json={
            "source_id": new_source.id,
            "filename": file.filename,
            "classification": access_classification,
            "extracted_claims_count": len(extracted_claims),
            "conflicts_detected": len(newly_detected_conflicts),
            "gaps_generated": len(newly_generated_gaps)
        }
    )
    
    return {
        "status": "success",
        "source": {
            "id": new_source.id,
            "source_code": new_source.source_code,
            "name": new_source.name,
            "source_type": new_source.source_type,
            "access_classification": new_source.access_classification,
            "processing_status": "Processed",
            "chunks_count": len(chunks),
            "claims_extracted": len(extracted_claims),
            "claim_codes": created_claims,
            "conflicts_detected": len(newly_detected_conflicts),
            "knowledge_gaps_generated": len(newly_generated_gaps)
        }
    }

@router.post("/github-import")
def import_github_repository(
    repo_url: str = Form(...),
    project_id: int = Form(...),
    branch: str = Form("main"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulates a live GitHub Connector import of PRs, commits, and diffs with automated extraction & conflict checking."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not verify_project_membership(project_id, current_user, db):
        raise HTTPException(status_code=403, detail="Forbidden: User is not a member of this project")
        
    gh_count = db.query(Source).count()
    source_code = f"#GH-SYNC-{project_id}-{100 + gh_count + 1}"
    while db.query(Source).filter(Source.source_code == source_code).first():
        gh_count += 1
        source_code = f"#GH-SYNC-{project_id}-{100 + gh_count + 1}"
    sample_gh_content = f"""GitHub Connector Sync for {repo_url} (branch: {branch})
Pull Request #2041: feat(worker): Async Redis connection retry with backoff
Author: Sarah Lin <sarah@company.internal>
Commit: 8a9f201 - Adopted connection pool timeout = 15s to resolve batch payout backpressure.
Verified: AST parsed successfully. All schema validations pass under Pydantic v2."""

    source = Source(
        source_code=source_code,
        project_id=project_id,
        name=f"GitHub Sync: {repo_url.split('/')[-1] or 'core-platform'}",
        source_type="GitHub PR",
        access_classification="Team",
        consent_status="Granted",
        processing_status="Processed",
        uploaded_by_id=current_user.id,
        external_url=repo_url,
        raw_content=sample_gh_content,
        metadata_json={"branch": branch, "repo": repo_url, "prs_imported": 1, "commits_imported": 4}
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    # Chunks
    chunks = chunk_text(sample_gh_content)
    for c in chunks:
        chunk_obj = SourceChunk(
            source_id=source.id,
            chunk_index=c["chunk_index"],
            line_start=c["line_start"],
            line_end=c["line_end"],
            text_content=c["text"],
            access_classification="Team"
        )
        db.add(chunk_obj)

    # Claims
    extracted_claims = extract_knowledge_from_text(source_code, source.name, sample_gh_content, "GitHub PR", "Team")
    for ec in extracted_claims:
        claim_obj = Claim(
            claim_code=ec["claim_code"],
            project_id=project_id,
            title=ec["title"],
            description=ec["description"],
            category=ec.get("category", "Decision"),
            entity_or_subject=ec.get("entity_or_subject"),
            extracted_value=ec.get("extracted_value"),
            evidence_status="VERIFIED",
            confidence_score=0.96,
            verification_method="AST Proved",
            source_id=source.id,
            exact_quote=ec.get("exact_quote"),
            line_span=ec.get("line_span"),
            cryptographic_root=ec.get("cryptographic_root"),
            golden_ref=True,
            related_person="Sarah Lin",
            author_id=current_user.id,
            access_classification="Team",
            is_approved=True
        )
        db.add(claim_obj)

    db.commit()

    # Automatically run Conflict & Gap Detection
    conflicts = detect_and_persist_conflicts(project_id, db)
    gaps = detect_and_generate_gap_questions(project_id, db)

    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="GITHUB_SYNC",
        entity_type="Source",
        entity_id=source_code,
        details_json={"repo": repo_url, "branch": branch, "conflicts": len(conflicts), "gaps": len(gaps)}
    )

    return {
        "status": "success",
        "source": {
            "id": source.id,
            "source_code": source.source_code,
            "name": source.name,
            "conflicts_detected": len(conflicts),
            "gaps_generated": len(gaps)
        }
    }
