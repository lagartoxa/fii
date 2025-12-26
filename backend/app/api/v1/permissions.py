"""
Permission CRUD API endpoints.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.db.repositories.permission_repository import PermissionRepository
from app.schemas.permission import PermissionCreate, PermissionResponse, PermissionUpdate

router = APIRouter()


@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new Permission or restore a soft-deleted one.

    Args:
        permission_data: Permission creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created or restored Permission

    Raises:
        HTTPException: If active resource:action already exists
    """
    with PermissionRepository(db, current_user_pk=current_user.pk) as permission_repo:
        # Check if resource:action already exists (active records only)
        existing_permission = permission_repo.get_by_resource_action(
            permission_data.resource,
            permission_data.action
        )

        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission '{permission_data.resource}:{permission_data.action}' already exists"
            )

        # Check if a soft-deleted record exists
        deleted_permission = permission_repo.get_by_resource_action_including_deleted(
            permission_data.resource,
            permission_data.action
        )

        if deleted_permission and deleted_permission.rm_timestamp is not None:
            # Restore the soft-deleted record and update its data
            deleted_permission.description = permission_data.description
            restored_permission = permission_repo.restore(deleted_permission)
            return restored_permission

        # Create new Permission
        new_permission = permission_repo.create(permission_data)

        return new_permission


@router.get("/", response_model=List[PermissionResponse])
def list_permissions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    resource: str | None = Query(None, description="Filter by resource"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    List all Permissions with optional filtering and pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        resource: Optional resource filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of Permissions
    """
    with PermissionRepository(db) as permission_repo:
        permissions = permission_repo.get_all(skip=skip, limit=limit)

        # Apply resource filter if provided
        if resource:
            permissions = [p for p in permissions if p.resource == resource]

        return permissions


@router.get("/{pk}", response_model=PermissionResponse)
def get_permission(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a single Permission by primary key.

    Args:
        pk: Permission primary key
        db: Database session
        current_user: Current authenticated user

    Returns:
        Permission record

    Raises:
        HTTPException: If Permission not found
    """
    with PermissionRepository(db) as permission_repo:
        permission = permission_repo.get_by_pk(pk)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        return permission


@router.patch("/{pk}", response_model=PermissionResponse)
def update_permission(
    pk: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a Permission.

    Args:
        pk: Permission primary key
        permission_data: Permission update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated Permission

    Raises:
        HTTPException: If Permission not found or resource:action already exists
    """
    with PermissionRepository(db, current_user_pk=current_user.pk) as permission_repo:
        # Get existing Permission
        permission = permission_repo.get_by_pk(pk)

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        # Check if new resource:action already exists (if either is being updated)
        new_resource = permission_data.resource if permission_data.resource else permission.resource
        new_action = permission_data.action if permission_data.action else permission.action

        if (permission_data.resource or permission_data.action) and \
           (new_resource != permission.resource or new_action != permission.action):
            existing_permission = permission_repo.get_by_resource_action(new_resource, new_action)

            if existing_permission:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permission '{new_resource}:{new_action}' already exists"
                )

        # Update Permission
        updated_permission = permission_repo.update(pk, permission_data)

        return updated_permission


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Soft delete a Permission.

    Args:
        pk: Permission primary key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If Permission not found
    """
    with PermissionRepository(db, current_user_pk=current_user.pk) as permission_repo:
        success = permission_repo.delete(pk)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
