# Repository Pattern Implementation

## Overview

All database operations have been refactored to use the **Repository Pattern** with context managers. This ensures:

1. **No direct database queries in API endpoints** - All queries go through repositories
2. **Automatic transaction management** - Context managers handle commit/rollback
3. **Audit trail support** - Repositories automatically set created_by_pk and updated_by_pk
4. **Soft delete enforcement** - All queries automatically filter out soft-deleted records
5. **Separation of concerns** - Business logic separated from data access logic

## Architecture

### Base Repository

**Location:** `/home/parallels/projects/fii/backend/app/db/repositories/base.py`

The `BaseRepository` class provides:

- **Context Manager Protocol** (`__enter__` and `__exit__`)
- **Generic CRUD Methods:**
  - `create(schema)` - Create record from Pydantic schema
  - `update(pk, schema)` - Update record with Pydantic schema (PATCH semantics)
  - `delete(pk)` - Soft delete (sets rm_timestamp)
  - `get_by_pk(pk, include_deleted)` - Get single record
  - `get_all(skip, limit, include_deleted)` - Get all records with pagination
- **Automatic Audit Trail** - Sets created_by_pk and updated_by_pk from current_user_pk
- **Automatic Soft Delete Filtering** - Excludes rm_timestamp IS NOT NULL by default

### Repository Hierarchy

```
BaseRepository (Generic)
├── UserRepository
├── FiiRepository
├── FiiTransactionRepository
├── DividendRepository
└── RefreshTokenRepository
```

## Usage Pattern

### Basic Usage

```python
# Read operation (no user context needed)
with FiiRepository(db) as fii_repo:
    fii = fii_repo.get_by_pk(1)

# Write operation (with user context for audit trail)
with FiiRepository(db, current_user_pk=user.pk) as fii_repo:
    new_fii = fii_repo.create(fii_data)
```

### In API Endpoints

```python
@router.post("/", response_model=FiiResponse, status_code=status.HTTP_201_CREATED)
def create_fii(
    fii_data: FiiCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    with FiiRepository(db, current_user_pk=current_user.pk) as fii_repo:
        # Check if tag already exists
        existing_fii = fii_repo.get_by_tag(fii_data.tag)

        if existing_fii:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"FII with tag '{fii_data.tag}' already exists"
            )

        # Create new FII - audit fields set automatically
        new_fii = fii_repo.create(fii_data)

        return new_fii
```

## Repositories

### 1. UserRepository

**Location:** `app/db/repositories/user_repository.py`

**Custom Methods:**
- `get_by_email(email)` - Find user by email
- `get_by_username(username)` - Find user by username
- `get_by_username_or_email(identifier)` - Find user by username OR email

**Used in:** Authentication endpoints (register, login, refresh)

### 2. FiiRepository

**Location:** `app/db/repositories/fii_repository.py`

**Custom Methods:**
- `get_by_tag(tag)` - Find FII by tag (ticker)
- `get_by_sector(sector, skip, limit)` - Get FIIs by sector
- `get_all(skip, limit, sector, include_deleted)` - Overridden to support sector filtering

**Used in:** FII CRUD endpoints, transaction/dividend creation (FII validation)

### 3. FiiTransactionRepository

**Location:** `app/db/repositories/fii_transaction_repository.py`

**Custom Methods:**
- `get_by_user(user_pk, skip, limit, fii_pk, transaction_type, start_date, end_date)` - Get user's transactions with filters
- `get_by_user_and_pk(user_pk, pk)` - Get specific transaction for a user (enforces ownership)

**Used in:** Transaction CRUD endpoints

### 4. DividendRepository

**Location:** `app/db/repositories/dividend_repository.py`

**Custom Methods:**
- `get_by_user(user_pk, skip, limit, fii_pk, start_date, end_date)` - Get user's dividends with filters
- `get_by_user_and_pk(user_pk, pk)` - Get specific dividend for a user (enforces ownership)

**Used in:** Dividend CRUD endpoints

### 5. RefreshTokenRepository

**Location:** `app/db/repositories/refresh_token_repository.py`

**Custom Methods:**
- `get_by_token(token)` - Find refresh token by token string
- `create_token(user_pk, token, device_info)` - Create refresh token

**Used in:** Authentication endpoints (login, refresh, logout)

## Transaction Management

### Automatic Commit/Rollback

The context manager (`__exit__` method) automatically:

1. **Commits** if no exception occurs
2. **Rolls back** if an exception is raised
3. **Does NOT close** the session (FastAPI dependency handles this)

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type is not None:
        # Exception occurred, rollback
        self.session.rollback()
    else:
        # No exception, commit
        self.session.commit()

    return False  # Don't suppress exceptions
```

### Multiple Repositories in One Transaction

When using multiple repositories, they share the same database session, so all operations are part of the same transaction:

```python
# Verify FII exists
with FiiRepository(db) as fii_repo:
    fii = fii_repo.get_by_pk(transaction_data.fii_pk)

    if not fii:
        raise HTTPException(...)

