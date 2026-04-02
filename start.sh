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

# 2. 进入后端目录
cd backend || { echo "❌ 错误：无法进入 backend 目录"; exit 1; }

echo "📂 当前目录：$(pwd)"

# 3. 安装 Python 依赖（使用 uv）
if command -v uv &> /dev/null; then
    echo "📦 使用 uv 安装依赖..."
    uv sync --frozen || {
        echo "⚠️  uv sync 失败，使用 pip..."
        pip install -r requirements.txt
    }
else
    echo "📦 使用 pip 安装依赖..."
    pip install -r requirements.txt || {
        echo "⚠️  pip install 失败，继续..."
    }
fi

# 4. 运行数据库迁移
echo "🗄️  运行数据库迁移..."
python -m alembic upgrade head 2>&1 || {
    echo "⚠️  数据库迁移失败或已完成，继续启动应用..."
}

# 5. 初始化多租户（如果需要）
echo "👥 检查多租户初始化..."
python -c "
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 检查默认租户
    from app.models import Tenant
    default = session.query(Tenant).filter(Tenant.id == 'default').first()
    if not default:
        session.add(Tenant(id='default', name='Default Tenant', is_active=True))
        session.commit()
        print('✅ 默认租户已创建')
    else:
        print('✅ 默认租户已存在')
    session.close()
except Exception as e:
    print(f'⚠️  租户初始化失败或不需要：{e}')
" 2>&1 || echo "⚠️  多租户初始化跳过"

# 6. 启动应用
echo "🎯 启动 FastAPI 应用..."
echo "   主机：0.0.0.0"
echo "   端口：$PORT"
echo "   工作进程：${WORKERS:-4}"

WORKERS=${WORKERS:-4}
python -m uvicorn app.gateway.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level info
