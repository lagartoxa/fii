"""
FiiTransaction model - Purchase and sale transactions with cost basis tracking.
"""

from typing import TYPE_CHECKING
from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.fii import Fii


class FiiTransaction(BaseModel):
    """
    FII Transaction model for tracking buy/sell operations.

    Table: fii_transaction (SINGULAR)

    Purpose: Record all FII purchase and sale transactions.

    Relationships:
    - Many-to-one → User (user who owns this transaction)
    - Many-to-one → Fii (FII being transacted)

    RLS: Enabled - users can only access their own transactions
    """

    __tablename__ = "fii_transaction"
    __table_args__ = (
        CheckConstraint("transaction_type IN ('buy', 'sell')", name='ck_fii_transaction_type'),
        CheckConstraint('quantity > 0', name='ck_fii_transaction_quantity'),
        CheckConstraint('price_per_unit > 0', name='ck_fii_transaction_price'),
        CheckConstraint('total_amount > 0', name='ck_fii_transaction_total'),
        {'comment': 'Purchase/sale transactions'}
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

    transaction_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="Transaction type: 'buy' or 'sell'"
    )

    transaction_date: Mapped[date_type] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Date of transaction"
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of units bought/sold"
    )

    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
        comment="Price per unit in BRL"
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
        comment="Total transaction amount (quantity * price_per_unit)"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="fii_transactions",
        foreign_keys=[user_pk]
    )

    fii = relationship(
        "Fii",
        back_populates="fii_transactions",
        foreign_keys=[fii_pk]
    )

    def __repr__(self) -> str:
        return (
            f"<FiiTransaction(pk={self.pk}, type='{self.transaction_type}', "
            f"tag='{self.fii.tag if self.fii else None}', "
            f"quantity={self.quantity}, date={self.transaction_date})>"
        )

    @property
    def is_buy(self) -> bool:
        """Returns True if this is a buy transaction."""
        return self.transaction_type == 'buy'

    @property
    def is_sell(self) -> bool:
        """Returns True if this is a sell transaction."""
        return self.transaction_type == 'sell'
