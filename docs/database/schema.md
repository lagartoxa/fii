# Database Schema Documentation

## Overview

The FII Portfolio Management System uses a PostgreSQL database with 12 tables implementing a comprehensive RBAC (Role-Based Access Control) system and financial transaction tracking.

**Database Name:** `fii_portfolio`
**PostgreSQL Version:** 16+
**Character Set:** UTF-8
**Timezone:** UTC (all timestamps stored in UTC)

## Schema Principles

### 1. Naming Conventions (MANDATORY)

- **Table names:** SINGULAR form (e.g., `user`, `fii_transaction`, NOT `users`, `fii_transactions`)
- **Primary keys:** `pk` BIGINT (auto-increment)
- **Foreign keys:** suffixed with `_pk` (e.g., `user_pk`, `fii_pk`)
- **Indexes:** prefixed with `idx_`
- **Constraints:** prefixed with constraint type (`uq_`, `fk_`, `ck_`)

### 2. Soft Delete Pattern (ALL tables)

Every table includes:
```sql
rm_timestamp BIGINT NULL  -- Unix epoch timestamp when deleted, NULL if active
```

**Usage:**
- Active records: `WHERE rm_timestamp IS NULL`
- Deleted records: `WHERE rm_timestamp IS NOT NULL`
- Never use SQL DELETE operations
- Soft delete: `UPDATE table SET rm_timestamp = EXTRACT(EPOCH FROM NOW())::BIGINT`

### 3. Audit Trail (ALL tables)

Every table includes:
```sql
created_at    TIMESTAMP NOT NULL DEFAULT NOW()
created_by_pk BIGINT NULL FK → user.pk  -- NULLABLE for system operations
updated_at    TIMESTAMP NOT NULL DEFAULT NOW()
updated_by_pk BIGINT NULL FK → user.pk  -- NULLABLE for system operations
```

**Automatic Updates:**
- `updated_at` automatically set by trigger on UPDATE
- Audit FKs are NULLABLE to support system-initiated operations

### 4. Row-Level Security (RLS)

PostgreSQL RLS enabled on user-scoped tables to enforce data isolation:
- `fii_transaction` - Users can only access their own transactions
- `dividend` - Users can only access their own dividends
- `fii_holding` - Users can only access their own holdings
- `import_job` - Users can only access their own import jobs
- `refresh_token` - Users can only access their own tokens
- `log` - Users can only READ their own logs (superusers read all)

**RLS Context Variables:**
```sql
SET app.current_user_pk = 123;  -- Set in API dependency
SET app.is_superuser = true;    -- Set in API dependency
```

## Table Inventory

### RBAC System (5 tables)

#### 1. user
User accounts and authentication.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User email address |
| username | VARCHAR(100) | NOT NULL, UNIQUE | Username for login |
| full_name | VARCHAR(255) | NULL | Full name |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | Account active status |
| is_superuser | BOOLEAN | NOT NULL, DEFAULT false | Superuser flag |
| email_verified | BOOLEAN | NOT NULL, DEFAULT false | Email verification status |
| last_login_at | TIMESTAMP | NULL | Last successful login |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Indexes:**
- `idx_user_email` - Partial index on email (WHERE rm_timestamp IS NULL)
- `idx_user_username` - Partial index on username (WHERE rm_timestamp IS NULL)
- `idx_user_is_active` - Partial index on is_active (WHERE rm_timestamp IS NULL)

**Relationships:**
- One-to-many → user_role
- One-to-many → fii_transaction
- One-to-many → dividend
- One-to-many → fii_holding
- One-to-many → import_job
- One-to-many → refresh_token
- One-to-many → log

---

#### 2. role
Role definitions for RBAC.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| name | VARCHAR(50) | NOT NULL, UNIQUE | Role name (admin, user, viewer) |
| description | VARCHAR(255) | NULL | Role description |
| is_system | BOOLEAN | NOT NULL, DEFAULT false | System role (cannot be deleted) |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Indexes:**
- `idx_role_name` - Partial index on name (WHERE rm_timestamp IS NULL)

