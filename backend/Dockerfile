# Backend Development Dockerfile

# UV source image (override for restricted networks that cannot reach ghcr.io)
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.7.20
FROM ${UV_IMAGE} AS uv-source

FROM python:3.12-slim-bookworm

ARG NODE_MAJOR=22
ARG APT_MIRROR

# Optionally override apt mirror for restricted networks (e.g. APT_MIRROR=mirrors.aliyun.com)
RUN if [ -n "${APT_MIRROR}" ]; then \
      sed -i "s|deb.debian.org|${APT_MIRROR}|g" /etc/apt/sources.list.d/debian.sources 2>/dev/null || true; \
      sed -i "s|deb.debian.org|${APT_MIRROR}|g" /etc/apt/sources.list 2>/dev/null || true; \
    fi

# Install system dependencies + Node.js (provides npx for MCP servers)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gnupg \
    ca-certificates \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for DooD: allows starting sandbox containers via host Docker socket)
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker

# Install uv (source image overridable via UV_IMAGE build arg)
COPY --from=uv-source /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy frontend source code
COPY backend ./backend

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    sh -c "cd backend && uv sync"

# Expose ports (gateway: 8001, langgraph: 2024)
EXPOSE 8001 2024

# Copy virtual environment and startup script
COPY --from=builder /app/backend/.venv /app/backend/.venv
COPY start.sh /app/start.sh

# Make startup script executable and create Python startup helper
RUN chmod +x /app/start.sh && \
    python3 -c "code='''import os,sys,subprocess;cfg=os.environ.get(\"DEER_FLOW_CONFIG_PATH\",\"/app/backend/config.yaml\");print(f\"Config: {cfg}\");os.path.exists(cfg) or (print(f\"ERROR: {cfg} not found\"),sys.exit(1));os.environ[\"DEER_FLOW_CONFIG_PATH\"]=cfg;os.chdir(\"/app/backend\");os.execvp(sys.executable,[sys.executable,\"-m\",\"uvicorn\",\"app.gateway.app:app\",\"--host\",\"0.0.0.0\",\"--port\",\"8001\",\"--workers\",\"2\"])''';open('/app/startup.py','w').write('#!' + '/usr/bin/env python3\\n' + code);print('Created /app/startup.py')" && \
    chmod +x /app/startup.py

# Set working directory
WORKDIR /app/backend

# Environment variables
ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8001

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# 启动应用
CMD ["/start.sh"]
