"""
User Management Routes
API endpoints for user operations (optional feature)
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from app.models.user import User, UserCreate

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo (replace with database in production)
users_db = {}


@router.get("/", response_model=List[User])
async def list_users():
    """Get all users (admin only in production)"""
    return list(users_db.values())


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user"""
    # Check if user exists
    if any(u.email == user.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user (simplified - no password hashing for demo)
    from datetime import datetime
    import uuid
    
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        created_at=datetime.utcnow()
    )
    
    users_db[user_id] = new_user
    logger.info(f"Created new user: {user.email}")
    
    return new_user


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return users_db[user_id]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Delete user by ID"""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    del users_db[user_id]
    logger.info(f"Deleted user: {user_id}")
    return None

