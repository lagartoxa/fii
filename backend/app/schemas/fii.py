"""
Pydantic schemas for FII model.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class FiiBase(BaseModel):
    """Base schema for FII with shared fields."""
    tag: str = Field(..., min_length=1, max_length=20, description="FII tag/ticker symbol")
    name: str = Field(..., min_length=1, max_length=255, description="FII full name")
    sector: Optional[str] = Field(None, max_length=100, description="FII sector")

    @field_validator('tag')
    @classmethod
    def tag_must_be_uppercase(cls, v: str) -> str:
        """Ensure tag is uppercase."""
        return v.upper()


class FiiCreate(FiiBase):
    """Schema for creating a new FII."""
    pass


class FiiUpdate(BaseModel):
    """Schema for updating an existing FII."""
    tag: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)

    @field_validator('tag')
    @classmethod
    def tag_must_be_uppercase(cls, v: Optional[str]) -> Optional[str]:
        """Ensure tag is uppercase if provided."""
        return v.upper() if v else None


class FiiInDB(FiiBase):
    """Schema for FII as stored in database."""
    pk: int
    rm_timestamp: Optional[int]
    created_at: datetime
    created_by_pk: Optional[int]
    updated_at: datetime
    updated_by_pk: Optional[int]

    class Config:
        from_attributes = True


class FiiResponse(FiiBase):
    """Schema for FII API responses."""
    pk: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
