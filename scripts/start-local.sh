#!/bin/bash
#
# Local Development Server Startup Script
# Starts all services with local-friendly URLs
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_PORT=8000
REACT_PORT=5173
STREAMLIT_PORT=8501

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Market Analyst - Local Development Startup       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
        echo -e "${YELLOW}⚠ Please edit .env and add your GROQ_API_KEY${NC}"
    else
        echo -e "${RED}✗ .env.example not found!${NC}"
        exit 1
    fi
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -Pi :$port -sTCP:LISTEN -t 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}⚠ Port $port is in use. Killing process $pid...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Check ports
echo -e "${BLUE}Checking ports...${NC}"
for port in $API_PORT $REACT_PORT $STREAMLIT_PORT; do
    if check_port $port; then
        kill_port $port
    fi
done
echo -e "${GREEN}✓ Ports are available${NC}"
echo ""

# Start Backend
echo -e "${BLUE}Starting FastAPI Backend on http://localhost:$API_PORT${NC}"
python3 -m uvicorn backend.api.fastapi_server:app \
    --host 0.0.0.0 \
    --port $API_PORT \
    --reload \
    --log-level info > logs/api.log 2>&1 &
API_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $API_PID)${NC}"
echo ""

# Wait for backend to be ready
echo -e "${BLUE}Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$API_PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start${NC}"
        echo "Check logs/api.log for details"
        exit 1
    fi
done
echo ""

# Start React Frontend
echo -e "${BLUE}Starting React Frontend on http://localhost:$REACT_PORT${NC}"
cd react-directory
npm run dev -- --host 0.0.0.0 --port $REACT_PORT > ../logs/react.log 2>&1 &
REACT_PID=$!
cd ..
echo -e "${GREEN}✓ React frontend started (PID: $REACT_PID)${NC}"
echo ""

# Start Streamlit
echo -e "${BLUE}Starting Streamlit on http://localhost:$STREAMLIT_PORT${NC}"
streamlit run frontend/streamlit_app.py \
    --server.port $STREAMLIT_PORT \
    --server.address 0.0.0.0 \
    --server.headless true > logs/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo -e "${GREEN}✓ Streamlit started (PID: $STREAMLIT_PID)${NC}"
echo ""

# Create logs directory if not exists
mkdir -p logs

# Print summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🚀 ALL SERVICES STARTED!                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo -e "  • Backend API:   ${GREEN}http://localhost:$API_PORT${NC}"
echo -e "  • Health Check:  ${GREEN}http://localhost:$API_PORT/health${NC}"
echo -e "  • React App:     ${GREEN}http://localhost:$REACT_PORT${NC}"
echo -e "  • Streamlit:     ${GREEN}http://localhost:$STREAMLIT_PORT${NC}"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  • Backend:   logs/api.log"
echo -e "  • React:     logs/react.log"
echo -e "  • Streamlit: logs/streamlit.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for interrupt
trap "echo ''; echo -e '${YELLOW}Stopping services...${NC}'; kill $API_PID $REACT_PID $STREAMLIT_PID 2>/dev/null; exit 0" INT
wait
