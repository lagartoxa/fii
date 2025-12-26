"""
User CRUD API endpoints.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import get_password_hash
from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


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
            return restored_user

        # Create new User with hashed password
        user_dict = user_data.model_dump()
        password = user_dict.pop('password')
        user_dict['hashed_password'] = get_password_hash(password)

        from pydantic import BaseModel
        class UserCreateDB(BaseModel):
            email: str
            username: str
            full_name: str | None
            hashed_password: str

        new_user = user_repo.create(UserCreateDB(**user_dict))

        return new_user


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

        return users


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

        return user


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

        # Hash password if provided
        update_dict = user_data.model_dump(exclude_unset=True)
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

        return updated_user


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
