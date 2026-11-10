from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user, get_optional_current_user
from app.models.models import Project, ProjectMember, Claim, Source, User, AuditLog
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.id.asc()).all()

@router.post("/", response_model=ProjectResponse)
def create_project(project_in: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Project).filter(Project.slug == project_in.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project slug already exists")
    
    project = Project(
        name=project_in.name,
        slug=project_in.slug,
        description=project_in.description,
        status=project_in.status or "Active",
        bus_factor_score=project_in.bus_factor_score or 1.0,
        owner_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Assign creator as Owner
    member = ProjectMember(project_id=project.id, user_id=current_user.id, role_in_project="Owner")
    db.add(member)
    
    audit = AuditLog(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        action="PROJECT_CREATE",
        entity_type="Project",
        entity_id=str(project.id),
        details_json={"name": project.name, "slug": project.slug}
    )
    db.add(audit)
    db.commit()
    
    return project

@router.get("/{project_id}")
def get_project_details(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()
    member_list = []
    for m in members:
        u = db.query(User).filter(User.id == m.user_id).first()
        if u:
            member_list.append({
                "id": u.id,
                "name": u.full_name,
                "role": u.role,
                "project_role": m.role_in_project,
                "title": u.title,
                "avatar_url": u.avatar_url
            })
            
    sources_count = db.query(Source).filter(Source.project_id == project_id).count()
    claims_count = db.query(Claim).filter(Claim.project_id == project_id).count()
    verified_count = db.query(Claim).filter(Claim.project_id == project_id, Claim.evidence_status == "VERIFIED").count()
    conflicts_count = db.query(Claim).filter(Claim.project_id == project_id, Claim.evidence_status == "CONFLICTING").count()
    
    return {
        "id": project.id,
        "name": project.name,
        "slug": project.slug,
        "description": project.description,
        "status": project.status,
        "bus_factor_score": project.bus_factor_score,
        "members": member_list,
        "stats": {
            "sources_count": sources_count,
            "claims_count": claims_count,
            "verified_count": verified_count,
            "conflicts_count": conflicts_count
        }
    }

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project_in.name:
        project.name = project_in.name
    if project_in.description:
        project.description = project_in.description
    if project_in.status:
        project.status = project_in.status
    if project_in.bus_factor_score is not None:
        project.bus_factor_score = project_in.bus_factor_score
        
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"status": "success", "message": f"Project {project_id} deleted"}
