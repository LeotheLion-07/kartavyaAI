import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.models import User
    
    if not token:
        # Default mock user if not authenticated in demo mode or raise 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token subject")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None

def is_manager_or_admin(user) -> bool:
    if not user:
        return False
    role = (user.role or "").lower()
    return "admin" in role or "manager" in role

def log_audit_event(
    db: Session,
    user_id: Optional[int],
    user_name: str,
    user_role: str,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details_json: Optional[dict] = None,
    ip_address: str = "127.0.0.1"
):
    from app.models.models import AuditLog
    from app.core.dlp import mask_sensitive_tokens
    
    # Sanitize details_json if string values exist
    sanitized_details = None
    if details_json:
        sanitized_details = {}
        for k, v in details_json.items():
            if isinstance(v, str):
                sanitized_details[k] = mask_sensitive_tokens(v)
            else:
                sanitized_details[k] = v
                
    audit = AuditLog(
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details_json=sanitized_details,
        ip_address=ip_address,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(audit)
    try:
        db.commit()
    except Exception:
        db.rollback()

def verify_project_membership(project_id: int, user, db: Session) -> bool:
    from app.models.models import Project, ProjectMember
    if not user:
        return False
    # Admins have universal system access
    if "admin" in (user.role or "").lower():
        return True
    # Check if project owner
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        return False
    if proj.owner_id == user.id:
        return True
    # Check ProjectMember table
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id
    ).first()
    return membership is not None

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user = Depends(get_current_user)):
        # Normalize role string (e.g., "admin", "manager", "departing", "incoming")
        user_role = (current_user.role or "").lower()
        normalized_allowed = [r.lower() for r in allowed_roles]
        if user_role not in normalized_allowed and "admin" not in user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker
