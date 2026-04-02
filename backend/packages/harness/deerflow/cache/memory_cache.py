"""
内存缓存实现模块

提供 LRU 和 TTL 支持的本地进程内缓存
"""

import asyncio
import time
from collections import OrderedDict
from typing import Any

from deerflow.cache.config import MemoryCacheConfig

# 哨兵值，用于表示"使用默认 TTL"
_DEFAULT = object()


class CacheEntry:
    """缓存项"""

    def __init__(self, value: Any, ttl: int | None = None):
        """初始化缓存项

        Args:
            value: 缓存的值
            ttl: 过期时间（秒），None 表示永不过期
        """
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.last_accessed = self.created_at
        self.access_count = 0

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def access(self) -> Any:
        """记录访问并返回值"""
        self.last_accessed = time.time()
        self.access_count += 1
        return self.value

    def get_age(self) -> float:
        """获取缓存项的年龄（秒）"""
        return time.time() - self.created_at


class MemoryCache:
    """内存缓存实现（LRU + TTL）"""

    def __init__(self, config: MemoryCacheConfig):
        """初始化内存缓存

        Args:
            config: 内存缓存配置
        """
        self.config = config
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = asyncio.Lock()

        # 统计信息
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    async def get(self, key: str) -> Any | None:
        """获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期则返回 None
        """
        async with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            entry = self.cache[key]

            # 检查是否过期
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None

            # 更新 LRU 顺序（移到末尾）
            self.cache.move_to_end(key)

            # 记录访问
            value = entry.access()
            self.hits += 1

            return value

    async def set(self, key: str, value: Any, ttl: Any = _DEFAULT) -> None:
        """设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示永不过期，不传递或 _DEFAULT 表示使用配置的默认值
        """
        async with self.lock:
            # 确定有效的 TTL 值
            if ttl is _DEFAULT:
                # 未传递 ttl，使用配置的默认值
                effective_ttl = self.config.default_ttl
            else:
                # 显式传递了 ttl 值（包括 None，表示永不过期）
                effective_ttl = ttl

            # 创建新的缓存项
            entry = CacheEntry(value, effective_ttl)
            self.cache[key] = entry

            # 移到末尾（最近使用）
            self.cache.move_to_end(key)

            # 检查是否需要驱逐
            if len(self.cache) > self.config.max_size:
                await self._evict()

    async def delete(self, key: str) -> bool:
        """删除缓存项

        Args:
            key: 缓存键

        Returns:
            如果项存在则返回 True，否则返回 False
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    async def clear(self) -> None:
        """清空所有缓存"""
        async with self.lock:
            self.cache.clear()

    async def _evict(self) -> None:
        """执行驱逐（内部方法，应在锁持有时调用）

        根据配置的驱逐策略驱逐项
        """
        if self.config.eviction_policy == "lru":
            # LRU：删除最久未使用的项（第一个）
            if self.cache:
                self.cache.popitem(last=False)
                self.evictions += 1
        elif self.config.eviction_policy == "fifo":
            # FIFO：删除最早插入的项（第一个）
            if self.cache:
                self.cache.popitem(last=False)
                self.evictions += 1

    async def cleanup_expired(self) -> int:
        """清理过期的项

        Returns:
            清理的项数
        """
        async with self.lock:
            expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]

            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)

    async def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息

        Returns:
            统计信息字典
        """
        async with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0

            # 计算内存使用估计
            memory_usage = sum(len(str(entry.value)) for entry in self.cache.values())

            return {
                "size": len(self.cache),
                "max_size": self.config.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "evictions": self.evictions,
                "estimated_memory_bytes": memory_usage,
                "eviction_policy": self.config.eviction_policy,
            }

    async def get_entries(self) -> dict[str, dict[str, Any]]:
        """获取所有缓存项的详细信息

        Returns:
            缓存项的详细信息字典
        """
        async with self.lock:
            return {
                key: {
                    "age_seconds": entry.get_age(),
                    "ttl": entry.ttl,
                    "is_expired": entry.is_expired(),
                    "access_count": entry.access_count,
                    "last_accessed": entry.last_accessed,
                }
                for key, entry in self.cache.items()
            }

    async def exists(self, key: str) -> bool:
        """检查缓存项是否存在且未过期

        Args:
            key: 缓存键

        Returns:
            如果存在且未过期则返回 True
        """
        async with self.lock:
            if key not in self.cache:
                return False
            return not self.cache[key].is_expired()

    async def ttl(self, key: str) -> int | None:
        """获取缓存项的剩余 TTL

        Args:
            key: 缓存键

        Returns:
            剩余的秒数，-1 表示永不过期，None 表示不存在
        """
        async with self.lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]

            if entry.ttl is None:
                return -1

            remaining = entry.ttl - entry.get_age()
            return max(0, int(remaining))

    async def size(self) -> int:
        """获取缓存项数

        Returns:
            缓存中的项数
        """
        async with self.lock:
            return len(self.cache)
