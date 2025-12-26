"""
Database models for the FII Portfolio Management System.

This module imports all SQLAlchemy models to ensure they are registered
with the Base metadata. This is required for Alembic autogenerate to work properly.

All models follow these conventions:
- Table names: SINGULAR (e.g., user, role, fii_transaction)
- Primary keys: pk (BIGINT, auto-increment)
- Foreign keys: suffixed with _pk (e.g., user_pk, fii_pk)
- Soft delete: rm_timestamp (BIGINT, nullable)
- Audit trail: created_at, created_by_pk, updated_at, updated_by_pk

Models:
- User: User accounts and authentication
- Role: Role definitions for RBAC
- Permission: Granular permissions (resource:action format)
- UserRole: Many-to-many junction for users and roles
- RolePermission: Many-to-many junction for roles and permissions
- Fii: FII master catalog (tickers, names, sectors, prices)
- FiiTransaction: Purchase/sale transactions with cost basis tracking
- Dividend: Monthly dividend payment records
- FiiHolding: Cached portfolio positions (performance optimization)
- ImportJob: CSV/Excel file import tracking with error details
- RefreshToken: JWT refresh token storage with device tracking
- Log: System-wide logging and audit trail
"""

from app.db.models.base import Base, BaseModel, SoftDeleteMixin, AuditMixin, TimestampMixin

# RBAC models
from app.db.models.user import User
from app.db.models.role import Role
from app.db.models.permission import Permission
from app.db.models.user_role import UserRole
from app.db.models.role_permission import RolePermission

# Financial models
from app.db.models.fii import Fii
from app.db.models.fii_transaction import FiiTransaction
from app.db.models.dividend import Dividend
from app.db.models.fii_holding import FiiHolding

# Import & audit models
from app.db.models.import_job import ImportJob
from app.db.models.refresh_token import RefreshToken
from app.db.models.log import Log

# Export all models for easy importing
__all__ = [
    # Base classes
    "Base",
    "BaseModel",
    "SoftDeleteMixin",
    "AuditMixin",
    "TimestampMixin",
    # RBAC models
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    # Financial models
    "Fii",
    "FiiTransaction",
    "Dividend",
    "FiiHolding",
    # Import & audit models
    "ImportJob",
    "RefreshToken",
    "Log",
]
