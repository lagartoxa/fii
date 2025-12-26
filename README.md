# FII Portfolio Manager

A comprehensive portfolio management system for Brazilian Real Estate Investment Trusts (Fundos Imobiliários - FIIs).

## Features

- **Transaction Tracking**: Record and manage all FII purchase and sale transactions
- **Dividend Management**: Track monthly dividend payments with historical records
- **Portfolio Analytics**: Real-time portfolio positions, performance metrics, and allocation analysis
- **File Import**: Bulk import transactions and dividends from CSV/Excel files
- **Reports**: Generate performance reports and export portfolio data
- **Multi-user Support**: Secure authentication with individual user portfolios

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Reliable relational database
- **SQLAlchemy** - Powerful ORM
- **Alembic** - Database migrations
- **Celery** - Background task processing
- **Redis** - Task queue and caching
- **JWT** - Secure authentication

### Frontend
- **React** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Axios** - HTTP client
- **Recharts** - Data visualization

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 16+ (or Docker)
- Redis 7+ (or Docker)
- Git

**Don't have these installed?** Run our automated installer:
```bash
./install-dependencies.sh
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fii
   ```

2. **Install dependencies** (if not already done)
   ```bash
   ./install-dependencies.sh
   ```

3. **Start services** (PostgreSQL and Redis)
   ```bash
   make start-services
   ```

4. **Setup backend and frontend**
   ```bash
   make setup
   ```

5. **Configure environment**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env with your settings

   # Frontend
   cp frontend/.env.example frontend/.env
   ```

6. **Run database migrations**
   ```bash
   make migrate
   ```

7. **Start development servers**

   **Option 1: Start both together (recommended)**
   ```bash
   make start
   # or
   ./start-dev.sh
   ```

   **Option 2: Start separately**

   Terminal 1 - Backend:
   ```bash
   make start-backend
   ```

   Terminal 2 - Frontend:
   ```bash
   make start-frontend
   ```

8. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

9. **Stop the application**
   ```bash
   make stop
   # or
   ./stop-dev.sh
   ```

## Project Structure

```
fii/
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── api/         # API endpoints and routers
│   │   ├── core/        # Configuration and security
│   │   ├── db/          # Database connection
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── repositories/# Data access layer
│   │   ├── utils/       # Utilities
│   │   └── tasks/       # Celery background tasks
│   ├── alembic/         # Database migrations
│   └── tests/           # Backend tests
│
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── services/    # API client services
│   │   ├── context/     # React Context providers
│   │   ├── routes/      # Routing configuration
│   │   ├── types/       # TypeScript definitions
│   │   └── utils/       # Utility functions
│   └── public/          # Static assets
│
├── docs/                # Documentation
│   ├── api/            # API documentation
│   ├── architecture/   # Architecture documentation
│   ├── database/       # Database schema docs
│   └── development/    # Development guides
│
├── scripts/            # Utility scripts
├── docker-compose.yml  # Docker services
└── Makefile           # Development commands
```

## Available Commands

Run `make help` to see all available commands:

```bash
# Setup
make setup              # Complete project setup
make setup-backend      # Setup backend only
make setup-frontend     # Setup frontend only

# Services
make start-services     # Start PostgreSQL and Redis
make stop-services      # Stop services

# Development
make start              # Start both backend and frontend
make stop               # Stop both backend and frontend
make start-backend      # Start backend server only
make start-frontend     # Start frontend dev server only

# Database
make migrate            # Run migrations
make migration MSG="x"  # Create new migration
make reset-db           # Reset database

# Testing
make test               # Run all tests
make test-backend       # Run backend tests
make test-frontend      # Run frontend tests

