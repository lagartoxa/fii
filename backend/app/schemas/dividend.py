"""
Pydantic schemas for Dividend model.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class DividendBase(BaseModel):
    """Base schema for Dividend with shared fields."""
    fii_pk: int = Field(..., gt=0, description="FII reference")
    payment_date: date = Field(..., description="Date dividend was paid")
    reference_date: Optional[date] = Field(None, description="Reference date (ex-dividend date)")
    amount_per_unit: Decimal = Field(..., gt=0, description="Dividend amount per unit in BRL")
    units_held: int = Field(..., gt=0, description="Number of units held on payment date")
    total_amount: Decimal = Field(..., gt=0, description="Total dividend received")


class DividendCreate(DividendBase):
    """Schema for creating a new Dividend."""
    pass


class DividendUpdate(BaseModel):
    """Schema for updating an existing Dividend."""
    fii_pk: Optional[int] = Field(None, gt=0)
    payment_date: Optional[date] = None
    reference_date: Optional[date] = None
    amount_per_unit: Optional[Decimal] = Field(None, gt=0)
    units_held: Optional[int] = Field(None, gt=0)
    total_amount: Optional[Decimal] = Field(None, gt=0)


class DividendInDB(DividendBase):
    """Schema for Dividend as stored in database."""
    pk: int
    user_pk: int
    rm_timestamp: Optional[int]
    created_at: datetime
    created_by_pk: Optional[int]
    updated_at: datetime
    updated_by_pk: Optional[int]

    class Config:
        from_attributes = True


class DividendResponse(DividendBase):
    """Schema for Dividend API responses."""
    pk: int
    user_pk: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
