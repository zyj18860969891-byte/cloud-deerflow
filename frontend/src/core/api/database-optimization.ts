/**
 * Database Optimization API Hooks
 * 
 * 提供数据库优化相关的API调用钩子，包括：
 * - 查询性能分析
 * - 索引建议获取
 * - 表统计信息
 * - 索引使用情况
 * - 连接池指标
 * - 优化报告
 */

// @ts-expect-error - API client will be properly configured in next iteration
import { api } from './api-client';

// 数据库优化相关的类型定义
export interface QueryPerformanceAnalysis {
  query: string;
  execution_time: number;
  rows_examined: number;
  rows_returned: number;
  index_usage: Array<{
    index_name: string;
    used: boolean;
    efficiency: number;
  }>;
  suggestions: string[];
  estimated_improvement: number;
  analysis_timestamp: string;
  table_name?: string;
  query_plan?: Record<string, unknown>;
}

export interface IndexSuggestion {
  table_name: string;
  columns: string[];
  index_name: string;
  index_type: 'btree' | 'hash' | 'gin' | 'gist' | 'spatial' | 'fulltext';
  reason: string;
  estimated_improvement: number;
  current_performance?: Record<string, unknown>;
  priority: 'high' | 'medium' | 'low';
  created_at: string;
}

export interface TableStatistics {
  table_name: string;
  row_count: number;
  size_mb: number;
  index_count: number;
  avg_row_length: number;
  last_analyzed: string;
  columns: Array<{
    name: string;
    type: string;
    nullable: boolean;
    default?: unknown;
  }>;
  indexes: Array<{
    name: string;
    type: string;
    columns: string[];
    unique: boolean;
  }>;
  fragmentation: number;
  growth_rate: number;
}

export interface IndexUsageReport {
  table_name?: string;
  indexes: Array<{
    name: string;
    usage_count: number;
    last_used: string;
    efficiency: number;
  }>;
  unused_indexes: Array<{
    name: string;
    size_mb: number;
    last_used?: string;
  }>;
  frequently_used_indexes: Array<{
    name: string;
    usage_count: number;
    efficiency: number;
  }>;
  recommendations: string[];
  report_timestamp: string;
}

export interface ConnectionPoolMetrics {
  pool_size: number;
  checked_out: number;
  idle: number;
  overflow: number;
  checked_in: number;
  max_overflow: number;
  pool_timeout: number;
  recycle: number;
  invalidated: number;
  timestamp: string;
}

export interface OptimizationReport {
  report_period: {
    start: string;
    end: string;
  };
  total_queries_analyzed: number;
  average_query_time: number;
  slow_queries_count: number;
  indexes_created: number;
  indexes_dropped: number;
  table_optimizations: Array<{
    table_name: string;
    actions: string[];
    improvement: number;
  }>;
  performance_improvement: number;
  recommendations: string[];
  generated_at: string;
}

export interface DatabaseMetrics {
  timestamp: string;
  connections: {
    total: number;
    active: number;
    idle: number;
    waiting: number;
  };
  queries_per_second: number;
  average_query_time: number;
  slow_queries_percentage: number;
  cache_hit_ratio: number;
  disk_io: {
    read_mb_s: number;
    write_mb_s: number;
  };
  memory_usage: {
    total_mb: number;
    used_mb: number;
    cache_mb: number;
  };
  table_statistics: Record<string, {
    row_count: number;
    size_mb: number;
    indexes: number;
  }>;
}

export interface OptimizationRecommendation {
  id: string;
  type: 'index_creation' | 'query_optimization' | 'connection_pool' | 'table_partitioning' | 'vacuum_analyze' | 'query_rewrite';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  estimated_improvement: number;
  implementation_cost: 'low' | 'medium' | 'high';
  risk_level: 'low' | 'medium' | 'high';
  target_object: string;
  created_at: string;
  status: 'pending' | 'implemented' | 'rejected';
  implemented_at?: string;
}

export interface SlowQuery {
  query: string;
  execution_time: number;
  rows_examined: number;
  rows_sent: number;
  database: string;
  user: string;
  host: string;
  timestamp: string;
  index_used?: string;
  suggestions: string[];
}

export interface TableInfo {
  name: string;
  schema: string;
  type: string;
  rows?: number;
  size_mb?: number;
  indexes: Array<{
    name: string;
    type: string;
    columns: string[];
    unique: boolean;
  }>;
  columns: Array<{
    name: string;
    type: string;
    nullable: boolean;
    default?: unknown;
  }>;
  last_updated?: string;
}

