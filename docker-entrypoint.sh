#!/bin/bash
set -e

# 设置配置文件路径
export DEER_FLOW_CONFIG_PATH=/app/backend/config.yaml
export PYTHONPATH=/app/backend:$PYTHONPATH

# 验证配置文件存在
if [ ! -f "$DEER_FLOW_CONFIG_PATH" ]; then
    echo "❌ 错误：找不到配置文件 $DEER_FLOW_CONFIG_PATH"
    exit 1
fi

echo "✅ 配置文件已找到: $DEER_FLOW_CONFIG_PATH"
echo "🚀 启动 FastAPI 应用..."

# 启动应用
cd /app/backend
exec python -m uvicorn app.gateway.app:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 4 \
    --log-level info
