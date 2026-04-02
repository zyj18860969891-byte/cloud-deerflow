"""
缓存系统的单元测试
"""

import asyncio

import pytest

pytest_plugins = ("pytest_asyncio",)

from deerflow.cache import (
    CacheConfig,
    CacheManager,
    MemoryCache,
    MemoryCacheConfig,
)


@pytest.fixture(scope="function")
def memory_cache_config():
    """内存缓存配置"""
    return MemoryCacheConfig(max_size=10, default_ttl=60)


@pytest.fixture(scope="function")
async def memory_cache(memory_cache_config):
    """内存缓存实例"""
    cache = MemoryCache(memory_cache_config)
    yield cache
    await cache.clear()


@pytest.fixture(scope="function")
def cache_config():
    """缓存配置"""
    config = CacheConfig()
    config.redis.enabled = False  # 禁用 Redis 以进行单元测试
    return config


@pytest.fixture(scope="function")
async def cache_manager(cache_config):
    """缓存管理器实例"""
    manager = CacheManager(cache_config)
    await manager.initialize()
    yield manager
    await manager.shutdown()


# ==================== 内存缓存测试 ====================


class TestMemoryCache:
    """内存缓存基础测试"""

    @pytest.mark.asyncio
    async def test_set_and_get(self, memory_cache):
        """测试设置和获取缓存"""
        await memory_cache.set("key1", "value1")
        value = await memory_cache.get("key1")

        assert value == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, memory_cache):
        """测试获取不存在的键"""
        value = await memory_cache.get("nonexistent")

        assert value is None

    @pytest.mark.asyncio
    async def test_delete(self, memory_cache):
        """测试删除缓存"""
        await memory_cache.set("key1", "value1")
        await memory_cache.delete("key1")
        value = await memory_cache.get("key1")

        assert value is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, memory_cache):
        """测试 TTL 过期"""
        await memory_cache.set("key1", "value1", ttl=1)
        value = await memory_cache.get("key1")
        assert value == "value1"

        # 等待过期
        await asyncio.sleep(1.1)
        value = await memory_cache.get("key1")

        assert value is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self, memory_cache):
        """测试 LRU 驱逐"""
        # 填满缓存（max_size = 10）
        for i in range(10):
            await memory_cache.set(f"key{i}", f"value{i}")

        # 获取第一个键（更新访问时间）
        await memory_cache.get("key0")

        # 添加新键，应该驱逐最久未使用的（key1）
        await memory_cache.set("key10", "value10")

        # key0 应该存在（最近使用）
        assert await memory_cache.get("key0") is not None

        # key1 应该被驱逐
        assert await memory_cache.get("key1") is None

        # key10 应该存在
        assert await memory_cache.get("key10") is not None

    @pytest.mark.asyncio
    async def test_clear(self, memory_cache):
        """测试清空缓存"""
        await memory_cache.set("key1", "value1")
        await memory_cache.set("key2", "value2")
        await memory_cache.clear()

        assert await memory_cache.size() == 0

    @pytest.mark.asyncio
    async def test_exists(self, memory_cache):
        """测试存在性检查"""
        await memory_cache.set("key1", "value1")

        assert await memory_cache.exists("key1") is True
        assert await memory_cache.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_stats(self, memory_cache):
        """测试统计信息"""
        await memory_cache.set("key1", "value1")
        await memory_cache.set("key2", "value2")
        await memory_cache.get("key1")  # 命中
        await memory_cache.get("key3")  # 未命中

        stats = await memory_cache.get_stats()

        assert stats["size"] == 2
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_ttl_query(self, memory_cache):
        """测试 TTL 查询"""
        await memory_cache.set("key1", "value1", ttl=60)
        ttl = await memory_cache.ttl("key1")

        assert ttl is not None
        assert 50 <= ttl <= 60  # 允许一些浮动

    @pytest.mark.asyncio
    async def test_ttl_no_expiry(self, memory_cache):
        """测试永不过期的项"""
        await memory_cache.set("key1", "value1", ttl=None)
        ttl = await memory_cache.ttl("key1")

        assert ttl == -1  # -1 表示永不过期

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, memory_cache):
        """测试清理过期项"""
        # 设置一些项，不同的过期时间
        await memory_cache.set("key1", "value1", ttl=1)
        await memory_cache.set("key2", "value2", ttl=100)

        # 等待第一个过期
        await asyncio.sleep(1.1)

        # 清理过期项
        cleaned = await memory_cache.cleanup_expired()

        assert cleaned == 1
        assert await memory_cache.get("key1") is None
        assert await memory_cache.get("key2") is not None


