"""
缓存性能监控

提供 Prometheus 指标和性能追踪
"""

import asyncio
import logging

try:
    from prometheus_client import Counter, Gauge, Histogram, Summary

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Gauge = Histogram = Summary = type(None)  # type: ignore

from deerflow.cache.cache import CacheManager
from deerflow.cache.config import CacheMetricsConfig

logger = logging.getLogger(__name__)


class CacheMetrics:
    """缓存性能指标收集器"""

    def __init__(self, config: CacheMetricsConfig):
        """初始化指标收集器

        Args:
            config: 指标配置
        """
        self.config = config
        self.enabled = config.enabled and PROMETHEUS_AVAILABLE

        if not PROMETHEUS_AVAILABLE and config.enabled:
            logger.warning("Prometheus client not installed, metrics disabled")
            self.enabled = False

        if self.enabled:
            self._setup_metrics()
            logger.info("Cache metrics initialized")
        else:
            logger.info("Cache metrics disabled")

    def _setup_metrics(self) -> None:
        """设置 Prometheus 指标"""
        # 缓存操作计数器
        self.cache_operations_total = Counter(
            "deerflow_cache_operations_total",
            "Total number of cache operations",
            ["operation", "result"],  # operation: get/set/delete, result: hit/miss/error
        )

        # 缓存命中率
        self.cache_hit_rate = Gauge(
            "deerflow_cache_hit_rate",
            "Cache hit rate (hits / total requests)",
        )

        # 缓存大小
        self.cache_size = Gauge(
            "deerflow_cache_size",
            "Current number of items in cache",
            ["layer"],  # layer: memory/redis
        )

        # 驱逐计数
        self.cache_evictions_total = Counter(
            "deerflow_cache_evictions_total",
            "Total number of cache evictions",
            ["reason"],  # reason: lru/ttl/other
        )

        # 操作延迟
        self.cache_operation_duration = Histogram(
            "deerflow_cache_operation_duration_seconds",
            "Duration of cache operations",
            ["operation"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
        )

        # 内存使用
        self.cache_memory_bytes = Gauge(
            "deerflow_cache_memory_bytes",
            "Estimated memory usage of cache",
        )

        # 故障转移计数
        self.cache_fallbacks_total = Counter(
            "deerflow_cache_fallbacks_total",
            "Total number of cache fallbacks (Redis -> Memory)",
        )

    def record_operation(
        self,
        operation: str,
        result: str,
        duration: float,
        layer: str = "combined",
    ) -> None:
        """记录缓存操作

        Args:
            operation: 操作类型 (get/set/delete)
            result: 操作结果 (hit/miss/error)
            duration: 操作耗时（秒）
            layer: 缓存层 (memory/redis/combined)
        """
        if not self.enabled:
            return

        self.cache_operations_total.labels(operation=operation, result=result).inc()

        if operation in ["get", "set", "delete"]:
            self.cache_operation_duration.labels(operation=operation).observe(duration)

    def update_hit_rate(self, hits: int, total: int) -> None:
        """更新缓存命中率

        Args:
            hits: 命中次数
            total: 总请求次数
        """
        if not self.enabled:
            return

        rate = hits / total if total > 0 else 0.0
        self.cache_hit_rate.set(rate)

    def update_size(self, size: int, layer: str = "combined") -> None:
        """更新缓存大小

        Args:
            size: 缓存项数
            layer: 缓存层
        """
        if not self.enabled:
            return

        self.cache_size.labels(layer=layer).set(size)

    def record_eviction(self, reason: str = "lru") -> None:
        """记录驱逐事件

        Args:
            reason: 驱逐原因 (lru/ttl/other)
        """
        if not self.enabled:
            return

        self.cache_evictions_total.labels(reason=reason).inc()

    def update_memory_usage(self, bytes_used: int) -> None:
        """更新内存使用量

        Args:
            bytes_used: 使用的字节数
        """
        if not self.enabled:
            return

        self.cache_memory_bytes.set(bytes_used)

    def record_fallback(self) -> None:
        """记录故障转移事件"""
        if not self.enabled:
            return

        self.cache_fallbacks_total.inc()

    def collect_from_cache_manager(self, cache_manager: CacheManager) -> None:
        """从缓存管理器收集指标

        Args:
            cache_manager: 缓存管理器实例
        """
        if not self.enabled:
            return

        try:
            stats = cache_manager.get_stats_sync()

            # 更新命中率
            hits = stats.get("hits", 0)
            misses = stats.get("misses", 0)
            self.update_hit_rate(hits, hits + misses)

            # 更新大小
            size = stats.get("size", 0)
            self.update_size(size)

            # 更新内存使用
            memory_bytes = stats.get("estimated_memory_bytes", 0)
            self.update_memory_usage(memory_bytes)

        except Exception as e:
            logger.exception(f"Failed to collect metrics: {e}")


class MetricsCollector:
    """定期指标收集器"""

    def __init__(
        self,
        config: CacheMetricsConfig,
        cache_manager: CacheManager,
        metrics: CacheMetrics,
    ):
        """初始化收集器

        Args:
            config: 指标配置
            cache_manager: 缓存管理器
            metrics: 指标实例
        """
        self.config = config
        self.cache_manager = cache_manager
        self.metrics = metrics
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        """启动定期收集"""
        if not self.config.enabled or not self.metrics.enabled:
            return

        logger.info(f"Starting metrics collection every {self.config.collection_interval} seconds")
        self._task = asyncio.create_task(self._collect_loop())

    async def stop(self) -> None:
        """停止收集"""
        if self._task is not None:
            self._stop_event.set()
            await self._task
            self._task = None
            logger.info("Metrics collection stopped")

    async def _collect_loop(self) -> None:
        """收集循环"""
        while not self._stop_event.is_set():
            try:
                # 收集指标
                self.metrics.collect_from_cache_manager(self.cache_manager)

                # 等待下一次收集
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.config.collection_interval,
                )
                break

            except TimeoutError:
                # 正常超时，继续
                continue
            except Exception as e:
                logger.exception(f"Metrics collection error: {e}")
                await asyncio.sleep(5)  # 出错后等待 5 秒


# 全局指标实例
_global_metrics: CacheMetrics | None = None
_global_collector: MetricsCollector | None = None


async def get_cache_metrics(
    config: CacheMetricsConfig,
    cache_manager: CacheManager | None = None,
) -> CacheMetrics:
    """获取或创建全局缓存指标实例

    Args:
        config: 指标配置
        cache_manager: 缓存管理器（可选，用于自动收集）

    Returns:
        CacheMetrics 实例
    """
    global _global_metrics, _global_collector

    if _global_metrics is None:
        _global_metrics = CacheMetrics(config)

        # 如果有缓存管理器，创建收集器
        if cache_manager is not None and config.enabled:
            _global_collector = MetricsCollector(config, cache_manager, _global_metrics)
            await _global_collector.start()

    return _global_metrics


async def shutdown_cache_metrics() -> None:
    """关闭全局缓存指标"""
    global _global_metrics, _global_collector

    if _global_collector is not None:
        await _global_collector.stop()
        _global_collector = None

    if _global_metrics is not None:
        _global_metrics = None
        logger.info("Global cache metrics shut down")
