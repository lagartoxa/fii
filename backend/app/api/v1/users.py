"""
User CRUD API endpoints.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import get_password_hash
from app.db.models.user import User
from app.db.models.user_role import UserRole
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


def _sync_user_roles(db: Session, user: User, role_pks: List[int], current_user_pk: int) -> None:
    """
    Synchronize user roles - add new and remove old.

    Args:
        db: Database session
        user: User instance
        role_pks: List of role PKs to assign
        current_user_pk: Current user PK for audit
    """
    # Get current role PKs
    current_role_pks = {ur.role_pk for ur in user.user_roles if not ur.deleted}

    # Roles to add
    to_add = set(role_pks) - current_role_pks

    # Roles to remove
    to_remove = current_role_pks - set(role_pks)

    # Add new roles
    for role_pk in to_add:
        user_role = UserRole(
            user_pk=user.pk,
            role_pk=role_pk,
            created_by_pk=current_user_pk,
            updated_by_pk=current_user_pk
        )
        db.add(user_role)

    # Remove old roles (soft delete)
    for ur in user.user_roles:
        if not ur.deleted and ur.role_pk in to_remove:
            ur.soft_delete(current_user_pk)

    db.flush()


def _user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse schema."""
    return UserResponse(
        pk=user.pk,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at,
        role_pks=[ur.role_pk for ur in user.user_roles if not ur.deleted]
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new User or restore a soft-deleted one.

    Args:
        user_data: User creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created or restored User

    Raises:
        HTTPException: If active username or email already exists
    """
    with UserRepository(db, current_user_pk=current_user.pk) as user_repo:
        # Check if username already exists (active records only)
        existing_user = user_repo.get_by_username(user_data.username)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username '{user_data.username}' already exists"
            )

        # Check if email already exists (active records only)
        existing_email = user_repo.get_by_email(user_data.email)

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{user_data.email}' already exists"
            )

        # Check if a soft-deleted record exists with same username
        deleted_user = user_repo.get_by_username_including_deleted(user_data.username)

        if deleted_user and deleted_user.rm_timestamp is not None:
            # Restore the soft-deleted record and update its data
            deleted_user.email = user_data.email
            deleted_user.full_name = user_data.full_name
            deleted_user.hashed_password = get_password_hash(user_data.password)
            restored_user = user_repo.restore(deleted_user)

            # Sync roles
            _sync_user_roles(db, restored_user, user_data.role_pks, current_user.pk)

            return _user_to_response(restored_user)

        # Create new User (excluding role_pks which is not a DB field)
        role_pks = user_data.role_pks
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            created_by_pk=current_user.pk,
            updated_by_pk=current_user.pk
        )
        db.add(new_user)
        db.flush()
        db.refresh(new_user)

        # Sync roles
        _sync_user_roles(db, new_user, role_pks, current_user.pk)

        return _user_to_response(new_user)


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    List all Users with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of Users
    """
    with UserRepository(db) as user_repo:
        users = user_repo.get_all(skip=skip, limit=limit)

        return [_user_to_response(user) for user in users]


@router.get("/{pk}", response_model=UserResponse)
def get_user(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a single User by primary key.

    Args:
        pk: User primary key
        db: Database session
        current_user: Current authenticated user

    Returns:
        User record

    Raises:
        HTTPException: If User not found
    """
    with UserRepository(db) as user_repo:
        user = user_repo.get_by_pk(pk)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return _user_to_response(user)


@router.patch("/{pk}", response_model=UserResponse)
def update_user(
    pk: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a User.

    Args:
        pk: User primary key
        user_data: User update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated User

    Raises:
        HTTPException: If User not found or username/email already exists
    """
    with UserRepository(db, current_user_pk=current_user.pk) as user_repo:
        # Get existing User
        user = user_repo.get_by_pk(pk)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if new username already exists (if username is being updated)
        if user_data.username and user_data.username != user.username:
            existing_user = user_repo.get_by_username(user_data.username)

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with username '{user_data.username}' already exists"
                )

        # Check if new email already exists (if email is being updated)
        if user_data.email and user_data.email != user.email:
            existing_email = user_repo.get_by_email(user_data.email)

            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{user_data.email}' already exists"
                )

        # Extract role_pks and hash password if provided
        update_dict = user_data.model_dump(exclude_unset=True)
        role_pks = update_dict.pop('role_pks', None)

        if 'password' in update_dict:
            password = update_dict.pop('password')
            update_dict['hashed_password'] = get_password_hash(password)

        from pydantic import BaseModel
        class UserUpdateDB(BaseModel):
            email: str | None = None
            username: str | None = None
            full_name: str | None = None
            hashed_password: str | None = None
            is_active: bool | None = None

        # Update User
        updated_user = user_repo.update(pk, UserUpdateDB(**update_dict))

        # Sync roles if provided
        if role_pks is not None:
            _sync_user_roles(db, updated_user, role_pks, current_user.pk)

        return _user_to_response(updated_user)


@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    pk: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Soft delete a User.

    Args:
        pk: User primary key
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If User not found or trying to delete yourself
    """
    if pk == current_user.pk:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete yourself"
        )

    with UserRepository(db, current_user_pk=current_user.pk) as user_repo:
        success = user_repo.delete(pk)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
