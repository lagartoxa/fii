.PHONY: help setup setup-backend setup-frontend start-services stop-services start-backend start-frontend start stop test clean

help:
	@echo "FII Portfolio Manager - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup              - Complete project setup (backend + frontend + services)"
	@echo "  make setup-backend      - Setup backend environment"
	@echo "  make setup-frontend     - Setup frontend environment"
	@echo ""
	@echo "Service Commands:"
	@echo "  make start-services     - Start PostgreSQL and Redis (Docker Compose)"
	@echo "  make stop-services      - Stop all services"
	@echo ""
	@echo "Development Commands:"
	@echo "  make start              - Start both backend and frontend (recommended)"
	@echo "  make stop               - Stop both backend and frontend"
	@echo "  make start-backend      - Start FastAPI backend server"
	@echo "  make start-frontend     - Start React frontend dev server"
	@echo "  make migrate            - Run database migrations"
	@echo "  make migration MSG=...  - Create new migration"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test               - Run all tests"
	@echo "  make test-backend       - Run backend tests"
	@echo "  make test-frontend      - Run frontend tests"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean              - Clean build artifacts and caches"
	@echo "  make reset-db           - Reset database to clean state"

setup: setup-backend setup-frontend start-services
	@echo "Setup complete! Run 'make start-backend' and 'make start-frontend' to start development"

setup-backend:
	@echo "Setting up backend..."
	cd backend && python3 -m venv venv
	cd backend && . venv/bin/activate && pip install --upgrade pip
	cd backend && . venv/bin/activate && pip install -r requirements.txt
	cd backend && . venv/bin/activate && pip install -r requirements-dev.txt
	@echo "Backend setup complete!"

setup-frontend:
	@echo "Setting up frontend..."
	cd frontend && npm install
	@echo "Frontend setup complete!"

start-services:
	@echo "Starting PostgreSQL and Redis..."
	@if command -v docker-compose &> /dev/null; then \
		docker-compose up -d; \
	elif command -v docker &> /dev/null; then \
		docker compose up -d; \
	else \
		echo "Error: Docker is not installed."; \
		echo "Please install Docker or use manual PostgreSQL/Redis setup."; \
		echo "See SETUP_WITHOUT_DOCKER.md for alternative setup."; \
		exit 1; \
	fi
	@echo "Services started! PostgreSQL on port 5432, Redis on port 6379"

stop-services:
	@echo "Stopping services..."
	@if command -v docker-compose &> /dev/null; then \
		docker-compose down; \
	elif command -v docker &> /dev/null; then \
		docker compose down; \
	else \
		echo "Error: Docker is not installed."; \
		exit 1; \
	fi

start-backend:
	@echo "Starting backend server..."
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start-frontend:
	@echo "Starting frontend dev server..."
	cd frontend && npm run dev

start:
	@echo "Starting FII Portfolio Manager (backend + frontend)..."
	@./start-dev.sh

stop:
	@echo "Stopping all services..."
	@./stop-dev.sh

migrate:
	@echo "Running database migrations..."
	cd backend && . venv/bin/activate && alembic upgrade head

migration:
	@echo "Creating new migration: $(MSG)"
	cd backend && . venv/bin/activate && alembic revision --autogenerate -m "$(MSG)"

test:
	make test-backend
	make test-frontend

test-backend:
	@echo "Running backend tests..."
	cd backend && . venv/bin/activate && pytest

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm run test

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd backend && rm -rf .pytest_cache 2>/dev/null || true
	cd frontend && rm -rf dist node_modules/.cache 2>/dev/null || true
	@echo "Clean complete!"

reset-db:
	@echo "Resetting database..."
	cd backend && . venv/bin/activate && alembic downgrade base
	cd backend && . venv/bin/activate && alembic upgrade head
	@echo "Database reset complete!"
