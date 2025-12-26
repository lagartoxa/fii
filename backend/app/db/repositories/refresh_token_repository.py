"""
RefreshToken repository for token-related database operations.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.refresh_token import RefreshToken
from app.db.repositories.base import BaseRepository
from app.schemas.auth import TokenRefreshRequest


class RefreshTokenRepository(BaseRepository[RefreshToken, None, None]):
    """Repository for RefreshToken model."""

    model_class = RefreshToken

    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """
        Get refresh token by token string.

        Args:
            token: Refresh token string

        Returns:
            RefreshToken instance or None if not found
        """
        return self.session.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.rm_timestamp.is_(None)
        ).first()

    def create_token(self, user_pk: int, token: str, expires_at, device_info: Optional[str] = None) -> RefreshToken:
        """
        Create a new refresh token.

        Args:
            user_pk: User primary key
            token: Token string
            expires_at: Expiration datetime
            device_info: Optional device information

        Returns:
            Created RefreshToken instance
        """
        refresh_token = RefreshToken(
            user_pk=user_pk,
            token=token,
            expires_at=expires_at,
            device_info=device_info
        )

        self.session.add(refresh_token)
        self.session.flush()
        self.session.refresh(refresh_token)

        return refresh_token
