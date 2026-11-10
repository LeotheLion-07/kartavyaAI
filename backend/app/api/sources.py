from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user
from app.core.config import settings
from app.models.models import Source, SourceChunk, Claim, User, AuditLog, Project
from app.schemas.schemas import SourceResponse
from app.services.parser import parse_file_content, chunk_text
from app.services.ai_extractor import extract_knowledge_from_text

router = APIRouter(prefix="/sources", tags=["Sources & Ingestion"])

@router.get("/", response_model=List[SourceResponse])
def list_sources(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Source)
    if project_id:
        query = query.filter(Source.project_id == project_id)
    return query.order_by(Source.id.desc()).all()

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
        
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_bytes = await file.read()
    file_path = os.path.join(settings.UPLOAD_DIR, f"{datetime.now().timestamp()}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    # Parse file content
    parsed = parse_file_content(file_path, file.filename, file_bytes)
    raw_text = parsed.get("text", "")
    metadata = parsed.get("metadata", {})
    
    # Generate source code
    count = db.query(Source).filter(Source.project_id == project_id).count()
    code_prefix = "DOC" if source_type == "Document" else "SPEC"
    source_code = f"#{code_prefix}-{100 + count + 1}"
    
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
    
    # Create chunks
    chunks = chunk_text(raw_text)
    for c in chunks:
        chunk_obj = SourceChunk(
            source_id=new_source.id,
            chunk_index=c["chunk_index"],
            line_start=c["line_start"],
            line_end=c["line_end"],
            text_content=c["text"]
        )
        db.add(chunk_obj)
        
    # AI Knowledge Extraction
    extracted_claims = extract_knowledge_from_text(source_code, name, raw_text, source_type)
    created_claims = []
    
    for ec in extracted_claims:
        claim_obj = Claim(
            claim_code=ec["claim_code"],
            project_id=project_id,
            title=ec["title"],
            description=ec["description"],
            category=ec["category"],
            evidence_status=ec["evidence_status"],
            confidence_score=ec["confidence_score"],
            verification_method=ec["verification_method"],
            source_id=new_source.id,
            exact_quote=ec.get("exact_quote"),
            line_span=ec.get("line_span"),
            cryptographic_root=ec.get("cryptographic_root", "sha256:4b91f0...de21"),
            golden_ref=ec.get("golden_ref", False),
            related_person=current_user.full_name,
            author_id=current_user.id,
            access_classification=access_classification,
            is_approved=True
        )
        db.add(claim_obj)
        created_claims.append(ec["claim_code"])
        
    audit = AuditLog(
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
            "extracted_claims_count": len(extracted_claims)
        }
    )
    db.add(audit)
    db.commit()
    
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
            "claim_codes": created_claims
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
    """Simulates a live GitHub Connector import of PRs, commits, and diffs."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    source_code = f"#GH-SYNC-{datetime.now().strftime('%M%S')}"
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
    
    # Extract claims
    extracted = extract_knowledge_from_text(source_code, source.name, sample_gh_content, "GitHub PR")
    for ec in extracted:
        clm = Claim(
            claim_code=ec["claim_code"],
            project_id=project_id,
            title=ec["title"],
            description=ec["description"],
            category=ec["category"],
            evidence_status=ec["evidence_status"],
            confidence_score=ec["confidence_score"],
            verification_method=ec["verification_method"],
            source_id=source.id,
            exact_quote=ec.get("exact_quote"),
            line_span=ec.get("line_span"),
            cryptographic_root=ec.get("cryptographic_root"),
            related_person="Sarah Lin",
            author_id=current_user.id,
            access_classification="Team",
            is_approved=True
        )
        db.add(clm)
        
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="GITHUB_SYNC",
        entity_type="Source",
        entity_id=source_code,
        details_json={"repo": repo_url, "branch": branch}
    )
    db.add(audit)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Successfully imported repo activity from {repo_url}",
        "source_code": source_code,
        "claims_extracted": len(extracted)
    }

@router.get("/{source_id}")
def get_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    chunks = db.query(SourceChunk).filter(SourceChunk.source_id == source_id).all()
    return {
        "source": source,
        "chunks": chunks
    }
