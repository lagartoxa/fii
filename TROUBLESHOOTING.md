# Troubleshooting Guide

Common issues and their solutions for the FII Portfolio Manager.

## Frontend Issues

### Frontend Won't Start - "Unexpected reserved word" Error

**Symptoms:**
- Backend works (http://localhost:8000)
- API docs work (http://localhost:8000/api/docs)
- Frontend doesn't load (http://localhost:5173)
- Frontend logs show: `SyntaxError: Unexpected reserved word`

**Cause:**
Node.js version is too old. Vite (the frontend build tool) requires Node.js 18.0.0 or higher.

**Check your Node.js version:**
```bash
node --version
```

If it shows v12.x, v14.x, or v16.x, you need to upgrade.

**Solution:**

Run the upgrade script:
```bash
./upgrade-nodejs.sh
```

Or upgrade manually:

**Ubuntu/Debian:**
```bash
# Remove old Node.js
sudo apt-get remove -y nodejs npm
sudo apt-get autoremove -y

# Add NodeSource repository for Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js 20
sudo apt-get install -y nodejs

# Verify
node --version  # Should show v20.x.x
```

**After upgrading Node.js:**
```bash
# Stop the application
make stop

# Reinstall frontend dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..

# Start the application
make start
```

### Frontend Port Already in Use

**Error:** `Port 5173 is already in use`

**Solution:**
```bash
# Find what's using port 5173
lsof -i :5173

# Kill the process
kill -9 <PID>

# Or use a different port by editing frontend/vite.config.ts
```

### Frontend Build Errors

**Error:** `Failed to resolve import` or module errors

**Solution:**
```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

cd ..
make start
```

## Backend Issues

### Backend Won't Start - Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Backend Database Connection Error

**Error:** `could not connect to server` or `connection refused`

**Cause:** PostgreSQL is not running

**Solution:**

**If using Docker:**
```bash
# Check if Docker containers are running
docker ps

# If not running, start them
make start-services

# Check logs
docker-compose logs postgres
```

**If using local PostgreSQL:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql
```

**If using SQLite:**
- No service needed, check DATABASE_URL in backend/.env

### Migration Errors

**Error:** `Target database is not up to date`

**Solution:**
```bash
cd backend
source venv/bin/activate

# Check migration status
alembic current

# Run migrations
alembic upgrade head

# If that fails, try
alembic downgrade base
alembic upgrade head
```

### Import Errors - Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Cause:** Backend dependencies not installed

**Solution:**
```bash
cd backend

# Remove old virtual environment
rm -rf venv

# Create new one
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

cd ..
make start-backend
```

## Docker Issues

### Docker Daemon Not Running

**Error:** `Cannot connect to the Docker daemon`

**Solution:**
```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### Docker Permission Denied

**Error:** `permission denied while trying to connect to the Docker daemon socket`

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes (choose one)
newgrp docker  # Apply in current terminal
# OR
# Log out and log back in
```

### Docker Compose Not Found

**Error:** `docker-compose: command not found`

**Solution:**

The Makefile handles both old and new Docker Compose syntax. If you see this error:

```bash
# Install Docker Compose plugin (new syntax)
sudo apt-get install docker-compose-plugin

# OR install standalone (old syntax)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Containers Won't Start

**Error:** `port is already allocated`

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis

# Stop conflicting service
sudo systemctl stop postgresql  # If local PostgreSQL is running

# Or stop and remove old containers
docker-compose down
docker-compose up -d
```

## Database Issues

### Can't Create Database User

**Error:** `role "fii_user" already exists`

**Solution:**
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Drop and recreate user
DROP DATABASE IF EXISTS fii_portfolio;
DROP USER IF EXISTS fii_user;
CREATE USER fii_user WITH PASSWORD 'fii_password';
CREATE DATABASE fii_portfolio OWNER fii_user;
\q
```

### SQLite Database Locked

**Error:** `database is locked`

**Cause:** Multiple processes trying to access SQLite

**Solution:**
```bash
# Stop all services
make stop

# Remove lock file
rm backend/fii_portfolio.db-journal

# Start again
make start
```

## Authentication Issues

### Can't Login - Invalid Credentials

**Problem:** Created user but can't login

**Solution:**

1. Check if user exists:
```bash
cd backend
source venv/bin/activate
python
```

```python
from app.db.session import SessionLocal
from app.db.models.user import User

db = SessionLocal()
users = db.query(User).filter(User.rm_timestamp.is_(None)).all()
for user in users:
    print(f"Username: {user.username}, Email: {user.email}, Active: {user.is_active}")
db.close()
```

2. Reset user password:
```python
from app.db.session import SessionLocal
from app.db.repositories.user_repository import UserRepository
from app.core.security import get_password_hash

db = SessionLocal()
repo = UserRepository(db)
user = repo.get_by_username("admin")  # Replace with your username
if user:
    user.hashed_password = get_password_hash("NewPassword123!")
    db.commit()
    print("Password reset successfully")
db.close()
```

### JWT Token Errors

**Error:** `Invalid authentication credentials`

**Cause:** SECRET_KEY mismatch or token expired

**Solution:**

Check backend/.env:
```bash
# Make sure SECRET_KEY is set and doesn't change
SECRET_KEY=your-secret-key-here
```

Clear browser localStorage and login again.

## General Issues

### Make Commands Don't Work

**Error:** `make: command not found`

**Solution:**

Use scripts directly:
```bash
# Instead of: make start
./start-dev.sh

# Instead of: make stop
./stop-dev.sh
```

Or install make:
```bash
# Ubuntu/Debian
sudo apt install make

# macOS
xcode-select --install
```

### Python Version Too Old

**Error:** `Python 3.7 is too old`

**Solution:**

**Ubuntu/Debian:**
```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv

# Or use deadsnakes PPA for latest
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### Virtual Environment Activation Fails

**Error:** `venv/bin/activate: No such file or directory`

**Solution:**
```bash
cd backend

# Remove old venv
rm -rf venv

# Create new one
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Logging and Debugging

### View Application Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Follow logs in real-time
make logs

# PostgreSQL logs (Docker)
docker-compose logs -f postgres

# Redis logs (Docker)
docker-compose logs -f redis
```

### Enable Debug Mode

Edit backend/.env:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

Restart backend to see detailed logs.

### Check Process Status

```bash
# Check if backend is running
pgrep -f "uvicorn app.main:app"

# Check if frontend is running
pgrep -f "vite"

# Check Docker containers
docker ps

# Check PostgreSQL (local)
sudo systemctl status postgresql
```

## Clean Install

If nothing works, try a clean installation:

```bash
# Stop everything
make stop
docker-compose down

# Clean backend
cd backend
rm -rf venv __pycache__ *.db *.db-journal
cd ..

# Clean frontend
cd frontend
rm -rf node_modules package-lock.json dist
cd ..

# Clean logs
rm -rf logs/*.log

# Start fresh
./setup-wizard.sh
```

## Getting Help

If you're still stuck:

1. Check the logs: `make logs`
2. Review [QUICKSTART.md](QUICKSTART.md)
3. Check [INSTALL.md](INSTALL.md)
4. See [SETUP_WITHOUT_DOCKER.md](SETUP_WITHOUT_DOCKER.md)
5. Open an issue on GitHub with:
   - Error message
   - Relevant logs
   - OS and versions (node --version, python3 --version, etc.)

## Quick Diagnostic

Run this to check your environment:

```bash
echo "=== System Info ==="
uname -a
echo ""
echo "=== Python ==="
python3 --version
echo ""
echo "=== Node.js ==="
node --version
echo ""
echo "=== npm ==="
npm --version
echo ""
echo "=== Docker ==="
docker --version
echo ""
echo "=== Docker Compose ==="
docker compose version || docker-compose --version
echo ""
echo "=== Running Processes ==="
pgrep -f uvicorn && echo "Backend: Running" || echo "Backend: Not running"
pgrep -f vite && echo "Frontend: Running" || echo "Frontend: Not running"
echo ""
echo "=== Docker Containers ==="
docker ps
```

Save this as check-environment.sh and run it when troubleshooting.
