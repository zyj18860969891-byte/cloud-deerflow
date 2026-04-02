#!/usr/bin/env python3
"""
Railway 启动脚本 - 处理配置文件和环境变量
"""

import os
import sys
from pathlib import Path

# 先验证并设置配置文件路径
print("🔍 寻找 config.yaml...")

config_path = None
for possible_path in [
    '/app/backend/config.yaml',
    '/app/config.yaml',
    '/root/config.yaml',
    'config.yaml',
    '../config.yaml'
]:
    p = Path(possible_path)
    if p.exists():
        config_path = p.resolve()
        print(f"✅ 找到: {config_path}")
        break

if not config_path:
    print("❌ 未找到 config.yaml！检查以下位置：")
    os.system("find / -name 'config.yaml' 2>/dev/null | head -10")
    sys.exit(1)

# 设置环境变量
os.environ['DEER_FLOW_CONFIG_PATH'] = str(config_path)
os.environ['PYTHONPATH'] = '/app/backend:' + os.environ.get('PYTHONPATH', '')

print(f"✅ 环境变量 DEER_FLOW_CONFIG_PATH={os.environ['DEER_FLOW_CONFIG_PATH']}")
print(f"✅ 环境变量 PYTHONPATH={os.environ.get('PYTHONPATH')}")

# 在启动 uvicorn 之前，预加载配置以验证
print("🔐 验证配置...")
try:
    # 切换到 backend 目录
    os.chdir('/app/backend')
    sys.path.insert(0, '/app/backend')
    
    # 现在尝试导入和加载配置
    from deerflow.config.app_config import get_app_config
    config = get_app_config()
    print("✅ 配置加载成功")
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🚀 启动 Uvicorn...")

# 现在启动应用
os.execvp('python', [
    'python', '-m', 'uvicorn',
    'app.gateway.app:app',
    '--host', '0.0.0.0',
    '--port', '8080',
    '--workers', '4',
    '--log-level', 'info'
])
