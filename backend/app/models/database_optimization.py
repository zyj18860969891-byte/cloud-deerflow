"""
Database Optimization Data Models

定义数据库优化相关的数据模型，包括：
- 查询性能分析结果
- 索引建议
- 表统计信息
- 索引使用情况报告
- 连接池指标
- 优化报告
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class OptimizationType(str, Enum):
    """优化类型枚举"""

    INDEX_CREATION = "index_creation"
    QUERY_OPTIMIZATION = "query_optimization"
    CONNECTION_POOL = "connection_pool"
    TABLE_PARTITIONING = "table_partitioning"
    VACUUM_ANALYZE = "vacuum_analyze"
    QUERY_REWRITE = "query_rewrite"


class IndexType(str, Enum):
    """索引类型枚举"""

    B_TREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GiST = "gist"
    SPATIAL = "spatial"
    FULLTEXT = "fulltext"


class QueryPerformanceAnalysis(BaseModel):
    """查询性能分析结果"""

    query: str = Field(..., description="分析的查询")
    execution_time: float = Field(..., description="执行时间（秒）")
    rows_examined: int = Field(..., description="检查的行数")
    rows_returned: int = Field(..., description="返回的行数")
    index_usage: list[dict[str, Any]] = Field(default_factory=list, description="索引使用情况")
    suggestions: list[str] = Field(default_factory=list, description="优化建议")
    estimated_improvement: float = Field(0.0, description="预估改进百分比")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, description="分析时间戳")
    table_name: str | None = Field(None, description="表名")
    query_plan: dict[str, Any] | None = Field(None, description="查询执行计划")


class IndexSuggestion(BaseModel):
    """索引建议"""

    table_name: str = Field(..., description="表名")
    columns: list[str] = Field(..., description="列名列表")
    index_name: str = Field(..., description="建议的索引名")
    index_type: IndexType = Field(default=IndexType.B_TREE, description="索引类型")
    reason: str = Field(..., description="创建索引的原因")
    estimated_improvement: float = Field(..., description="预估改进百分比")
    current_performance: dict[str, Any] | None = Field(None, description="当前性能指标")
    priority: str = Field(..., description="优先级 (high/medium/low)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="建议创建时间")


class TableStatistics(BaseModel):
    """表统计信息"""

    table_name: str = Field(..., description="表名")
    row_count: int = Field(..., description="行数")
    size_mb: float = Field(..., description="表大小（MB）")
    index_count: int = Field(..., description="索引数量")
    avg_row_length: float = Field(..., description="平均行长度")
    last_analyzed: datetime = Field(..., description="最后分析时间")
    columns: list[dict[str, Any]] = Field(default_factory=list, description="列统计信息")
    indexes: list[dict[str, Any]] = Field(default_factory=list, description="索引信息")
    fragmentation: float = Field(0.0, description="碎片化程度")
    growth_rate: float = Field(0.0, description="增长率（%）")


class IndexUsageReport(BaseModel):
    """索引使用情况报告"""

    table_name: str | None = Field(None, description="表名")
    indexes: list[dict[str, Any]] = Field(default_factory=list, description="索引使用情况")
    unused_indexes: list[dict[str, Any]] = Field(default_factory=list, description="未使用的索引")
    frequently_used_indexes: list[dict[str, Any]] = Field(default_factory=list, description="频繁使用的索引")
    recommendations: list[str] = Field(default_factory=list, description="建议")
    report_timestamp: datetime = Field(default_factory=datetime.utcnow, description="报告时间戳")


class ConnectionPoolMetrics(BaseModel):
    """连接池指标"""

    pool_size: int = Field(..., description="连接池大小")
    checked_out: int = Field(..., description="已检查出的连接数")
    idle: int = Field(..., description="空闲连接数")
    overflow: int = Field(..., description="溢出连接数")
    checked_in: int = Field(..., description="已检查入的连接数")
    max_overflow: int = Field(..., description="最大溢出连接数")
    pool_timeout: float = Field(..., description="连接池超时时间")
    recycle: int = Field(..., description="连接回收时间")
    invalidated: int = Field(..., description="无效连接数")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="指标时间戳")


class OptimizationRequest(BaseModel):
    """优化请求"""

    query: str = Field(..., description="要优化的查询")
    table_name: str | None = Field(None, description="表名")
    sample_size: int | None = Field(1000, description="样本大小")
    optimization_type: OptimizationType | None = Field(None, description="优化类型")


class IndexCreationRequest(BaseModel):
    """索引创建请求"""

    table_name: str = Field(..., description="表名")
    columns: list[str] = Field(..., description="列名列表")
    index_name: str | None = Field(None, description="索引名")
    index_type: IndexType = Field(default=IndexType.B_TREE, description="索引类型")
    unique: bool = Field(False, description="是否唯一索引")
    concurrently: bool = Field(True, description="是否并发创建")
    if_not_exists: bool = Field(True, description="如果不存在则创建")

    @validator("index_name")
    def generate_index_name(cls, v, values):
        """生成索引名"""
        if v is None:
            table_name = values.get("table_name")
            columns = values.get("columns", [])
            if table_name and columns:
                v = f"idx_{table_name}_{'_'.join(columns)}"
        return v


class OptimizationReport(BaseModel):
    """数据库优化报告"""

    report_period: dict[str, datetime] = Field(..., description="报告时间段")
    total_queries_analyzed: int = Field(..., description="总分析查询数")
    average_query_time: float = Field(..., description="平均查询时间")
    slow_queries_count: int = Field(..., description="慢查询数量")
    indexes_created: int = Field(..., description="创建的索引数")
    indexes_dropped: int = Field(..., description="删除的索引数")
    table_optimizations: list[dict[str, Any]] = Field(default_factory=list, description="表优化情况")
    performance_improvement: float = Field(..., description="性能改进百分比")
    recommendations: list[str] = Field(default_factory=list, description="建议")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="报告生成时间")


class BenchmarkResult(BaseModel):
    """基准测试结果"""

    test_name: str = Field(..., description="测试名称")
    query: str = Field(..., description="测试查询")
    execution_time: float = Field(..., description="执行时间（秒）")
    rows_processed: int = Field(..., description="处理的行数")
    throughput: float = Field(..., description="吞吐量（行/秒）")
    memory_usage: float = Field(..., description="内存使用（MB）")
    cpu_usage: float = Field(..., description="CPU使用率（%）")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="测试时间")


class QueryPlan(BaseModel):
    """查询执行计划"""

    query: str = Field(..., description="查询语句")
    plan: list[dict[str, Any]] = Field(..., description="执行计划")
    total_cost: float = Field(..., description="总成本")
    execution_time: float | None = Field(None, description="预估执行时间")
    indexes_used: list[str] = Field(default_factory=list, description="使用的索引")
    suggestions: list[str] = Field(default_factory=list, description="优化建议")


class DatabaseMetrics(BaseModel):
    """数据库性能指标"""

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="指标时间戳")
    connections: dict[str, int] = Field(default_factory=dict, description="连接统计")
    queries_per_second: float = Field(..., description="每秒查询数")
    average_query_time: float = Field(..., description="平均查询时间")
    slow_queries_percentage: float = Field(..., description="慢查询百分比")
    cache_hit_ratio: float = Field(..., description="缓存命中率")
    disk_io: dict[str, float] = Field(default_factory=dict, description="磁盘I/O")
    memory_usage: dict[str, float] = Field(default_factory=dict, description="内存使用")
    table_statistics: dict[str, dict[str, Any]] = Field(default_factory=dict, description="表统计")


class OptimizationRecommendation(BaseModel):
    """优化建议"""

    id: str = Field(..., description="建议ID")
    type: OptimizationType = Field(..., description="优化类型")
    priority: str = Field(..., description="优先级")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="建议描述")
    estimated_improvement: float = Field(..., description="预估改进百分比")
    implementation_cost: str = Field(..., description="实施成本")
    risk_level: str = Field(..., description="风险级别")
    target_object: str = Field(..., description="目标对象")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="建议创建时间")
    status: str = Field("pending", description="建议状态")
    implemented_at: datetime | None = Field(None, description="实施时间")


class SlowQuery(BaseModel):
    """慢查询信息"""

    query: str = Field(..., description="查询语句")
    execution_time: float = Field(..., description="执行时间（秒）")
    rows_examined: int = Field(..., description="检查的行数")
    rows_sent: int = Field(..., description="发送的行数")
    database: str = Field(..., description="数据库名")
    user: str = Field(..., description="用户")
    host: str = Field(..., description="主机")
    timestamp: datetime = Field(..., description="查询时间")
    index_used: str | None = Field(None, description="使用的索引")
    suggestions: list[str] = Field(default_factory=list, description="优化建议")


class TableInfo(BaseModel):
    """表信息"""

    name: str = Field(..., description="表名")
    schema_name: str = Field(..., description="模式名", alias="schema")
    type: str = Field(..., description="表类型")
    rows: int | None = Field(None, description="行数")
    size_mb: float | None = Field(None, description="大小（MB）")
    indexes: list[dict[str, Any]] = Field(default_factory=list, description="索引列表")
    columns: list[dict[str, Any]] = Field(default_factory=list, description="列列表")
    last_updated: datetime | None = Field(None, description="最后更新时间")

    class Config:
        populate_by_name = True  # 允许同时使用 schema_name 和 schema


class OptimizationAction(BaseModel):
    """优化操作"""

    action_id: str = Field(..., description="操作ID")
    action_type: OptimizationType = Field(..., description="操作类型")
    target: str = Field(..., description="目标对象")
    description: str = Field(..., description="操作描述")
    parameters: dict[str, Any] = Field(default_factory=dict, description="操作参数")
    status: str = Field("pending", description="操作状态")
    started_at: datetime | None = Field(None, description="开始时间")
    completed_at: datetime | None = Field(None, description="完成时间")
    result: dict[str, Any] | None = Field(None, description="操作结果")
    error: str | None = Field(None, description="错误信息")