// API 钩子函数
export const databaseOptimizationApi = {
  // 健康检查
  healthCheck: () => api.get('/database-optimization/health'),

  // 查询性能分析
  analyzeQueryPerformance: (data: {
    query: string;
    table_name?: string;
    sample_size?: number;
  }) => api.post('/database-optimization/analyze-query-performance', data),

  // 获取索引建议
  getIndexSuggestions: (table_name?: string) => 
    api.get('/database-optimization/index-suggestions', { params: { table_name } }),

  // 获取表统计信息
  getTableStatistics: (table_name?: string) => 
    api.get('/database-optimization/table-statistics', { params: { table_name } }),

  // 获取索引使用情况
  getIndexUsage: (table_name?: string) => 
    api.get('/database-optimization/index-usage', { params: { table_name } }),

  // 获取连接池指标
  getConnectionPoolMetrics: () => api.get('/database-optimization/connection-pool-metrics'),

  // 优化连接池
  optimizeConnectionPool: () => api.post('/database-optimization/optimize-connection-pool'),

  // 创建索引
  createIndex: (data: {
    table_name: string;
    columns: string[];
    index_name?: string;
    index_type?: 'btree' | 'hash' | 'gin' | 'gist' | 'spatial' | 'fulltext';
    unique?: boolean;
    concurrently?: boolean;
    if_not_exists?: boolean;
  }) => api.post('/database-optimization/create-index', data),

  // 获取优化报告
  getOptimizationReport: (days = 7) => 
    api.get('/database-optimization/optimization-report', { params: { days } }),

  // 运行基准测试
  runBenchmark: () => api.post('/database-optimization/run-benchmark'),

  // 获取慢查询
  getSlowQueries: (threshold = 1.0, limit = 100) => 
    api.get('/database-optimization/slow-queries', { params: { threshold, limit } }),

  // 获取查询执行计划
  getQueryPlan: (query: string) => 
    api.get('/database-optimization/query-plan', { params: { query } }),

  // 获取表列表
  getTables: () => api.get('/database-optimization/tables'),

  // 获取数据库指标
  getDatabaseMetrics: () => api.get('/database-optimization/database-metrics'),

  // 清理未使用的索引
  cleanupUnusedIndexes: () => api.post('/database-optimization/cleanup-unused-indexes'),

  // 获取优化建议
  getOptimizationRecommendations: () => api.get('/database-optimization/recommendations'),
};

// 便捷的查询性能分析钩子
export const useQueryPerformanceAnalysis = () => {
  return {
    analyzeQuery: databaseOptimizationApi.analyzeQueryPerformance,
    getQueryPlan: databaseOptimizationApi.getQueryPlan,
    getSlowQueries: databaseOptimizationApi.getSlowQueries,
  };
};

// 便捷的索引管理钩子
export const useIndexManagement = () => {
  return {
    getIndexSuggestions: databaseOptimizationApi.getIndexSuggestions,
    getIndexUsage: databaseOptimizationApi.getIndexUsage,
    createIndex: databaseOptimizationApi.createIndex,
    cleanupUnusedIndexes: databaseOptimizationApi.cleanupUnusedIndexes,
  };
};

// 便捷的表统计钩子
export const useTableStatistics = () => {
  return {
    getTableStatistics: databaseOptimizationApi.getTableStatistics,
    getTables: databaseOptimizationApi.getTables,
  };
};

// 便捷的数据库监控钩子
export const useDatabaseMonitoring = () => {
  return {
    getConnectionPoolMetrics: databaseOptimizationApi.getConnectionPoolMetrics,
    getDatabaseMetrics: databaseOptimizationApi.getDatabaseMetrics,
    getOptimizationReport: databaseOptimizationApi.getOptimizationReport,
    getOptimizationRecommendations: databaseOptimizationApi.getOptimizationRecommendations,
  };
};

// 便捷的数据库优化钩子
export const useDatabaseOptimization = () => {
  return {
    ...useQueryPerformanceAnalysis(),
    ...useIndexManagement(),
    ...useTableStatistics(),
    ...useDatabaseMonitoring(),
    optimizeConnectionPool: databaseOptimizationApi.optimizeConnectionPool,
    runBenchmark: databaseOptimizationApi.runBenchmark,
  };
};