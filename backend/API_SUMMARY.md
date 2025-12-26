# FII Portfolio Management API - Implementation Summary

## Overview

Complete CRUD API implementation for the FII Portfolio Management System with authentication, transactions, dividends, and FII catalog management.

## API Structure

Base URL: `/api/v1`

## Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register a new user | No |
| POST | `/login` | Login and get access/refresh tokens | No |
| POST | `/refresh` | Refresh access token | No |
| POST | `/logout` | Logout and revoke refresh token | No |

#### Registration Request
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

#### Login Request
```json
{
  "username": "johndoe",  // or email
  "password": "securepassword123"
}
```

#### Login Response
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### FIIs (`/api/v1/fiis`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create a new FII | Yes |
| GET | `/` | List all FIIs | Yes |
| GET | `/{pk}` | Get FII by primary key | Yes |
| PATCH | `/{pk}` | Update FII | Yes |
| DELETE | `/{pk}` | Soft delete FII | Yes |

#### Query Parameters (List)
- `skip` (default: 0) - Pagination offset
- `limit` (default: 100, max: 1000) - Records per page
- `sector` - Filter by sector

#### Create FII Request
```json
{
  "tag": "HGLG11",
  "name": "CSHG Logística FII",
  "sector": "Logística"
}
```

#### FII Response
```json
{
  "pk": 1,
  "tag": "HGLG11",
  "name": "CSHG Logística FII",
  "sector": "Logística",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

### Transactions (`/api/v1/transactions`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create a new transaction | Yes |
| GET | `/` | List user's transactions | Yes |
| GET | `/{pk}` | Get transaction by primary key | Yes |
| PATCH | `/{pk}` | Update transaction | Yes |
| DELETE | `/{pk}` | Soft delete transaction | Yes |

#### Query Parameters (List)
- `skip` (default: 0) - Pagination offset
- `limit` (default: 100, max: 1000) - Records per page
- `fii_pk` - Filter by FII
- `transaction_type` - Filter by type (buy/sell)
- `start_date` - Filter by start date (YYYY-MM-DD)
- `end_date` - Filter by end date (YYYY-MM-DD)

#### Create Transaction Request
```json
{
  "fii_pk": 1,
  "transaction_type": "buy",
  "transaction_date": "2025-01-15",
  "quantity": 100,
  "price_per_unit": 95.50,
  "total_amount": 9550.00
}
```

#### Transaction Response
```json
{
  "pk": 1,
  "user_pk": 1,
  "fii_pk": 1,
  "transaction_type": "buy",
  "transaction_date": "2025-01-15",
  "quantity": 100,
  "price_per_unit": 95.50,
  "total_amount": 9550.00,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

### Dividends (`/api/v1/dividends`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create a new dividend record | Yes |
| GET | `/` | List user's dividends | Yes |
| GET | `/{pk}` | Get dividend by primary key | Yes |
| PATCH | `/{pk}` | Update dividend | Yes |
| DELETE | `/{pk}` | Soft delete dividend | Yes |

#### Query Parameters (List)
- `skip` (default: 0) - Pagination offset
- `limit` (default: 100, max: 1000) - Records per page
- `fii_pk` - Filter by FII
- `start_date` - Filter by start payment date (YYYY-MM-DD)
- `end_date` - Filter by end payment date (YYYY-MM-DD)

#### Create Dividend Request
```json
{
  "fii_pk": 1,
  "payment_date": "2025-01-15",
  "reference_date": "2024-12-31",
  "amount_per_unit": 0.85,
  "units_held": 100,
  "total_amount": 85.00
}
```

#### Dividend Response
```json
{
  "pk": 1,
  "user_pk": 1,
  "fii_pk": 1,
  "payment_date": "2025-01-15",
  "reference_date": "2024-12-31",
  "amount_per_unit": 0.85,
  "units_held": 100,
  "total_amount": 85.00,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

## Authentication

All endpoints (except `/auth/*`) require JWT authentication.

Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Token Expiration
- Access tokens expire after 30 minutes (configurable)
- Refresh tokens expire after 7 days (configurable)
- Use `/auth/refresh` to get new tokens before expiration

## Security Features

1. **Row-Level Security (RLS)**: Users can only access their own data (transactions, dividends)
2. **Soft Deletes**: All deletions are soft deletes using `rm_timestamp`
3. **Audit Trail**: All records track created_at, created_by_pk, updated_at, updated_by_pk
4. **Password Hashing**: Passwords are hashed using bcrypt
5. **JWT Tokens**: Access and refresh token rotation
6. **Input Validation**: Pydantic schemas validate all input

## Data Validation

### FII
- `tag`: 1-20 characters, automatically converted to uppercase, unique
- `name`: 1-255 characters, required
- `sector`: max 100 characters, optional

### Transaction
- `transaction_type`: must be "buy" or "sell"
- `quantity`: must be > 0
- `price_per_unit`: must be > 0
- `total_amount`: must be > 0

### Dividend
- `amount_per_unit`: must be > 0
- `units_held`: must be > 0
- `total_amount`: must be > 0

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error message here"
}
```

### Common Status Codes
- `200` - Success (GET, PATCH)
- `201` - Created (POST)
- `204` - No Content (DELETE)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Database Models

### User
- email, username, hashed_password, full_name
- is_active, is_superuser
- Soft delete + audit trail

### Fii
- tag, name, sector
- Soft delete + audit trail

### FiiTransaction
- user_pk, fii_pk, transaction_type, transaction_date
- quantity, price_per_unit, total_amount
- Soft delete + audit trail + RLS

### Dividend
- user_pk, fii_pk, payment_date, reference_date
- amount_per_unit, units_held, total_amount
- Soft delete + audit trail + RLS

## API Documentation

When running in development mode:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Files Created

### Pydantic Schemas
- `/app/schemas/fii.py` - FII validation schemas
- `/app/schemas/fii_transaction.py` - Transaction validation schemas
- `/app/schemas/dividend.py` - Dividend validation schemas
- `/app/schemas/user.py` - User validation schemas
- `/app/schemas/auth.py` - Authentication schemas

### API Routers
- `/app/api/v1/auth.py` - Authentication endpoints
- `/app/api/v1/fiis.py` - FII CRUD endpoints
- `/app/api/v1/transactions.py` - Transaction CRUD endpoints
- `/app/api/v1/dividends.py` - Dividend CRUD endpoints
- `/app/api/v1/router.py` - Main API router aggregator

### Configuration
- `/app/main.py` - Updated to include API router

## Next Steps

To complete the backend:

1. **Run the migration**: `alembic upgrade head`
2. **Test the API**: Use the Swagger UI or Postman
3. **Add more endpoints**:
   - Portfolio analytics
   - Import jobs
   - User management
   - Reports
4. **Add unit tests**: Use pytest for testing
5. **Add data seeding**: Create seed script for RBAC and sample FIIs
