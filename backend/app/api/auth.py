from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.models.models import User, AuditLog
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token
from typing import List, Dict, Any

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        title=user_in.title,
        department=user_in.department,
        avatar_url=user_in.avatar_url or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token({"sub": new_user.email, "role": new_user.role, "id": new_user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "title": new_user.title,
            "department": new_user.department,
            "avatar_url": new_user.avatar_url
        }
    }

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    
    # Audit log
    audit = AuditLog(
        user_id=user.id,
        user_name=user.full_name,
        user_role=user.role,
        action="LOGIN",
        entity_type="User",
        entity_id=str(user.id),
        details_json={"email": user.email, "method": "password"}
    )
    db.add(audit)
    db.commit()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "title": user.title,
            "department": user.department,
            "avatar_url": user.avatar_url
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password")
def forgot_password(payload: Dict[str, str]):
    email = payload.get("email")
    return {"message": f"Password reset instructions dispatched to {email}. In demo mode, use password 'password123'."}

@router.get("/sample-users")
def get_sample_users(db: Session = Depends(get_db)):
    """Returns sample pre-seeded users for 1-click login and testing."""
    users = db.query(User).all()
    results = []
    for u in users:
        token = create_access_token({"sub": u.email, "role": u.role, "id": u.id})
        results.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "title": u.title,
            "department": u.department,
            "avatar_url": u.avatar_url,
            "access_token": token
        })
    return results
