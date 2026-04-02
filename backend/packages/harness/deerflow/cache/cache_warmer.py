"""
缓存预热器

在应用启动时和定期预热缓存，提高缓存命中率
"""

import asyncio
import logging
from collections.abc import Callable

from deerflow.cache.cache import CacheManager
from deerflow.cache.config import CacheWarmingConfig

logger = logging.getLogger(__name__)


class CacheWarmer:
    """缓存预热器

    负责在应用启动时和定期预热缓存数据
    """

    def __init__(
        self,
        config: CacheWarmingConfig,
        cache_manager: CacheManager,
    ):
        """初始化缓存预热器

        Args:
            config: 预热配置
            cache_manager: 缓存管理器实例
        """
        self.config = config
        self.cache_manager = cache_manager
        self._warmup_tasks: list[asyncio.Task] = []
        self._stop_event = asyncio.Event()
        self._warmup_callbacks: dict[str, Callable] = {}

    def register_warmup_callback(self, name: str, callback: Callable) -> None:
        """注册预热回调函数

        Args:
            name: 回调名称（用于日志和调试）
            callback: 异步回调函数，接收 cache_manager 参数
        """
        self._warmup_callbacks[name] = callback
        logger.debug(f"注册缓存预热回调: {name}")

    async def warmup_single(self, name: str, callback: Callable) -> bool:
        """执行单个预热任务

        Args:
            name: 预热任务名称
            callback: 预热回调函数

        Returns:
            是否成功完成
        """
        try:
            logger.info(f"开始缓存预热: {name}")
            start_time = asyncio.get_event_loop().time()

            await asyncio.wait_for(
                callback(self.cache_manager),
                timeout=self.config.warmup_timeout,
            )

            elapsed = asyncio.get_event_loop().time() - start_time
            logger.info(f"缓存预热完成: {name} (耗时: {elapsed:.2f}秒)")
            return True

        except TimeoutError:
            logger.warning(f"缓存预热超时: {name} (超时: {self.config.warmup_timeout}秒)")
            return False

        except Exception as e:
            logger.exception(f"缓存预热失败: {name} - {e}")
            return False

    async def warmup_all(self) -> dict[str, bool]:
        """执行所有已注册的预热任务

        Returns:
            任务名称到成功状态的字典
        """
        if not self.config.enabled:
            logger.info("缓存预热已禁用")
            return {}

        logger.info("开始执行所有缓存预热任务...")
        results = {}

        # 并发执行所有预热任务
        tasks = []
        for name, callback in self._warmup_callbacks.items():
            task = asyncio.create_task(self.warmup_single(name, callback))
            tasks.append((name, task))

        # 等待所有任务完成
        for name, task in tasks:
            try:
                success = await task
                results[name] = success
            except Exception as e:
                logger.exception(f"预热任务异常: {name} - {e}")
                results[name] = False

        # 统计
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        logger.info(f"缓存预热完成: {success_count}/{total_count} 个任务成功")

        return results

    async def _periodic_warmup_loop(self) -> None:
        """定期预热循环"""
        logger.info(f"启动定期缓存预热，间隔: {self.config.periodic_interval}秒")

        while not self._stop_event.is_set():
            try:
                # 等待间隔时间
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.config.periodic_interval,
                )
                break  # 如果 stop_event 被设置，退出循环

                # 执行预热
                results = await self.warmup_all()
                success_count = sum(1 for v in results.values() if v)
                total_count = len(results)
                logger.info(f"定期预热完成: {success_count}/{total_count} 个任务成功")

            except TimeoutError:
                # 正常超时，继续下一轮
                continue
            except Exception as e:
                logger.exception(f"定期预热异常: {e}")
                await asyncio.sleep(5)  # 出错后等待 5 秒再重试

        logger.info("定期缓存预热已停止")

    async def start(self) -> None:
        """启动缓存预热器

        执行启动预热（如果配置）并启动定期预热循环
        """
        logger.info("启动缓存预热器...")

        # 启动时预热
        if self.config.on_startup:
            await self.warmup_all()

        # 启动定期预热
        if self.config.periodic and self._warmup_callbacks:
            task = asyncio.create_task(self._periodic_warmup_loop())
            self._warmup_tasks.append(task)

    async def stop(self) -> None:
        """停止缓存预热器"""
        logger.info("停止缓存预热器...")

        # 设置停止事件
        self._stop_event.set()

        # 等待所有任务完成
        if self._warmup_tasks:
            for task in self._warmup_callbacks:
                task.cancel()

            await asyncio.gather(*self._warmup_tasks, return_exceptions=True)
            self._warmup_tasks.clear()

        logger.info("缓存预热器已停止")


# 全局缓存预热器实例
_global_warmer: CacheWarmer | None = None


async def get_cache_warmer(
    config: CacheWarmingConfig,
    cache_manager: CacheManager,
) -> CacheWarmer:
    """获取或创建全局缓存预热器实例

    Args:
        config: 预热配置
        cache_manager: 缓存管理器

    Returns:
        CacheWarmer 实例
    """
    global _global_warmer

    if _global_warmer is None:
        _global_warmer = CacheWarmer(config, cache_manager)

    return _global_warmer


async def shutdown_cache_warmer() -> None:
    """关闭全局缓存预热器"""
    global _global_warmer

    if _global_warmer is not None:
        await _global_warmer.stop()
        _global_warmer = None
        logger.info("全局缓存预热器已关闭")
