"""
数据库优化工具

提供索引管理、查询优化、连接池调优、性能分析等功能
"""

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from deerflow.services.database import get_engine

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """数据库优化器"""

    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self._dialect = engine.dialect.name

    async def analyze_query_performance(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        分析查询性能。

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            性能分析结果
        """
        result = {
            "query": query,
            "execution_time_ms": 0,
            "rows_examined": 0,
            "rows_returned": 0,
            "index_used": [],
            "suggestions": [],
        }

        try:
            # 对于PostgreSQL，使用EXPLAIN ANALYZE
            if self._dialect == "postgresql":
                explain_query = f"EXPLAIN ANALYZE {query}"
                async with self.engine.connect() as conn:
                    # 执行查询并获取执行计划
                    start_time = await conn.execute(text("SELECT EXTRACT(EPOCH FROM clock_timestamp())"))
                    plan_result = await conn.execute(text(explain_query), params or {})
                    plan_rows = plan_result.fetchall()
                    end_time = await conn.execute(text("SELECT EXTRACT(EPOCH FROM clock_timestamp())"))

                    # 解析执行计划
                    plan_text = "\\n".join([row[0] for row in plan_rows])

                    # 提取关键信息
                    result["execution_plan"] = plan_text

                    # 查找索引使用情况
                    if "Index Scan" in plan_text or "Index Only Scan" in plan_text:
                        result["index_used"].append("existing_index")

                    # 检查是否有全表扫描
                    if "Seq Scan" in plan_text:
                        result["suggestions"].append("Consider adding an index to avoid sequential scan")

                    # 检查是否有临时表或文件排序
                    if "Temp" in plan_text or "File" in plan_text:
                        result["suggestions"].append("Query may benefit from optimization to avoid temp tables or file sorts")

            # 对于SQLite，使用EXPLAIN QUERY PLAN
            elif self._dialect == "sqlite":
                explain_query = f"EXPLAIN QUERY PLAN {query}"
                async with self.engine.connect() as conn:
                    plan_result = await conn.execute(text(explain_query), params or {})
                    plan_rows = plan_result.fetchall()

                    plan_text = "\\n".join([str(row) for row in plan_rows])
                    result["execution_plan"] = plan_text

                    # 简单的索引使用检查
                    if "USING INDEX" in plan_text:
                        result["index_used"].append("index_used")

            # 执行实际查询以获取时间
            async with self.engine.connect() as conn:
                import time

                start = time.time()
                query_result = await conn.execute(text(query), params or {})
                rows = query_result.fetchall()
                end = time.time()

                result["execution_time_ms"] = (end - start) * 1000
                result["rows_returned"] = len(rows)

        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            result["error"] = str(e)

        return result

    async def suggest_indexes(self) -> list[dict[str, Any]]:
        """
        分析数据库并建议新索引。

        Returns:
            索引建议列表
        """
        suggestions = []

        try:
            async with self.engine.connect() as conn:
                # 对于PostgreSQL，查询慢查询日志或统计信息
                if self._dialect == "postgresql":
                    # 查找缺少索引的查询（基于pg_stat_statements）
                    try:
                        query = """
                        SELECT
                            query,
                            calls,
                            total_time,
                            rows,
                            mean_time
                        FROM pg_stat_statements
                        WHERE query NOT LIKE '%pg_%'
                        AND query NOT LIKE '%ANALYZE%'
                        ORDER BY total_time DESC
                        LIMIT 10
                        """
                        result = await conn.execute(text(query))
                        slow_queries = result.fetchall()

                        for sq in slow_queries:
                            suggestions.append({"type": "slow_query", "query": sq[0], "calls": sq[1], "total_time_ms": sq[2], "suggestion": "Review this query for potential indexing opportunities"})
                    except Exception:
                        logger.warning("pg_stat_statements not available")

                # 对于SQLite，分析数据库模式
                elif self._dialect == "sqlite":
                    # 查找没有索引的表
                    tables_result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in tables_result.fetchall()]

                    for table in tables:
                        # 检查表的索引
                        index_result = await conn.execute(text(f"PRAGMA index_list('{table}')"))
                        indexes = index_result.fetchall()

                        if len(indexes) == 0:
                            suggestions.append({"type": "missing_index", "table": table, "suggestion": f"Consider adding indexes to table '{table}'"})

        except Exception as e:
            logger.error(f"Error suggesting indexes: {e}")

        return suggestions

    async def get_table_stats(self) -> list[dict[str, Any]]:
        """
        获取表统计信息。

        Returns:
            表统计信息列表
        """
        stats = []

        try:
            async with self.engine.connect() as conn:
                if self._dialect == "postgresql":
                    query = """
                    SELECT
                        schemaname AS schema,
                        tablename AS table,
                        n_tup_ins AS inserts,
                        n_tup_upd AS updates,
                        n_tup_del AS deletes,
                        n_live_tup AS live_rows,
                        n_dead_tup AS dead_rows,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    """
                    result = await conn.execute(text(query))
                    rows = result.fetchall()

                    for row in rows:
                        stats.append(
                            {
                                "schema": row[0],
                                "table": row[1],
                                "inserts": row[2],
                                "updates": row[3],
                                "deletes": row[4],
                                "live_rows": row[5],
                                "dead_rows": row[6],
                                "total_size": row[7],
                            }
                        )

                elif self._dialect == "sqlite":
                    # SQLite统计信息
                    tables_result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in tables_result.fetchall()]

                    for table in tables:
                        try:
                            # 获取表信息
                            pragma_result = await conn.execute(text(f"PRAGMA table_info('{table}')"))
                            columns = pragma_result.fetchall()

                            # 估算行数（SQLite没有直接的统计信息）
                            count_result = await conn.execute(text(f"SELECT COUNT(*) FROM '{table}'"))
                            row_count = count_result.scalar()

                            stats.append({"table": table, "columns": len(columns), "estimated_rows": row_count, "size_info": "N/A for SQLite"})
                        except Exception as e:
                            logger.warning(f"Could not get stats for table {table}: {e}")

        except Exception as e:
            logger.error(f"Error getting table stats: {e}")

        return stats

    async def check_index_usage(self) -> list[dict[str, Any]]:
        """
        检查索引使用情况。

        Returns:
            索引使用统计
        """
        indexes = []

        try:
            async with self.engine.connect() as conn:
                if self._dialect == "postgresql":
                    query = """
                    SELECT
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan AS index_scans,
                        idx_tup_read AS tuples_read,
                        idx_tup_fetch AS tuples_fetched
                    FROM pg_stat_user_indexes
                    ORDER BY idx_scan DESC
                    """
                    result = await conn.execute(text(query))
                    rows = result.fetchall()

                    for row in rows:
                        indexes.append(
                            {
                                "schema": row[0],
                                "table": row[1],
                                "index": row[2],
                                "scans": row[3],
                                "tuples_read": row[4],
                                "tuples_fetched": row[5],
                                "efficiency": row[5] / row[4] if row[4] > 0 else 0,
                            }
                        )

                elif self._dialect == "sqlite":
                    # SQLite索引信息
                    tables_result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                    tables = [row[0] for row in tables_result.fetchall()]

                    for table in tables:
                        index_result = await conn.execute(text(f"PRAGMA index_list('{table}')"))
                        table_indexes = index_result.fetchall()

                        for idx in table_indexes:
                            indexes.append(
                                {
                                    "table": table,
                                    "index": idx[1],
                                    "unique": bool(idx[2]),
                                    "origin": idx[3],
                                }
                            )

        except Exception as e:
            logger.error(f"Error checking index usage: {e}")

        return indexes

    async def optimize_connections(self, pool_size: int = 10, max_overflow: int = 20):
        """
        优化连接池配置。

        Args:
            pool_size: 连接池大小
            max_overflow: 最大溢出连接数
        """
        if self._dialect != "postgresql":
            logger.info("Connection pool optimization only applies to PostgreSQL")
            return

        # 对于PostgreSQL，可以根据服务器配置调整连接池
        # 建议的配置：
        # pool_size = (max_connections * 0.75) / number_of_workers
        # max_overflow = pool_size * 0.5

        logger.info(f"Connection pool configuration: pool_size={pool_size}, max_overflow={max_overflow}")

        # 重新创建引擎以应用新配置（需要重启应用）
        # 实际应用中，这应该在启动时配置
        return {"pool_size": pool_size, "max_overflow": max_overflow, "recommendation": "Configure these values in your database connection string or engine configuration"}

    async def vacuum_analyze(self) -> dict[str, Any]:
        """
        执行VACUUM ANALYZE（PostgreSQL）或ANALYZE（SQLite）。

        Returns:
            操作结果
        """
        result = {"tables_optimized": 0, "size_reduced_bytes": 0}

        try:
            async with self.engine.connect() as conn:
                if self._dialect == "postgresql":
                    # PostgreSQL VACUUM ANALYZE
                    await conn.execute(text("VACUUM ANALYZE"))
                    result["message"] = "VACUUM ANALYZE completed"

                elif self._dialect == "sqlite":
                    # SQLite ANALYZE
                    await conn.execute(text("ANALYZE"))
                    result["message"] = "ANALYZE completed"

                # 获取优化后的统计信息
                stats = await self.get_table_stats()
                result["tables_optimized"] = len(stats)

        except Exception as e:
            logger.error(f"Error during vacuum/analyze: {e}")
            result["error"] = str(e)

        return result

    async def create_recommended_indexes(self) -> list[dict[str, Any]]:
        """
        创建推荐的索引。

        Returns:
            创建的索引列表
        """
        created_indexes = []

        # 基于常见查询模式推荐索引
        recommendations = [
            # 工具表的常用查询索引
            {
                "table": "tools",
                "columns": ["enabled", "tool_type"],
                "name": "idx_tools_enabled_type",
            },
            {
                "table": "tools",
                "columns": ["tenant_id", "enabled"],
                "name": "idx_tools_tenant_enabled",
            },
            # 工具执行记录的索引
            {
                "table": "tool_executions",
                "columns": ["user_id", "created_at"],
                "name": "idx_tool_executions_user_created",
            },
            {
                "table": "tool_executions",
                "columns": ["tenant_id", "created_at"],
                "name": "idx_tool_executions_tenant_created",
            },
            {
                "table": "tool_executions",
                "columns": ["tool_id", "status"],
                "name": "idx_tool_executions_tool_status",
            },
            # API日志的索引
            {
                "table": "api_logs",
                "columns": ["user_id", "created_at"],
                "name": "idx_api_logs_user_created",
            },
            {
                "table": "api_logs",
                "columns": ["endpoint", "method", "status_code"],
                "name": "idx_api_logs_endpoint_status",
            },
            # 租户表的索引
            {
                "table": "tenants",
                "columns": ["is_active", "created_at"],
                "name": "idx_tenants_active_created",
            },
        ]

        try:
            async with self.engine.connect() as conn:
                for rec in recommendations:
                    # 检查表是否存在
                    try:
                        # 检查索引是否已存在
                        if self._dialect == "postgresql":
                            check_query = """
                            SELECT 1 FROM pg_indexes
                            WHERE tablename = :table AND indexname = :index
                            """
                        else:
                            # SQLite
                            check_query = """
                            SELECT 1 FROM sqlite_master
                            WHERE type='index' AND name = :index
                            """

                        result = await conn.execute(text(check_query), {"table": rec["table"], "index": rec["name"]})
                        existing = result.fetchone()

                        if not existing:
                            # 创建索引
                            columns = ", ".join(rec["columns"])
                            create_sql = f"CREATE INDEX {rec['name']} ON {rec['table']} ({columns})"

                            await conn.execute(text(create_sql))
                            created_indexes.append(rec)
                            logger.info(f"Created index: {rec['name']}")

                    except Exception as e:
                        logger.warning(f"Could not create index {rec['name']}: {e}")

                await conn.commit()

        except Exception as e:
            logger.error(f"Error creating recommended indexes: {e}")

        return created_indexes


async def get_database_optimizer() -> DatabaseOptimizer:
    """获取数据库优化器实例"""
    engine = get_engine()
    return DatabaseOptimizer(engine)
