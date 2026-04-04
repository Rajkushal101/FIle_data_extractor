"""
User Data Model
Pydantic models for user management
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating new users"""
    password: str = Field(..., min_length=8)


class User(UserBase):
    """Complete user model with all fields"""
    id: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password (for database storage)"""
    hashed_password: str

