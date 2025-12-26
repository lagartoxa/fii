#!/bin/bash

# FII Portfolio Manager - Stop Development Services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping FII Portfolio Manager services...${NC}"

# Kill backend (uvicorn)
BACKEND_PIDS=$(pgrep -f "uvicorn app.main:app")
if [ -n "$BACKEND_PIDS" ]; then
    echo -e "${GREEN}Stopping backend (PIDs: $BACKEND_PIDS)${NC}"
    kill $BACKEND_PIDS 2>/dev/null
else
    echo -e "${YELLOW}Backend is not running${NC}"
fi

# Kill frontend (vite)
FRONTEND_PIDS=$(pgrep -f "vite")
if [ -n "$FRONTEND_PIDS" ]; then
    echo -e "${GREEN}Stopping frontend (PIDs: $FRONTEND_PIDS)${NC}"
    kill $FRONTEND_PIDS 2>/dev/null
else
    echo -e "${YELLOW}Frontend is not running${NC}"
fi

echo -e "${GREEN}✓ Services stopped${NC}"
