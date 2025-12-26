# Database Migration Setup

## What Has Been Created

### Alembic Migrations (Phase 1 Complete)

Two critical migration files have been created:

1. **[001_initial_schema.py](../../backend/alembic/versions/001_initial_schema.py)** - Complete database schema
2. **[002_seed_rbac_data.py](../../backend/alembic/versions/002_seed_rbac_data.py)** - RBAC seed data

### Migration 001: Initial Schema

Creates all 12 tables with complete implementation:

**RBAC System (5 tables):**
- `user` - User accounts with authentication fields
- `role` - Role definitions (admin, user, viewer)
- `permission` - Granular permissions (resource:action format)
- `user_role` - Many-to-many junction table
- `role_permission` - Many-to-many junction table

**Core Financial Data (4 tables):**
- `fii` - FII master catalog with ticker, name, sector, price tracking
- `fii_transaction` - Purchase/sale transactions with cost basis for tax reporting
- `dividend` - Monthly dividend payment records
- `fii_holding` - Cached portfolio positions for performance optimization

**File Import (1 table):**
- `import_job` - CSV/Excel import tracking with JSONB error_details field

**Authentication & Audit (2 tables):**
- `refresh_token` - JWT refresh token storage with device tracking
- `log` - System-wide logging and audit trail

### Key Features Implemented

**1. Soft Delete Pattern (ALL tables):**
- `rm_timestamp` BIGINT column (stores Unix epoch when deleted)
- Partial indexes: `WHERE rm_timestamp IS NULL`
- Never uses hard DELETE operations

**2. Audit Trail (ALL tables):**
- `created_at` TIMESTAMP NOT NULL DEFAULT NOW()
- `created_by_pk` BIGINT NULLABLE FK → user.pk
- `updated_at` TIMESTAMP NOT NULL DEFAULT NOW()
- `updated_by_pk` BIGINT NULLABLE FK → user.pk
- Automatic updated_at triggers on all tables

**3. Row-Level Security (RLS):**
Enabled on user-scoped tables:
- `fii_transaction`
- `dividend`
- `fii_holding`
- `import_job`
- `refresh_token`
- `log` (read-only for regular users)

**4. Comprehensive Indexing:**
- All foreign keys indexed
- Commonly filtered columns indexed (user_pk, fii_pk, dates)
- Partial indexes excluding soft-deleted records
- Composite indexes for common query patterns

**5. Business Rules Enforcement:**
- CHECK constraints for valid transaction types, statuses, enums
- CHECK constraints for positive quantities and prices
- UNIQUE constraints for business keys (email, username, ticker)

**6. Financial Data Integrity:**
- All monetary values use NUMERIC type (never FLOAT)
- Precision: NUMERIC(10,2) for prices, NUMERIC(12,2) for totals
- Cost basis tracking in fii_transaction for FIFO tax reporting

### Migration 002: RBAC Seed Data

Seeds the following data:

**Permissions (42 total):**
- User management (create, read, update, delete, list)
- Role management (create, read, update, delete, list)
- Permission management (create, read, update, delete, list)
- FII catalog (create, read, update, delete, list)
- Transactions (create, read, update, delete, list, export)
- Dividends (create, read, update, delete, list, export)
- Portfolio (read, export)
- Imports (create, read, list)
- Logs (read, list)

**Roles (3 system roles):**

1. **admin** - Full system access (all 42 permissions)
2. **user** - Portfolio management access (transactions, dividends, portfolio, imports)
3. **viewer** - Read-only access (read and list permissions only)

**Default Admin User:**
- Email: admin@fii.local
- Username: admin
- Password: admin123 (CHANGE IN PRODUCTION!)
- is_superuser: true
- is_active: true
- email_verified: true
- Assigned to admin role

## How to Run the Migrations

### Prerequisites

1. **PostgreSQL 16+ must be running:**
   ```bash
   # Option 1: Using Docker Compose (if Docker is available)
   cd /home/parallels/projects/fii
   docker compose up -d postgres

   # Option 2: Install PostgreSQL locally
   sudo apt update && sudo apt install postgresql-16
   sudo systemctl start postgresql
   ```

2. **Create the database and user:**
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   CREATE DATABASE fii_portfolio;
   CREATE USER fii_user WITH PASSWORD 'fii_password';
   GRANT ALL PRIVILEGES ON DATABASE fii_portfolio TO fii_user;
   \q
   ```

3. **Create backend .env file:**
   ```bash
   cd /home/parallels/projects/fii/backend
   cp .env.example .env
   # Ensure DATABASE_URL is correct in .env
   ```

4. **Install Python dependencies:**
   ```bash
   cd /home/parallels/projects/fii/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Running the Migrations

**Step 1: Verify Alembic configuration**
```bash
cd /home/parallels/projects/fii/backend
cat alembic.ini | grep script_location
# Should show: script_location = alembic
```

**Step 2: Check migration files exist**
```bash
ls -l alembic/versions/
# Should show:
# 001_initial_schema.py
# 002_seed_rbac_data.py
```

**Step 3: Run the migrations**
```bash
# Activate virtual environment
source venv/bin/activate

# Run all migrations
alembic upgrade head

# OR run one at a time
alembic upgrade 001  # Create all tables
alembic upgrade 002  # Seed RBAC data
```

**Step 4: Verify migration success**
```bash
# Check current migration version
alembic current

# Should output:
# 002 (head)

# List all migrations
alembic history --verbose
```

## Verifying the Database Schema

### Connect to PostgreSQL
```bash
psql postgresql://fii_user:fii_password@localhost:5432/fii_portfolio
```

