# Setup Without Docker

This guide helps you set up PostgreSQL and Redis **without Docker** for development.

## Overview

The application needs:
- **PostgreSQL 14+** - Database
- **Redis 6+** - Optional (for background tasks, can skip for basic usage)

## Option 1: Install PostgreSQL and Redis Locally

### On Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Redis (optional)
sudo apt install redis-server

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server

# Enable services to start on boot
sudo systemctl enable postgresql
sudo systemctl enable redis-server
```

### On macOS

```bash
# Install using Homebrew
brew install postgresql@16
brew install redis

# Start services
brew services start postgresql@16
brew services start redis
```

### On Fedora/RHEL

```bash
# Install PostgreSQL
sudo dnf install postgresql-server postgresql-contrib

# Initialize database
sudo postgresql-setup --initdb

# Install Redis (optional)
sudo dnf install redis

# Start services
sudo systemctl start postgresql
sudo systemctl start redis

# Enable services
sudo systemctl enable postgresql
sudo systemctl enable redis
```

## Option 2: Use SQLite (Development Only)

For quick development without PostgreSQL, you can use SQLite:

### Step 1: Update Backend Configuration

Edit `backend/.env`:
```env
# Comment out PostgreSQL URL
# DATABASE_URL=postgresql://fii_user:fii_password@localhost:5432/fii_portfolio

# Use SQLite instead
DATABASE_URL=sqlite:///./fii_portfolio.db

# Other settings
SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
```

### Step 2: Skip Redis

Redis is optional for development. The application will work without it (background tasks just won't run).

### Step 3: Run Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

**Note:** SQLite is for development only. Use PostgreSQL for production.

## PostgreSQL Database Setup

### Step 1: Create Database User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell, run:
CREATE USER fii_user WITH PASSWORD 'fii_password';
CREATE DATABASE fii_portfolio OWNER fii_user;
GRANT ALL PRIVILEGES ON DATABASE fii_portfolio TO fii_user;
\q
```

### Step 2: Verify Connection

```bash
# Test connection
psql -U fii_user -d fii_portfolio -h localhost

# If it asks for password, enter: fii_password
# If you get in, type \q to exit
```

### Step 3: Configure Backend

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://fii_user:fii_password@localhost:5432/fii_portfolio
SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
```

### Step 4: Run Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

## Redis Setup (Optional)

Redis is only needed for:
- Background file import tasks
- Celery task queue

If you don't need these features, you can skip Redis.

### Verify Redis is Running

```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG
```

### Configure Backend for Redis

Edit `backend/.env`:
```env
REDIS_URL=redis://localhost:6379/0
```

## Troubleshooting

### PostgreSQL: Connection Refused

**Problem:** Can't connect to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql

# Check PostgreSQL is listening on port 5432
sudo netstat -plnt | grep 5432
```

### PostgreSQL: Authentication Failed

**Problem:** `FATAL: password authentication failed for user "fii_user"`

**Solution:** Reset the password
```bash
sudo -u postgres psql
ALTER USER fii_user WITH PASSWORD 'fii_password';
\q
```

### PostgreSQL: Peer Authentication Failed

**Problem:** `FATAL: Peer authentication failed`

**Solution:** Configure PostgreSQL to use password authentication

Edit `/etc/postgresql/16/main/pg_hba.conf` (path may vary):
```
# Change this line:
local   all             all                                     peer

# To this:
local   all             all                                     md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Redis: Connection Refused

**Problem:** Can't connect to Redis

**Solution:**
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Start if not running
sudo systemctl start redis-server

# Check Redis is listening
redis-cli ping
```

### Port Already in Use

**PostgreSQL:**
```bash
# Check what's using port 5432
sudo lsof -i :5432

# If needed, stop the service
sudo systemctl stop postgresql
```

**Redis:**
```bash
# Check what's using port 6379
sudo lsof -i :6379

# If needed, stop the service
sudo systemctl stop redis-server
```

## Quick Start After Setup

Once PostgreSQL is installed and configured:

```bash
# 1. Setup project (if not already done)
make setup

# 2. Run migrations
make migrate

# 3. Start the application (skip make start-services)
make start

# Or start individually:
make start-backend  # Terminal 1
make start-frontend # Terminal 2
```

## Summary

### With PostgreSQL Installed Locally

```bash
# One-time setup
sudo apt install postgresql  # or brew install postgresql
sudo -u postgres psql -c "CREATE USER fii_user WITH PASSWORD 'fii_password';"
sudo -u postgres psql -c "CREATE DATABASE fii_portfolio OWNER fii_user;"

# Configure backend/.env with PostgreSQL URL
# Then:
make setup
make migrate
make start
```

### With SQLite (Quick Development)

```bash
# Configure backend/.env with SQLite URL
DATABASE_URL=sqlite:///./fii_portfolio.db

# Then:
make setup
make migrate
make start
```

## Production Recommendations

For production:
- ✅ Use PostgreSQL (required)
- ✅ Use Redis (recommended)
- ✅ Use Docker for easy deployment
- ❌ Don't use SQLite in production

## Installing Docker (Recommended)

If you want to use Docker instead:

### Ubuntu/Debian
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version

# Start services
make start-services
```

### macOS
```bash
# Download and install Docker Desktop from:
# https://www.docker.com/products/docker-desktop

# Verify
docker --version
docker compose version

# Start services
make start-services
```

## Need Help?

- Check the [main README](README.md)
- Review the [Quick Start Guide](QUICKSTART.md)
- Check PostgreSQL logs: `sudo journalctl -u postgresql`
- Check Redis logs: `sudo journalctl -u redis-server`