**Relationships:**
- One-to-many → user_role
- One-to-many → role_permission

**Default Roles:**
- `admin` - Full system access
- `user` - Portfolio management access
- `viewer` - Read-only access

---

#### 3. permission
Granular permissions in resource:action format.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| resource | VARCHAR(100) | NOT NULL | Resource name (user, fii, transaction, etc.) |
| action | VARCHAR(50) | NOT NULL | Action (create, read, update, delete, list, export) |
| description | VARCHAR(255) | NULL | Permission description |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Unique Constraints:**
- `uq_permission_resource_action` - (resource, action) must be unique

**Indexes:**
- `idx_permission_resource` - Partial index on resource (WHERE rm_timestamp IS NULL)
- `idx_permission_action` - Partial index on action (WHERE rm_timestamp IS NULL)

**Relationships:**
- One-to-many → role_permission

**Permission Format:**
- Format: `{resource}:{action}`
- Examples: `user:create`, `transaction:read`, `portfolio:export`

---

#### 4. user_role
Many-to-many junction table: users ↔ roles.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| user_pk | BIGINT | NOT NULL, FK → user.pk | User reference |
| role_pk | BIGINT | NOT NULL, FK → role.pk | Role reference |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Unique Constraints:**
- `uq_user_role_user_role` - (user_pk, role_pk) must be unique

**Indexes:**
- `idx_user_role_user_pk` - Partial index on user_pk (WHERE rm_timestamp IS NULL)
- `idx_user_role_role_pk` - Partial index on role_pk (WHERE rm_timestamp IS NULL)

**Foreign Key Behavior:**
- user_pk: ON DELETE CASCADE
- role_pk: ON DELETE CASCADE

---

#### 5. role_permission
Many-to-many junction table: roles ↔ permissions.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| role_pk | BIGINT | NOT NULL, FK → role.pk | Role reference |
| permission_pk | BIGINT | NOT NULL, FK → permission.pk | Permission reference |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Unique Constraints:**
- `uq_role_permission_role_permission` - (role_pk, permission_pk) must be unique

**Indexes:**
- `idx_role_permission_role_pk` - Partial index on role_pk (WHERE rm_timestamp IS NULL)
- `idx_role_permission_permission_pk` - Partial index on permission_pk (WHERE rm_timestamp IS NULL)

**Foreign Key Behavior:**
- role_pk: ON DELETE CASCADE
- permission_pk: ON DELETE CASCADE

---

### Core Financial Data (4 tables)

#### 6. fii
FII (Fundos Imobiliários) master catalog.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| ticker | VARCHAR(20) | NOT NULL, UNIQUE | FII ticker symbol (e.g., MXRF11) |
| name | VARCHAR(255) | NOT NULL | FII full name |
| cnpj | VARCHAR(18) | NULL | Brazilian tax ID |
| sector | VARCHAR(100) | NULL | FII sector (commercial, residential, logistics, etc.) |
| segment | VARCHAR(100) | NULL | FII segment |
| current_price | NUMERIC(10,2) | NULL | Current market price per unit |
| price_updated_at | TIMESTAMP | NULL | When price was last updated |
| description | TEXT | NULL | FII description |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | FII is actively traded |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Indexes:**
- `idx_fii_ticker` - Partial index on ticker (WHERE rm_timestamp IS NULL)
- `idx_fii_sector` - Partial index on sector (WHERE rm_timestamp IS NULL)
- `idx_fii_is_active` - Partial index on is_active (WHERE rm_timestamp IS NULL)

**Relationships:**
- One-to-many → fii_transaction
- One-to-many → dividend
- One-to-many → fii_holding

**Notes:**
- Ticker is the primary identifier for FIIs in Brazil
- Prices can be updated via web scraping (separate agent)

