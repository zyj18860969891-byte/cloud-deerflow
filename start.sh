#!/bin/bash
set -e

echo "🚀 开始启动 DeerFlow..."

# 检查必需的环境变量
if [ -z "$DATABASE_URL" ]; then
    echo "❌ 错误：缺少 DATABASE_URL"
    exit 1
fi

# 设置端口（Railway 会覆盖这个）
export PORT=${PORT:-8080}

# 设置配置文件路径 - 尝试多个位置
if [ -f "/app/backend/config.yaml" ]; then
    export DEER_FLOW_CONFIG_PATH="/app/backend/config.yaml"
    echo "✅ 使用配置文件: /app/backend/config.yaml"
elif [ -f "/app/config.yaml" ]; then
    export DEER_FLOW_CONFIG_PATH="/app/config.yaml"
    echo "✅ 使用配置文件: /app/config.yaml"
else
    echo "⚠️  警告：未找到 config.yaml，应用将尝试自动查找"
fi

echo "✅ 环境变量已验证"
echo "   PORT: $PORT"
echo "   DATABASE_URL: [已设置]"
echo "   DEER_FLOW_CONFIG_PATH: ${DEER_FLOW_CONFIG_PATH:-[未设置]}"

# 进入后端目录
cd /app/backend || { echo "❌ 无法进入 /app/backend"; exit 1; }
echo "📂 当前目录：$(pwd)"

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 启动应用
WORKERS=${WORKERS:-4}
echo "🎯 启动 FastAPI 应用..."
echo "   主机：0.0.0.0"
echo "   端口：$PORT"
echo "   工作进程：$WORKERS"

exec python -m uvicorn app.gateway.app:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info