### Verify Tables Created
```sql
-- List all tables
\dt

-- Should show 12 tables:
-- user, role, permission, user_role, role_permission
-- fii, fii_transaction, dividend, fii_holding
-- import_job, refresh_token, log
```

### Verify Indexes
```sql
-- List indexes for a table
\d+ user

-- Check soft delete indexes
SELECT tablename, indexname
FROM pg_indexes
WHERE indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
```

### Verify RLS Policies
```sql
-- List all RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
ORDER BY tablename;

-- Should show policies for:
-- fii_transaction, dividend, fii_holding, import_job, refresh_token, log
```

### Verify Triggers
```sql
-- List all triggers
SELECT tgname, tgrelid::regclass AS table_name
FROM pg_trigger
WHERE tgname LIKE 'update_%_updated_at'
ORDER BY table_name;

-- Should show triggers on all 12 tables
```

### Verify Seed Data
```sql
-- Check roles
SELECT pk, name, description, is_system FROM role WHERE rm_timestamp IS NULL;
-- Should show: admin, user, viewer

-- Check permissions count
SELECT COUNT(*) FROM permission WHERE rm_timestamp IS NULL;
-- Should show: 42

-- Check admin user
SELECT pk, email, username, is_superuser, is_active FROM "user" WHERE rm_timestamp IS NULL;
-- Should show: admin@fii.local, admin, true, true

-- Check role assignments
SELECT
    u.username,
    r.name as role_name
FROM user_role ur
JOIN "user" u ON ur.user_pk = u.pk
JOIN role r ON ur.role_pk = r.pk
WHERE ur.rm_timestamp IS NULL;
-- Should show: admin - admin
```

### Test Soft Delete Pattern
```sql
-- Verify deleted hybrid property works via rm_timestamp
SELECT COUNT(*) FROM "user" WHERE rm_timestamp IS NULL;  -- Active users
SELECT COUNT(*) FROM "user" WHERE rm_timestamp IS NOT NULL;  -- Deleted users
```

## Rollback Instructions

If you need to rollback the migrations:

```bash
cd /home/parallels/projects/fii/backend
source venv/bin/activate

# Rollback to specific version
alembic downgrade 001  # Remove seed data
alembic downgrade base  # Remove all tables

# Or rollback one step at a time
alembic downgrade -1
```

## Troubleshooting

### Error: "relation does not exist"
- Ensure you're connected to the correct database
- Check DATABASE_URL in .env file
- Verify migrations have run: `alembic current`

### Error: "password authentication failed"
- Verify database credentials in .env
- Check PostgreSQL pg_hba.conf allows password authentication
- Try connecting manually: `psql postgresql://fii_user:fii_password@localhost:5432/fii_portfolio`

### Error: "could not connect to server"
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check PostgreSQL is listening on port 5432: `sudo netstat -tlnp | grep 5432`
- Verify firewall allows connections to port 5432

### Error: "permission denied for schema public"
- Grant schema permissions:
  ```sql
  \c fii_portfolio
  GRANT ALL ON SCHEMA public TO fii_user;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO fii_user;
  ```

### Error: "alembic: command not found"
- Activate virtual environment: `source venv/bin/activate`
- Install alembic: `pip install alembic`

## Next Steps

After successful migration:

1. **Verify all tables, indexes, and constraints**
   - Run the verification queries above
   - Check that all 12 tables exist
   - Verify RLS policies are active
   - Confirm triggers are in place

2. **Test database connection from FastAPI**
   ```bash
   cd /home/parallels/projects/fii/backend
   python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('Connection successful'); db.close()"
   ```

3. **Create SQLAlchemy models** (Phase 2)
   - Implement base model with soft delete and audit mixins
   - Create all 11 entity models
   - Add hybrid properties for deleted flag

4. **Implement Repository pattern** (Phase 2)
   - Create BaseRepository with context manager
   - Implement generic CRUD methods
   - Create specific repositories for each entity

5. **Create Pydantic schemas** (Phase 3)
   - Create 5 schema types per model (Base, Create, Update, InDB, Response)
   - Add validation rules
   - Implement custom validators

## Migration File Locations

- **Migration 001**: [backend/alembic/versions/001_initial_schema.py](../../backend/alembic/versions/001_initial_schema.py)
- **Migration 002**: [backend/alembic/versions/002_seed_rbac_data.py](../../backend/alembic/versions/002_seed_rbac_data.py)
- **Alembic Config**: [backend/alembic.ini](../../backend/alembic.ini)
- **Alembic Env**: [backend/alembic/env.py](../../backend/alembic/env.py)
- **Alembic Template**: [backend/alembic/script.py.mako](../../backend/alembic/script.py.mako)

## Summary

**What's Complete:**
- ✅ Alembic configuration files created
- ✅ Migration 001: Complete database schema (12 tables, all indexes, all constraints, RLS, triggers)
- ✅ Migration 002: RBAC seed data (3 roles, 42 permissions, admin user)
- ✅ All tables use SINGULAR naming convention
- ✅ Soft delete pattern on ALL tables (rm_timestamp)
- ✅ Audit trail on ALL tables (created_at, created_by_pk, updated_at, updated_by_pk)
- ✅ RLS policies on all user-scoped tables
- ✅ Financial data integrity (NUMERIC types, cost basis tracking)

**What's Needed:**
- ⏳ PostgreSQL must be running
- ⏳ Run migrations: `alembic upgrade head`
- ⏳ Verify schema creation

**Next Phases:**
- 📋 Phase 2: Create SQLAlchemy models and BaseRepository
- 📋 Phase 3: Implement specific repositories
- 📋 Phase 4: Create Pydantic schemas
- 📋 Phase 5: Integration testing