# ==================== 缓存管理器测试 ====================


class TestCacheManager:
    """缓存管理器集成测试"""

    @pytest.mark.asyncio
    async def test_initialization(self, cache_manager):
        """测试初始化"""
        assert cache_manager.is_ready is True
        assert cache_manager.memory_cache is not None

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_manager):
        """测试缓存管理器的设置和获取"""
        await cache_manager.set("key1", "value1")
        value = await cache_manager.get("key1")

        assert value == "value1"

    @pytest.mark.asyncio
    async def test_delete(self, cache_manager):
        """测试删除"""
        await cache_manager.set("key1", "value1")
        await cache_manager.delete("key1")
        value = await cache_manager.get("key1")

        assert value is None

    @pytest.mark.asyncio
    async def test_delete_pattern(self, cache_manager):
        """测试模式删除"""
        await cache_manager.set("user:1", "data1")
        await cache_manager.set("user:2", "data2")
        await cache_manager.set("other:1", "data3")

        deleted = await cache_manager.delete_pattern("user:*")

        assert deleted == 2
        assert await cache_manager.get("user:1") is None
        assert await cache_manager.get("user:2") is None
        assert await cache_manager.get("other:1") is not None

    @pytest.mark.asyncio
    async def test_exists(self, cache_manager):
        """测试存在性检查"""
        await cache_manager.set("key1", "value1")

        assert await cache_manager.exists("key1") is True
        assert await cache_manager.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_clear(self, cache_manager):
        """测试清空"""
        await cache_manager.set("key1", "value1")
        await cache_manager.set("key2", "value2")
        await cache_manager.clear()

        assert await cache_manager.get("key1") is None
        assert await cache_manager.get("key2") is None

    @pytest.mark.asyncio
    async def test_get_stats(self, cache_manager):
        """测试获取统计信息"""
        await cache_manager.set("key1", "value1")
        stats = await cache_manager.get_stats()

        assert stats["enabled"] is True
        assert "memory" in stats

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, cache_manager):
        """测试清理过期项"""
        await cache_manager.set("key1", "value1", ttl=1)
        await cache_manager.set("key2", "value2", ttl=100)

        await asyncio.sleep(1.1)

        cleaned = await cache_manager.cleanup_expired()

        assert cleaned == 1


# ==================== 并发测试 ====================


class TestCacheConcurrency:
    """并发访问测试"""

    @pytest.mark.asyncio
    async def test_concurrent_reads(self, memory_cache):
        """测试并发读取"""
        await memory_cache.set("key1", "value1")

        # 并发读取
        tasks = [memory_cache.get("key1") for _ in range(100)]
        results = await asyncio.gather(*tasks)

        assert all(r == "value1" for r in results)
        assert memory_cache.hits == 100

    @pytest.mark.asyncio
    async def test_concurrent_writes(self, memory_cache):
        """测试并发写入"""
        tasks = [memory_cache.set(f"key{i}", f"value{i}") for i in range(100)]
        await asyncio.gather(*tasks)

        # 验证所有项都被设置
        size = await memory_cache.size()
        assert size <= 10  # LRU 限制


# ==================== 配置测试 ====================


class TestCacheConfig:
    """缓存配置测试"""

    def test_key_building(self):
        """测试缓存键构建"""
        from deerflow.cache import CacheKeyConfig

        config = CacheKeyConfig()

        key = config.build_key("test", "data")
        assert key == "deerflow:test:data"

        tenant_key = config.build_tenant_key("tenant1", "data")
        assert tenant_key == "deerflow:tenants:tenant1:data"

    def test_cache_config_defaults(self):
        """测试缓存配置默认值"""
        config = CacheConfig()

        assert config.redis.default_ttl == 3600
        assert config.memory.default_ttl == 300
        assert config.memory.max_size == 1000
