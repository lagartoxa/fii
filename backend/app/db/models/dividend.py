"""
Dividend model - Monthly dividend payment records.
"""

from typing import TYPE_CHECKING, Optional
from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.fii import Fii


class Dividend(BaseModel):
    """
    Dividend model for tracking monthly dividend payments from FIIs.

    Table: dividend (SINGULAR)

    Purpose: Record dividend payments received from FIIs for income tracking.

    Relationships:
    - Many-to-one → User (user who received this dividend)
    - Many-to-one → Fii (FII that paid this dividend)

    RLS: Enabled - users can only access their own dividends
    """

    __tablename__ = "dividend"
    __table_args__ = (
        CheckConstraint('amount_per_unit > 0', name='ck_dividend_amount_per_unit'),
        {'comment': 'Monthly dividend payment records'}
    )

    user_pk: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('user.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Owner user reference"
    )

    fii_pk: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('fii.pk', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment="FII reference"
    )

    payment_date: Mapped[date_type] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date dividend was paid"
    )

    reference_date: Mapped[Optional[date_type]] = mapped_column(
        Date,
        nullable=True,
        comment="Reference date (ex-dividend date)"
    )

    com_date: Mapped[Optional[date_type]] = mapped_column(
        Date,
        nullable=True,
        index=True,
        comment="Data COM - cut-off date for dividend eligibility"
    )

    amount_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=4),
        nullable=False,
        comment="Dividend amount per unit in BRL"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="dividends",
        foreign_keys=[user_pk]
    )

    fii = relationship(
        "Fii",
        back_populates="dividends",
        foreign_keys=[fii_pk]
    )

    def __repr__(self) -> str:
        return (
            f"<Dividend(pk={self.pk}, ticker='{self.fii.tag if self.fii else None}', "
            f"amount={self.amount_per_unit}, date={self.payment_date})>"
        )
