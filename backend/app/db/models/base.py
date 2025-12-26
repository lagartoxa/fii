"""
Base model and mixins for all database models.

This module provides:
- Base declarative class for all models
- SoftDeleteMixin: Soft delete pattern with rm_timestamp
- AuditMixin: Audit trail with created_at, created_by_pk, updated_at, updated_by_pk
- TimestampMixin: Basic timestamp fields (created_at, updated_at)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Integer, Column, DateTime, ForeignKey, Identity, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

class Base(DeclarativeBase):
    """Base class for all models using SQLAlchemy 2.0 declarative base."""
    pass


class SoftDeleteMixin:
    """
    Soft delete pattern using Unix epoch timestamp.

    Provides:
    - rm_timestamp: BIGINT column storing Unix epoch when deleted (NULL if active)
    - deleted: Hybrid property returning True/False based on rm_timestamp

    Usage:
    - Active records: WHERE rm_timestamp IS NULL
    - Deleted records: WHERE rm_timestamp IS NOT NULL
    - Soft delete: UPDATE table SET rm_timestamp = EXTRACT(EPOCH FROM NOW())::BIGINT
    """

    rm_timestamp: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, index=False)

    @hybrid_property
    def deleted(self) -> bool:
        """Returns True if record is soft-deleted, False otherwise."""
        return self.rm_timestamp is not None

    @deleted.expression
    def deleted(cls):
        """SQL expression for deleted hybrid property."""
        return cls.rm_timestamp.isnot(None)

    def soft_delete(self) -> None:
        """Mark this record as deleted with current Unix timestamp."""
        self.rm_timestamp = int(datetime.utcnow().timestamp())

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.rm_timestamp = None


class TimestampMixin:
    """
    Basic timestamp fields for created_at and updated_at.

    Provides:
    - created_at: Timestamp when record was created (auto-set)
    - updated_at: Timestamp when record was last updated (auto-updated via trigger)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when record was created"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when record was last updated (auto-updated via trigger)"
    )


class AuditMixin(TimestampMixin):
    """
    Full audit trail with timestamps and user tracking.

    Provides:
    - created_at: Timestamp when record was created
    - created_by_pk: User who created the record (NULLABLE for system operations)
    - updated_at: Timestamp when record was last updated
    - updated_by_pk: User who last updated the record (NULLABLE for system operations)

    Note: Audit FKs are NULLABLE to support system operations where no user context exists.
    The updated_at field is automatically updated via PostgreSQL trigger.
    """

    @declared_attr
    def created_by_pk(cls) -> Mapped[Optional[int]]:
        """Foreign key to user who created this record (nullable for system operations)."""
        return mapped_column(
            BigInteger,
            ForeignKey('user.pk', ondelete='SET NULL'),
            nullable=True,
            comment="User who created this record (NULL for system operations)"
        )

    @declared_attr
    def updated_by_pk(cls) -> Mapped[Optional[int]]:
        """Foreign key to user who last updated this record (nullable for system operations)."""
        return mapped_column(
            BigInteger,
            ForeignKey('user.pk', ondelete='SET NULL'),
            nullable=True,
            comment="User who last updated this record (NULL for system operations)"
        )


class BaseModel(Base, SoftDeleteMixin, AuditMixin):
    """
    Base model for all database tables.

    Inherits from:
    - Base: SQLAlchemy declarative base
    - SoftDeleteMixin: Soft delete pattern with rm_timestamp and deleted property
    - AuditMixin: Full audit trail (created_at, created_by_pk, updated_at, updated_by_pk)

    All models should inherit from this class to get:
    - Primary key (pk)
    - Soft delete capability
    - Complete audit trail
    - Consistent column naming
    """

    __abstract__ = True

    pk: Mapped[int] = mapped_column(
        Integer,  # Use Integer instead of BigInteger for SQLite autoincrement compatibility
        primary_key=True,
        autoincrement=True,
        comment="Primary key"
    )

    def __repr__(self) -> str:
        """String representation of model instance."""
        return f"<{self.__class__.__name__}(pk={self.pk})>"
