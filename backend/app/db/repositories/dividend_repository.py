"""
Dividend repository for dividend-related database operations.
"""

from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models.dividend import Dividend
from app.db.repositories.base import BaseRepository
from app.schemas.dividend import DividendCreate, DividendUpdate


class DividendRepository(BaseRepository[Dividend, DividendCreate, DividendUpdate]):
    """Repository for Dividend model."""

    model_class = Dividend

    def get_by_user(
        self,
        user_pk: int,
        skip: int = 0,
        limit: int = 100,
        fii_pk: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dividend]:
        """
        Get dividends for a specific user with optional filters.

        Args:
            user_pk: User primary key
            skip: Number of records to skip
            limit: Maximum number of records to return
            fii_pk: Optional FII filter
            start_date: Optional start payment date filter
            end_date: Optional end payment date filter

        Returns:
            List of Dividend instances
        """
        query = self.session.query(Dividend).filter(
            Dividend.user_pk == user_pk,
            Dividend.rm_timestamp.is_(None)
        )

        # Apply filters
        if fii_pk:
            query = query.filter(Dividend.fii_pk == fii_pk)

        if start_date:
            query = query.filter(Dividend.payment_date >= start_date)

        if end_date:
            query = query.filter(Dividend.payment_date <= end_date)

        # Apply ordering and pagination
        return query.order_by(
            Dividend.payment_date.desc(),
            Dividend.pk.desc()
        ).offset(skip).limit(limit).all()

    def get_by_user_and_pk(self, user_pk: int, pk: int) -> Optional[Dividend]:
        """
        Get a specific dividend for a user.

        Args:
            user_pk: User primary key
            pk: Dividend primary key

        Returns:
            Dividend instance or None if not found
        """
        return self.session.query(Dividend).filter(
            Dividend.pk == pk,
            Dividend.user_pk == user_pk,
            Dividend.rm_timestamp.is_(None)
        ).first()
