"""
FII repository for FII-related database operations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models.fii import Fii
from app.db.repositories.base import BaseRepository
from app.schemas.fii import FiiCreate, FiiUpdate


class FiiRepository(BaseRepository[Fii, FiiCreate, FiiUpdate]):
    """Repository for Fii model."""

    model_class = Fii

    def get_by_tag(self, tag: str) -> Optional[Fii]:
        """
        Get FII by tag (ticker symbol).

        Args:
            tag: FII tag/ticker

        Returns:
            Fii instance or None if not found
        """
        return self.session.query(Fii).filter(
            Fii.tag == tag.upper(),
            Fii.rm_timestamp.is_(None)
        ).first()

    def get_by_sector(self, sector: str, skip: int = 0, limit: int = 100) -> List[Fii]:
        """
        Get FIIs by sector.

        Args:
            sector: FII sector
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Fii instances
        """
        return self.session.query(Fii).filter(
            Fii.sector == sector,
            Fii.rm_timestamp.is_(None)
        ).order_by(Fii.tag).offset(skip).limit(limit).all()

    def get_by_tag_including_deleted(self, tag: str) -> Optional[Fii]:
        """
        Get FII by tag including soft-deleted records.

        Args:
            tag: FII tag/ticker

        Returns:
            Fii instance or None if not found
        """
        return self.session.query(Fii).filter(
            Fii.tag == tag.upper()
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        sector: Optional[str] = None,
        include_deleted: bool = False
    ) -> List[Fii]:
        """
        Get all FIIs with optional sector filter.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            sector: Optional sector filter
            include_deleted: If True, include soft-deleted records

        Returns:
            List of Fii instances
        """
        query = self.session.query(Fii)

        # Apply soft delete filter
        if not include_deleted:
            query = query.filter(Fii.rm_timestamp.is_(None))

        # Apply sector filter
        if sector:
            query = query.filter(Fii.sector == sector)

        return query.order_by(Fii.tag).offset(skip).limit(limit).all()
