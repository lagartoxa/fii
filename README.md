# FII Portfolio Manager

Manage your Brazilian Real Estate Investment Trusts (Fundos Imobiliários - FIIs) portfolio easily.

This is a home made project, fully created using AI agents with Claude AI.

## What Can You Do?

- **Track your FII transactions**: Buy and sell records with automatic average price calculation
- **Manage dividends**: Record dividend payments with COM dates and automatic portfolio calculations
- **Monitor your portfolio**: See your current positions, total invested, and dividend income
- **Monthly summaries**: View dividend income by FII for any month
- **Multi-user**: Each user has their own private portfolio

## Built With

**Backend**: FastAPI (Python) + PostgreSQL + Redis
**Frontend**: React + TypeScript

## Installation & Setup

### Automatic Setup (Recommended)

```bash
# 1. Clone the project
git clone <repository-url>
cd fii

# 2. Run the setup wizard (installs everything)
./setup-wizard.sh

# 3. Start the application
./start-dev.sh
```

**That's it!** The application will be available at:
- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Manual Setup

If you prefer manual setup or the wizard fails, see [SETUP_WITHOUT_DOCKER.md](SETUP_WITHOUT_DOCKER.md).

### Stopping the Application

```bash
./stop-dev.sh
```

## Common Tasks

### Using the Application

After starting with `./start-dev.sh`:

1. **Register a user**: Go to http://localhost:5173 and create an account
2. **Add FIIs**: Go to "FIIs" page and add your investment trusts (e.g., HGLG11)
3. **Record transactions**: In "Transactions" page, add your buy/sell operations
4. **Add dividends**: In "Dividends" page, record dividend payments with COM dates
5. **View summary**: Check "Monthly Summary" to see your dividend income by month

### For Developers

```bash
# Start/stop application
./start-dev.sh          # Start everything
./stop-dev.sh           # Stop everything

# Database migrations (after model changes)
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "description"
alembic upgrade head

# View logs
tail -f backend/logs/backend.log
```

For more development commands, run `make help`.

## Troubleshooting

**Application won't start?**
- Check if PostgreSQL and Redis are running: `docker-compose ps`
- See detailed logs: `tail -f backend/logs/backend.log`
- For more help: see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Database issues?**
- Reset database: `cd backend && alembic downgrade base && alembic upgrade head`
- Check connection: Edit `backend/.env` file

**Port already in use?**
- Backend (8000): `lsof -ti:8000 | xargs kill -9`
- Frontend (5173): `lsof -ti:5173 | xargs kill -9`

## Project Structure

```
fii/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── db/       # Database models
│   │   └── schemas/  # Request/response schemas
│   └── alembic/      # Database migrations
│
├── frontend/         # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Page views
│   │   └── services/    # API calls
│
├── start-dev.sh      # Start application
├── stop-dev.sh       # Stop application
└── docker-compose.yml # PostgreSQL + Redis
```

## Documentation

- **Setup Guide**: [SETUP_WITHOUT_DOCKER.md](SETUP_WITHOUT_DOCKER.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Startup Scripts**: [STARTUP_SCRIPTS.md](STARTUP_SCRIPTS.md)
- **Installation Details**: [INSTALL.md](INSTALL.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **API Docs**: http://localhost:8000/docs (when running)

## Know issues
 - We have the RBAC structure (users, roles and permissions) but it's not implemented. Any user can access any page or API, without any kind of permission checking, only authentication checking. I don't plan to fix it, since my focus here is on report generation to myself

## License

MIT License - See LICENSE file for details.

---

Made for Brazilian FII investors 🇧🇷
