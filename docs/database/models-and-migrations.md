# Database Models and Migrations

## Overview

All database models have been created as SQLAlchemy ORM models. Alembic will auto-generate migrations from these models, eliminating the need for manual migration writing.

## Model Structure

### Location

All models are in [backend/app/db/models/](../../backend/app/db/models/)

### Models Created (12 total)

#### RBAC System (5 models)
1. **[user.py](../../backend/app/db/models/user.py)** - User accounts and authentication
2. **[role.py](../../backend/app/db/models/role.py)** - Role definitions
3. **[permission.py](../../backend/app/db/models/permission.py)** - Granular permissions
4. **[user_role.py](../../backend/app/db/models/user_role.py)** - Junction: users ↔ roles
5. **[role_permission.py](../../backend/app/db/models/role_permission.py)** - Junction: roles ↔ permissions

#### Financial Models (4 models)
6. **[fii.py](../../backend/app/db/models/fii.py)** - FII master catalog
7. **[fii_transaction.py](../../backend/app/db/models/fii_transaction.py)** - Purchase/sale transactions
8. **[dividend.py](../../backend/app/db/models/dividend.py)** - Monthly dividend payments
9. **[fii_holding.py](../../backend/app/db/models/fii_holding.py)** - Cached portfolio positions

#### Import & Audit (3 models)
10. **[import_job.py](../../backend/app/db/models/import_job.py)** - File import tracking
11. **[refresh_token.py](../../backend/app/db/models/refresh_token.py)** - JWT refresh tokens
12. **[log.py](../../backend/app/db/models/log.py)** - System-wide logging

### Base Model

All models inherit from **[BaseModel](../../backend/app/db/models/base.py)** which provides:

**SoftDeleteMixin:**
- `rm_timestamp` BIGINT column
- `deleted` hybrid property (returns True/False)
- `soft_delete()` method
- `restore()` method

**AuditMixin:**
- `created_at` TIMESTAMP
- `created_by_pk` BIGINT FK → user.pk (NULLABLE)
- `updated_at` TIMESTAMP
- `updated_by_pk` BIGINT FK → user.pk (NULLABLE)

**BaseModel:**
- `pk` BIGINT primary key (auto-increment)
- All mixins above

## Key Model Features

### User Model
- Authentication fields (email, username, hashed_password)
- Profile fields (full_name)
- Status fields (is_active, is_superuser, email_verified)
- **Properties:**
  - `roles` - Get all assigned roles
  - `permissions` - Get all permissions as strings
- **Methods:**
  - `has_permission(resource, action)` - Check permission
  - `update_last_login()` - Update login timestamp

### Fii Transaction Model
- Tracks buy/sell transactions
- Cost basis field for tax reporting (FIFO method)
- **Properties:**
  - `capital_gain` - Calculate gain/loss for sales
  - `is_buy`, `is_sell` - Boolean helpers

### Fii Holding Model
- Caches portfolio calculations
- **Properties:**
  - `unrealized_gain_loss` - Current value - invested
  - `total_return` - Unrealized gain + dividends
  - `return_percentage` - Return as percentage

### Import Job Model
- Tracks CSV/Excel imports
- JSONB `error_details` field for row-level errors
- **Properties:**
  - `success_rate` - Percentage of successful rows
  - `is_completed`, `is_failed`, `is_processing`, `is_pending`

### Refresh Token Model
- JWT refresh token management
- **Properties:**
  - `is_valid` - Check if token is valid
- **Methods:**
  - `revoke()` - Revoke token

### Log Model
- System-wide audit trail
- JSONB `details` field for structured data
- **Class Method:**
  - `create_log(...)` - Factory method to create log entries

## Generating Migrations from Models

### Prerequisites

1. **Install Python dependencies:**
   ```bash
   cd /home/parallels/projects/fii/backend

   # Install python3-venv if not available
   sudo apt install python3.10-venv

   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Ensure .env file exists:**
   ```bash
   cp .env.example .env
   # Edit .env if needed (DATABASE_URL, SECRET_KEY, etc.)
   ```

### Generate Initial Migration

**Option 1: With PostgreSQL Running (Recommended)**

This will generate the migration AND create the database schema:

```bash
cd /home/parallels/projects/fii/backend
source venv/bin/activate

# Ensure PostgreSQL is running
# docker compose up -d postgres
# OR: sudo systemctl start postgresql

# Generate migration
alembic revision --autogenerate -m "Initial schema with all 12 tables"

# Review the generated migration in alembic/versions/

# Apply the migration
alembic upgrade head

# Verify
alembic current
psql postgresql://fii_user:fii_password@localhost:5432/fii_portfolio -c "\dt"
```

**Option 2: Without PostgreSQL (Migration only, no DB creation)**

Generate migration file without connecting to database:

```bash
cd /home/parallels/projects/fii/backend
source venv/bin/activate

# Generate migration (offline mode)
alembic revision -m "Initial schema with all 12 tables"

