#!/usr/bin/env python3
"""
DeerFlow 生产配置文件生成工具
自动生成生产环境所需的配置文件
"""

import os
import sys
import json
import secrets
import argparse
from pathlib import Path
from datetime import datetime

class ProductionConfigGenerator:
    """生产配置文件生成器"""

    def __init__(self, repo_root: str = None, data_dir: str = None):
        self.repo_root = Path(repo_root or os.getenv('DEER_FLOW_REPO_ROOT', '/opt/deer-flow'))
        self.data_dir = Path(data_dir or os.getenv('DEER_FLOW_HOME', '/data/deer-flow/.deer-flow'))

    def generate_env_production(self, output_path: Path = None) -> str:
        """生成 .env.production 文件"""
        if output_path is None:
            output_path = self.repo_root / ".env.production"

        print(f"🔧 生成 .env.production 文件...")

        # 生成安全的密钥
        auth_secret = secrets.token_hex(32)

        env_content = f"""# DeerFlow 生产环境配置
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 重要：请根据实际情况修改以下配置项

# ============================================================================
# 认证配置（必须修改！）
# ============================================================================
BETTER_AUTH_SECRET={auth_secret}

# ============================================================================
# LLM API Keys（必须填写）
# ============================================================================
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
# 可选：其他提供商
# GOOGLE_API_KEY=your-google-api-key
# DEEPSEEK_API_KEY=your-deepseek-api-key
# OPENROUTER_API_KEY=your-openrouter-api-key

# ============================================================================
# 数据库配置（生产环境建议使用PostgreSQL）
# ============================================================================
# 如果使用Docker Compose部署，这些值会覆盖docker-compose中的配置
DB_HOST=postgres
DB_PORT=5432
DB_NAME=deerflow
DB_USER=deerflow
DB_PASSWORD=your-secure-db-password-change-this

# ============================================================================
# Redis 配置（用于缓存和会话）
# ============================================================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# ============================================================================
# 多租户配置
# ============================================================================
DEER_FLOW_MULTI_TENANT_ENABLED=true
DEER_FLOW_TENANT_ISOLATION_LEVEL=strict

# ============================================================================
# 服务端点配置
# ============================================================================
DEER_FLOW_CHANNELS_LANGGRAPH_URL=http://langgraph:2024
DEER_FLOW_CHANNELS_GATEWAY_URL=http://gateway:8001

# ============================================================================
# 路径配置
# ============================================================================
DEER_FLOW_HOME=/data/deer-flow/.deer-flow
DEER_FLOW_CONFIG_PATH=/app/backend/config.yaml
DEER_FLOW_EXTENSIONS_CONFIG_PATH=/data/deer-flow/.deer-flow/extensions_config.json
DEER_FLOW_REPO_ROOT=/opt/deer-flow
DEER_FLOW_DOCKER_SOCKET=/var/run/docker.sock

# ============================================================================
# 性能调优
# ============================================================================
WEB_CONCURRENCY=4
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
CACHE_TTL=3600
ENABLE_QUERY_CACHE=true

# ============================================================================
# 监控和日志
# ============================================================================
LOG_LEVEL=INFO
# LANGSMITH_TRACING=false
# LANGSMITH_API_KEY=

# ============================================================================
# 安全配置
# ============================================================================
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

# ============================================================================
# 通道配置（可选）
# ============================================================================
# FEISHU_APP_ID=
# FEISHU_APP_SECRET=
# SLACK_BOT_TOKEN=
# SLACK_APP_TOKEN=
# TELEGRAM_BOT_TOKEN=

# ============================================================================
# 邮件通知（可选）
# ============================================================================
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=
# SMTP_PASSWORD=
# NOTIFICATION_FROM=

# ============================================================================
# 备份配置
# ============================================================================
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=0 2 * * *

# ============================================================================
# 租户特定配置
# ============================================================================
DEFAULT_TENANT_MAX_THREADS=1000
DEFAULT_TENANT_MAX_MESSAGES_PER_THREAD=10000
DEFAULT_TENANT_MAX_API_CALLS_PER_DAY=100000
DEFAULT_TENANT_MAX_CONCURRENT_REQUESTS=50

# ============================================================================
# Docker配置
# ============================================================================
PORT=2026
COMPOSE_PROJECT_NAME=deer-flow
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(env_content)

        print(f"✅ .env.production 已生成: {output_path}")
        print("⚠️  请立即编辑此文件，填写实际的API密钥和配置！")

        return str(output_path)

    def generate_extensions_config(self, output_path: Path = None) -> str:
        """生成 extensions_config.json 文件"""
        if output_path is None:
            output_path = self.repo_root / "extensions_config.json"

        print(f"🔧 生成 extensions_config.json 文件...")

        config = {
            "mcpServers": {},
            "skills": {
                "enabled": True,
                "auto_install": False
            },
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✅ extensions_config.json 已生成: {output_path}")

        return str(output_path)

    def generate_nginx_config(self, output_path: Path = None, domain: str = "deerflow.example.com") -> str:
        """生成 Nginx 配置文件"""
        if output_path is None:
            output_path = self.repo_root / "docker" / "nginx" / "nginx.conf"

        print(f"🔧 生成 Nginx 配置文件...")

        nginx_config = f"""events {{
    worker_connections 1024;
}}

