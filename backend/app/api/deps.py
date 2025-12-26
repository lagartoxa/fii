from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.security import decode_token
from app.db.session import get_db

# HTTP Bearer security scheme
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Dependency to get current user ID from JWT token.

    Args:
        credentials: HTTP Bearer credentials containing JWT token

    Returns:
        User ID from token

    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def get_current_user(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Dependency to get current user from database.

    Args:
        db: Database session
        user_id: Current user ID from token

    Returns:
        User object

    Raises:
        HTTPException: If user not found or inactive
    """
    from app.db.models.user import User

    user = db.query(User).filter(
        User.pk == int(user_id),
        User.rm_timestamp.is_(None)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Set RLS context (PostgreSQL only)
    try:
        db.execute(text(f"SET app.current_user_pk = {user.pk}"))
        db.execute(text(f"SET app.is_superuser = {user.is_superuser}"))
    except Exception:
        # SQLite doesn't support SET command - skip RLS for testing
        pass

    return user


def get_current_active_superuser(
    current_user = Depends(get_current_user),
):
    """
    Dependency to get current superuser.

    Args:
        current_user: Current user object

    Returns:
        User object if superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
