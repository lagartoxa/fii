"""
Permission repository - Data access layer for Permission model.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.permission import Permission
from app.db.repositories.base import BaseRepository
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionRepository(BaseRepository[Permission, PermissionCreate, PermissionUpdate]):
    """
    Repository for Permission model operations.

    Provides CRUD operations and custom queries for Permission management.
    """

    model_class = Permission

    def get_by_resource_action(self, resource: str, action: str) -> Optional[Permission]:
        """
        Get permission by resource and action (active records only).

        Args:
            resource: Resource name
            action: Action name

        Returns:
            Permission instance or None if not found
        """
        return self.session.query(Permission).filter(
            Permission.resource == resource,
            Permission.action == action,
            Permission.rm_timestamp.is_(None)
        ).first()

    def get_by_resource_action_including_deleted(self, resource: str, action: str) -> Optional[Permission]:
        """
        Get permission by resource and action including soft-deleted records.

        Args:
            resource: Resource name
            action: Action name

        Returns:
            Permission instance or None if not found
        """
        return self.session.query(Permission).filter(
            Permission.resource == resource,
            Permission.action == action
        ).first()
