"""
Log model - System-wide logging and audit trail.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.user import User


class Log(BaseModel):
    """
    Log model for system-wide logging and audit trail.

    Table: log (SINGULAR)

    Purpose: Capture all significant system events, user actions, and errors for
    auditing, debugging, and compliance.

    Log Levels:
    - debug: Detailed debugging information
    - info: General informational messages
    - warning: Warning messages (recoverable issues)
    - error: Error messages (operation failed)
    - critical: Critical errors (system failure)

    Common Actions:
    - login, logout, login_failed
    - create_transaction, update_transaction, delete_transaction
    - create_dividend, update_dividend
    - import_started, import_completed, import_failed
    - price_updated, holdings_recalculated

    Details Format (JSONB):
    {
      "before": {"quantity": 100},
      "after": {"quantity": 150},
      "change": "+50 units"
    }

    Relationships:
    - Many-to-one → User (user who triggered the action, NULL for system)

    RLS: Enabled (read-only) - users can SELECT their own logs, superusers can SELECT all

    Retention Policy:
    - Consider archiving logs older than 1 year
    - Critical/error logs may need longer retention for compliance
    """

    __tablename__ = "log"
    __table_args__ = (
        CheckConstraint(
            "level IN ('debug', 'info', 'warning', 'error', 'critical')",
            name='ck_log_level'
        ),
        {'comment': 'System-wide logging and audit trail'}
    )

    user_pk: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey('user.pk', ondelete='SET NULL'),
        nullable=True,
        index=True,
        comment="User who triggered action (NULL for system operations)"
    )

    level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Log level: debug, info, warning, error, critical"
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Action performed (login, create_transaction, import_started, etc.)"
    )

    resource_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Resource type (user, fii, transaction, dividend, etc.)"
    )

    resource_pk: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="Resource primary key"
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Log message"
    )

    details: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional structured data in JSON format"
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address (supports IPv6)"
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Browser/client user agent"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="logs",
        foreign_keys=[user_pk]
    )

    def __repr__(self) -> str:
        return (
            f"<Log(pk={self.pk}, level='{self.level}', action='{self.action}', "
            f"user_pk={self.user_pk})>"
        )

    @classmethod
    def create_log(
        cls,
        level: str,
        action: str,
        message: str,
        user_pk: int = None,
        resource_type: str = None,
        resource_pk: int = None,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> "Log":
        """
        Factory method to create a log entry.

        Args:
            level: Log level (debug, info, warning, error, critical)
            action: Action performed
            message: Log message
            user_pk: User who triggered action (optional)
            resource_type: Resource type (optional)
            resource_pk: Resource primary key (optional)
            details: Additional structured data (optional)
            ip_address: IP address (optional)
            user_agent: User agent string (optional)

        Returns:
            Log instance (not yet committed to database)
        """
        return cls(
            level=level,
            action=action,
            message=message,
            user_pk=user_pk,
            resource_type=resource_type,
            resource_pk=resource_pk,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
