"""
Pydantic schemas for FiiTransaction model.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class FiiTransactionBase(BaseModel):
    """Base schema for FiiTransaction with shared fields."""
    fii_pk: int = Field(..., gt=0, description="FII reference")
    transaction_type: str = Field(..., description="Transaction type: 'buy' or 'sell'")
    transaction_date: date = Field(..., description="Date of transaction")
    quantity: int = Field(..., gt=0, description="Number of units")
    price_per_unit: Decimal = Field(..., gt=0, description="Price per unit in BRL")
    total_amount: Decimal = Field(..., gt=0, description="Total transaction amount")

    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        """Ensure transaction_type is 'buy' or 'sell'."""
        v_lower = v.lower()
        if v_lower not in ('buy', 'sell'):
            raise ValueError("transaction_type must be 'buy' or 'sell'")
        return v_lower


class FiiTransactionCreate(FiiTransactionBase):
    """Schema for creating a new FiiTransaction."""
    pass


class FiiTransactionUpdate(BaseModel):
    """Schema for updating an existing FiiTransaction."""
    fii_pk: Optional[int] = Field(None, gt=0)
    transaction_type: Optional[str] = None
    transaction_date: Optional[date] = None
    quantity: Optional[int] = Field(None, gt=0)
    price_per_unit: Optional[Decimal] = Field(None, gt=0)
    total_amount: Optional[Decimal] = Field(None, gt=0)

    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        """Ensure transaction_type is 'buy' or 'sell' if provided."""
        if v is None:
            return None
        v_lower = v.lower()
        if v_lower not in ('buy', 'sell'):
            raise ValueError("transaction_type must be 'buy' or 'sell'")
        return v_lower


class FiiTransactionInDB(FiiTransactionBase):
    """Schema for FiiTransaction as stored in database."""
    pk: int
    user_pk: int
    rm_timestamp: Optional[int]
    created_at: datetime
    created_by_pk: Optional[int]
    updated_at: datetime
    updated_by_pk: Optional[int]

    class Config:
        from_attributes = True


class FiiTransactionResponse(FiiTransactionBase):
    """Schema for FiiTransaction API responses."""
    pk: int
    user_pk: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
