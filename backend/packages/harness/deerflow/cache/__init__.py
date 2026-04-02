"""
缓存模块

提供 Redis + 内存缓存的集成解决方案
"""

from deerflow.cache.cache import (
    CacheManager,
    get_cache_manager,
    shutdown_cache_manager,
)
from deerflow.cache.cache_metrics import (
    CacheMetrics,
    MetricsCollector,
    get_cache_metrics,
    shutdown_cache_metrics,
)
from deerflow.cache.cache_warmer import (
    CacheWarmer,
    get_cache_warmer,
    shutdown_cache_warmer,
)
from deerflow.cache.config import (
    CacheConfig,
    CacheInvalidationConfig,
    CacheKeyConfig,
    CacheTTLConfig,
    MemoryCacheConfig,
    RedisCacheConfig,
    get_cache_config,
)
from deerflow.cache.memory_cache import MemoryCache

__all__ = [
    # 配置类
    "CacheConfig",
    "RedisCacheConfig",
    "MemoryCacheConfig",
    "CacheInvalidationConfig",
    "CacheKeyConfig",
    "CacheTTLConfig",
    # 缓存实现
    "MemoryCache",
    "CacheManager",
    "CacheWarmer",
    "CacheMetrics",
    "MetricsCollector",
    # 工厂函数
    "get_cache_config",
    "get_cache_manager",
    "shutdown_cache_manager",
    "get_cache_warmer",
    "shutdown_cache_warmer",
    "get_cache_metrics",
    "shutdown_cache_metrics",
]
