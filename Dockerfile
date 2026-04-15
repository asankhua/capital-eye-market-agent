# Capital Eye Market Agent - Production Dockerfile
# Multi-stage build for optimized deployment

FROM python:3.11-slim as backend-builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Frontend Stage ---
FROM node:20-slim as frontend-builder

WORKDIR /app/frontend/react-directory

# Copy package files
COPY frontend/react-directory/package*.json .
COPY frontend/react-directory/tsconfig*.json .
COPY frontend/react-directory/vite.config.ts .

# Install dependencies
RUN npm ci

# Copy source files
COPY frontend/react-directory/src ./src
COPY frontend/react-directory/index.html .
COPY frontend/react-directory/public ./public

# Build production bundle
RUN npm run build

# --- Production Stage ---
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python packages from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/react-directory/dist ./frontend/dist

# Copy other necessary files
COPY LICENSE .
COPY README.md .

# Create necessary directories
RUN mkdir -p logs db

# Expose the port Hugging Face expects
EXPOSE 7860

# Environment variables (will be overridden by Hugging Face secrets)
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV API_BASE_URL=http://localhost:7860
ENV REACT_APP_API_URL=http://localhost:7860

# Start command - serves both frontend and backend
CMD ["python", "-m", "uvicorn", "backend.api.fastapi_server:app", "--host", "0.0.0.0", "--port", "7860"]
