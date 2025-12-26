"""
Dividend CRUD API endpoints.
"""

from datetime import date, timedelta
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.db.models.fii_transaction import FiiTransaction
from app.db.repositories.dividend_repository import DividendRepository
from app.db.repositories.fii_repository import FiiRepository
from app.schemas.dividend import DividendCreate, DividendResponse, DividendUpdate, MonthlySummaryResponse, FiiMonthlySummary

router = APIRouter()


def _calculate_cut_date(payment_date: date, cut_day: int) -> date:
    """
    Calculate the cut-off date based on payment date and cut day of month.

    The cut_day represents the day of the PAYMENT MONTH up to which shares must be held.
    For example, if dividend is paid on 30/09 and cut_day is 30, then cut_date is 30/09.
    All shares bought on or before 30/09 are counted for that dividend.

    Args:
        payment_date: Date dividend was paid
        cut_day: Day of month for cut-off (1-31) in the payment month

    Returns:
        Calculated cut-off date (in the same month as payment)
    """
    year = payment_date.year
    month = payment_date.month

    # Handle months with fewer days (e.g., cut_day=31 but February only has 28/29)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day_of_month = (next_month - timedelta(days=1)).day

    # Use the minimum of cut_day and last_day_of_month
    actual_day = min(cut_day, last_day_of_month)

    return date(year, month, actual_day)


def _calculate_units_held(
    db: Session,
    user_pk: int,
    fii_pk: int,
    cut_date: date
) -> int:
    """
    Calculate units held on cut_date based on transactions.

    Rule: Share must be bought before or at cut_date and sold only after cut_date.

    Args:
        db: Database session
        user_pk: User primary key
        fii_pk: FII primary key
        cut_date: Cut-off date for dividend eligibility

    Returns:
        Number of units held that are eligible for dividend
    """
    # Get all transactions up to and including cut_date
    buy_transactions = db.query(FiiTransaction).filter(
        and_(
            FiiTransaction.user_pk == user_pk,
            FiiTransaction.fii_pk == fii_pk,
            FiiTransaction.transaction_type == 'buy',
            FiiTransaction.transaction_date <= cut_date,
            FiiTransaction.rm_timestamp.is_(None)
        )
    ).all()

    # Get all sell transactions up to and including cut_date
    sell_transactions = db.query(FiiTransaction).filter(
        and_(
            FiiTransaction.user_pk == user_pk,
            FiiTransaction.fii_pk == fii_pk,
            FiiTransaction.transaction_type == 'sell',
            FiiTransaction.transaction_date <= cut_date,
            FiiTransaction.rm_timestamp.is_(None)
        )
    ).all()

    # Calculate total bought and sold
    total_bought = sum(t.quantity for t in buy_transactions)
    total_sold = sum(t.quantity for t in sell_transactions)

    # Units held = bought - sold
    units_held = total_bought - total_sold

    return max(0, units_held)  # Ensure non-negative


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
            amount_per_unit=dividend_data.amount_per_unit,
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

        # Get update data
        update_dict = dividend_data.model_dump(exclude_unset=True)

        # Determine which values to use for calculation
        fii_pk_for_calc = update_dict.get('fii_pk', dividend.fii_pk)
        payment_date_for_calc = update_dict.get('payment_date', dividend.payment_date)
        amount_per_unit_for_calc = update_dict.get('amount_per_unit', dividend.amount_per_unit)

        # Verify FII exists if being updated and get cut_day from FII
        with FiiRepository(db) as fii_repo:
            fii = fii_repo.get_by_pk(fii_pk_for_calc)

            if not fii:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="FII not found"
                )

            # Recalculate units_held if FII has cut_day
            if fii.cut_day:
                # Calculate the actual cut date based on payment date and FII's cut day
                cut_date = _calculate_cut_date(payment_date_for_calc, fii.cut_day)
                units_held = _calculate_units_held(
                    db=db,
                    user_pk=current_user.pk,
                    fii_pk=fii_pk_for_calc,
                    cut_date=cut_date
                )
                update_dict['units_held'] = units_held

        # Update dividend
        updated_dividend = dividend_repo.update(pk, DividendUpdate(**update_dict))

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


@router.get(
    "/summary/monthly",
    response_model=MonthlySummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_monthly_summary(
    year: int = Query(..., description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MonthlySummaryResponse:
    """
    Get monthly dividend summary grouped by FII.

    Args:
        year: Year to get summary for
        month: Month to get summary for (1-12)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Monthly summary with totals by FII
    """
    from decimal import Decimal
    from sqlalchemy import extract
    from app.db.models.dividend import Dividend
    from app.db.models.fii import Fii

    # Query dividends for the specified month
    dividends = (
        db.query(Dividend, Fii)
        .join(Fii, Dividend.fii_pk == Fii.pk)
        .filter(
            and_(
                Dividend.user_pk == current_user.pk,
                Dividend.rm_timestamp.is_(None),
                Fii.rm_timestamp.is_(None),  # Exclude deleted FIIs
                extract('year', Dividend.payment_date) == year,
                extract('month', Dividend.payment_date) == month
            )
        )
        .order_by(Fii.tag)
        .all()
    )

    # Group by FII and calculate totals
    from app.schemas.dividend import DividendDetail

    fii_summary = {}
    for dividend, fii in dividends:
        # Calculate units_held for this dividend
        if fii.cut_day:
            cut_date = _calculate_cut_date(dividend.payment_date, fii.cut_day)
            units_held = _calculate_units_held(
                db=db,
                user_pk=current_user.pk,
                fii_pk=dividend.fii_pk,
                cut_date=cut_date
            )
        else:
            units_held = 0  # No cut_day configured, can't calculate

        # Calculate total for this dividend
        dividend_total = dividend.amount_per_unit * units_held

        # Add to FII summary
        if fii.pk not in fii_summary:
            fii_summary[fii.pk] = {
                'fii_pk': fii.pk,
                'fii_tag': fii.tag,
                'fii_name': fii.name,
                'dividends': [],
                'total_amount': Decimal('0'),
                'dividend_count': 0
            }

        # Add dividend detail
        fii_summary[fii.pk]['dividends'].append(
            DividendDetail(
                dividend_pk=dividend.pk,
                payment_date=dividend.payment_date,
                amount_per_unit=dividend.amount_per_unit,
                units_held=units_held,
                total_amount=dividend_total
            )
        )
        fii_summary[fii.pk]['total_amount'] += dividend_total
        fii_summary[fii.pk]['dividend_count'] += 1

    # Build response
    fiis = [
        FiiMonthlySummary(**summary)
        for summary in fii_summary.values()
    ]

    # Calculate grand total
    total = sum((fii.total_amount for fii in fiis), Decimal('0'))

    return MonthlySummaryResponse(
        year=year,
        month=month,
        fiis=fiis,
        total=total
    )
