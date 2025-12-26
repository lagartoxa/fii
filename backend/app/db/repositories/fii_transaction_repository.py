"""
FiiTransaction repository for transaction-related database operations.
"""

from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models.fii_transaction import FiiTransaction
from app.db.repositories.base import BaseRepository
from app.schemas.fii_transaction import FiiTransactionCreate, FiiTransactionUpdate


class FiiTransactionRepository(BaseRepository[FiiTransaction, FiiTransactionCreate, FiiTransactionUpdate]):
    """Repository for FiiTransaction model."""

    model_class = FiiTransaction

    def get_by_user(
        self,
        user_pk: int,
        skip: int = 0,
        limit: int = 100,
        fii_pk: Optional[int] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[FiiTransaction]:
        """
        Get transactions for a specific user with optional filters.

        Args:
            user_pk: User primary key
            skip: Number of records to skip
            limit: Maximum number of records to return
            fii_pk: Optional FII filter
            transaction_type: Optional type filter (buy/sell)
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of FiiTransaction instances
        """
        query = self.session.query(FiiTransaction).filter(
            FiiTransaction.user_pk == user_pk,
            FiiTransaction.rm_timestamp.is_(None)
        )

        # Apply filters
        if fii_pk:
            query = query.filter(FiiTransaction.fii_pk == fii_pk)

        if transaction_type:
            query = query.filter(FiiTransaction.transaction_type == transaction_type.lower())

        if start_date:
            query = query.filter(FiiTransaction.transaction_date >= start_date)

        if end_date:
            query = query.filter(FiiTransaction.transaction_date <= end_date)

        # Apply ordering and pagination
        return query.order_by(
            FiiTransaction.transaction_date.desc(),
            FiiTransaction.pk.desc()
        ).offset(skip).limit(limit).all()

    def get_by_user_and_pk(self, user_pk: int, pk: int) -> Optional[FiiTransaction]:
        """
        Get a specific transaction for a user.

        Args:
            user_pk: User primary key
            pk: Transaction primary key

        Returns:
            FiiTransaction instance or None if not found
        """
        return self.session.query(FiiTransaction).filter(
            FiiTransaction.pk == pk,
            FiiTransaction.user_pk == user_pk,
            FiiTransaction.rm_timestamp.is_(None)
        ).first()