# Create transaction (separate context, same session)
with FiiTransactionRepository(db, current_user_pk=current_user.pk) as transaction_repo:
    new_transaction = transaction_repo.create(transaction_data)

    return new_transaction
```

**Note:** Each `with` block commits independently. If you need multiple operations in a single transaction, use a single repository context or manually manage the transaction.

## Audit Trail

All repositories that accept `current_user_pk` in the constructor will automatically:

1. **On Create:** Set `created_by_pk` and `updated_by_pk` to current_user_pk
2. **On Update:** Set `updated_by_pk` to current_user_pk
3. **On Delete:** Set `updated_by_pk` to current_user_pk (before setting rm_timestamp)

### System Operations

For system-level operations (no user context), omit the `current_user_pk` parameter:

```python
with FiiRepository(db) as fii_repo:  # No current_user_pk
    fii = fii_repo.create(fii_data)  # created_by_pk and updated_by_pk will be None
```

## Soft Delete

All repositories enforce soft delete:

- **Delete operation:** Sets `rm_timestamp` to current Unix epoch timestamp
- **Query operations:** Automatically filter `WHERE rm_timestamp IS NULL`
- **Include deleted:** Use `include_deleted=True` parameter to see deleted records

```python
# Get only active records (default)
fii = fii_repo.get_by_pk(1)  # Returns None if deleted

# Include deleted records
fii = fii_repo.get_by_pk(1, include_deleted=True)  # Returns record even if deleted
```

## Benefits

### 1. Consistency
- All database operations follow the same pattern
- Audit trail is automatically maintained
- Soft delete is enforced everywhere

### 2. Testability
- Repositories can be mocked for unit testing
- Business logic can be tested without database

### 3. Maintainability
- Single place to update query logic
- Easy to add caching, logging, or performance monitoring
- Clear separation of concerns

### 4. Security
- Centralized RLS enforcement (can be added to BaseRepository)
- Consistent permission checking
- No raw SQL in API endpoints

### 5. Type Safety
- Generic types ensure type consistency
- Pydantic schemas validated before database operations
- Clear return types

## Migration from Direct Queries

### Before (Direct Queries)

```python
@router.post("/")
def create_fii(fii_data: FiiCreate, db: Session = Depends(get_db)):
    # Direct database query
    existing_fii = db.query(Fii).filter(
        Fii.tag == fii_data.tag.upper(),
        Fii.rm_timestamp.is_(None)
    ).first()

    # Manual object creation
    new_fii = Fii(
        tag=fii_data.tag.upper(),
        name=fii_data.name,
        sector=fii_data.sector,
        created_by_pk=current_user.pk
    )

    # Manual session management
    db.add(new_fii)
    db.commit()
    db.refresh(new_fii)

    return new_fii
```

### After (Repository Pattern)

```python
@router.post("/")
def create_fii(fii_data: FiiCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    with FiiRepository(db, current_user_pk=current_user.pk) as fii_repo:
        # Use repository method
        existing_fii = fii_repo.get_by_tag(fii_data.tag)

        # Create using repository (audit fields set automatically)
        new_fii = fii_repo.create(fii_data)

        # Commit handled automatically by context manager
        return new_fii
```

## Refactored Files

### Repositories Created
1. ✅ `app/db/repositories/base.py` - Base repository with generic CRUD
2. ✅ `app/db/repositories/user_repository.py` - User operations
3. ✅ `app/db/repositories/fii_repository.py` - FII operations
4. ✅ `app/db/repositories/fii_transaction_repository.py` - Transaction operations
5. ✅ `app/db/repositories/dividend_repository.py` - Dividend operations
6. ✅ `app/db/repositories/refresh_token_repository.py` - Token operations
7. ✅ `app/db/repositories/__init__.py` - Repository exports

### API Endpoints Refactored
1. ✅ `app/api/v1/auth.py` - Authentication endpoints
2. ✅ `app/api/v1/fiis.py` - FII CRUD endpoints
3. ✅ `app/api/v1/transactions.py` - Transaction CRUD endpoints
4. ✅ `app/api/v1/dividends.py` - Dividend CRUD endpoints

## Next Steps

1. **Add RLS Support** - Integrate PostgreSQL Row-Level Security in BaseRepository
2. **Add Caching** - Add optional caching layer in repositories
3. **Add Logging** - Log all database operations
4. **Performance Monitoring** - Track query performance
5. **Unit Tests** - Create comprehensive repository tests
6. **Integration Tests** - Test repository interactions

## Validation Checklist

- ✅ All API endpoints use repositories
- ✅ No direct `db.query()` calls in API endpoints
- ✅ No direct `db.add()` or `db.commit()` in API endpoints (except where manually needed)
- ✅ Context managers used consistently
- ✅ Audit trail automatically maintained
- ✅ Soft delete enforced everywhere
- ✅ Generic CRUD methods in BaseRepository
- ✅ Custom methods in specific repositories
- ✅ Type safety with generics
- ✅ Pydantic schema integration