---

#### 7. fii_transaction
Purchase and sale transactions with cost basis tracking.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| user_pk | BIGINT | NOT NULL, FK → user.pk | Owner user |
| fii_pk | BIGINT | NOT NULL, FK → fii.pk | FII reference |
| transaction_type | VARCHAR(10) | NOT NULL, CHECK IN ('buy', 'sell') | Transaction type |
| transaction_date | DATE | NOT NULL | Date of transaction |
| quantity | INTEGER | NOT NULL, CHECK > 0 | Number of units |
| price_per_unit | NUMERIC(10,2) | NOT NULL, CHECK > 0 | Price per unit in BRL |
| total_amount | NUMERIC(12,2) | NOT NULL, CHECK > 0 | Total transaction amount |
| fees | NUMERIC(10,2) | NOT NULL, DEFAULT 0.00 | Brokerage fees |
| taxes | NUMERIC(10,2) | NOT NULL, DEFAULT 0.00 | Transaction taxes |
| cost_basis | NUMERIC(12,2) | NULL | FIFO cost basis for sales (tax reporting) |
| notes | TEXT | NULL | Additional notes |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Indexes:**
- `idx_fii_transaction_user_pk` - Partial index on user_pk (WHERE rm_timestamp IS NULL)
- `idx_fii_transaction_fii_pk` - Partial index on fii_pk (WHERE rm_timestamp IS NULL)
- `idx_fii_transaction_date` - Partial index on transaction_date (WHERE rm_timestamp IS NULL)
- `idx_fii_transaction_type` - Partial index on transaction_type (WHERE rm_timestamp IS NULL)
- `idx_fii_transaction_user_fii` - Composite index on (user_pk, fii_pk, transaction_date) (WHERE rm_timestamp IS NULL)

**Foreign Key Behavior:**
- user_pk: ON DELETE CASCADE
- fii_pk: ON DELETE RESTRICT (cannot delete FII with transactions)

**RLS:** Enabled - users can only access their own transactions

**Tax Reporting:**
- `cost_basis` field stores FIFO-calculated cost basis for sale transactions
- Used for Brazilian IRPF tax calculation
- Capital gain/loss = (total_amount - fees - taxes) - cost_basis

---

#### 8. dividend
Monthly dividend payment records.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| user_pk | BIGINT | NOT NULL, FK → user.pk | Owner user |
| fii_pk | BIGINT | NOT NULL, FK → fii.pk | FII reference |
| payment_date | DATE | NOT NULL | Date dividend was paid |
| reference_date | DATE | NULL | Reference date (ex-dividend date) |
| amount_per_unit | NUMERIC(10,4) | NOT NULL, CHECK > 0 | Dividend per unit in BRL |
| units_held | INTEGER | NOT NULL, CHECK > 0 | Number of units held |
| total_amount | NUMERIC(12,2) | NOT NULL, CHECK > 0 | Total dividend received |
| tax_withheld | NUMERIC(10,2) | NOT NULL, DEFAULT 0.00 | Tax withheld at source |
| is_verified | BOOLEAN | NOT NULL, DEFAULT false | Dividend verified against statement |
| notes | TEXT | NULL | Additional notes |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Indexes:**
- `idx_dividend_user_pk` - Partial index on user_pk (WHERE rm_timestamp IS NULL)
- `idx_dividend_fii_pk` - Partial index on fii_pk (WHERE rm_timestamp IS NULL)
- `idx_dividend_payment_date` - Partial index on payment_date (WHERE rm_timestamp IS NULL)
- `idx_dividend_user_fii_date` - Composite index on (user_pk, fii_pk, payment_date) (WHERE rm_timestamp IS NULL)

**Foreign Key Behavior:**
- user_pk: ON DELETE CASCADE
- fii_pk: ON DELETE RESTRICT (cannot delete FII with dividends)