http {{
    # 上游服务器
    upstream backend {{
        server gateway:8001;
    }}

    upstream frontend {{
        server frontend:3000;
    }}

    # HTTP 重定向到 HTTPS
    server {{
        listen 80;
        server_name {domain};
        return 301 https://$host$request_uri;
    }}

    # HTTPS 服务器（需要SSL证书）
    server {{
        listen 443 ssl http2;
        server_name {domain};

        # SSL 证书（需要提前配置）
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # SSL 安全设置
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # 限流配置
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
        limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

        # API 路由到后端
        location /api/ {{
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket 支持
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";

            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }}

        # 登录接口限流更严格
        location /api/auth/login {{
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        # 前端路由
        location / {{
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 静态文件缓存
            proxy_cache STATIC;
            proxy_cache_valid 200 1h;
            proxy_cache_redirect_static on;
        }}

        # 健康检查
        location /health {{
            access_log off;
            proxy_pass http://backend/health;
            add_header Content-Type text/plain;
        }}

        # 机器人爬虫限制
        location ~* \\.(jpg|jpeg|png|gif|ico|css|js)$ {{
            expires 30d;
            add_header Cache-Control "public, immutable";
        }}
    }}
}}
"""

        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(nginx_config)

        print(f"✅ Nginx 配置已生成: {output_path}")
        print("⚠️  注意：需要提前配置SSL证书才能启用HTTPS")

        return str(output_path)

    def generate_all_configs(self, domain: str = "deerflow.example.com") -> Dict[str, str]:
        """生成所有配置文件"""
        print("=" * 60)
        print("🚀 DeerFlow 生产配置文件生成工具")
        print("=" * 60)
        print(f"仓库根目录: {self.repo_root}")
        print(f"数据目录: {self.data_dir}")
        print(f"域名: {domain}")
        print()

        generated_files = {}

        # 生成配置文件
        generated_files["env_production"] = self.generate_env_production()
        generated_files["extensions_config"] = self.generate_extensions_config()
        generated_files["nginx_config"] = self.generate_nginx_config(domain=domain)

        print("\n" + "=" * 60)
        print("✅ 配置文件生成完成！")
        print("=" * 60)

        print("\n📋 生成的文件:")
        for name, path in generated_files.items():
            print(f"  • {name}: {path}")

        print("\n📝 后续步骤:")
        print("1. 编辑 .env.production 文件，填写所有必需的API密钥和配置")
        print("2. 配置SSL证书到 docker/nginx/ssl/ 目录")
        print("3. 根据实际域名修改 nginx.conf 中的 server_name")
        print("4. 运行部署验证: python scripts/deploy_validator.py")
        print("5. 启动服务: docker-compose -f docker/docker-compose.yaml up -d")

        return generated_files

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DeerFlow 生产配置文件生成工具")
    parser.add_argument("--repo-root", default="/opt/deer-flow",
                       help="仓库根目录路径 (默认: /opt/deer-flow)")
    parser.add_argument("--data-dir", default="/data/deer-flow/.deer-flow",
                       help="数据目录路径 (默认: /data/deer-flow/.deer-flow)")
    parser.add_argument("--domain", default="deerflow.example.com",
                       help="生产域名 (默认: deerflow.example.com)")

    args = parser.parse_args()

    generator = ProductionConfigGenerator(
        repo_root=args.repo_root,
        data_dir=args.data_dir
    )

    generator.generate_all_configs(domain=args.domain)

if __name__ == "__main__":
    main()