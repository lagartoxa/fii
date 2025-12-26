# Testing Guide for FII Portfolio Management System

## Test Suite Overview

The project includes **84 comprehensive API tests** covering all endpoints:

- **Authentication API**: 17 tests (register, login, refresh, logout)
- **FII API**: 23 tests (CRUD operations with filtering and pagination)
- **Transaction API**: 23 tests (CRUD with ownership enforcement and filtering)
- **Dividend API**: 21 tests (CRUD with ownership enforcement and filtering)

## Prerequisites

### 1. Install Python Virtual Environment Support

The system requires `python3-venv` package:

```bash
sudo apt install python3.10-venv
```

### 2. Create Virtual Environment

```bash
cd /home/parallels/projects/fii/backend
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 4. Install Dependencies

Install production dependencies:
```bash
pip install -r requirements.txt
```

Install development/testing dependencies:
```bash
pip install -r requirements-dev.txt
```

Or install manually if requirements-dev.txt needs updating:
```bash
pip install pytest==8.3.4 pytest-asyncio==0.24.0 pytest-cov==6.0.0 httpx==0.28.1 faker==33.1.0
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with short traceback on errors
pytest --tb=short

# Run specific test file
pytest tests/api/test_auth.py
pytest tests/api/test_fiis.py
pytest tests/api/test_transactions.py
pytest tests/api/test_dividends.py

# Run specific test class
pytest tests/api/test_auth.py::TestRegisterEndpoint

# Run specific test function
pytest tests/api/test_auth.py::TestRegisterEndpoint::test_register_success
```

### Coverage Reporting

```bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open HTML report (generates in htmlcov/ directory)
xdg-open htmlcov/index.html
```

### Filtering Tests

```bash
# Run only API tests
pytest tests/api/

# Run only authentication tests
pytest tests/api/test_auth.py

# Run tests matching a pattern
pytest -k "test_create"
pytest -k "test_delete"
pytest -k "authentication"
```

### Advanced Options

```bash
# Stop on first failure
pytest -x

# Run last failed tests only
pytest --lf

# Show local variables in tracebacks
pytest -l

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Quiet mode (less verbose)
pytest -q

# Very verbose (show all test output)
pytest -vv
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Global fixtures (database, clients, test data)
├── utils/
│   ├── __init__.py
│   └── test_helpers.py            # Helper functions for creating test data
├── api/                           # API endpoint tests
│   ├── __init__.py
│   ├── test_auth.py               # Authentication endpoints (17 tests)
│   ├── test_fiis.py               # FII CRUD endpoints (23 tests)
│   ├── test_transactions.py       # Transaction CRUD endpoints (23 tests)
│   └── test_dividends.py          # Dividend CRUD endpoints (21 tests)
└── services/                      # Service layer tests (future)
    └── __init__.py
