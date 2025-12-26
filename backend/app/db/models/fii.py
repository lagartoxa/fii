"""
FII model - Brazilian Real Estate Investment Trust (Fundos Imobiliários) catalog.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.fii_transaction import FiiTransaction
    from app.db.models.dividend import Dividend
    from app.db.models.fii_holding import FiiHolding


class Fii(BaseModel):
    """
    FII (Fundos Imobiliários) master catalog model.

    Table: fii (SINGULAR)

    Purpose: Store FII master data including tag, name, and sector.

    Relationships:
    - One-to-many → FiiTransaction (all transactions for this FII)
    - One-to-many → Dividend (all dividends paid by this FII)
    - One-to-many → FiiHolding (portfolio holdings of this FII by users)
    """

    __tablename__ = "fii"
    __table_args__ = (
        UniqueConstraint('tag', 'rm_timestamp', name='uq_fii_tag_rm_timestamp'),
        {'comment': 'FII master catalog (tags, names, sectors)'}
    )

    tag: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="FII tag/ticker symbol (e.g., MXRF11, HGLG11)"
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="FII full name"
    )

    sector: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="FII sector (commercial, residential, logistics, hybrid, etc.)"
    )

    cut_day: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Day of month for dividend cut-off (1-31)"
    )

    # Relationships
    fii_transactions = relationship(
        "FiiTransaction",
        back_populates="fii",
        foreign_keys="FiiTransaction.fii_pk"
    )

    dividends = relationship(
        "Dividend",
        back_populates="fii",
        foreign_keys="Dividend.fii_pk"
    )

    fii_holdings = relationship(
        "FiiHolding",
        back_populates="fii",
        cascade="all, delete-orphan",
        foreign_keys="FiiHolding.fii_pk"
    )

    def __repr__(self) -> str:
        return f"<Fii(pk={self.pk}, tag='{self.tag}', name='{self.name}')>"

    def __str__(self) -> str:
        return f"{self.tag} - {self.name}"
