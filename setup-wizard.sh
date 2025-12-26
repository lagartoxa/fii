#!/bin/bash

# FII Portfolio Manager - Setup Wizard
# Interactive setup script that guides you through installation

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}FII Portfolio Manager - Setup Wizard${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "  Please install Python 3.11+ and try again"
    exit 1
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo "  Please install Node.js 18+ and try again"
    exit 1
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
else
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ npm $NPM_VERSION${NC}"
fi

echo ""

# Database selection
echo -e "${YELLOW}Database Setup${NC}"
echo "Choose your database option:"
echo "  1) PostgreSQL with Docker (recommended)"
echo "  2) PostgreSQL locally installed"
echo "  3) SQLite (development only, no installation needed)"
echo ""
read -p "Enter your choice (1-3): " DB_CHOICE

case $DB_CHOICE in
    1)
        echo -e "${BLUE}Checking Docker...${NC}"
        if command -v docker &> /dev/null; then
            echo -e "${GREEN}✓ Docker is installed${NC}"
            echo -e "${YELLOW}Starting PostgreSQL and Redis with Docker...${NC}"

            if command -v docker-compose &> /dev/null; then
                docker-compose up -d
            else
                docker compose up -d
            fi

            DATABASE_URL="postgresql://fii_user:fii_password@localhost:5432/fii_portfolio"
            echo -e "${GREEN}✓ Database services started${NC}"
        else
            echo -e "${RED}✗ Docker is not installed${NC}"
            echo "Please install Docker or choose option 2 or 3"
            exit 1
        fi
        ;;
    2)
        echo -e "${YELLOW}Using locally installed PostgreSQL${NC}"
        echo ""
        echo "Make sure PostgreSQL is installed and running, then:"
        echo "  sudo -u postgres psql -c \"CREATE USER fii_user WITH PASSWORD 'fii_password';\""
        echo "  sudo -u postgres psql -c \"CREATE DATABASE fii_portfolio OWNER fii_user;\""
        echo ""
        read -p "Press Enter when database is ready..."
        DATABASE_URL="postgresql://fii_user:fii_password@localhost:5432/fii_portfolio"
        ;;
    3)
        echo -e "${YELLOW}Using SQLite (development only)${NC}"
        DATABASE_URL="sqlite:///./fii_portfolio.db"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"

# Backend
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

cd ..

# Frontend
echo -e "${BLUE}Setting up frontend...${NC}"
cd frontend
npm install
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
cd ..

echo ""

# Create .env files
echo -e "${YELLOW}Creating configuration files...${NC}"

# Backend .env
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << EOF
DATABASE_URL=$DATABASE_URL
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
ALGORITHM=HS256
EOF
    echo -e "${GREEN}✓ Created backend/.env${NC}"
else
    echo -e "${YELLOW}  backend/.env already exists (skipping)${NC}"
fi

# Frontend .env
if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << EOF
VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF
    echo -e "${GREEN}✓ Created frontend/.env${NC}"
else
    echo -e "${YELLOW}  frontend/.env already exists (skipping)${NC}"
fi

echo ""

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
cd backend
source venv/bin/activate
alembic upgrade head
echo -e "${GREEN}✓ Migrations complete${NC}"
cd ..

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Create your first user:"
echo "   ${BLUE}cd backend${NC}"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo "   ${BLUE}python -c \"from app.db.session import SessionLocal; from app.db.repositories.user_repository import UserRepository; from app.schemas.user import UserCreate; db = SessionLocal(); repo = UserRepository(db); user = repo.create_user(UserCreate(email='admin@example.com', username='admin', password='Admin123!', full_name='Admin')); print(f'User created: {user.username}'); db.close()\"${NC}"
echo ""
echo "2. Start the application:"
echo "   ${BLUE}make start${NC}"
echo ""
echo "3. Open your browser:"
echo "   Frontend: ${GREEN}http://localhost:5173${NC}"
echo "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}To stop the application later, run:${NC} ${BLUE}make stop${NC}"
echo ""
