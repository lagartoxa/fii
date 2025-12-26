# Quick Start Guide - FII Portfolio Manager

This guide will help you get the application running in just a few minutes.

## Prerequisites Check

Before starting, ensure you have these installed:

```bash
# Check Python version (need 3.11+)
python3 --version

# Check Node.js version (need 18+)
node --version

# Check npm
npm --version

# Check Docker (optional, for PostgreSQL/Redis)
docker --version
```

## 5-Minute Setup

### Step 1: Clone and Navigate
```bash
git clone <repository-url>
cd fii
```

### Step 2: Start Database Services

**If you have Docker installed:**
```bash
make start-services
```

**If Docker is NOT installed:**

You have two options:

**Option A: Install PostgreSQL locally (recommended for development)**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql -c "CREATE USER fii_user WITH PASSWORD 'fii_password';"
sudo -u postgres psql -c "CREATE DATABASE fii_portfolio OWNER fii_user;"
```

**Option B: Use SQLite (quickest, development only)**
```bash
# Skip this step entirely, just configure SQLite in Step 4
```

See [SETUP_WITHOUT_DOCKER.md](SETUP_WITHOUT_DOCKER.md) for detailed instructions.

### Step 3: Install Dependencies
```bash
# Install both backend and frontend dependencies
make setup
```

This will:
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies

### Step 4: Configure Environment

**Backend Configuration:**
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

**If using PostgreSQL (Docker or local):**
```env
DATABASE_URL=postgresql://fii_user:fii_password@localhost:5432/fii_portfolio
SECRET_KEY=change-this-in-production
CORS_ORIGINS=http://localhost:5173
```

**If using SQLite (development only):**
```env
DATABASE_URL=sqlite:///./fii_portfolio.db
SECRET_KEY=change-this-in-production
CORS_ORIGINS=http://localhost:5173
```

**Frontend Configuration:**
```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env` if needed (defaults should work):
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Step 5: Run Database Migrations
```bash
make migrate
```

### Step 6: Start the Application
```bash
# Start both backend and frontend together
make start
```

That's it! The application is now running:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Step 7: Create Your First User

Since you now have a login page, you need to create a user account first. You can do this via:

**Option 1: Using the API directly (recommended for testing)**

Open a new terminal and run:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "Admin123!",
    "full_name": "Admin User"
  }'
```

**Option 2: Using the API documentation**

1. Go to http://localhost:8000/docs
2. Find the `POST /api/v1/auth/register` endpoint
3. Click "Try it out"
4. Fill in the user details
5. Click "Execute"

**Option 3: Using Python shell**

```bash
cd backend
source venv/bin/activate
python
```

```python
from app.db.session import SessionLocal
from app.db.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

db = SessionLocal()
user_repo = UserRepository(db)

user_data = UserCreate(
    email="admin@example.com",
    username="admin",
    password="Admin123!",
    full_name="Admin User"
)

user = user_repo.create_user(user_data)
print(f"User created: {user.username}")
db.close()
```

### Step 8: Login

1. Open http://localhost:5173
2. You'll be redirected to the login page
3. Enter your credentials:
   - Username: `admin`
   - Password: `Admin123!`
4. Click "Sign In"
5. You'll be redirected to the home page with "Hello World" message

## Stopping the Application

```bash
# Stop all services
make stop

# Or press Ctrl+C in the terminal where you ran 'make start'
```

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
# Check what's using port 8000 (backend)
lsof -i :8000

# Check what's using port 5173 (frontend)
lsof -i :5173

# Kill the process if needed
kill -9 <PID>
```

### Backend Won't Start

```bash
# Check if PostgreSQL is running
docker-compose ps

# View backend logs
tail -f logs/backend.log

# Restart services
make stop-services
make start-services
```

### Frontend Won't Start

```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules
npm install

# View frontend logs
tail -f ../logs/frontend.log
```

### Database Connection Errors

```bash
# Test PostgreSQL connection
psql postgresql://fii_user:fii_password@localhost:5432/fii_portfolio

# If it fails, check Docker
docker-compose logs postgres
```

### Migration Issues

```bash
# Reset database and run migrations again
make reset-db
```

## Next Steps

Now that you're up and running:

1. ✅ Login to the application
2. Explore the API documentation at http://localhost:8000/docs
3. Check out the [full README](README.md) for more details
4. Review the [development guide](docs/development/setup.md)
5. Start building features!

## Common Development Workflows

### Making Database Changes

```bash
# 1. Modify your models in backend/app/db/models/
# 2. Create a migration
make migration MSG="add_new_field"
# 3. Apply the migration
make migrate
```

### Running Tests

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend
```

### Viewing Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# PostgreSQL logs
docker-compose logs -f postgres
```

## Need Help?

- Check the [main README](README.md)
- Review the [documentation](docs/)
- Open an issue on GitHub
- Check the [troubleshooting section](#troubleshooting) above

---

Happy coding! 🚀
