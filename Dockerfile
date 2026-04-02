# Multi-stage Dockerfile at project root
# This delegates to backend/Dockerfile to build the application

# Build stage - using backend Dockerfile logic
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY backend/ /app/backend/
COPY .github/ /app/.github/
COPY README.md LICENSE /app/
COPY config.yaml /app/
COPY config.yaml /app/backend/
COPY backend/pyproject.toml /app/backend/

# Set working directory to backend for dependency installation
WORKDIR /app/backend

# Install uv (fast Python package manager)
RUN pip install uv

# Create virtual environment and install dependencies
RUN uv venv .venv && \
    uv pip install --upgrade pip setuptools && \
    uv pip install -e ".[dev]"

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend and other necessary files
COPY backend/ /app/backend/
COPY .github/ /app/.github/
COPY README.md LICENSE /app/
COPY config.yaml /app/
COPY config.yaml /app/backend/

# Copy virtual environment from builder
COPY --from=builder /app/backend/.venv /app/backend/.venv

# Copy startup script to root
COPY start.sh /start.sh

# Make script executable and create Python startup helper
RUN chmod +x /start.sh && \
    python3 -c "code='''import os,sys,subprocess;cfg=os.environ.get(\"DEER_FLOW_CONFIG_PATH\",\"/app/backend/config.yaml\");print(f\"Config: {cfg}\");os.path.exists(cfg) or (print(f\"ERROR: {cfg} not found\"),sys.exit(1));os.environ[\"DEER_FLOW_CONFIG_PATH\"]=cfg;os.chdir(\"/app/backend\");os.execvp(sys.executable,[sys.executable,\"-m\",\"uvicorn\",\"app.gateway.app:app\",\"--host\",\"0.0.0.0\",\"--port\",\"8080\",\"--workers\",\"1\"])''';open('/startup.py','w').write('#!' + '/usr/bin/env python3\\n' + code);print('Created /startup.py')" && \
    chmod +x /startup.py

# Set working directory
WORKDIR /app/backend

# Environment variables
ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# 启动应用
CMD ["/start.sh"]
