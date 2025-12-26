"""
FiiTransaction CRUD API endpoints.
"""

from datetime import date
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.db.repositories.fii_repository import FiiRepository
from app.db.repositories.fii_transaction_repository import FiiTransactionRepository
from app.schemas.fii_transaction import FiiTransactionCreate, FiiTransactionResponse, FiiTransactionUpdate

router = APIRouter()


@router.post("/", response_model=FiiTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: FiiTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new FII transaction.

    Args:
        transaction_data: Transaction creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created transaction

    Raises:
        HTTPException: If FII not found
    """
    # Verify FII exists
    with FiiRepository(db) as fii_repo:
        fii = fii_repo.get_by_pk(transaction_data.fii_pk)

        if not fii:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FII not found"
            )

    # Create transaction
    with FiiTransactionRepository(db, current_user_pk=current_user.pk) as transaction_repo:
        # Add user_pk to transaction data
        new_transaction = transaction_repo.model_class(
            user_pk=current_user.pk,
            fii_pk=transaction_data.fii_pk,
            transaction_type=transaction_data.transaction_type,
            transaction_date=transaction_data.transaction_date,
            quantity=transaction_data.quantity,
            price_per_unit=transaction_data.price_per_unit,
            total_amount=transaction_data.total_amount,
            created_by_pk=current_user.pk,
            updated_by_pk=current_user.pk
        )

        db.add(new_transaction)
        db.flush()
        db.refresh(new_transaction)

        return new_transaction


@router.get("/", response_model=List[FiiTransactionResponse])
def list_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    fii_pk: int | None = Query(None, description="Filter by FII"),
    transaction_type: str | None = Query(None, description="Filter by type (buy/sell)"),
    start_date: date | None = Query(None, description="Filter by start date"),
    end_date: date | None = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    List all transactions for the current user with optional filtering and pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        fii_pk: Optional FII filter
        transaction_type: Optional type filter (buy/sell)
        start_date: Optional start date filter
        end_date: Optional end date filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of transactions
    """
    with FiiTransactionRepository(db) as transaction_repo:
        transactions = transaction_repo.get_by_user(
            user_pk=current_user.pk,
            skip=skip,
            limit=limit,
            fii_pk=fii_pk,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )

        return transactions


@router.get("/{pk}", response_model=FiiTransactionResponse)
def get_transaction(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a single transaction by primary key.

    Args:
        pk: Transaction primary key
        db: Database session
        current_user: Current authenticated user

    Returns:
        Transaction record

    Raises:
        HTTPException: If transaction not found
    """
    with FiiTransactionRepository(db) as transaction_repo:
        transaction = transaction_repo.get_by_user_and_pk(current_user.pk, pk)

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        return transaction


@router.patch("/{pk}", response_model=FiiTransactionResponse)
def update_transaction(
    pk: int,
    transaction_data: FiiTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a transaction.

    Args:
        pk: Transaction primary key
        transaction_data: Transaction update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated transaction

    Raises:
        HTTPException: If transaction not found or FII not found
    """
    with FiiTransactionRepository(db, current_user_pk=current_user.pk) as transaction_repo:
        # Check transaction exists and belongs to user
        transaction = transaction_repo.get_by_user_and_pk(current_user.pk, pk)

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        # Verify FII exists if being updated
        if transaction_data.fii_pk:
            with FiiRepository(db) as fii_repo:
                fii = fii_repo.get_by_pk(transaction_data.fii_pk)

                if not fii:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="FII not found"
                    )

        # Update transaction
        updated_transaction = transaction_repo.update(pk, transaction_data)

        return updated_transaction


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Soft delete a transaction.

    Args:
        pk: Transaction primary key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If transaction not found
    """
    with FiiTransactionRepository(db, current_user_pk=current_user.pk) as transaction_repo:
        # Check transaction exists and belongs to user
        transaction = transaction_repo.get_by_user_and_pk(current_user.pk, pk)

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )

        success = transaction_repo.delete(pk)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
