# Startup Scripts Documentation

This document explains the different ways to start the FII Portfolio Manager application.

## Available Startup Methods

### 1. Using Make (Recommended)

The easiest way to start the application:

```bash
# Start both backend and frontend
make start

# Stop both
make stop
```

**Advantages:**
- Simple one-command startup
- Cross-platform (works on Linux, macOS, Windows with WSL)
- Integrates with existing project commands
- Easy to remember

**How it works:**
- Calls the `start-dev.sh` script
- Starts backend and frontend in background
- Logs output to `logs/` directory

### 2. Using Shell Scripts Directly

For more control, use the shell scripts:

```bash
# Start application
./start-dev.sh

# Stop application
./stop-dev.sh
```

**Advantages:**
- More detailed output and status messages
- Color-coded output
- Dependency checking
- Automatic virtual environment setup

**How it works:**
- Checks for Python and Node.js
- Creates/activates virtual environment
- Installs dependencies if needed
- Starts backend on port 8000
- Starts frontend on port 5173
- Logs to `logs/backend.log` and `logs/frontend.log`

### 3. Manual Startup (Advanced)

Start each service manually in separate terminals:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Advantages:**
- See real-time output in terminal
- Easier debugging
- More control over each service
- Can restart services independently

**Disadvantages:**
- Requires multiple terminal windows
- More manual steps

## Script Details

### start-dev.sh

**Location:** `/home/parallels/projects/fii/start-dev.sh`

**What it does:**
1. Checks if Python 3 and Node.js are installed
2. Creates Python virtual environment if missing
3. Installs backend dependencies (first run only)
4. Starts backend server in background
5. Installs frontend dependencies (first run only)
6. Starts frontend dev server in background
7. Displays status and URLs
8. Waits for user to press Ctrl+C to stop

**Output:**
- Backend logs: `logs/backend.log`
- Frontend logs: `logs/frontend.log`

**Example output:**
```
========================================
FII Portfolio Manager - Starting...
========================================

Starting Backend API...
Backend API starting on http://localhost:8000
Starting Frontend...
Frontend starting on http://localhost:5173

========================================
✓ Application started successfully!
========================================

Services:
  Backend API:  http://localhost:8000
  API Docs:     http://localhost:8000/docs
  Frontend:     http://localhost:5173

Logs:
  Backend:  logs/backend.log
  Frontend: logs/frontend.log

Press Ctrl+C to stop all services
```

### stop-dev.sh

**Location:** `/home/parallels/projects/fii/stop-dev.sh`

**What it does:**
1. Finds all running uvicorn processes (backend)
2. Finds all running vite processes (frontend)
3. Kills them gracefully

**Example output:**
```
Stopping FII Portfolio Manager services...
Stopping backend (PIDs: 12345)
Stopping frontend (PIDs: 12346)
✓ Services stopped
```

## Logs

Both scripts create log files in the `logs/` directory:

### View Backend Logs
```bash
# View last 50 lines
tail -n 50 logs/backend.log

# Follow logs in real-time
tail -f logs/backend.log
```

### View Frontend Logs
```bash
# View last 50 lines
tail -n 50 logs/frontend.log

# Follow logs in real-time
tail -f logs/frontend.log
```

### View All Logs
```bash
# Using make
make logs

# Manually
tail -n 50 logs/backend.log logs/frontend.log
```

## Troubleshooting

### Scripts Won't Execute

Make sure they're executable:
```bash
chmod +x start-dev.sh stop-dev.sh
```

### Permission Denied

Run with explicit shell:
```bash
bash start-dev.sh
bash stop-dev.sh
```

### Services Don't Stop

Manually kill processes:
```bash
# Find backend process
pgrep -f "uvicorn app.main:app"

# Find frontend process
pgrep -f "vite"

# Kill them
pkill -f "uvicorn app.main:app"
pkill -f "vite"
```

### Port Already in Use

Check what's using the ports:
```bash
# Backend port (8000)
lsof -i :8000

# Frontend port (5173)
lsof -i :5173

# Kill the process
kill -9 <PID>
```

### Dependencies Not Installing

The scripts create a marker file after first installation. If you need to reinstall:

```bash
# Backend
rm backend/venv/.dependencies_installed
./start-dev.sh

# Frontend
rm -rf frontend/node_modules
./start-dev.sh
```

## Environment Variables

Both scripts respect environment variables set in `.env` files:

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql://fii_user:fii_password@localhost:5432/fii_portfolio
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:5173
```

**Frontend** (`frontend/.env`):
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Customization

### Change Ports

**Backend port:**
Edit `start-dev.sh` line:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Change `--port 8000` to your desired port.

**Frontend port:**
Frontend uses default Vite port (5173). To change it, edit `frontend/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 3000  // Your desired port
  }
})
```

### Disable Auto-Dependency Installation

Edit `start-dev.sh` and remove these sections:
```bash
# Remove for backend
if [ ! -f "venv/.dependencies_installed" ]; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -r requirements.txt
    touch venv/.dependencies_installed
fi

# Remove for frontend
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi
```

### Add Pre-Start Checks

You can add custom checks to `start-dev.sh`:
```bash
# Check if PostgreSQL is running
if ! docker-compose ps | grep -q postgres; then
    echo -e "${RED}PostgreSQL is not running. Start with: make start-services${NC}"
    exit 1
fi
```

## Integration with IDEs

### VS Code

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Application",
      "type": "shell",
      "command": "./start-dev.sh",
      "problemMatcher": []
    },
    {
      "label": "Stop Application",
      "type": "shell",
      "command": "./stop-dev.sh",
      "problemMatcher": []
    }
  ]
}
```

### PyCharm / IntelliJ

1. Go to Run → Edit Configurations
2. Add new "Shell Script" configuration
3. Set script path to `/home/parallels/projects/fii/start-dev.sh`
4. Save and run

## Summary

**Quick Reference:**

| Command | Description |
|---------|-------------|
| `make start` | Start both backend and frontend (recommended) |
| `make stop` | Stop all services |
| `./start-dev.sh` | Start with detailed output |
| `./stop-dev.sh` | Stop all services |
| `make start-backend` | Start only backend |
| `make start-frontend` | Start only frontend |
| `make logs` | View logs |

Choose the method that works best for your workflow!
