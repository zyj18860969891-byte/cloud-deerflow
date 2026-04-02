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

# Copy virtual environment from builder
COPY --from=builder /app/backend/.venv /app/backend/.venv

# Copy start script from project root
COPY start.sh /app/start.sh

# Set working directory
WORKDIR /app/backend

# Make start script executable
RUN chmod +x /app/start.sh

# Environment variables
ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8001 \
    WORKERS=4 \
    ENVIRONMENT=production

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE 8001

# Run start script
CMD ["bash", "/app/start.sh"]