**RLS:** Enabled - users can only access their own dividends

**Tax Notes:**
- Brazilian tax law: Monthly dividends up to R$ 200 are tax-exempt for individuals
- Dividends above R$ 200/month are taxable
- `tax_withheld` tracks any IR (income tax) withheld at source

---

#### 9. fii_holding
Cached portfolio positions for performance optimization.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| user_pk | BIGINT | NOT NULL, FK → user.pk | Owner user |
| fii_pk | BIGINT | NOT NULL, FK → fii.pk | FII reference |
| total_quantity | INTEGER | NOT NULL, CHECK >= 0 | Current units held |
| average_price | NUMERIC(10,2) | NOT NULL, CHECK >= 0 | Average purchase price |
| total_invested | NUMERIC(12,2) | NOT NULL, CHECK >= 0 | Total amount invested |
| current_value | NUMERIC(12,2) | NULL | Current market value |
| total_dividends | NUMERIC(12,2) | NOT NULL, DEFAULT 0.00 | Total dividends received |
| last_calculated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When holdings were recalculated |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Unique Constraints:**
- `uq_fii_holding_user_fii` - (user_pk, fii_pk) must be unique

**Indexes:**
- `idx_fii_holding_user_pk` - Partial index on user_pk (WHERE rm_timestamp IS NULL)
- `idx_fii_holding_fii_pk` - Partial index on fii_pk (WHERE rm_timestamp IS NULL)

**Foreign Key Behavior:**
- user_pk: ON DELETE CASCADE
- fii_pk: ON DELETE CASCADE

**RLS:** Enabled - users can only access their own holdings

**Purpose:**
- Caches expensive portfolio calculations
- Recalculated after each transaction or dividend
- Avoids SUM/GROUP BY queries on every portfolio view
- Improves dashboard performance

**Calculation Trigger:**
- After INSERT/UPDATE/DELETE on fii_transaction → recalculate holding
- After INSERT on dividend → update total_dividends

---

### File Import (1 table)

#### 10. import_job
CSV/Excel file import tracking with error details.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| user_pk | BIGINT | NOT NULL, FK → user.pk | Owner user |
| file_name | VARCHAR(255) | NOT NULL | Original file name |
| file_size | BIGINT | NOT NULL | File size in bytes |
| file_type | VARCHAR(50) | NOT NULL | MIME type (text/csv, application/xlsx) |
| import_type | VARCHAR(50) | NOT NULL, CHECK IN ('transaction', 'dividend') | Import type |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending', CHECK IN ('pending', 'processing', 'completed', 'failed') | Job status |
| total_rows | INTEGER | NULL | Total rows in file |
| processed_rows | INTEGER | NOT NULL, DEFAULT 0 | Rows processed |
| successful_rows | INTEGER | NOT NULL, DEFAULT 0 | Rows imported successfully |
| failed_rows | INTEGER | NOT NULL, DEFAULT 0 | Rows that failed |
| error_details | JSONB | NULL | Row-level error details |
| started_at | TIMESTAMP | NULL | Job start time |
| completed_at | TIMESTAMP | NULL | Job completion time |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Indexes:**
- `idx_import_job_user_pk` - Partial index on user_pk (WHERE rm_timestamp IS NULL)
- `idx_import_job_status` - Partial index on status (WHERE rm_timestamp IS NULL)
- `idx_import_job_created_at` - Partial index on created_at (WHERE rm_timestamp IS NULL)

**Foreign Key Behavior:**
- user_pk: ON DELETE CASCADE

**RLS:** Enabled - users can only access their own import jobs

**Error Details JSONB Format:**
```json
{
  "errors": [
    {
      "row": 5,
      "field": "ticker",
      "message": "Invalid ticker symbol",
      "value": "INVALID"
    },
    {
      "row": 12,
      "field": "date",
      "message": "Invalid date format",
      "value": "2024-13-45"
    }
  ]
}
```

