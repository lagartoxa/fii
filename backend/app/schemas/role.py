"""
Pydantic schemas for Role model.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Base schema for Role with shared fields."""
    name: str = Field(..., min_length=1, max_length=50, description="Role name")
    description: Optional[str] = Field(None, max_length=255, description="Role description")


class RoleCreate(RoleBase):
    """Schema for creating a new Role."""
    permission_pks: List[int] = Field(default_factory=list, description="List of permission PKs to assign")


class RoleUpdate(BaseModel):
    """Schema for updating an existing Role."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    permission_pks: Optional[List[int]] = Field(None, description="List of permission PKs to assign")


class RoleInDB(RoleBase):
    """Schema for Role as stored in database."""
    pk: int
    rm_timestamp: Optional[int]
    created_at: datetime
    created_by_pk: Optional[int]
    updated_at: datetime
    updated_by_pk: Optional[int]

    class Config:
        from_attributes = True


class RoleResponse(RoleBase):
    """Schema for Role API responses."""
    pk: int
    created_at: datetime
    updated_at: datetime
    permission_pks: List[int] = Field(default_factory=list, description="List of assigned permission PKs")

    class Config:
        from_attributes = True
