"""
RolePermission model - Many-to-many junction table for roles and permissions.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.role import Role
    from app.db.models.permission import Permission


class RolePermission(BaseModel):
    """
    RolePermission junction table for many-to-many relationship between roles and permissions.

    Table: role_permission (SINGULAR)

    Purpose: Maps which permissions are granted to which roles.

    Relationships:
    - Many-to-one → Role (role that has this permission assignment)
    - Many-to-one → Permission (permission granted to the role)
    """

    __tablename__ = "role_permission"
    __table_args__ = (
        UniqueConstraint('role_pk', 'permission_pk', name='uq_role_permission_role_permission'),
        {'comment': 'Many-to-many junction: roles ↔ permissions'}
    )

    role_pk = Column(
        BigInteger,
        ForeignKey('role.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Role reference"
    )

    permission_pk = Column(
        BigInteger,
        ForeignKey('permission.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Permission reference"
    )

    # Relationships
    role = relationship(
        "Role",
        back_populates="role_permissions",
        foreign_keys=[role_pk]
    )

    permission = relationship(
        "Permission",
        back_populates="role_permissions",
        foreign_keys=[permission_pk]
    )

    def __repr__(self) -> str:
        return f"<RolePermission(pk={self.pk}, role_pk={self.role_pk}, permission_pk={self.permission_pk})>"