**Processing Flow:**
1. User uploads file → create import_job (status: pending)
2. Celery task picks up job → update status to processing
3. Parse file row by row, tracking errors in error_details
4. Update processed_rows, successful_rows, failed_rows
5. Set status to completed or failed
6. Set completed_at timestamp

---

### Authentication & Audit (2 tables)

#### 11. refresh_token
JWT refresh token storage with device tracking.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| user_pk | BIGINT | NOT NULL, FK → user.pk | Owner user |
| token | VARCHAR(500) | NOT NULL, UNIQUE | Refresh token string |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time |
| is_revoked | BOOLEAN | NOT NULL, DEFAULT false | Token revoked |
| device_info | VARCHAR(255) | NULL | Device/browser info |
| ip_address | VARCHAR(45) | NULL | IP address (supports IPv6) |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Indexes:**
- `idx_refresh_token_user_pk` - Partial index on user_pk (WHERE rm_timestamp IS NULL)
- `idx_refresh_token_token` - Partial index on token (WHERE rm_timestamp IS NULL)
- `idx_refresh_token_expires_at` - Partial index on expires_at (WHERE rm_timestamp IS NULL)

**Foreign Key Behavior:**
- user_pk: ON DELETE CASCADE

**RLS:** Enabled - users can only access their own tokens

**JWT Strategy:**
- Access tokens: Short-lived (15-30 minutes), stored in memory
- Refresh tokens: Long-lived (7 days), stored in database
- Refresh token rotation: New refresh token issued on each access token refresh
- Old refresh token marked as revoked

**Cleanup:**
- Periodically delete expired tokens: `DELETE FROM refresh_token WHERE expires_at < NOW() AND rm_timestamp IS NULL`
- Consider retention policy for revoked tokens

---

#### 12. log
System-wide logging and audit trail.

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| pk | BIGINT | PK, AUTO | Primary key |
| user_pk | BIGINT | NULL, FK → user.pk | User who triggered action (NULL for system) |
| level | VARCHAR(20) | NOT NULL, CHECK IN ('debug', 'info', 'warning', 'error', 'critical') | Log level |
| action | VARCHAR(100) | NOT NULL | Action performed (login, create_transaction, etc.) |
| resource_type | VARCHAR(50) | NULL | Resource type (user, fii, transaction, etc.) |
| resource_pk | BIGINT | NULL | Resource primary key |
| message | TEXT | NOT NULL | Log message |
| details | JSONB | NULL | Additional structured data |
| ip_address | VARCHAR(45) | NULL | IP address (supports IPv6) |
| user_agent | VARCHAR(255) | NULL | Browser/client user agent |
| rm_timestamp | BIGINT | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| created_by_pk | BIGINT | NULL, FK → user.pk | Creator user |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |
| updated_by_pk | BIGINT | NULL, FK → user.pk | Last updater user |

**Indexes:**
- `idx_log_user_pk` - Partial index on user_pk (WHERE rm_timestamp IS NULL)
- `idx_log_level` - Partial index on level (WHERE rm_timestamp IS NULL)
- `idx_log_action` - Partial index on action (WHERE rm_timestamp IS NULL)
- `idx_log_created_at` - Partial index on created_at (WHERE rm_timestamp IS NULL)
- `idx_log_resource` - Composite index on (resource_type, resource_pk) (WHERE rm_timestamp IS NULL)

**Foreign Key Behavior:**
- user_pk: ON DELETE SET NULL (preserve logs even if user deleted)

**RLS:** Enabled (read-only) - users can SELECT their own logs, superusers can SELECT all

**Log Levels:**
- `debug` - Detailed debugging information
- `info` - General informational messages
- `warning` - Warning messages (recoverable issues)
- `error` - Error messages (operation failed)
- `critical` - Critical errors (system failure)

