#!/bin/bash
set -e

echo "🚀 开始启动 DeerFlow..."

# 1. 检查环境变量
if [ -z "$DATABASE_URL" ]; then
    echo "❌ 错误：缺少 DATABASE_URL"
    exit 1
fi

if [ -z "$PORT" ]; then
    export PORT=8001
fi

echo "✅ 环境变量已验证"
echo "   PORT: $PORT"
echo "   DATABASE_URL: [已设置]"

# 2. 进入后端目录（在容器中 /app/backend 是工作目录）
if [ -d "/app/backend" ]; then
    cd /app/backend
elif [ -d "backend" ]; then
    cd backend
else
    echo "❌ 错误：无法找到后端目录"
    exit 1
fi

echo "📂 当前目录：$(pwd)"

# 3. 虚拟环境已在构建时创建，激活它
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ 虚拟环境已激活"
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️  虚拟环境未找到，继续..."
fi

# 4. 激活虚拟环境（使用绝对路径）
if [ -f "/app/backend/.venv/bin/activate" ]; then
    source /app/backend/.venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 5. 运行数据库迁移（可选，失败则继续）
echo "🗄️  检查数据库..."
python -c "import sqlalchemy; print('✅ SQLAlchemy 可用')" 2>/dev/null || echo "⚠️  数据库驱动检查失败"

# 6. 启动应用
PORT=${PORT:-8001}
WORKERS=${WORKERS:-4}

echo "🎯 启动 FastAPI 应用..."
echo "   主机：0.0.0.0"
echo "   端口：$PORT"
echo "   工作进程：$WORKERS"

exec python -m uvicorn app.gateway.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info
