# Development Setup Guide

This guide will help you set up the FII Portfolio Manager for local development.

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 16+ (or Docker for services)
- Redis 7+ (or Docker for services)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fii
```

### 2. Setup Services

Start PostgreSQL and Redis using Docker Compose:

```bash
make start-services
```

Or install them locally and configure manually.

### 3. Setup Backend

```bash
make setup-backend
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Prepare the backend for development

### 4. Setup Frontend

```bash
make setup-frontend
```

This will:
- Install npm dependencies
- Prepare the frontend for development

### 5. Configure Environment

Copy the example environment files and update with your settings:

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your database credentials

# Frontend
cp frontend/.env.example frontend/.env
# Update if needed
```

### 6. Initialize Database

Run database migrations:

```bash
make migrate
```

### 7. Start Development Servers

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
make start-backend
```

Backend will be available at: http://localhost:8000
API documentation at: http://localhost:8000/api/docs

**Terminal 2 - Frontend:**
```bash
make start-frontend
```

Frontend will be available at: http://localhost:3000

## Manual Setup

### Backend Setup (Manual)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (Manual)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Run development server
npm run dev
```

## Database Configuration

### Using Docker (Recommended)

The docker-compose.yml in the root directory provides PostgreSQL and Redis:

```bash
docker-compose up -d
```

Default credentials:
- PostgreSQL: `postgresql://fii_user:fii_password@localhost:5432/fii_portfolio`
- Redis: `redis://localhost:6379/0`

### Local Installation

If you prefer to install PostgreSQL locally:

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib redis-server
```

#### macOS
```bash
brew install postgresql@16 redis
brew services start postgresql@16
brew services start redis
```

Then create the database:

```bash
sudo -u postgres psql
CREATE DATABASE fii_portfolio;
CREATE USER fii_user WITH PASSWORD 'fii_password';
GRANT ALL PRIVILEGES ON DATABASE fii_portfolio TO fii_user;
\q
```

## Common Commands

See the Makefile for all available commands:

```bash
make help
```

Key commands:
- `make setup` - Complete project setup
- `make start-services` - Start PostgreSQL and Redis
- `make start-backend` - Start backend server
- `make start-frontend` - Start frontend server
- `make migrate` - Run database migrations
- `make migration MSG="description"` - Create new migration
- `make test` - Run all tests
- `make clean` - Clean build artifacts
- `make reset-db` - Reset database

## Troubleshooting

### Backend won't start

1. Check if virtual environment is activated
2. Verify DATABASE_URL in backend/.env
3. Ensure PostgreSQL is running: `docker-compose ps` or `systemctl status postgresql`
4. Check logs in backend/logs/app.log

### Frontend won't start

1. Ensure npm dependencies are installed: `npm install`
2. Check if port 3000 is available
3. Verify API URL in frontend/.env

### Database connection errors

1. Check if PostgreSQL is running
2. Verify credentials in backend/.env
3. Test connection: `psql postgresql://fii_user:fii_password@localhost:5432/fii_portfolio`

### Migration errors

1. Check if database exists
2. Verify DATABASE_URL is correct
3. Try: `make reset-db` to reset database

## Next Steps

Once your environment is set up:

1. Review the [Architecture Overview](../architecture/overview.md)
2. Read the [Contributing Guidelines](contributing.md)
3. Check the [API Documentation](../api/endpoints.md)
4. Start developing!

## Development Workflow

1. Create a new branch for your feature
2. Make your changes
3. Run tests: `make test`
4. Commit your changes
5. Push and create a pull request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Vite Documentation](https://vitejs.dev/)
