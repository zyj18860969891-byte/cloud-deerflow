"""
缓存管理器

统一的缓存接口，支持 Redis 和内存缓存
"""

import logging
from typing import Any

try:
    import aioredis
except ImportError:
    aioredis = None

from deerflow.cache.config import CacheConfig
from deerflow.cache.memory_cache import _DEFAULT, MemoryCache

logger = logging.getLogger(__name__)


class CacheManager:
    """统一的缓存管理器"""

    def __init__(self, config: CacheConfig):
        """初始化缓存管理器

        Args:
            config: 缓存配置
        """
        self.config = config
        self.redis_client = None
        self.memory_cache = None
        self.is_ready = False

    async def initialize(self) -> None:
        """初始化缓存管理器"""
        logger.info("初始化缓存管理器...")

        try:
            # 初始化内存缓存
            if self.config.is_memory_cache_enabled():
                self.memory_cache = MemoryCache(self.config.memory)
                logger.info("内存缓存已初始化")

            # 初始化 Redis 连接
            if self.config.is_redis_enabled():
                if aioredis is None:
                    logger.warning("aioredis 未安装，Redis 缓存将被禁用")
                else:
                    try:
                        self.redis_client = await aioredis.create_redis_pool(
                            f"redis://{self.config.redis.host}:{self.config.redis.port}",
                            db=self.config.redis.db,
                            password=self.config.redis.password,
                            minsize=1,
                            maxsize=self.config.redis.max_connections,
                        )
                        logger.info("Redis 连接已建立")
                    except Exception as e:
                        logger.error(f"无法连接到 Redis: {e}")
                        self.redis_client = None

            self.is_ready = True
            logger.info("缓存管理器初始化完成")
        except Exception as e:
            logger.error(f"缓存管理器初始化失败: {e}")
            raise

    async def shutdown(self) -> None:
        """关闭缓存管理器"""
        logger.info("关闭缓存管理器...")

        if self.redis_client:
            self.redis_client.close()
            await self.redis_client.wait_closed()
            logger.info("Redis 连接已关闭")

        if self.memory_cache:
            await self.memory_cache.clear()
            logger.info("内存缓存已清空")

    async def get(self, key: str) -> Any | None:
        """获取缓存值

        优先尝试 Redis，回退到内存缓存

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在则返回 None
        """
        if not self.is_ready:
            return None

        # 尝试从 Redis 获取
        if self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value is not None:
                    logger.debug(f"Redis 缓存命中: {key}")
                    return value
            except Exception as e:
                logger.warning(f"Redis 获取失败 {key}: {e}")

        # 回退到内存缓存
        if self.memory_cache:
            value = await self.memory_cache.get(key)
            if value is not None:
                logger.debug(f"内存缓存命中: {key}")
                return value

        logger.debug(f"缓存未命中: {key}")
        return None

    async def set(self, key: str, value: Any, ttl: Any = _DEFAULT) -> None:
        """设置缓存值

        同时写入 Redis 和内存缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示永不过期，不传递表示使用配置的默认值
        """
        if not self.is_ready:
            return

        # 确定有效的 TTL 值
        if ttl is _DEFAULT:
            effective_ttl = self.config.redis.default_ttl
        else:
            effective_ttl = ttl or self.config.redis.default_ttl

        # 写入 Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(key, effective_ttl, value)
                logger.debug(f"Redis 缓存已设置: {key}")
            except Exception as e:
                logger.warning(f"Redis 设置失败 {key}: {e}")

        # 写入内存缓存
        if self.memory_cache:
            await self.memory_cache.set(key, value, ttl)
            logger.debug(f"内存缓存已设置: {key}")

    async def delete(self, key: str) -> None:
        """删除缓存项

        同时从 Redis 和内存缓存中删除

        Args:
            key: 缓存键
        """
        if not self.is_ready:
            return

        # 从 Redis 删除
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
                logger.debug(f"Redis 缓存已删除: {key}")
            except Exception as e:
                logger.warning(f"Redis 删除失败 {key}: {e}")

        # 从内存缓存删除
        if self.memory_cache:
            await self.memory_cache.delete(key)
            logger.debug(f"内存缓存已删除: {key}")

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的所有缓存项

        Args:
            pattern: 键模式（支持通配符 *）

        Returns:
            删除的项数
        """
        if not self.is_ready:
            return 0

        deleted = 0

        # 从 Redis 删除
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    deleted = len(keys)
                    logger.debug(f"Redis 删除 {deleted} 个匹配项: {pattern}")
            except Exception as e:
                logger.warning(f"Redis 模式删除失败 {pattern}: {e}")

        # 从内存缓存删除（需要遍历）
        if self.memory_cache:
            import fnmatch

            keys_to_delete = []
            entries = await self.memory_cache.get_entries()

            for key in entries:
                if fnmatch.fnmatch(key, pattern):
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                await self.memory_cache.delete(key)
                deleted = len(keys_to_delete)

            if deleted > 0:
                logger.debug(f"内存缓存删除 {deleted} 个匹配项: {pattern}")

        return deleted

    async def clear(self) -> None:
        """清空所有缓存"""
        if not self.is_ready:
            return

        logger.info("清空所有缓存...")

        # 清空 Redis
        if self.redis_client:
            try:
                await self.redis_client.flushdb()
                logger.info("Redis 已清空")
            except Exception as e:
                logger.warning(f"Redis 清空失败: {e}")

        # 清空内存缓存
        if self.memory_cache:
            await self.memory_cache.clear()
            logger.info("内存缓存已清空")

    async def exists(self, key: str) -> bool:
        """检查缓存项是否存在

        Args:
            key: 缓存键

        Returns:
            如果存在则返回 True
        """
        if not self.is_ready:
            return False

        # 检查 Redis
        if self.redis_client:
            try:
                exists = await self.redis_client.exists(key)
                if exists:
                    return True
            except Exception as e:
                logger.warning(f"Redis 存在性检查失败 {key}: {e}")

        # 检查内存缓存
        if self.memory_cache:
            return await self.memory_cache.exists(key)

        return False

    async def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "enabled": self.config.enabled,
            "redis": {"enabled": False, "stats": {}},
            "memory": {"enabled": False, "stats": {}},
        }

        # Redis 统计
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats["redis"] = {
                    "enabled": True,
                    "stats": {
                        "used_memory": info.get("used_memory", 0),
                        "used_memory_human": info.get("used_memory_human", ""),
                        "connected_clients": info.get("connected_clients", 0),
                    },
                }
            except Exception as e:
                logger.warning(f"获取 Redis 统计失败: {e}")

        # 内存缓存统计
        if self.memory_cache:
            stats["memory"] = {
                "enabled": True,
                "stats": await self.memory_cache.get_stats(),
            }

        return stats

    def get_stats_sync(self) -> dict[str, Any]:
        """同步获取缓存统计信息（用于指标收集）

        Returns:
            统计信息字典（不包含 Redis 异步信息）
        """
        stats = {
            "enabled": self.config.enabled,
            "memory": {"enabled": False, "stats": {}},
        }

        # 内存缓存统计（同步访问）
        if self.memory_cache:
            # 注意：这是同步调用，需要确保 memory_cache 的方法在同步上下文中安全
            # 由于 memory_cache 使用 asyncio.Lock，这里我们直接访问内部状态
            # 这应该在指标收集器的上下文中使用，该上下文在事件循环中运行
            with self.memory_cache.lock:
                total_requests = self.memory_cache.hits + self.memory_cache.misses
                hit_rate = self.memory_cache.hits / total_requests if total_requests > 0 else 0
                memory_usage = sum(len(str(entry.value)) for entry in self.memory_cache.cache.values())

                stats["memory"] = {
                    "enabled": True,
                    "stats": {
                        "size": len(self.memory_cache.cache),
                        "max_size": self.memory_cache.config.max_size,
                        "hits": self.memory_cache.hits,
                        "misses": self.memory_cache.misses,
                        "hit_rate": hit_rate,
                        "evictions": self.memory_cache.evictions,
                        "estimated_memory_bytes": memory_usage,
                        "eviction_policy": self.memory_cache.config.eviction_policy,
                    },
                }

        return stats

    async def cleanup_expired(self) -> int:
        """清理过期的缓存项

        Returns:
            清理的项数
        """
        cleaned = 0

        if self.memory_cache:
            cleaned = await self.memory_cache.cleanup_expired()
            logger.info(f"清理了 {cleaned} 个过期的内存缓存项")

        return cleaned


# 全局缓存管理器实例
_cache_manager: CacheManager | None = None


async def get_cache_manager(config: CacheConfig | None = None) -> CacheManager:
    """获取全局缓存管理器实例

    Args:
        config: 缓存配置（仅在第一次调用时使用）

    Returns:
        缓存管理器实例
    """
    global _cache_manager

    if _cache_manager is None:
        if config is None:
            from deerflow.cache.config import DEFAULT_CACHE_CONFIG

            config = DEFAULT_CACHE_CONFIG

        _cache_manager = CacheManager(config)
        await _cache_manager.initialize()

    return _cache_manager


async def shutdown_cache_manager() -> None:
    """关闭全局缓存管理器"""
    global _cache_manager

    if _cache_manager:
        await _cache_manager.shutdown()
        _cache_manager = None
