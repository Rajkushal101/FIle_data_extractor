"""
Authentication Routes
User registration, login, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from typing import Optional

from app.models.database import User, UserTier
from app.core.database import get_db
from app.core.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    generate_api_key
)

router = APIRouter()


# ==================== Request/Response Models ====================

class UserCreate(BaseModel):
    """User registration request"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User profile response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    tier: str
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True


# ==================== Routes ====================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - Creates user account
    - Returns authentication token
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        tier=UserTier.FREE
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(
        data={"sub": new_user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "tier": new_user.tier.value
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user
    
    - Validates credentials
    - Returns authentication token
    """
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "tier": user.tier.value
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    """
    Get current user profile
    
    Requires authentication
    """
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "tier": user.tier.value,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat()
    }


@router.post("/api-key/generate")
async def create_api_key(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Generate new API key for programmatic access
    
    Requires authentication
    """
    # Generate new API key
    api_key = generate_api_key()
    
    # Update user
    user.api_key = api_key
    db.commit()
    
    return {
        "api_key": api_key,
        "message": "API key generated successfully. Store it securely!"
    }


@router.delete("/api-key/revoke")
async def revoke_api_key(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Revoke current API key
    
    Requires authentication
    """
    user.api_key = None
    db.commit()
    
    return {"message": "API key revoked successfully"}


@router.put("/me", response_model=UserResponse)
async def update_profile(
    full_name: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    
    Requires authentication
    """
    if full_name is not None:
        user.full_name = full_name
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "tier": user.tier.value,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat()
    }


@router.get("/stats")
async def get_user_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get user statistics
    
    - Total documents processed
    - Total exports
    - Account age
    """
    from app.models.database import Document, ExportHistory
    
    document_count = db.query(Document).filter(Document.user_id == user.id).count()
    export_count = db.query(ExportHistory).join(Document).filter(Document.user_id == user.id).count()
    
    return {
        "documents_processed": document_count,
        "total_exports": export_count,
        "account_tier": user.tier.value,
        "member_since": user.created_at.isoformat()
    }
