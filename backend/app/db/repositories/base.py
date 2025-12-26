"""
Base repository with generic CRUD operations and context manager protocol.
"""

import time
from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.orm import Session

from app.db.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository implementing generic CRUD operations with context manager protocol.

    All repositories must inherit from this class and set the model_class attribute.

    Usage:
        with MyRepository(session, current_user_pk=user_pk) as repo:
            item = repo.create(schema)
    """

    model_class: Type[ModelType] = None

    def __init__(self, session: Session, current_user_pk: Optional[int] = None):
        """
        Initialize repository with database session and optional current user for audit.

        Args:
            session: SQLAlchemy session
            current_user_pk: Current user PK for audit trail (None for system operations)
        """
        if self.model_class is None:
            raise NotImplementedError("model_class must be set in child class")

        self.session = session
        self.current_user_pk = current_user_pk
        self._should_close = False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - handles commit/rollback.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        if exc_type is not None:
            # Exception occurred, rollback
            self.session.rollback()
        else:
            # No exception, commit
            self.session.commit()

        # Don't close session here - let FastAPI dependency handle it
        return False

    def create(self, schema: CreateSchemaType) -> ModelType:
        """
        Generic create method - creates a new record from Pydantic schema.

        Args:
            schema: Pydantic schema instance with creation data

        Returns:
            Created model instance
        """
        # Extract data from schema
        data = schema.model_dump(exclude_unset=True)

        # Create model instance
        instance = self.model_class(**data)

        # Set audit fields
        if hasattr(instance, 'created_by_pk'):
            instance.created_by_pk = self.current_user_pk
        if hasattr(instance, 'updated_by_pk'):
            instance.updated_by_pk = self.current_user_pk

        # Add to session
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)

        return instance

    def update(self, pk: int, schema: UpdateSchemaType) -> Optional[ModelType]:
        """
        Generic update method - updates a record from Pydantic schema.

        Args:
            pk: Primary key of record to update
            schema: Pydantic schema instance with update data

        Returns:
            Updated model instance or None if not found
        """
        # Get existing record
        instance = self.get_by_pk(pk)

        if not instance:
            return None

        # Extract data from schema (exclude unset for PATCH semantics)
        data = schema.model_dump(exclude_unset=True)

        # Update fields
        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        # Set audit fields
        if hasattr(instance, 'updated_by_pk'):
            instance.updated_by_pk = self.current_user_pk

        self.session.flush()
        self.session.refresh(instance)

        return instance

    def delete(self, pk: int) -> bool:
        """
        Generic soft delete method - sets rm_timestamp.

        Args:
            pk: Primary key of record to delete

        Returns:
            True if deleted successfully, False if not found
        """
        # Get existing record
        instance = self.get_by_pk(pk)

        if not instance:
            return False

        # Soft delete
        instance.rm_timestamp = int(time.time())

        # Set audit fields
        if hasattr(instance, 'updated_by_pk'):
            instance.updated_by_pk = self.current_user_pk

        self.session.flush()

        return True

    def restore(self, instance: ModelType) -> ModelType:
        """
        Generic restore method - clears rm_timestamp to restore a soft-deleted record.

        Args:
            instance: Soft-deleted model instance to restore

        Returns:
            Restored model instance
        """
        # Restore by clearing rm_timestamp
        instance.rm_timestamp = None

        # Set audit fields
        if hasattr(instance, 'updated_by_pk'):
            instance.updated_by_pk = self.current_user_pk

        self.session.flush()
        self.session.refresh(instance)

        return instance

    def get_by_pk(self, pk: int, include_deleted: bool = False) -> Optional[ModelType]:
        """
        Get a single record by primary key.

        Args:
            pk: Primary key
            include_deleted: If True, include soft-deleted records

        Returns:
            Model instance or None if not found
        """
        query = self.session.query(self.model_class).filter(
            self.model_class.pk == pk
        )

        # Apply soft delete filter
        if not include_deleted:
            query = query.filter(self.model_class.rm_timestamp.is_(None))

        return query.first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: If True, include soft-deleted records

        Returns:
            List of model instances
        """
        query = self.session.query(self.model_class)

        # Apply soft delete filter
        if not include_deleted:
            query = query.filter(self.model_class.rm_timestamp.is_(None))

        return query.offset(skip).limit(limit).all()
