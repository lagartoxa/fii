"""
User repository for user-related database operations.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for User model."""

    model_class = User

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email

        Returns:
            User instance or None if not found
        """
        return self.session.query(User).filter(
            User.email == email,
            User.rm_timestamp.is_(None)
        ).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            User instance or None if not found
        """
        return self.session.query(User).filter(
            User.username == username,
            User.rm_timestamp.is_(None)
        ).first()

    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """
        Get user by username or email.

        Args:
            identifier: Username or email

        Returns:
            User instance or None if not found
        """
        return self.session.query(User).filter(
            (User.username == identifier) | (User.email == identifier),
            User.rm_timestamp.is_(None)
        ).first()

    def get_by_username_including_deleted(self, username: str) -> Optional[User]:
        """
        Get user by username including soft-deleted records.

        Args:
            username: Username

        Returns:
            User instance or None if not found
        """
        return self.session.query(User).filter(
            User.username == username
        ).first()