```

## Test Database

Tests use an **SQLite in-memory database** for:
- Fast execution
- Complete isolation between tests
- No need for separate test database setup
- Automatic cleanup

Each test gets a fresh database session that is automatically rolled back after the test completes.

## Test Fixtures

### Database Fixtures
- `test_engine` - Session-scoped SQLite engine
- `db_session` - Function-scoped database session (fresh for each test)

### Client Fixtures
- `client` - Unauthenticated FastAPI test client
- `authenticated_client` - Client with JWT authentication header

### User Fixtures
- `test_user` - Standard active user
- `inactive_test_user` - Inactive user (for testing login restrictions)
- `another_test_user` - Second user (for testing ownership enforcement)

### FII Fixtures
- `test_fii` - Single FII
- `another_test_fii` - Second FII
- `deleted_test_fii` - Soft-deleted FII
- `multiple_test_fiis` - 10 FIIs for pagination testing
- `fiis_multiple_sectors` - FIIs grouped by sector for filtering tests

### Transaction Fixtures
- `test_transaction` - Single buy transaction
- `other_user_transaction` - Transaction owned by another user
- `buy_and_sell_transactions` - Mixed transaction types
- `transactions_multiple_fiis` - Transactions across multiple FIIs
- `transactions_various_dates` - Transactions spanning date range
- `many_transactions` - 15 transactions for pagination

### Dividend Fixtures
- `test_dividend` - Single dividend payment
- `other_user_dividend` - Dividend owned by another user
- `dividends_multiple_fiis` - Dividends across multiple FIIs
- `dividends_various_dates` - Dividends spanning date range
- `many_dividends` - 12 monthly dividends for pagination

### Token Fixtures
- `test_user_token` - JWT access token for test user
- `test_user_refresh_token` - Refresh token for test user

## Test Coverage Areas

### 1. Authentication & Authorization
- ✅ User registration with validation
- ✅ Login with email or username
- ✅ Token refresh and rotation
- ✅ Logout and token revocation
- ✅ Inactive user handling
- ✅ Invalid credentials

### 2. CRUD Operations
- ✅ Create (POST) with validation
- ✅ Read single (GET /{pk})
- ✅ Read multiple (GET /) with pagination
- ✅ Update (PATCH) with partial updates
- ✅ Delete (DELETE) with soft delete

### 3. Data Filtering
- ✅ Pagination (skip, limit)
- ✅ Filter by FII
- ✅ Filter by transaction type (buy/sell)
- ✅ Filter by date range
- ✅ Filter by sector (FIIs)

### 4. Data Integrity
- ✅ Soft delete enforcement (rm_timestamp)
- ✅ Audit trail verification (created_by_pk, updated_by_pk)
- ✅ Ownership enforcement (users can only access their own data)
- ✅ Foreign key validation (FII must exist)
- ✅ Duplicate prevention (unique constraints)

### 5. Error Scenarios
- ✅ 401 Unauthorized (no authentication)
- ✅ 404 Not Found (non-existent resource)
- ✅ 400 Bad Request (duplicate data)
- ✅ 422 Validation Error (invalid input)

## Writing New Tests

### Basic Test Template

```python
def test_example(authenticated_client, test_user, db_session):
    """Test description"""
    # Arrange - Set up test data
    data = {
        "field": "value"
    }

    # Act - Execute the action
    response = authenticated_client.post("/api/v1/endpoint/", json=data)

    # Assert - Verify the result
    assert response.status_code == 201
    assert response.json()["field"] == "value"

    # Verify database state if needed
    obj = db_session.query(Model).filter(...).first()
    assert obj is not None
```

### Using Test Helpers

```python
from tests.utils.test_helpers import (
    create_test_user,
    create_test_fii,
    assert_audit_fields,
    assert_not_soft_deleted,
)

def test_with_helpers(db_session):
    # Create test data
    user = create_test_user(db_session, email="custom@example.com")
    fii = create_test_fii(db_session, user_pk=user.pk, tag="XPLG11")

    # Assert audit trail
    assert_audit_fields(fii, created_by_pk=user.pk)
    assert_not_soft_deleted(fii)
```

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd backend
    source venv/bin/activate
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

## Troubleshooting

### Import Errors
If you get import errors, ensure you're in the backend directory and the virtual environment is activated:
```bash
cd /home/parallels/projects/fii/backend
source venv/bin/activate
```

### Database Errors
If you get database errors, check that:
1. All database models are imported in `app/db/base.py`
2. The test database is being created correctly in `conftest.py`

### Fixture Not Found
If pytest can't find a fixture:
1. Check that `conftest.py` is in the tests directory
2. Ensure the fixture is defined with `@pytest.fixture`
3. Check fixture scope (session, module, function)

### SQLAlchemy Errors
For "Table not found" errors:
1. Ensure `Base.metadata.create_all()` is called in `test_engine` fixture
2. Check that all models inherit from the correct `Base`

## Test Metrics

- **Total Tests**: 84
- **Test Files**: 4
- **Test Lines of Code**: ~2,726
- **Coverage Goal**: 90%+
- **Expected Runtime**: < 10 seconds (in-memory SQLite)

## Next Steps

1. Install python3-venv: `sudo apt install python3.10-venv`
2. Create virtual environment: `python3 -m venv venv`
3. Activate environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements-dev.txt`
5. Run tests: `pytest -v`
6. Generate coverage report: `pytest --cov=app --cov-report=html`
7. Review results and iterate

---

**Note**: All test files have been validated for syntax correctness and follow best practices for FastAPI testing with pytest.
