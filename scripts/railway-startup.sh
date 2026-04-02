#!/bin/bash
# Railway 部署后置脚本
# 此脚本在容器启动时运行，用于初始化数据库和环境

set -e

echo "🚀 开始 Railway 部署初始化..."

# 1. 检查环境变量
echo "✓ 检查环境变量..."
if [ -z "$DATABASE_URL" ]; then
    echo "❌ 错误：缺少 DATABASE_URL 环境变量"
    exit 1
fi

if [ -z "$ALIPAY_APPID" ]; then
    echo "❌ 错误：缺少 ALIPAY_APPID 环境变量"
    exit 1
fi

# 2. 等待数据库就绪
echo "✓ 等待数据库连接..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; then
        echo "✅ 数据库已连接"
        break
    fi
    attempt=$((attempt + 1))
    echo "⏳ 等待数据库... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ 数据库连接超时"
    exit 1
fi

# 3. 运行数据库迁移
echo "✓ 运行数据库迁移..."
cd /app/backend
python -m alembic upgrade head || {
    echo "⚠️ 迁移失败，尝试初始化..."
    python -c "from app.models import Base; from app.database import engine; Base.metadata.create_all(bind=engine)"
}

# 4. 初始化多租户数据
echo "✓ 初始化多租户数据..."
python -c "
from app.database import SessionLocal
from app.models.tenant import Tenant
db = SessionLocal()
default_tenant = db.query(Tenant).filter(Tenant.id == 'default').first()
if not default_tenant:
    db.add(Tenant(id='default', name='Default Tenant', is_active=True))
    db.commit()
    print('✅ 默认租户已创建')
else:
    print('✅ 默认租户已存在')
"

# 5. 验证支付宝配置
echo "✓ 验证支付宝配置..."
python -c "
import os
from alipay.aop.api.default.AlipayOpenAuthTokenAppClient import AlipayOpenAuthTokenAppClient

alipay_client = AlipayOpenAuthTokenAppClient(
    app_id=os.getenv('ALIPAY_APPID'),
    private_key=os.getenv('ALIPAY_PRIVATE_KEY'),
    alipay_public_key=os.getenv('ALIPAY_PUBLIC_KEY'),
)
print('✅ 支付宝客户端已初始化')
" || echo "⚠️ 支付宝配置验证失败，但继续启动"

# 6. 启动应用
echo "✅ 初始化完成，启动应用..."
exec python -m app.gateway.main
