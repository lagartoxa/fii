# Architecture Overview

## System Architecture

The FII Portfolio Manager is built using a modern full-stack architecture with clear separation of concerns.

## High-Level Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │────────>│   FastAPI    │────────>│ PostgreSQL  │
│  Frontend   │  HTTP   │   Backend    │   SQL   │  Database   │
│   (Vite)    │<────────│   (Python)   │<────────│             │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               │
                               v
                        ┌──────────────┐
                        │    Celery    │
                        │  (Background │
                        │     Jobs)    │
                        └──────────────┘
                               │
                               v
                        ┌──────────────┐
                        │    Redis     │
                        │ (Task Queue) │
                        └──────────────┘
```

## Architecture Pattern

**Layered Architecture with Clean Architecture Principles**

### Backend Layers

1. **API Layer** (`app/api/`)
   - FastAPI routers and endpoints
   - HTTP request/response handling
   - Input validation (Pydantic schemas)
   - Authentication and authorization

2. **Service Layer** (`app/services/`)
   - Business logic implementation
   - Transaction orchestration
   - Complex calculations (portfolio analytics)
   - Cross-entity operations

3. **Repository Layer** (`app/repositories/`)
   - Data access abstraction
   - Database query construction
   - CRUD operations
   - Query optimization

4. **Model Layer** (`app/models/`)
   - SQLAlchemy ORM models
   - Database schema definition
   - Relationships and constraints

### Frontend Structure

**Feature-Based Organization**

```
src/
├── components/      # Reusable UI components
│   ├── common/     # Generic components (Button, Input, etc.)
│   ├── layout/     # Layout components (Header, Sidebar)
│   └── [feature]/  # Feature-specific components
├── pages/          # Route-level page components
├── services/       # API client services
├── hooks/          # Custom React hooks
├── context/        # React Context providers
├── types/          # TypeScript type definitions
└── utils/          # Utility functions
```

## Technology Stack

### Backend

- **Framework**: FastAPI 0.115
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic 1.14
- **Database**: PostgreSQL 16
- **Task Queue**: Celery 5.4
- **Cache/Broker**: Redis 7
- **Auth**: JWT (python-jose)
- **Password**: bcrypt (passlib)

### Frontend

- **Framework**: React 18
- **Language**: TypeScript 5.6
- **Build Tool**: Vite 6
- **Routing**: React Router 7
- **State Management**: React Query 5
- **HTTP Client**: Axios 1.7
- **Charts**: Recharts 2
- **Date Handling**: date-fns 4

### Infrastructure

- **Services**: Docker Compose (PostgreSQL, Redis)
- **Development**: Local (no Docker for app)

## Core Design Decisions

### 1. Authentication: JWT with Refresh Tokens

**Why:**
- Stateless authentication (scalable)
- Short-lived access tokens (security)
- Refresh tokens for UX (no frequent re-login)
- Industry standard for SPAs

**Implementation:**
- Access tokens: 15-30 minutes
- Refresh tokens: 7 days (stored in DB)
- Tokens transmitted via HTTP Bearer header

### 2. Soft Deletes for Financial Data

**Why:**
- Audit compliance
- Data recovery capability
- Historical accuracy
- Regulatory requirements

**Implementation:**
- `is_deleted` flag on transactions and dividends
- Queries must filter deleted records
- Delete operations set flag instead of removing

### 3. Background Jobs with Celery

**Why:**
- Non-blocking file imports
- Long-running report generation
- Progress tracking
- Retry capabilities

**Implementation:**
- Redis as message broker
- Async task processing
- Status updates in database

### 4. Repository Pattern

**Why:**
- Abstraction over data access
- Easier to test (mock repositories)
- Consistent query patterns
- Easier to swap database later

**Implementation:**
- Base repository with common CRUD
- Specialized repositories per entity
- Services use repositories, not models directly

## Database Design

### Key Principles

1. **Normalization**: 3NF for data integrity
2. **Indexes**: On frequently queried fields (user_id, ticker, dates)
3. **Constraints**: CHECK constraints for business rules
4. **Relationships**: Foreign keys with proper cascading
5. **Audit Fields**: created_at, updated_at, created_by on all tables

### Core Entities

- **Users**: Authentication and user management
- **FIIs**: FII catalog (tickers, names, sectors)
- **Transactions**: Buy/sell operations
- **Dividends**: Monthly dividend payments
- **Portfolio Snapshots**: Cached positions (optimization)
- **Import Jobs**: File import tracking
- **Refresh Tokens**: JWT refresh token storage

## API Design

### RESTful Principles

- Resource-based URLs: `/api/v1/transactions`
- HTTP methods: GET (read), POST (create), PATCH (update), DELETE (delete)
- Status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found)
- JSON request/response bodies

### Versioning

- URL-based: `/api/v1/`, `/api/v2/`
- Clear deprecation policy
- Backward compatibility within major version

### Error Responses

Consistent error format:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid data",
    "details": {...}
  }
}
```

## Security Considerations

1. **Authentication**: JWT tokens with secure secret keys
2. **Authorization**: User-based access control
3. **Password Security**: bcrypt hashing (12 rounds)
4. **Input Validation**: Pydantic schemas on all endpoints
5. **SQL Injection**: Prevented by SQLAlchemy ORM
6. **CORS**: Configured for frontend origin only
7. **Rate Limiting**: Planned for production
8. **HTTPS**: Required in production

## Performance Optimizations

1. **Database**:
   - Indexes on frequently queried fields
   - Connection pooling
   - Query optimization (avoid N+1)
   - Portfolio snapshots for expensive calculations

2. **Backend**:
   - Async endpoints where beneficial
   - Pagination on list endpoints
   - Response caching headers

3. **Frontend**:
   - Code splitting (route-based)
   - React Query caching
   - Lazy loading components
   - Optimized bundle size

## Scalability Considerations

1. **Horizontal Scaling**: Stateless API (can run multiple instances)
2. **Database**: Connection pooling, read replicas (future)
3. **Caching**: Redis for frequent queries
4. **Background Jobs**: Celery workers can scale independently
5. **CDN**: For frontend static assets (production)

## Development Workflow

1. **Branch Strategy**: Feature branches from master
2. **Code Review**: Pull requests required
3. **Testing**: Unit and integration tests
4. **Migrations**: Alembic for database changes
5. **Deployment**: Automated CI/CD (future)

## Future Enhancements

- [ ] Tax calculation engine
- [ ] Real-time market data integration
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Mobile app (React Native)
- [ ] Multi-currency support

## Related Documentation

- [API Endpoints](../api/endpoints.md)
- [Database Schema](../database/schema.md)
- [Development Setup](../development/setup.md)
