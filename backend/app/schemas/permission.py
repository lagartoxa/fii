"""
Pydantic schemas for Permission model.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """Base schema for Permission with shared fields."""
    resource: str = Field(..., min_length=1, max_length=100, description="Resource name")
    action: str = Field(..., min_length=1, max_length=50, description="Action name")
    description: Optional[str] = Field(None, max_length=255, description="Permission description")


class PermissionCreate(PermissionBase):
    """Schema for creating a new Permission."""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating an existing Permission."""
    resource: Optional[str] = Field(None, min_length=1, max_length=100)
    action: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class PermissionInDB(PermissionBase):
    """Schema for Permission as stored in database."""
    pk: int
    rm_timestamp: Optional[int]
    created_at: datetime
    created_by_pk: Optional[int]
    updated_at: datetime
    updated_by_pk: Optional[int]

    class Config:
        from_attributes = True


class PermissionResponse(PermissionBase):
    """Schema for Permission API responses."""
    pk: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
