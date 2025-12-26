"""
Backwards compatibility import.

This file now imports from app.db.models.base to maintain compatibility.
All new code should import directly from app.db.models.
"""

from app.db.models.base import Base, BaseModel, SoftDeleteMixin, AuditMixin, TimestampMixin
from app.db.models import *  # noqa

__all__ = [
    "Base",
    "BaseModel",
    "SoftDeleteMixin",
    "AuditMixin",
    "TimestampMixin",
]
