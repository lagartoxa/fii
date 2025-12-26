"""
FiiHolding model - Cached portfolio positions for performance optimization.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.fii import Fii


class FiiHolding(BaseModel):
    """
    FII Holding model for caching portfolio positions.

    Table: fii_holding (SINGULAR)

    Purpose: Cache expensive portfolio calculations to avoid SUM/GROUP BY queries
    on every portfolio view. Holdings are recalculated after each transaction or dividend.

    Relationships:
    - Many-to-one → User (user who owns this holding)
    - Many-to-one → Fii (FII being held)

    RLS: Enabled - users can only access their own holdings

    Calculation Triggers:
    - After INSERT/UPDATE/DELETE on fii_transaction → recalculate holding
    - After INSERT on dividend → update total_dividends
    """

    __tablename__ = "fii_holding"
    __table_args__ = (
        UniqueConstraint('user_pk', 'fii_pk', name='uq_fii_holding_user_fii'),
        CheckConstraint('total_quantity >= 0', name='ck_fii_holding_quantity'),
        CheckConstraint('average_price >= 0', name='ck_fii_holding_price'),
        CheckConstraint('total_invested >= 0', name='ck_fii_holding_invested'),
        {'comment': 'Cached portfolio positions (performance optimization)'}
    )

    user_pk = Column(
        BigInteger,
        ForeignKey('user.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Owner user reference"
    )

    fii_pk = Column(
        BigInteger,
        ForeignKey('fii.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="FII reference"
    )

    total_quantity = Column(
        Integer,
        nullable=False,
        comment="Current units held (sum of all transactions)"
    )

    average_price = Column(
        Numeric(precision=10, scale=2),
        nullable=False,
        comment="Average purchase price per unit"
    )

    total_invested = Column(
        Numeric(precision=12, scale=2),
        nullable=False,
        comment="Total amount invested (buys - sells + fees + taxes)"
    )

    current_value = Column(
        Numeric(precision=12, scale=2),
        nullable=True,
        comment="Current market value (total_quantity * fii.current_price)"
    )

    total_dividends = Column(
        Numeric(precision=12, scale=2),
        nullable=False,
        server_default='0.00',
        comment="Total dividends received for this holding"
    )

    last_calculated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When holdings were last recalculated"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="fii_holdings",
        foreign_keys=[user_pk]
    )

    fii = relationship(
        "Fii",
        back_populates="fii_holdings",
        foreign_keys=[fii_pk]
    )

    def __repr__(self) -> str:
        return (
            f"<FiiHolding(pk={self.pk}, ticker='{self.fii.ticker if self.fii else None}', "
            f"quantity={self.total_quantity}, avg_price={self.average_price})>"
        )

    @property
    def unrealized_gain_loss(self) -> float:
        """
        Calculate unrealized gain/loss.

        Returns:
            Unrealized gain (positive) or loss (negative). None if current_value not set.

        Formula:
            unrealized_gain_loss = current_value - total_invested
        """
        if self.current_value is None:
            return None

        return float(self.current_value) - float(self.total_invested)

    @property
    def total_return(self) -> float:
        """
        Calculate total return including dividends and unrealized gains.

        Returns:
            Total return. None if current_value not set.

        Formula:
            total_return = (current_value - total_invested) + total_dividends
        """
        if self.current_value is None:
            return None

        unrealized = float(self.current_value) - float(self.total_invested)
        return unrealized + float(self.total_dividends)

    @property
    def return_percentage(self) -> float:
        """
        Calculate return percentage.

        Returns:
            Return percentage. None if current_value not set or total_invested is 0.

        Formula:
            return_percentage = (total_return / total_invested) * 100
        """
        if self.current_value is None or float(self.total_invested) == 0:
            return None

        total_ret = self.total_return
        if total_ret is None:
            return None

        return (total_ret / float(self.total_invested)) * 100
