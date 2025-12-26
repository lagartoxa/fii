"""
Role CRUD API endpoints.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.db.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate

router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new Role or restore a soft-deleted one.

    Args:
        role_data: Role creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created or restored Role

    Raises:
        HTTPException: If active name already exists
    """
    with RoleRepository(db, current_user_pk=current_user.pk) as role_repo:
        # Check if name already exists (active records only)
        existing_role = role_repo.get_by_name(role_data.name)

        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_data.name}' already exists"
            )

        # Check if a soft-deleted record exists
        deleted_role = role_repo.get_by_name_including_deleted(role_data.name)

        if deleted_role and deleted_role.rm_timestamp is not None:
            # Restore the soft-deleted record and update its data
            deleted_role.description = role_data.description
            restored_role = role_repo.restore(deleted_role)
            return restored_role

        # Create new Role
        new_role = role_repo.create(role_data)

        return new_role


@router.get("/", response_model=List[RoleResponse])
def list_roles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    List all Roles with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of Roles
    """
    with RoleRepository(db) as role_repo:
        roles = role_repo.get_all(skip=skip, limit=limit)

        return roles


@router.get("/{pk}", response_model=RoleResponse)
def get_role(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a single Role by primary key.

    Args:
        pk: Role primary key
        db: Database session
        current_user: Current authenticated user

    Returns:
        Role record

    Raises:
        HTTPException: If Role not found
    """
    with RoleRepository(db) as role_repo:
        role = role_repo.get_by_pk(pk)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        return role


@router.patch("/{pk}", response_model=RoleResponse)
def update_role(
    pk: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a Role.

    Args:
        pk: Role primary key
        role_data: Role update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated Role

    Raises:
        HTTPException: If Role not found or name already exists
    """
    with RoleRepository(db, current_user_pk=current_user.pk) as role_repo:
        # Get existing Role
        role = role_repo.get_by_pk(pk)

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )

        # Check if new name already exists (if name is being updated)
        if role_data.name and role_data.name != role.name:
            existing_role = role_repo.get_by_name(role_data.name)

            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role with name '{role_data.name}' already exists"
                )

        # Update Role
        updated_role = role_repo.update(pk, role_data)

        return updated_role


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Soft delete a Role.

    Args:
        pk: Role primary key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If Role not found
    """
    with RoleRepository(db, current_user_pk=current_user.pk) as role_repo:
        success = role_repo.delete(pk)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
