"""
FII CRUD API endpoints.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.db.repositories.fii_repository import FiiRepository
from app.schemas.fii import FiiCreate, FiiResponse, FiiUpdate

router = APIRouter()


@router.post("/", response_model=FiiResponse, status_code=status.HTTP_201_CREATED)
def create_fii(
    fii_data: FiiCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new FII or restore a soft-deleted one.

    Args:
        fii_data: FII creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created or restored FII

    Raises:
        HTTPException: If active tag already exists
    """
    with FiiRepository(db, current_user_pk=current_user.pk) as fii_repo:
        # Check if tag already exists (active records only)
        existing_fii = fii_repo.get_by_tag(fii_data.tag)

        if existing_fii:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"FII with tag '{fii_data.tag}' already exists"
            )

        # Check if a soft-deleted record exists
        deleted_fii = fii_repo.get_by_tag_including_deleted(fii_data.tag)

        if deleted_fii and deleted_fii.rm_timestamp is not None:
            # Restore the soft-deleted record and update its data
            deleted_fii.name = fii_data.name
            deleted_fii.sector = fii_data.sector
            restored_fii = fii_repo.restore(deleted_fii)
            return restored_fii

        # Create new FII
        new_fii = fii_repo.create(fii_data)

        return new_fii


@router.get("/", response_model=List[FiiResponse])
def list_fiis(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    sector: str | None = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    List all FIIs with optional filtering and pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        sector: Optional sector filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of FIIs
    """
    with FiiRepository(db) as fii_repo:
        fiis = fii_repo.get_all(skip=skip, limit=limit, sector=sector)

        return fiis


@router.get("/{pk}", response_model=FiiResponse)
def get_fii(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a single FII by primary key.

    Args:
        pk: FII primary key
        db: Database session
        current_user: Current authenticated user

    Returns:
        FII record

    Raises:
        HTTPException: If FII not found
    """
    with FiiRepository(db) as fii_repo:
        fii = fii_repo.get_by_pk(pk)

        if not fii:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FII not found"
            )

        return fii


@router.patch("/{pk}", response_model=FiiResponse)
def update_fii(
    pk: int,
    fii_data: FiiUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a FII.

    Args:
        pk: FII primary key
        fii_data: FII update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated FII

    Raises:
        HTTPException: If FII not found or tag already exists
    """
    with FiiRepository(db, current_user_pk=current_user.pk) as fii_repo:
        # Get existing FII
        fii = fii_repo.get_by_pk(pk)

        if not fii:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FII not found"
            )

        # Check if new tag already exists (if tag is being updated)
        if fii_data.tag and fii_data.tag.upper() != fii.tag:
            existing_fii = fii_repo.get_by_tag(fii_data.tag)

            if existing_fii:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"FII with tag '{fii_data.tag}' already exists"
                )

        # Update FII
        updated_fii = fii_repo.update(pk, fii_data)

        return updated_fii


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fii(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Soft delete a FII.

    Args:
        pk: FII primary key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If FII not found
    """
    with FiiRepository(db, current_user_pk=current_user.pk) as fii_repo:
        success = fii_repo.delete(pk)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FII not found"
            )
