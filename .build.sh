#!/bin/bash
# Render.com build script for Capital Eye Market Agent
# This script runs during the build phase

set -e

echo "🔧 Building Capital Eye Market Agent..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js 20.x if not available
if ! command -v node &> /dev/null; then
    echo "📥 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ NPM version: $(npm --version)"

# Build frontend
echo "🏗️  Building React frontend..."
cd frontend/react-directory
npm ci
npm run build

echo "✅ Build complete!"
echo "📂 Frontend build location: $(pwd)/dist"
