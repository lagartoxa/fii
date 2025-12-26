"""
UserRole model - Many-to-many junction table for users and roles.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.models.base import BaseModel

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.role import Role


class UserRole(BaseModel):
    """
    UserRole junction table for many-to-many relationship between users and roles.

    Table: user_role (SINGULAR)

    Purpose: Maps which roles are assigned to which users.

    Relationships:
    - Many-to-one → User (user who has this role assignment)
    - Many-to-one → Role (role assigned to the user)
    """

    __tablename__ = "user_role"
    __table_args__ = (
        UniqueConstraint('user_pk', 'role_pk', name='uq_user_role_user_role'),
        {'comment': 'Many-to-many junction: users ↔ roles'}
    )

    user_pk = Column(
        BigInteger,
        ForeignKey('user.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="User reference"
    )

    role_pk = Column(
        BigInteger,
        ForeignKey('role.pk', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Role reference"
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="user_roles",
        foreign_keys=[user_pk]
    )

    role = relationship(
        "Role",
        back_populates="user_roles",
        foreign_keys=[role_pk]
    )

    def __repr__(self) -> str:
        return f"<UserRole(pk={self.pk}, user_pk={self.user_pk}, role_pk={self.role_pk})>"
