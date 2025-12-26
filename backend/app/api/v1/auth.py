"""
Authentication API endpoints.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenRefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If email or username already exists
    """
    with UserRepository(db) as user_repo:
        # Check if email already exists
        existing_user = user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if username already exists
        existing_user = user_repo.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create user schema with hashed password
        user_create = UserCreate(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )

        # Hash password and create user
        new_user = user_repo.model_class(
            email=user_create.email,
            username=user_create.username,
            hashed_password=get_password_hash(user_create.password),
            full_name=user_create.full_name,
            is_active=True,
            is_superuser=False
        )

        db.add(new_user)
        db.flush()
        db.refresh(new_user)

        return new_user


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    User login - returns access and refresh tokens.

    Args:
        credentials: Login credentials (username/email + password)
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    with UserRepository(db) as user_repo:
        # Find user by username or email
        user = user_repo.get_by_username_or_email(credentials.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Create tokens
        access_token = create_access_token(data={"sub": str(user.pk)})
        refresh_token_str = create_refresh_token(data={"sub": str(user.pk)})

    # Store refresh token in database
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    with RefreshTokenRepository(db) as token_repo:
        token_repo.create_token(
            user_pk=user.pk,
            token=refresh_token_str,
            expires_at=expires_at,
            device_info=None  # Can be enhanced to capture user agent
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    token_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token.

    Args:
        token_data: Refresh token request
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    with RefreshTokenRepository(db) as token_repo:
        # Find refresh token in database
        refresh_token_record = token_repo.get_by_token(token_data.refresh_token)

        if not refresh_token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_pk = refresh_token_record.user_pk
        device_info = refresh_token_record.device_info

        # Revoke old refresh token (soft delete)
        token_repo.delete(refresh_token_record.pk)

    # Get user
    with UserRepository(db) as user_repo:
        user = user_repo.get_by_pk(user_pk)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )

        # Create new tokens
        access_token = create_access_token(data={"sub": str(user.pk)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.pk)})

    # Store new refresh token
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    with RefreshTokenRepository(db) as token_repo:
        token_repo.create_token(
            user_pk=user.pk,
            token=new_refresh_token,
            expires_at=new_expires_at,
            device_info=device_info
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
) -> None:
    """
    User logout - revokes refresh token.

    Args:
        token_data: Refresh token to revoke
        db: Database session
    """
    with RefreshTokenRepository(db) as token_repo:
        # Find and revoke refresh token
        refresh_token_record = token_repo.get_by_token(token_data.refresh_token)

        if refresh_token_record:
            token_repo.delete(refresh_token_record.pk)