# Utilities
make clean              # Clean build artifacts
```

## Development

### Backend Development

The backend follows a layered architecture:

- **API Layer**: FastAPI routers (`app/api/`)
- **Service Layer**: Business logic (`app/services/`)
- **Repository Layer**: Data access (`app/repositories/`)
- **Model Layer**: Database models (`app/models/`)

Key files:
- [app/main.py](backend/app/main.py) - FastAPI application entry point
- [app/core/config.py](backend/app/core/config.py) - Configuration management
- [app/core/security.py](backend/app/core/security.py) - Authentication utilities

### Frontend Development

The frontend uses a feature-based structure:

- **Components**: Reusable UI components
- **Pages**: Route-level containers
- **Services**: API communication
- **Hooks**: Custom React hooks

Key files:
- [src/App.tsx](frontend/src/App.tsx) - Root component
- [src/services/api.ts](frontend/src/services/api.ts) - API client configuration

### Creating Database Migrations

```bash
# After modifying models
make migration MSG="add_new_field_to_users"

# Apply migrations
make migrate
```

### Running Tests

```bash
# All tests
make test

# Backend only
cd backend && pytest

# Frontend only
cd frontend && npm run test
```

## Database Schema

### Core Tables

- **users** - User accounts and authentication
- **fiis** - FII catalog (tickers, names, sectors)
- **transactions** - Purchase/sale transaction history
- **dividends** - Monthly dividend payment records
- **portfolio_snapshots** - Cached portfolio positions
- **import_jobs** - File import job tracking
- **refresh_tokens** - JWT refresh token storage

See [Database Schema Documentation](docs/database/schema.md) for details.

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout

### Transactions
- `GET /api/v1/transactions` - List transactions
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions/{id}` - Get transaction details
- `PATCH /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction

### Dividends
- `GET /api/v1/dividends` - List dividends
- `POST /api/v1/dividends` - Create dividend record
- `GET /api/v1/dividends/summary` - Get dividend summary

### Portfolio
- `GET /api/v1/portfolio` - Get portfolio overview
- `GET /api/v1/portfolio/positions` - Get positions by FII
- `GET /api/v1/portfolio/performance` - Get performance metrics

See [API Documentation](http://localhost:8000/api/docs) for complete endpoint reference.

## Configuration

### Backend Environment Variables

See [backend/.env.example](backend/.env.example):

```bash
DATABASE_URL=postgresql://fii_user:fii_password@localhost:5432/fii_portfolio
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
REDIS_URL=redis://localhost:6379/0
```

### Frontend Environment Variables

See [frontend/.env.example](frontend/.env.example):

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=FII Portfolio Manager
```

## Security

- **Authentication**: JWT tokens with refresh token rotation
- **Password Hashing**: bcrypt with 12 rounds
- **CORS**: Configured for frontend origin only
- **Input Validation**: Pydantic schemas on all endpoints
- **SQL Injection**: Prevented by SQLAlchemy ORM
- **Soft Deletes**: Audit trail for financial records

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Development Setup Guide](docs/development/setup.md)
- [API Documentation](docs/api/endpoints.md)
- [Database Schema](docs/database/schema.md)
- [Contributing Guidelines](docs/development/contributing.md)

## Troubleshooting

### Backend won't start
- Verify PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL in backend/.env
- Review logs: `backend/logs/app.log`

### Frontend won't start
- Install dependencies: `cd frontend && npm install`
- Verify port 3000 is available
- Check VITE_API_BASE_URL in frontend/.env

### Database connection errors
- Test PostgreSQL: `psql postgresql://fii_user:fii_password@localhost:5432/fii_portfolio`
- Check credentials in backend/.env
- Restart services: `make stop-services && make start-services`

See [Development Setup Guide](docs/development/setup.md) for more troubleshooting help.

## Roadmap

- [x] Project structure and foundation
- [ ] User authentication system
- [ ] Transaction management
- [ ] Dividend tracking
- [ ] Portfolio analytics
- [ ] File import (CSV/Excel)
- [ ] Report generation
- [ ] Tax calculation engine
- [ ] Real-time market data integration
- [ ] Email notifications
- [ ] Mobile app (React Native)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [Contributing Guidelines](docs/development/contributing.md) for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Review [troubleshooting guide](docs/development/setup.md#troubleshooting)

---

Built with ❤️ for Brazilian FII investors
