"""
缓存系统配置模块

提供 Redis、内存缓存的配置定义
"""

from pydantic import BaseModel, ConfigDict, Field


class RedisCacheConfig(BaseModel):
    """Redis 缓存配置"""

    enabled: bool = Field(default=True, description="是否启用 Redis 缓存")
    host: str = Field(default="localhost", description="Redis 主机")
    port: int = Field(default=6379, description="Redis 端口")
    db: int = Field(default=0, description="Redis 数据库索引")
    password: str | None = Field(default=None, description="Redis 密码")
    default_ttl: int = Field(default=3600, description="默认 TTL（秒），1 小时")
    max_connections: int = Field(default=10, description="最大连接数")
    socket_timeout: float = Field(default=5.0, description="socket 超时（秒）")
    socket_connect_timeout: float = Field(default=5.0, description="连接超时（秒）")

    model_config = ConfigDict(frozen=False)


class MemoryCacheConfig(BaseModel):
    """内存缓存配置"""

    enabled: bool = Field(default=True, description="是否启用内存缓存")
    max_size: int = Field(default=1000, description="最大缓存项数（LRU 驱逐）")
    default_ttl: int = Field(default=300, description="默认 TTL（秒），5 分钟")
    eviction_policy: str = Field(
        default="lru",
        description="驱逐策略：lru（最近最少使用）、fifo（先进先出）",
    )

    model_config = ConfigDict(frozen=False)


class CacheWarmingConfig(BaseModel):
    """缓存预热配置"""

    enabled: bool = Field(default=True, description="是否启用缓存预热")
    on_startup: bool = Field(default=True, description="应用启动时预热")
    periodic: bool = Field(default=True, description="定期预热")
    periodic_interval: int = Field(default=3600, description="定期预热间隔（秒），1 小时")
    warmup_timeout: float = Field(default=10.0, description="预热超时时间（秒）")

    model_config = ConfigDict(frozen=False)


class CacheInvalidationConfig(BaseModel):
    """缓存失效策略配置"""

    ttl_variance: float = Field(
        default=0.1,
        description="TTL 方差（0-1），减少缓存雪崩：ttl * (1 ± variance)",
    )
    use_soft_delete: bool = Field(default=True, description="使用软删除策略（逻辑过期）")
    enable_lockout: bool = Field(default=True, description="启用击穿保护（互斥锁）")
    lockout_timeout: float = Field(default=5.0, description="锁定超时时间（秒）")

    model_config = ConfigDict(frozen=False)


class CacheMetricsConfig(BaseModel):
    """缓存指标配置"""

    enabled: bool = Field(default=True, description="是否启用缓存指标收集")
    track_hits_misses: bool = Field(default=True, description="是否追踪命中/未命中")
    track_latency: bool = Field(default=True, description="是否追踪延迟")
    track_memory: bool = Field(default=True, description="是否追踪内存使用")
    report_interval: int = Field(default=60, description="指标报告间隔（秒）")

    model_config = ConfigDict(frozen=False)


class CacheKeyConfig(BaseModel):
    """缓存键配置"""

    prefix: str = Field(default="deerflow", description="所有缓存键的前缀")
    separator: str = Field(default=":", description="键部分的分隔符")

    # 各类缓存键的前缀
    tenants_prefix: str = Field(default="tenants", description="租户缓存前缀")
    agents_prefix: str = Field(default="agents", description="Agent 缓存前缀")
    skills_prefix: str = Field(default="skills", description="技能缓存前缀")
    memory_prefix: str = Field(default="memory", description="内存数据缓存前缀")
    mcp_prefix: str = Field(default="mcp", description="MCP 缓存前缀")
    threads_prefix: str = Field(default="threads", description="线程数据缓存前缀")

    model_config = ConfigDict(frozen=False)

    def build_key(self, *parts: str) -> str:
        """构建缓存键

        Args:
            *parts: 键的各个部分

        Returns:
            完整的缓存键
        """
        all_parts = [self.prefix] + list(parts)
        return self.separator.join(all_parts)

    def build_tenant_key(self, tenant_id: str, *parts: str) -> str:
        """构建租户相关的缓存键"""
        return self.build_key(self.tenants_prefix, tenant_id, *parts)

    def build_agent_key(self, agent_id: str, *parts: str) -> str:
        """构建 Agent 相关的缓存键"""
        return self.build_key(self.agents_prefix, agent_id, *parts)

    def build_skill_key(self, skill_name: str, *parts: str) -> str:
        """构建技能相关的缓存键"""
        return self.build_key(self.skills_prefix, skill_name, *parts)

    def build_memory_key(self, query_hash: str, *parts: str) -> str:
        """构建内存数据相关的缓存键"""
        return self.build_key(self.memory_prefix, query_hash, *parts)

    def build_mcp_key(self, mcp_name: str, *parts: str) -> str:
        """构建 MCP 相关的缓存键"""
        return self.build_key(self.mcp_prefix, mcp_name, *parts)

    def build_thread_key(self, thread_id: str, *parts: str) -> str:
        """构建线程相关的缓存键"""
        return self.build_key(self.threads_prefix, thread_id, *parts)


