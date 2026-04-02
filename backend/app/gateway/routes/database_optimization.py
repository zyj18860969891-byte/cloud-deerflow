"""
Database Optimization API Routes

提供数据库性能优化相关的API端点，包括：
- 查询性能分析
- 索引建议生成
- 表统计信息
- 索引使用情况检查
- 连接池优化
- 推荐索引创建
"""

import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncEngine

from deerflow.auth import get_current_active_user
from deerflow.services.database import get_database_service
from deerflow.services.database_optimization import DatabaseOptimizer

from ...models.database_optimization import ConnectionPoolMetrics, IndexCreationRequest, IndexSuggestion, IndexUsageReport, OptimizationReport, OptimizationRequest, QueryPerformanceAnalysis, TableStatistics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/database-optimization", tags=["database-optimization"])


async def get_engine() -> AsyncEngine:
    """获取数据库引擎依赖"""
    db_service = await get_database_service()
    return db_service.engine


@router.get("/health")
async def health_check():
    """数据库优化服务健康检查"""
    return {"status": "healthy", "service": "database-optimization", "timestamp": datetime.now(UTC)}


@router.post("/analyze-query-performance")
async def analyze_query_performance(request: OptimizationRequest, engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> QueryPerformanceAnalysis:
    """
    分析查询性能

    Args:
        request: 包含要分析的查询和表名
        engine: 数据库引擎
        current_user: 当前管理员用户

    Returns:
        QueryPerformanceAnalysis: 查询性能分析结果
    """
    try:
        optimizer = DatabaseOptimizer(engine)
        result = await optimizer.analyze_query_performance(query=request.query, table_name=request.table_name, sample_size=request.sample_size)
        return result
    except Exception as e:
        logger.error(f"Query performance analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query performance analysis failed: {str(e)}")


@router.get("/index-suggestions")
async def get_index_suggestions(table_name: str | None = Query(None, description="表名，如果为空则分析所有表"), engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> list[IndexSuggestion]:
    """
    获取索引建议

    Args:
        table_name: 表名，可选
        engine: 数据库引擎
        current_user: 当前管理员用户

    Returns:
        List[IndexSuggestion]: 索引建议列表
    """
    try:
        optimizer = DatabaseOptimizer(engine)
        suggestions = await optimizer.get_index_suggestions(table_name)
        return suggestions
    except Exception as e:
        logger.error(f"Failed to get index suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get index suggestions: {str(e)}")


@router.get("/table-statistics")
async def get_table_statistics(table_name: str | None = Query(None, description="表名，如果为空则获取所有表统计"), engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> list[TableStatistics]:
    """
    获取表统计信息

    Args:
        table_name: 表名，可选
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        List[TableStatistics]: 表统计信息列表
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        stats = await optimizer.get_table_statistics(table_name)
        return stats
    except Exception as e:
        logger.error(f"Failed to get table statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get table statistics: {str(e)}")


@router.get("/index-usage")
async def get_index_usage(table_name: str | None = Query(None, description="表名，可选"), engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> IndexUsageReport:
    """
    获取索引使用情况报告

    Args:
        table_name: 表名，可选
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        IndexUsageReport: 索引使用情况报告
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        usage_report = await optimizer.get_index_usage(table_name)
        return usage_report
    except Exception as e:
        logger.error(f"Failed to get index usage report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get index usage report: {str(e)}")


@router.get("/connection-pool-metrics")
async def get_connection_pool_metrics(engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> ConnectionPoolMetrics:
    """
    获取连接池指标

    Args:
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        ConnectionPoolMetrics: 连接池指标
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        metrics = await optimizer.get_connection_pool_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get connection pool metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get connection pool metrics: {str(e)}")


@router.post("/optimize-connection-pool")
async def optimize_connection_pool(background_tasks: BackgroundTasks, engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> dict[str, Any]:
    """
    优化连接池配置

    Args:
        background_tasks: 后台任务
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        Dict[str, Any]: 优化结果
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)

        # 在后台执行连接池优化
        background_tasks.add_task(optimizer.optimize_connection_pool)

        return {"status": "optimization_started", "message": "Connection pool optimization started in background", "timestamp": datetime.now(UTC)}
    except Exception as e:
        logger.error(f"Failed to start connection pool optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start connection pool optimization: {str(e)}")


@router.post("/create-index")
async def create_index(request: IndexCreationRequest, engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> dict[str, Any]:
    """
    创建推荐索引

    Args:
        request: 索引创建请求
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        Dict[str, Any]: 创建结果
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        result = await optimizer.create_recommended_index(request)
        return result
    except Exception as e:
        logger.error(f"Failed to create index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create index: {str(e)}")


@router.get("/optimization-report")
async def get_optimization_report(days: int = Query(7, description="报告天数", ge=1, le=30), engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> OptimizationReport:
    """
    获取数据库优化报告

    Args:
        days: 报告天数
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        OptimizationReport: 数据库优化报告
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        report = await optimizer.get_optimization_report(days)
        return report
    except Exception as e:
        logger.error(f"Failed to get optimization report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization report: {str(e)}")


@router.post("/run-benchmark")
async def run_database_benchmark(background_tasks: BackgroundTasks, engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> dict[str, Any]:
    """
    运行数据库性能基准测试

    Args:
        background_tasks: 后台任务
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        Dict[str, Any]: 基准测试启动结果
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)

        # 在后台执行基准测试
        background_tasks.add_task(optimizer.run_benchmark)

        return {"status": "benchmark_started", "message": "Database benchmark started in background", "timestamp": datetime.now(UTC)}
    except Exception as e:
        logger.error(f"Failed to start database benchmark: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start database benchmark: {str(e)}")


@router.get("/slow-queries")
async def get_slow_queries(
    threshold: float = Query(1.0, description="慢查询阈值（秒）", ge=0.1), limit: int = Query(100, description="返回数量限制", ge=1, le=1000), engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)
) -> list[dict[str, Any]]:
    """
    获取慢查询列表

    Args:
        threshold: 慢查询阈值（秒）
        limit: 返回数量限制
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        List[Dict[str, Any]]: 慢查询列表
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        slow_queries = await optimizer.get_slow_queries(threshold, limit)
        return slow_queries
    except Exception as e:
        logger.error(f"Failed to get slow queries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get slow queries: {str(e)}")


@router.get("/query-plan")
async def get_query_plan(query: str = Query(..., description="要分析的SQL查询"), engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> dict[str, Any]:
    """
    获取查询执行计划

    Args:
        query: SQL查询
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        Dict[str, Any]: 查询执行计划
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        plan = await optimizer.get_query_plan(query)
        return plan
    except Exception as e:
        logger.error(f"Failed to get query plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get query plan: {str(e)}")


@router.get("/tables")
async def get_tables(engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> list[dict[str, Any]]:
    """
    获取数据库表列表

    Args:
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        List[Dict[str, Any]]: 表列表
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        tables = await optimizer.get_tables()
        return tables
    except Exception as e:
        logger.error(f"Failed to get tables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")


@router.get("/database-metrics")
async def get_database_metrics(engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> dict[str, Any]:
    """
    获取数据库性能指标

    Args:
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        Dict[str, Any]: 数据库性能指标
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        metrics = await optimizer.get_database_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get database metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get database metrics: {str(e)}")


@router.post("/cleanup-unused-indexes")
async def cleanup_unused_indexes(background_tasks: BackgroundTasks, engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> dict[str, Any]:
    """
    清理未使用的索引

    Args:
        background_tasks: 后台任务
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        Dict[str, Any]: 清理结果
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)

        # 在后台执行索引清理
        background_tasks.add_task(optimizer.cleanup_unused_indexes)

        return {"status": "cleanup_started", "message": "Unused indexes cleanup started in background", "timestamp": datetime.now(UTC)}
    except Exception as e:
        logger.error(f"Failed to start unused indexes cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start unused indexes cleanup: {str(e)}")


@router.get("/recommendations")
async def get_optimization_recommendations(engine: AsyncEngine = Depends(get_engine), current_user=Depends(get_current_active_user)) -> list[dict[str, Any]]:
    """
    获取数据库优化建议

    Args:
        engine: 数据库引擎
        current_user: 当前激活用户

    Returns:
        List[Dict[str, Any]]: 优化建议列表
    """
    # 权限检查：只有管理员可以访问
    if not current_user.has_role("admin"):
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only administrators can access database optimization")
    try:
        optimizer = DatabaseOptimizer(engine)
        recommendations = await optimizer.get_optimization_recommendations()
        return recommendations
    except Exception as e:
        logger.error(f"Failed to get optimization recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization recommendations: {str(e)}")
