#!/usr/bin/env python
"""验证脚本：检查缓存集成"""

import asyncio

from deerflow.cache import (
    get_cache_config,
    get_cache_manager,
    shutdown_cache_manager,
)


async def main():
    """验证缓存系统"""
    print("✓ 导入成功")

    # 获取缓存配置
    config = get_cache_config()
    print(f"✓ 缓存配置加载: {config.redis.default_ttl}s TTL")

    # 初始化缓存管理器
    cache_manager = await get_cache_manager(config)
    print("✓ 缓存管理器初始化成功")

    # 测试缓存操作
    await cache_manager.set("test_key", "test_value", ttl=60)
    value = await cache_manager.get("test_key")
    assert value == "test_value", f"Expected 'test_value', got {value}"
    print("✓ 缓存读写测试通过")

    # 关闭缓存管理器
    await shutdown_cache_manager()
    print("✓ 缓存管理器关闭成功")

    print("\n✅ 所有验证通过！")


if __name__ == "__main__":
    asyncio.run(main())
