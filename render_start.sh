#!/bin/bash
# Render.com start script for Capital Eye Market Agent
# This script starts the FastAPI server with proper configuration

set -e

echo "🚀 Starting Capital Eye Market Agent on Render..."
echo "PORT: $PORT"
echo "PYTHON_VERSION: $(python3 --version)"

# Create necessary directories
mkdir -p logs db data

# Set production paths for frontend
export FRONTEND_DIST=/app/frontend/react-directory/dist

# Check if frontend build exists
if [ -d "$FRONTEND_DIST" ]; then
    echo "✅ Frontend build found at: $FRONTEND_DIST"
else
    echo "⚠️  Frontend build not found at $FRONTEND_DIST"
    echo "   API-only mode will be used"
fi

echo "🎯 Starting Uvicorn server on port $PORT"

# Start the FastAPI server
# Render expects the app to listen on $PORT
exec python3 -m uvicorn backend.api.fastapi_server:app \
    --host 0.0.0.0 \
    --port ${PORT:-10000} \
    --workers 1 \
    --loop uvloop \
    --http httptools
