"""
Pydantic schemas for User model.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for User with shared fields."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")


class UserCreate(UserBase):
    """Schema for creating a new User."""
    password: str = Field(..., min_length=8, description="User password")
    role_pks: List[int] = Field(default_factory=list, description="List of role PKs to assign")


class UserUpdate(BaseModel):
    """Schema for updating an existing User."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    role_pks: Optional[List[int]] = Field(None, description="List of role PKs to assign")


class UserInDB(UserBase):
    """Schema for User as stored in database."""
    pk: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    rm_timestamp: Optional[int]
    created_at: datetime
    created_by_pk: Optional[int]
    updated_at: datetime
    updated_by_pk: Optional[int]

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """Schema for User API responses."""
    pk: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    role_pks: List[int] = Field(default_factory=list, description="List of assigned role PKs")

    class Config:
        from_attributes = True
