"""
Pydantic schemas for Dividend model.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ValidationInfo


class DividendCreate(BaseModel):
    """Schema for creating a new Dividend."""
    fii_pk: int = Field(..., gt=0, description="FII reference")
    payment_date: date = Field(..., description="Date dividend was paid")
    amount_per_unit: Decimal = Field(..., gt=0, description="Dividend amount per unit in BRL")
    com_date: Optional[date] = Field(None, description="Data COM - cut-off date for dividend eligibility")

    @field_validator('com_date')
    @classmethod
    def validate_com_date(cls, v: Optional[date], info: ValidationInfo) -> Optional[date]:
        if v is None:
            return v

        # Check against payment_date if available
        if 'payment_date' in info.data and info.data['payment_date']:
            if v > info.data['payment_date']:
                raise ValueError('COM date must be on or before payment date')

        return v


class DividendUpdate(BaseModel):
    """Schema for updating an existing Dividend."""
    fii_pk: Optional[int] = Field(None, gt=0)
    payment_date: Optional[date] = None
    amount_per_unit: Optional[Decimal] = Field(None, gt=0)
    com_date: Optional[date] = None


class DividendInDB(BaseModel):
    """Schema for Dividend as stored in database."""
    pk: int
    user_pk: int
    fii_pk: int
    payment_date: date
    amount_per_unit: Decimal
    com_date: Optional[date]
    rm_timestamp: Optional[int]
    created_at: datetime
    created_by_pk: Optional[int]
    updated_at: datetime
    updated_by_pk: Optional[int]

    class Config:
        from_attributes = True


class DividendResponse(BaseModel):
    """Schema for Dividend API responses."""
    pk: int
    user_pk: int
    fii_pk: int
    payment_date: date
    amount_per_unit: Decimal
    com_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DividendDetail(BaseModel):
    """Schema for individual dividend detail in monthly summary."""
    dividend_pk: int
    payment_date: date
    amount_per_unit: Decimal
    com_date: Optional[date]
    units_held: int
    total_amount: Decimal

    class Config:
        from_attributes = True


class FiiMonthlySummary(BaseModel):
    """Schema for FII monthly dividend summary."""
    fii_pk: int
    fii_tag: str
    fii_name: str
    dividends: list[DividendDetail]
    total_amount: Decimal
    dividend_count: int

    class Config:
        from_attributes = True


class MonthlySummaryResponse(BaseModel):
    """Schema for monthly dividend summary response."""
    year: int
    month: int
    fiis: list[FiiMonthlySummary]
    total: Decimal
