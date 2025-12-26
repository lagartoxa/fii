"""
Dividend CRUD API endpoints.
"""

from datetime import date
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.db.repositories.dividend_repository import DividendRepository
from app.db.repositories.fii_repository import FiiRepository
from app.schemas.dividend import DividendCreate, DividendResponse, DividendUpdate

router = APIRouter()


@router.post("/", response_model=DividendResponse, status_code=status.HTTP_201_CREATED)
def create_dividend(
    dividend_data: DividendCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new dividend record.

    Args:
        dividend_data: Dividend creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created dividend

    Raises:
        HTTPException: If FII not found
    """
    # Verify FII exists
    with FiiRepository(db) as fii_repo:
        fii = fii_repo.get_by_pk(dividend_data.fii_pk)

        if not fii:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FII not found"
            )

    # Create dividend
    with DividendRepository(db, current_user_pk=current_user.pk) as dividend_repo:
        # Add user_pk to dividend data
        new_dividend = dividend_repo.model_class(
            user_pk=current_user.pk,
            fii_pk=dividend_data.fii_pk,
            payment_date=dividend_data.payment_date,
            reference_date=dividend_data.reference_date,
            amount_per_unit=dividend_data.amount_per_unit,
            units_held=dividend_data.units_held,
            total_amount=dividend_data.total_amount,
            created_by_pk=current_user.pk,
            updated_by_pk=current_user.pk
        )

        db.add(new_dividend)
        db.flush()
        db.refresh(new_dividend)

        return new_dividend


@router.get("/", response_model=List[DividendResponse])
def list_dividends(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    fii_pk: int | None = Query(None, description="Filter by FII"),
    start_date: date | None = Query(None, description="Filter by start payment date"),
    end_date: date | None = Query(None, description="Filter by end payment date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    List all dividends for the current user with optional filtering and pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        fii_pk: Optional FII filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of dividends
    """
    with DividendRepository(db) as dividend_repo:
        dividends = dividend_repo.get_by_user(
            user_pk=current_user.pk,
            skip=skip,
            limit=limit,
            fii_pk=fii_pk,
            start_date=start_date,
            end_date=end_date
        )

        return dividends


@router.get("/{pk}", response_model=DividendResponse)
def get_dividend(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a single dividend by primary key.

    Args:
        pk: Dividend primary key
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dividend record

    Raises:
        HTTPException: If dividend not found
    """
    with DividendRepository(db) as dividend_repo:
        dividend = dividend_repo.get_by_user_and_pk(current_user.pk, pk)

        if not dividend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dividend not found"
            )

        return dividend


@router.patch("/{pk}", response_model=DividendResponse)
def update_dividend(
    pk: int,
    dividend_data: DividendUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a dividend.

    Args:
        pk: Dividend primary key
        dividend_data: Dividend update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated dividend

    Raises:
        HTTPException: If dividend not found or FII not found
    """
    with DividendRepository(db, current_user_pk=current_user.pk) as dividend_repo:
        # Check dividend exists and belongs to user
        dividend = dividend_repo.get_by_user_and_pk(current_user.pk, pk)

        if not dividend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dividend not found"
            )

        # Verify FII exists if being updated
        if dividend_data.fii_pk:
            with FiiRepository(db) as fii_repo:
                fii = fii_repo.get_by_pk(dividend_data.fii_pk)

                if not fii:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="FII not found"
                    )

        # Update dividend
        updated_dividend = dividend_repo.update(pk, dividend_data)

        return updated_dividend


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dividend(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Soft delete a dividend.

    Args:
        pk: Dividend primary key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If dividend not found
    """
    with DividendRepository(db, current_user_pk=current_user.pk) as dividend_repo:
        # Check dividend exists and belongs to user
        dividend = dividend_repo.get_by_user_and_pk(current_user.pk, pk)

        if not dividend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dividend not found"
            )

        success = dividend_repo.delete(pk)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dividend not found"
            )
