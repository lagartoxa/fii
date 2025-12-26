"""
Role model - Role definitions for RBAC.
"""

from typing import TYPE_CHECKING, List

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.permission import Permission
    from app.db.models.user_role import UserRole
    from app.db.models.role_permission import RolePermission


class Role(BaseModel):
    """
    Role model for Role-Based Access Control (RBAC).

    Table: role (SINGULAR)

    Relationships:
    - One-to-many → UserRole (users assigned to this role)
    - One-to-many → RolePermission (permissions granted to this role)

    Default Roles (seeded):
    - admin: Full system access (all permissions)
    - user: Portfolio management access (transactions, dividends, portfolio, imports)
    - viewer: Read-only access (read and list permissions only)
    """

    __tablename__ = "role"
    __table_args__ = (
        UniqueConstraint('name', 'rm_timestamp', name='uq_role_name_rm_timestamp'),
        UniqueConstraint('description', 'rm_timestamp', name='uq_role_description_rm_timestamp'),
        {'comment': 'Role definitions for RBAC'}
    )

    name = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Role name (e.g., admin, user, viewer)"
    )

    description = Column(
        String(255),
        nullable=True,
        comment="Role description"
    )

    # Relationships
    user_roles = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan"
    )

    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Role(pk={self.pk}, name='{self.name}')>"

    @property
    def permissions(self) -> List["Permission"]:
        """Get all permissions assigned to this role."""
        return [
            rp.permission
            for rp in self.role_permissions
            if not rp.deleted and rp.permission and not rp.permission.deleted
        ]

    @property
    def permission_strings(self) -> List[str]:
        """
        Get all permissions as strings in 'resource:action' format.

        Returns:
            List of permission strings (e.g., ['user:create', 'transaction:read'])
        """
        return sorted([
            f"{p.resource}:{p.action}"
            for p in self.permissions
        ])

    def has_permission(self, resource: str, action: str) -> bool:
        """
        Check if role has a specific permission.

        Args:
            resource: Resource name (e.g., 'transaction', 'dividend')
            action: Action name (e.g., 'create', 'read', 'update', 'delete')

        Returns:
            True if role has the permission, False otherwise.
        """
        permission_str = f"{resource}:{action}"
        return permission_str in self.permission_strings
