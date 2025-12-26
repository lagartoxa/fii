"""
Role repository - Data access layer for Role model.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.role import Role
from app.db.repositories.base import BaseRepository
from app.schemas.role import RoleCreate, RoleUpdate


class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    """
    Repository for Role model operations.

    Provides CRUD operations and custom queries for Role management.
    """

    model_class = Role

    def get_by_name(self, name: str) -> Optional[Role]:
        """
        Get role by name (active records only).

        Args:
            name: Role name

        Returns:
            Role instance or None if not found
        """
        return self.session.query(Role).filter(
            Role.name == name,
            Role.rm_timestamp.is_(None)
        ).first()

    def get_by_name_including_deleted(self, name: str) -> Optional[Role]:
        """
        Get role by name including soft-deleted records.

        Args:
            name: Role name

        Returns:
            Role instance or None if not found
        """
        return self.session.query(Role).filter(
            Role.name == name
        ).first()
