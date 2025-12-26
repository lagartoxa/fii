"""
RefreshToken model - JWT refresh token storage with device tracking.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.user import User


class RefreshToken(BaseModel):
    """
    RefreshToken model for JWT refresh token management.

    Table: refresh_token (SINGULAR)

    Purpose: Store JWT refresh tokens with expiration and revocation tracking.

    JWT Strategy:
    - Access tokens: Short-lived (15-30 minutes), stored in memory
    - Refresh tokens: Long-lived (7 days), stored in database
    - Refresh token rotation: New refresh token issued on each access token refresh
    - Old refresh token marked as revoked

    Relationships:
    - Many-to-one → User (user who owns this refresh token)

    RLS: Enabled - users can only access their own tokens

    Cleanup:
    - Periodically delete expired tokens:
      DELETE FROM refresh_token WHERE expires_at < NOW() AND rm_timestamp IS NULL
    """

    __tablename__ = "refresh_token"
    __table_args__ = (
        {'comment': 'JWT refresh token storage with device tracking'}
    )

    user_pk: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('user.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Owner user reference"
    )

    token: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        index=True,
        comment="Refresh token string"
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Token expiration timestamp"
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
        comment="Token revoked (true after refresh token rotation)"
    )

    device_info: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Device/browser information"
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address (supports IPv6)"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="refresh_tokens",
        foreign_keys=[user_pk]
    )

    def __repr__(self) -> str:
        return (
            f"<RefreshToken(pk={self.pk}, user_pk={self.user_pk}, "
            f"revoked={self.is_revoked}, expires_at={self.expires_at})>"
        )

    @property
    def is_valid(self) -> bool:
        """
        Check if refresh token is valid (not revoked and not expired).

        Returns:
            True if token is valid, False otherwise.
        """
        from datetime import datetime, timezone
        return not self.is_revoked and self.expires_at > datetime.now(timezone.utc)

    def revoke(self) -> None:
        """Revoke this refresh token."""
        self.is_revoked = True