class CacheTTLConfig(BaseModel):
    """各类数据的 TTL 配置（秒）"""

    # 短期数据（几分钟）
    short_term: int = Field(default=300, description="短期缓存 TTL（5 分钟）")

    # 中期数据（半小时）
    medium_term: int = Field(default=1800, description="中期缓存 TTL（30 分钟）")

    # 长期数据（1 小时）
    long_term: int = Field(default=3600, description="长期缓存 TTL（1 小时）")

    # 超长期数据（1 天）
    very_long_term: int = Field(default=86400, description="超长期缓存 TTL（1 天）")

    # 具体业务数据 TTL
    tenants_ttl: int = Field(default=1800, description="租户数据 TTL（30 分钟）")
    agents_ttl: int = Field(default=600, description="Agent 数据 TTL（10 分钟）")
    skills_ttl: int = Field(default=3600, description="技能数据 TTL（1 小时）")
    memory_ttl: int = Field(default=300, description="内存数据 TTL（5 分钟）")
    mcp_ttl: int = Field(default=1800, description="MCP 数据 TTL（30 分钟）")
    threads_ttl: int = Field(default=600, description="线程数据 TTL（10 分钟）")

    model_config = ConfigDict(frozen=False)


class CacheConfig(BaseModel):
    """全局缓存配置"""

    # 各个缓存类型的配置
    redis: RedisCacheConfig = Field(default_factory=RedisCacheConfig)
    memory: MemoryCacheConfig = Field(default_factory=MemoryCacheConfig)
    warming: CacheWarmingConfig = Field(default_factory=CacheWarmingConfig)
    invalidation: CacheInvalidationConfig = Field(default_factory=CacheInvalidationConfig)
    metrics: CacheMetricsConfig = Field(default_factory=CacheMetricsConfig)
    keys: CacheKeyConfig = Field(default_factory=CacheKeyConfig)
    ttls: CacheTTLConfig = Field(default_factory=CacheTTLConfig)

    # 全局设置
    enabled: bool = Field(default=True, description="是否启用整个缓存系统")
    environment: str = Field(
        default="development",
        description="环境（development、staging、production）",
    )

    model_config = ConfigDict(frozen=False)

    def is_redis_enabled(self) -> bool:
        """Redis 是否启用"""
        return self.enabled and self.redis.enabled

    def is_memory_cache_enabled(self) -> bool:
        """内存缓存是否启用"""
        return self.enabled and self.memory.enabled

    def should_warm_on_startup(self) -> bool:
        """应该在启动时预热缓存"""
        return self.enabled and self.warming.enabled and self.warming.on_startup

    def should_warm_periodically(self) -> bool:
        """应该定期预热缓存"""
        return self.enabled and self.warming.enabled and self.warming.periodic


# 默认配置实例
DEFAULT_CACHE_CONFIG = CacheConfig()


def get_cache_config(environment: str | None = None) -> CacheConfig:
    """获取缓存配置

    Args:
        environment: 环境名称（可选）

    Returns:
        缓存配置实例
    """
    config = CacheConfig()

    if environment:
        config.environment = environment

        # 按环境调整配置
        if environment == "development":
            # 开发环境：短 TTL，小缓存
            config.memory.max_size = 500
            config.memory.default_ttl = 60
            config.redis.enabled = False
        elif environment == "production":
            # 生产环境：长 TTL，大缓存
            config.memory.max_size = 10000
            config.memory.default_ttl = 600
            config.redis.enabled = True

    return config