# Manually edit the generated migration if needed
# Then apply when PostgreSQL is available
```

### What the Auto-Generated Migration Will Include

Alembic will automatically generate SQL for:

✅ **All 12 tables** with SINGULAR naming
✅ **All columns** with correct types and constraints
✅ **All foreign keys** with proper ondelete behavior
✅ **All unique constraints**
✅ **All CHECK constraints**
✅ **All indexes** (from model `index=True` fields)

⚠️ **Manual additions needed:**

The following must be added manually to the migration:

1. **Partial indexes** (excluding soft-deleted records)
2. **RLS policies** (Row-Level Security)
3. **Triggers** (auto-update updated_at)
4. **PostgreSQL functions** (update_updated_at_column)

### Adding Manual Items to Auto-Generated Migration

After running `alembic revision --autogenerate`, edit the generated migration:

```python
def upgrade() -> None:
    # Auto-generated table creation code will be here
    # ...

    # MANUALLY ADD: PostgreSQL function for triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # MANUALLY ADD: Triggers for each table
    for table in ['user', 'role', 'permission', 'user_role', 'role_permission',
                  'fii', 'fii_transaction', 'dividend', 'fii_holding',
                  'import_job', 'refresh_token', 'log']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

    # MANUALLY ADD: Partial indexes for soft delete
    # Example for user table:
    op.create_index(
        'idx_user_email_active',
        'user',
        ['email'],
        unique=False,
        postgresql_where=sa.text('rm_timestamp IS NULL')
    )

    # MANUALLY ADD: RLS policies
    op.execute("ALTER TABLE fii_transaction ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY user_own_transactions ON fii_transaction
        FOR ALL
        USING (
            user_pk = current_setting('app.current_user_pk', true)::BIGINT OR
            current_setting('app.is_superuser', true)::BOOLEAN = TRUE
        )
    """)
    # Repeat for other RLS-enabled tables...


def downgrade() -> None:
    # MANUALLY ADD: Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Auto-generated table drops will be here
    # ...
```

## Creating Seed Data Migration

After creating the initial schema migration, create a separate migration for seed data:

```bash
cd /home/parallels/projects/fii/backend
source venv/bin/activate

# Create empty migration for seed data
alembic revision -m "Seed RBAC data"

# Edit the generated file and add seed data
# See: docs/database/migration-setup.md for seed data SQL
```

Seed data should include:
- 42 permissions (resource:action format)
- 3 roles (admin, user, viewer)
- Role-permission assignments
- Admin user (email: admin@fii.local, password: admin123)

## Model Modification Workflow

When modifying models:

1. **Edit the SQLAlchemy model** in `app/db/models/`
2. **Generate migration:**
   ```bash
   alembic revision --autogenerate -m "Add field to user table"
   ```
3. **Review generated migration** - verify it matches your intent
4. **Add manual items** if needed (indexes, RLS, triggers)
5. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

## Relationships

All relationships are bidirectional using SQLAlchemy `relationship()`:

```python
# User model
user_roles = relationship("UserRole", back_populates="user")

# UserRole model
user = relationship("User", back_populates="user_roles")
```

**Cascade Behavior:**
- `cascade="all, delete-orphan"` - Delete children when parent is deleted
- `ondelete='CASCADE'` - Database-level cascade
- `ondelete='RESTRICT'` - Prevent deletion if children exist
- `ondelete='SET NULL'` - Set FK to NULL when parent is deleted

## Querying Examples

### Basic Query with Soft Delete Filter
```python
from app.db.models import User

# Get active users only
active_users = session.query(User).filter(User.rm_timestamp.is_(None)).all()

# OR use the hybrid property
active_users = session.query(User).filter(~User.deleted).all()
```

### Query with Relationships
```python
from app.db.models import User, FiiTransaction, Fii

# Get user with transactions (eager loading)
user = session.query(User).filter(User.pk == user_pk).first()
transactions = user.fii_transactions  # Already loaded

# Get transactions with FII details
transactions = session.query(FiiTransaction).join(Fii).filter(
    FiiTransaction.user_pk == user_pk,
    FiiTransaction.rm_timestamp.is_(None),
    Fii.rm_timestamp.is_(None)
).all()
```

### Using Properties
```python
user = session.query(User).filter(User.pk == user_pk).first()

# Get all permissions
permissions = user.permissions  # Returns list of "resource:action" strings

# Check permission
has_access = user.has_permission('transaction', 'create')  # Returns bool
```

## File Structure

```
backend/
├── app/
│   └── db/
│       ├── base.py                    # Backwards compatibility (imports from models/)
│       ├── models/
│       │   ├── __init__.py            # Import all models
│       │   ├── base.py                # BaseModel with mixins
│       │   ├── user.py
│       │   ├── role.py
│       │   ├── permission.py
│       │   ├── user_role.py
│       │   ├── role_permission.py
│       │   ├── fii.py
│       │   ├── fii_transaction.py
│       │   ├── dividend.py
│       │   ├── fii_holding.py
│       │   ├── import_job.py
│       │   ├── refresh_token.py
│       │   └── log.py
│       └── session.py
├── alembic/
│   ├── env.py                         # Updated to import models
│   └── versions/
│       └── (auto-generated migrations)
└── alembic.ini
```

## Next Steps

1. **Install dependencies** (if not done):
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL**:
   ```bash
   cd /home/parallels/projects/fii
   docker compose up -d postgres
   # OR: sudo systemctl start postgresql
   ```

3. **Generate initial migration**:
   ```bash
   cd backend
   source venv/bin/activate
   alembic revision --autogenerate -m "Initial schema with all 12 tables"
   ```

4. **Add manual items** to generated migration (RLS, triggers, partial indexes)

5. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

6. **Create seed data migration**:
   ```bash
   alembic revision -m "Seed RBAC data"
   # Edit migration to add seed data
   alembic upgrade head
   ```

7. **Verify**:
   ```bash
   alembic current
   psql postgresql://fii_user:fii_password@localhost:5432/fii_portfolio -c "\dt"
   ```

## See Also

- [Database Schema Documentation](schema.md)
- [Migration Setup Guide](migration-setup.md)
- [Architecture Overview](../architecture/overview.md)
