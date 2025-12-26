"""
User model - User accounts and authentication.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.role import Role
    from app.db.models.user_role import UserRole
    from app.db.models.fii_transaction import FiiTransaction
    from app.db.models.dividend import Dividend
    from app.db.models.fii_holding import FiiHolding
    from app.db.models.import_job import ImportJob
    from app.db.models.refresh_token import RefreshToken
    from app.db.models.log import Log


class User(BaseModel):
    """
    User model for authentication and user management.

    Table: user (SINGULAR)

    Relationships:
    - One-to-many → UserRole (roles assigned to this user)
    - One-to-many → FiiTransaction (transactions created by this user)
    - One-to-many → Dividend (dividends tracked by this user)
    - One-to-many → FiiHolding (portfolio holdings for this user)
    - One-to-many → ImportJob (import jobs created by this user)
    - One-to-many → RefreshToken (refresh tokens for this user)
    - One-to-many → Log (log entries for this user)
    """

    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint('username', 'rm_timestamp', name='uq_user_username_rm_timestamp'),
        UniqueConstraint('email', 'rm_timestamp', name='uq_user_email_rm_timestamp'),
        {'comment': 'User accounts and authentication'}
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="User email address (unique)"
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Username for login (unique)"
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="bcrypt hashed password"
    )

    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User's full name"
    )

    # Status fields
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='true',
        index=True,
        comment="Account active status"
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
        comment="Superuser flag (bypasses RLS and has all permissions)"
    )

    # Relationships
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="UserRole.user_pk"
    )

    fii_transactions = relationship(
        "FiiTransaction",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="FiiTransaction.user_pk"
    )

    dividends = relationship(
        "Dividend",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Dividend.user_pk"
    )

    fii_holdings = relationship(
        "FiiHolding",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="FiiHolding.user_pk"
    )

    import_jobs = relationship(
        "ImportJob",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="ImportJob.user_pk"
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="RefreshToken.user_pk"
    )

    logs = relationship(
        "Log",
        back_populates="user",
        foreign_keys="Log.user_pk"
    )

    def __repr__(self) -> str:
        return f"<User(pk={self.pk}, username='{self.username}', email='{self.email}')>"

    @property
    def roles(self) -> List["Role"]:
        """Get all roles assigned to this user."""
        return [ur.role for ur in self.user_roles if not ur.deleted]

    @property
    def permissions(self) -> List[str]:
        """
        Get all permissions for this user (from all assigned roles).

        Returns:
            List of permission strings in 'resource:action' format.
        """
        permissions = set()
        for role in self.roles:
            for rp in role.role_permissions:
                if not rp.deleted and rp.permission and not rp.permission.deleted:
                    permissions.add(f"{rp.permission.resource}:{rp.permission.action}")
        return sorted(list(permissions))

    def has_permission(self, resource: str, action: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            resource: Resource name (e.g., 'transaction', 'dividend')
            action: Action name (e.g., 'create', 'read', 'update', 'delete')

        Returns:
            True if user has the permission, False otherwise.
        """
        if self.is_superuser:
            return True

        permission_str = f"{resource}:{action}"
        return permission_str in self.permissions
