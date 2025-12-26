"""
Permission model - Granular permissions for RBAC.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.role_permission import RolePermission


class Permission(BaseModel):
    """
    Permission model for fine-grained access control.

    Table: permission (SINGULAR)

    Format: resource:action
    - resource: Resource name (e.g., user, fii, transaction, dividend, portfolio, import, log)
    - action: Action name (e.g., create, read, update, delete, list, export)

    Examples:
    - user:create - Can create users
    - transaction:read - Can read transactions
    - portfolio:export - Can export portfolio data

    Relationships:
    - One-to-many → RolePermission (roles that have this permission)
    """

    __tablename__ = "permission"
    __table_args__ = (
        UniqueConstraint('resource', 'action', 'rm_timestamp', name='uq_permission_resource_action_rm_timestamp'),
        UniqueConstraint('description', 'rm_timestamp', name='uq_permission_description_rm_timestamp'),
        {'comment': 'Granular permissions for RBAC (resource:action format)'}
    )

    resource = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Resource name (user, fii, transaction, dividend, portfolio, import, log)"
    )

    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Action name (create, read, update, delete, list, export)"
    )

    description = Column(
        String(255),
        nullable=True,
        comment="Permission description"
    )

    # Relationships
    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Permission(pk={self.pk}, resource='{self.resource}', action='{self.action}')>"

    @property
    def permission_string(self) -> str:
        """
        Get permission as a string in 'resource:action' format.

        Returns:
            Permission string (e.g., 'user:create', 'transaction:read')
        """
        return f"{self.resource}:{self.action}"

    def __str__(self) -> str:
        return self.permission_string
