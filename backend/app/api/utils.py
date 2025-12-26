"""
Utility functions for API endpoints.
"""

from typing import Callable, Optional, TypeVar
from app.db.repositories.base import BaseRepository

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")


def create_or_restore(
    repository: BaseRepository,
    create_data: CreateSchemaType,
    find_deleted_fn: Callable[[], Optional[ModelType]],
    update_deleted_fn: Optional[Callable[[ModelType, CreateSchemaType], None]] = None
) -> ModelType:
    """
    Generic helper to create a new record or restore a soft-deleted one.

    This pattern is useful for master data tables with unique constraints.
    When a user tries to create a record that was previously soft-deleted,
    this function will restore the deleted record instead of creating a new one.

    Args:
        repository: Repository instance
        create_data: Pydantic schema with creation data
        find_deleted_fn: Function that searches for a soft-deleted record
                        Returns the deleted record or None
        update_deleted_fn: Optional function to update the deleted record's fields
                          before restoring. Receives (deleted_record, create_data)

    Returns:
        Created or restored model instance

    Example:
        ```python
        def create_fii(fii_data: FiiCreate, ...):
            with FiiRepository(db, current_user_pk=user.pk) as repo:
                # Check if active record exists
                existing = repo.get_by_tag(fii_data.tag)
                if existing:
                    raise HTTPException(400, "Already exists")

                # Try to restore or create
                def find_deleted():
                    return repo.get_by_tag_including_deleted(fii_data.tag)

                def update_deleted(fii, data):
                    fii.name = data.name
                    fii.sector = data.sector

                return create_or_restore(
                    repo, fii_data, find_deleted, update_deleted
                )
        ```
    """
    # Check if a soft-deleted record exists
    deleted_record = find_deleted_fn()

    if deleted_record and deleted_record.rm_timestamp is not None:
        # Update the deleted record's fields if update function provided
        if update_deleted_fn:
            update_deleted_fn(deleted_record, create_data)

        # Restore the soft-deleted record
        restored = repository.restore(deleted_record)
        return restored

    # Create new record
    new_record = repository.create(create_data)
    return new_record
