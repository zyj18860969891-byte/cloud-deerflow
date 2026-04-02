"""
缓存预热回调示例

展示如何注册缓存预热任务以在启动时预加载常用数据
"""

import logging

from deerflow.cache import CacheManager

logger = logging.getLogger(__name__)


async def warmup_skills_cache(cache_manager: CacheManager) -> None:
    """预热技能缓存

    在应用启动时加载所有启用的技能到缓存

    Args:
        cache_manager: 缓存管理器实例
    """
    logger.info("开始预热技能缓存...")

    # 这里应该从数据库或文件系统加载技能定义
    # 示例：模拟加载技能
    skills = [
        {"name": "weather", "enabled": True, "version": "1.0"},
        {"name": "calculator", "enabled": True, "version": "1.0"},
        {"name": "web_search", "enabled": True, "version": "1.0"},
    ]

    # 将技能信息缓存，TTL 1 小时
    for skill in skills:
        key = f"skill:{skill['name']}"
        await cache_manager.set(key, skill, ttl=3600)
        logger.debug(f"缓存技能: {key}")

    logger.info(f"技能缓存预热完成，加载了 {len(skills)} 个技能")


async def warmup_mcp_configs(cache_manager: CacheManager) -> None:
    """预热 MCP 配置缓存

    Args:
        cache_manager: 缓存管理器实例
    """
    logger.info("开始预热 MCP 配置缓存...")

    # 模拟加载 MCP 配置
    mcp_configs = {
        "filesystem": {"enabled": True, "root": "/data"},
        "github": {"enabled": True, "token": "***"},
    }

    for name, config in mcp_configs.items():
        key = f"mcp:config:{name}"
        await cache_manager.set(key, config, ttl=3600)
        logger.debug(f"缓存 MCP 配置: {key}")

    logger.info(f"MCP 配置缓存预热完成，加载了 {len(mcp_configs)} 个配置")


async def warmup_tenant_data(cache_manager: CacheManager) -> None:
    """预热租户数据缓存

    Args:
        cache_manager: 缓存管理器实例
    """
    logger.info("开始预热租户数据缓存...")

    # 模拟加载租户数据
    tenants = [
        {"id": "tenant1", "name": "Tenant 1", "plan": "enterprise"},
        {"id": "tenant2", "name": "Tenant 2", "plan": "startup"},
    ]

    for tenant in tenants:
        key = f"tenant:{tenant['id']}:info"
        await cache_manager.set(key, tenant, ttl=3600)
        logger.debug(f"缓存租户数据: {key}")

    logger.info(f"租户数据缓存预热完成，加载了 {len(tenants)} 个租户")


# 所有预热回调的列表
WARMUP_CALLBACKS = [
    warmup_skills_cache,
    warmup_mcp_configs,
    warmup_tenant_data,
]


async def register_all_warmup_callbacks(cache_warmer, cache_manager: CacheManager) -> None:
    """注册所有预热回调

    Args:
        cache_warmer: 缓存预热器实例
        cache_manager: 缓存管理器实例
    """
    for callback in WARMUP_CALLBACKS:
        name = callback.__name__
        cache_warmer.register_warmup_callback(name, callback)
        logger.info(f"已注册预热回调: {name}")
