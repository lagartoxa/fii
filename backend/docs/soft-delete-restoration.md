# Soft Delete Restoration Pattern

## Overview

This application uses a soft delete pattern where records are marked as deleted (via `rm_timestamp`) rather than being permanently removed from the database. This allows for data recovery and maintains referential integrity.

However, this creates a challenge: **what happens when a user tries to recreate data that was previously deleted?**

## The Problem

Consider this scenario:

1. User creates a FII with tag "HGLG11"
2. User deletes the FII (soft delete - sets `rm_timestamp`)
3. User tries to create a FII with tag "HGLG11" again
4. ❌ **ERROR**: Unique constraint violation or "tag already exists"

This is frustrating UX - from the user's perspective, the FII is gone, so they should be able to recreate it.

## The Solution

When creating a record that has unique constraints, follow this pattern:

1. Check if an **active** record with that unique value exists
   - If yes: Return error (it truly already exists)
2. Check if a **soft-deleted** record with that unique value exists
   - If yes: **Restore it** and update its data
3. Otherwise: Create a new record

## Implementation

### Base Repository

The `BaseRepository` class provides a generic `restore()` method:

```python
def restore(self, instance: ModelType) -> ModelType:
    """Restore a soft-deleted record by clearing rm_timestamp."""
    instance.rm_timestamp = None

    if hasattr(instance, 'updated_by_pk'):
        instance.updated_by_pk = self.current_user_pk

    self.session.flush()
    self.session.refresh(instance)

    return instance
```

### Repository Layer

Add methods to find records including deleted ones:

```python
class FiiRepository(BaseRepository):
    def get_by_tag(self, tag: str) -> Optional[Fii]:
        """Get active FII by tag (excludes deleted)."""
        return self.session.query(Fii).filter(
            Fii.tag == tag.upper(),
            Fii.rm_timestamp.is_(None)
        ).first()

    def get_by_tag_including_deleted(self, tag: str) -> Optional[Fii]:
        """Get FII by tag including soft-deleted records."""
        return self.session.query(Fii).filter(
            Fii.tag == tag.upper()
        ).first()
```

### API Endpoint

Implement the restore-or-create pattern:

```python
@router.post("/", response_model=FiiResponse, status_code=201)
def create_fii(
    fii_data: FiiCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    with FiiRepository(db, current_user_pk=current_user.pk) as repo:
        # 1. Check if active record exists
        existing_fii = repo.get_by_tag(fii_data.tag)

        if existing_fii:
            raise HTTPException(
                status_code=400,
                detail=f"FII with tag '{fii_data.tag}' already exists"
            )

        # 2. Check if soft-deleted record exists
        deleted_fii = repo.get_by_tag_including_deleted(fii_data.tag)

        if deleted_fii and deleted_fii.rm_timestamp is not None:
            # Restore and update the deleted record
            deleted_fii.name = fii_data.name
            deleted_fii.sector = fii_data.sector
            restored_fii = repo.restore(deleted_fii)
            return restored_fii

        # 3. Create new record
        new_fii = repo.create(fii_data)
        return new_fii
```

## When to Apply This Pattern

### ✅ Apply for Master Data Tables

Tables with **unique business constraints** that users might want to "recreate":

- **FII table** (`tag` is unique)
  - User deletes "HGLG11" and later wants to add it again
  - ✅ Should restore the deleted record

### ❌ Don't Apply for Transactional Data

Tables without unique constraints or where each record is independent:

- **Transactions** (no unique constraint, just time-series data)
  - User deleted a transaction by mistake
  - Creating a "new" transaction with same data is fine (new PK, new timestamps)
  - ❌ No need for restore pattern

- **Dividends** (no unique constraint, just time-series data)
  - Same reasoning as transactions
  - ❌ No need for restore pattern

### Decision Checklist

Ask these questions:

1. **Does the table have a unique business key** (other than PK)?
   - Examples: `tag`, `email`, `username`, `document_number`
   - If NO → Don't need restore pattern

2. **Would a user expect to "recreate" this data after deleting it?**
   - If it's master/reference data → YES, use restore pattern
   - If it's transactional/event data → NO, don't need it

3. **Would creating a "duplicate" be confusing or wasteful?**
   - Master data: YES, wasteful to have multiple soft-deleted "HGLG11" records
   - Transactional: NO, each transaction is independent

## Tables in This Application

| Table | Unique Constraint | Apply Restore Pattern? | Reason |
|-------|-------------------|------------------------|--------|
| `fii` | `tag` | ✅ YES | Master data - users expect to recreate FIIs |
| `fii_transaction` | None | ❌ NO | Transactional data - each record independent |
| `dividend` | None | ❌ NO | Transactional data - each record independent |
| `user` | `email`, `username` | ✅ YES | Master data - usernames/emails should be reusable |
| `fii_holding` | Composite? | 🤔 MAYBE | Depends on business rules |

## Testing the Pattern

### Test Case 1: Create, Delete, Recreate
```python
# 1. Create FII
POST /api/v1/fiis {"tag": "HGLG11", "name": "Test"}
# Response: 201 Created, pk=1

# 2. Delete FII
DELETE /api/v1/fiis/1
# Response: 204 No Content

# 3. Recreate FII with same tag
POST /api/v1/fiis {"tag": "HGLG11", "name": "Test Updated"}
# Expected: 201 Created, pk=1 (restored with updated data)
# ❌ Without pattern: 400 "Tag already exists"
```

### Test Case 2: Active Record Exists
```python
# 1. Create FII
POST /api/v1/fiis {"tag": "HGLG11", "name": "Test"}
# Response: 201 Created, pk=1

# 2. Try to create duplicate (WITHOUT deleting first)
POST /api/v1/fiis {"tag": "HGLG11", "name": "Duplicate"}
# Expected: 400 "FII with tag 'HGLG11' already exists"
# ✅ Should always reject active duplicates
```

## Utility Helper (Optional)

For consistency, you can use the `create_or_restore()` helper from `app/api/utils.py`:

```python
from app.api.utils import create_or_restore

@router.post("/")
def create_fii(fii_data: FiiCreate, ...):
    with FiiRepository(db, current_user_pk=user.pk) as repo:
        # Check if active exists
        if repo.get_by_tag(fii_data.tag):
            raise HTTPException(400, "Already exists")

        # Create or restore
        return create_or_restore(
            repository=repo,
            create_data=fii_data,
            find_deleted_fn=lambda: repo.get_by_tag_including_deleted(fii_data.tag),
            update_deleted_fn=lambda fii, data: setattr(fii, 'name', data.name) or setattr(fii, 'sector', data.sector)
        )
```

## Benefits

1. **Better UX**: Users can recreate deleted data without confusion
2. **Data Integrity**: Maintains referential integrity (FK references preserved)
3. **Audit Trail**: Preserves original `created_at`, `created_by_pk`
4. **Efficiency**: Reuses existing records instead of creating orphaned deleted records

## Caveats

1. **Business Logic**: Some systems may want to prevent recreation for compliance reasons
2. **Audit Trail**: The restored record shows original creation date, not recreation date
3. **Relationships**: Restoring a parent may restore cascade-deleted children (check cascade rules)
