"""
主应用配置

整合所有子系统的配置
"""

import os

from pydantic import BaseModel, Field

from deerflow.cache.config import CacheConfig as DeerflowCacheConfig


class DatabaseConfig(BaseModel):
    """数据库配置"""

    url: str = Field(default="sqlite+aiosqlite:///deerflow.db", description="数据库连接 URL（支持 postgresql+asyncpg 或 sqlite+aiosqlite）")
    echo: bool = Field(default=False, description="是否输出 SQL 日志")
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="最大溢出连接数")
    auto_create_tables: bool = Field(default=True, description="启动时自动创建表")


class AppConfig(BaseModel):
    """主应用配置"""

    # 网关配置
    gateway_host: str = Field(default="0.0.0.0", description="网关监听地址")
    gateway_port: int = Field(default=8001, description="网关监听端口")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], description="允许的 CORS 源")

    # 数据库配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    # 缓存配置
    cache: DeerflowCacheConfig = Field(default_factory=DeerflowCacheConfig)

    # 工具管理配置
    tools_enabled: bool = Field(default=True, description="是否启用工具管理功能")
    tools_allow_custom: bool = Field(default=True, description="是否允许自定义工具")
    tools_max_custom_per_tenant: int = Field(default=10, description="每个租户最大自定义工具数")

    # 安全配置
    enable_rate_limiting: bool = Field(default=True, description="启用速率限制")
    rate_limit_requests_per_minute: int = Field(default=60, description="每分钟请求数限制")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式（json 或 text）")

    model_config = {"env_prefix": "DEERFLOW_"}


# 全局配置实例
_app_config: AppConfig | None = None


def get_app_config() -> AppConfig:
    """获取主应用配置

    Returns:
        应用配置实例
    """
    global _app_config

    if _app_config is None:
        # 从环境变量加载
        database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

        # 如果环境变量中没有完整配置，使用默认值
        if not database_url:
            database_url = "sqlite+aiosqlite:///:memory:"

        _app_config = AppConfig(
            gateway_host=os.getenv("GATEWAY_HOST", "0.0.0.0"),
            gateway_port=int(os.getenv("GATEWAY_PORT", "8001")),
            cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
            database=DatabaseConfig(
                url=database_url,
                echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
                pool_size=int(os.getenv("DATABASE_POOL_SIZE", "5")),
                max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "10")),
                auto_create_tables=os.getenv("DATABASE_AUTO_CREATE", "true").lower() == "true",
            ),
            # 缓存配置从 deerflow.cache.config 获取
            cache=DeerflowCacheConfig(),
        )

    return _app_config


def get_gateway_config():
    """获取网关配置（从主配置中提取）"""
    app_config = get_app_config()
    return {
        "host": app_config.gateway_host,
        "port": app_config.gateway_port,
        "cors_origins": app_config.cors_origins,
    }