**Common Actions:**
- `login`, `logout`, `login_failed`
- `create_transaction`, `update_transaction`, `delete_transaction`
- `create_dividend`, `update_dividend`
- `import_started`, `import_completed`, `import_failed`
- `price_updated`, `holdings_recalculated`

**Details JSONB Examples:**
```json
{
  "before": {"quantity": 100},
  "after": {"quantity": 150},
  "change": "+50 units"
}
```

**Retention Policy:**
- Consider archiving logs older than 1 year
- Critical/error logs may need longer retention for compliance

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       RBAC SUBSYSTEM                         │
└─────────────────────────────────────────────────────────────┘

    user ←→ user_role ←→ role ←→ role_permission ←→ permission

┌─────────────────────────────────────────────────────────────┐
│                   CORE FINANCIAL DATA                        │
└─────────────────────────────────────────────────────────────┘

    user ──┬──< fii_transaction >── fii
           ├──< dividend >────────── fii
           └──< fii_holding >─────── fii

┌─────────────────────────────────────────────────────────────┐
│                    FILE IMPORT & AUDIT                       │
└─────────────────────────────────────────────────────────────┘

    user ──┬──< import_job
           ├──< refresh_token
           └──< log
```

## Data Types Reference

| Type | Usage | Examples |
|------|-------|----------|
| BIGINT | Primary keys, foreign keys, large integers | pk, user_pk, file_size |
| VARCHAR(n) | Short text with max length | email, ticker, status |
| TEXT | Long text without limit | notes, description, message |
| NUMERIC(p,s) | Financial precision | NUMERIC(10,2) for prices, NUMERIC(12,2) for totals |
| INTEGER | Quantities, counts | quantity, processed_rows |
| BOOLEAN | True/false flags | is_active, is_verified |
| DATE | Date without time | transaction_date, payment_date |
| TIMESTAMP | Date and time (UTC) | created_at, updated_at |
| JSONB | Structured JSON data | error_details, details |

## Query Examples

### Get User Permissions
```sql
SELECT DISTINCT p.resource, p.action
FROM permission p
JOIN role_permission rp ON p.pk = rp.permission_pk
JOIN user_role ur ON rp.role_pk = ur.role_pk
WHERE ur.user_pk = :user_pk
  AND p.rm_timestamp IS NULL
  AND rp.rm_timestamp IS NULL
  AND ur.rm_timestamp IS NULL;
```

### Calculate Portfolio Summary
```sql
SELECT
    COUNT(DISTINCT fii_pk) as total_fiis,
    SUM(total_quantity) as total_units,
    SUM(total_invested) as total_invested,
    SUM(current_value) as current_value,
    SUM(total_dividends) as total_dividends
FROM fii_holding
WHERE user_pk = :user_pk
  AND rm_timestamp IS NULL
  AND total_quantity > 0;
```

### Get Monthly Dividend Income
```sql
SELECT
    DATE_TRUNC('month', payment_date) as month,
    SUM(total_amount) as total_dividends,
    COUNT(*) as dividend_count
FROM dividend
WHERE user_pk = :user_pk
  AND rm_timestamp IS NULL
  AND payment_date >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY DATE_TRUNC('month', payment_date)
ORDER BY month DESC;
```

### Transaction History with FII Details
```sql
SELECT
    t.pk,
    t.transaction_date,
    t.transaction_type,
    f.ticker,
    f.name,
    t.quantity,
    t.price_per_unit,
    t.total_amount,
    t.fees,
    t.taxes
FROM fii_transaction t
JOIN fii f ON t.fii_pk = f.pk
WHERE t.user_pk = :user_pk
  AND t.rm_timestamp IS NULL
  AND f.rm_timestamp IS NULL
ORDER BY t.transaction_date DESC, t.created_at DESC;
```

## See Also

- [Migration Setup Guide](migration-setup.md)
- [API Endpoints Documentation](../api/endpoints.md)
- [Architecture Overview](../architecture/overview.md)
