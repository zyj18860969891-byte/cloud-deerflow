# P1 缓存优化实现计划

## 任务概述

**优先级**: P1  
**预计耗时**: 2 天  
**目标**: 实现 Redis 缓存层，实现内存缓存策略，达到 P99 响应时间 < 100ms

---

## 一、需求分析

### 性能目标
- ✅ P99 响应时间: < 100ms（当前估计 150-200ms）
- ✅ P95 响应时间: < 50ms
- ✅ 平均响应时间: < 30ms
- ✅ 缓存命中率: > 80%

### 优化范围
1. **Redis 缓存层** - 分布式缓存
   - 租户数据缓存
   - Agent 配置缓存
   - 内存数据缓存
   - 工具/技能缓存

2. **内存缓存策略** - 本地进程内缓存
   - LRU (Least Recently Used) 缓存
   - TTL (Time To Live) 支持
   - 自动过期清理
   - 缓存预热

3. **缓存预热机制**
   - 应用启动时预热热点数据
   - 定期刷新缓存
   - 缓存失效策略

---

## 二、技术栈

### Redis 相关
- `redis` - Redis Python 客户端
- `aioredis` - 异步 Redis 客户端
- 配置: Redis 单机（本地开发），哨兵（生产环境）

### 内存缓存
- `cachetools` - Python 缓存库（LRU、TTL）
- 或自制缓存（使用 OrderedDict）

### 监控
- Prometheus 指标
- Redis 性能指标
- 缓存命中率统计

---

## 三、实现步骤

### Phase 1: 基础缓存工具 (4 小时)

#### 1. 创建缓存配置模块
**文件**: `backend/packages/harness/deerflow/cache/config.py`

```python
class CacheConfig:
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_ttl: int = 3600  # 1 小时
    
    # 内存缓存配置
    memory_cache_maxsize: int = 1000
    memory_cache_ttl: int = 300  # 5 分钟
    
    # 缓存预热
    enable_cache_warming: bool = True
    cache_warming_interval: int = 3600  # 1 小时
```

#### 2. 创建缓存层类
**文件**: `backend/packages/harness/deerflow/cache/cache.py`

```python
class CacheManager:
    """统一的缓存管理器"""
    
    async def get(key: str) -> Any
    async def set(key: str, value: Any, ttl: int) -> None
    async def delete(key: str) -> None
    async def clear() -> None
    async def get_stats() -> CacheStats
```

#### 3. LRU 内存缓存实现
**文件**: `backend/packages/harness/deerflow/cache/memory_cache.py`

```python
class MemoryCache:
    """进程内的 LRU 缓存实现"""
    
    def get(key: str) -> Optional[Any]
    def set(key: str, value: Any, ttl: int = None) -> None
    def delete(key: str) -> None
    def clear() -> None
    def get_stats() -> Dict
```

### Phase 2: 缓存集成 (5 小时)

#### 1. 租户数据缓存
**修改**: `backend/app/gateway/routes/tenants.py`

```python
# 在 get_all_tenants 中添加缓存
@router.get("/api/tenants")
async def get_all_tenants():
    # 尝试从缓存获取
    cached = await cache_manager.get("tenants:list")
    if cached:
        return cached
    
    # 从存储获取（当前是内存存储）
    tenants = ...
    
    # 存储到缓存
    await cache_manager.set("tenants:list", tenants, ttl=300)
    return tenants
```

#### 2. Agent 配置缓存
**文件**: `backend/packages/harness/deerflow/agents/cache.py`

```python
# 缓存 Agent 配置、工具列表、内存数据
async def get_agent_tools_cached():
    key = f"agent:tools:{agent_id}"
    cached = await cache_manager.get(key)
    if cached:
        return cached
    
    tools = await get_agent_tools()
    await cache_manager.set(key, tools, ttl=600)
    return tools
```

#### 3. 技能/工具缓存
**文件**: `backend/packages/harness/deerflow/skills/cache.py`

```python
# 缓存技能列表和详细信息
async def get_skills_cached():
    cached = await cache_manager.get("skills:all")
    if cached:
        return cached
    
    skills = await get_all_skills()
    await cache_manager.set("skills:all", skills, ttl=600)
    return skills
```

#### 4. 内存数据缓存
**修改**: `backend/packages/harness/deerflow/memory/...`

```python
# 缓存内存数据查询结果
async def query_memory_cached(query):
    cache_key = f"memory:query:{hash(query)}"
    cached = await cache_manager.get(cache_key)
    if cached:
        return cached
    
    result = await query_memory(query)
    await cache_manager.set(cache_key, result, ttl=600)
    return result
```

### Phase 3: 缓存预热和管理 (3 小时)

#### 1. 缓存预热机制
**文件**: `backend/packages/harness/deerflow/cache/warmer.py`

```python
class CacheWarmer:
    """缓存预热管理器"""
    
    async def warm_startup() -> None:
        """应用启动时预热"""
        # 加载热点数据
        # - 所有租户
        # - 常用技能
        # - 默认内存数据
    
    async def warm_periodic() -> None:
        """定期预热"""
        # 每小时刷新一次热数据
    
    async def warm_on_demand(keys: List[str]) -> None:
        """按需预热"""
```

#### 2. 缓存失效策略
**文件**: `backend/packages/harness/deerflow/cache/invalidation.py`

```python
class CacheInvalidator:
    """缓存失效管理器"""
    
    async def invalidate_tenant(tenant_id: str) -> None:
        """失效租户相关缓存"""
    
    async def invalidate_agent(agent_id: str) -> None:
        """失效 Agent 相关缓存"""
    
    async def invalidate_skills() -> None:
        """失效技能缓存"""
    
    async def invalidate_memory(query_hash: str) -> None:
        """失效内存查询缓存"""
```

### Phase 4: 性能测试和监控 (3 小时)

#### 1. 基准测试
**文件**: `backend/tests/test_cache_performance.py`

```python
# 测试缓存命中/未命中性能
# 测试 Redis 性能
# 测试内存缓存性能
# 比对无缓存性能

class TestCachePerformance:
    def test_cache_hit_latency()
    def test_cache_miss_latency()
    def test_redis_vs_memory_cache()
    def test_cache_warmup_performance()
```

#### 2. Prometheus 指标
**文件**: `backend/packages/harness/deerflow/cache/metrics.py`

```python
# 创建 Prometheus 指标
cache_hits = Counter("cache_hits_total", "Total cache hits", ["cache_type"])
cache_misses = Counter("cache_misses_total", "Total cache misses", ["cache_type"])
cache_latency = Histogram("cache_latency_ms", "Cache operation latency")
cache_size = Gauge("cache_size_bytes", "Cache size in bytes")

# 定期收集统计
def collect_cache_stats():
    pass
```

#### 3. Redis 监控面板
**Grafana 仪表板**: 展示缓存统计和性能指标

---

## 四、代码结构

```
backend/
├── packages/harness/deerflow/
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── config.py          # 缓存配置
│   │   ├── cache.py           # 缓存管理器
│   │   ├── memory_cache.py    # 内存缓存实现
│   │   ├── warmer.py          # 缓存预热
│   │   ├── invalidation.py    # 缓存失效
│   │   └── metrics.py         # Prometheus 指标
│   └── ...
├── app/gateway/
│   └── routes/
│       ├── tenants.py         # (修改) 添加缓存
│       └── ...
└── tests/
    ├── test_cache_*.py        # 新增缓存测试
    └── test_cache_performance.py  # 性能测试
```

---

## 五、集成清单

### 需要修改的模块
- [ ] `backend/app/gateway/routes/tenants.py` - 缓存租户数据
- [ ] `backend/app/gateway/routes/agents.py` - 缓存 Agent 配置
- [ ] `backend/app/gateway/routes/skills.py` - 缓存技能数据
- [ ] `backend/packages/harness/deerflow/memory/` - 缓存内存查询
- [ ] `backend/packages/harness/deerflow/mcp/` - 缓存 MCP 工具

### 新增配置
- [ ] Redis 连接配置
- [ ] 缓存键前缀约定
- [ ] TTL 策略定义
- [ ] 缓存预热清单

### 新增工具
- [ ] 缓存管理命令行工具
- [ ] 缓存统计查询工具
- [ ] 缓存预热触发工具

---

## 六、性能预期

### 优化前
```
平均响应时间: ~150-200ms
P95: ~100ms
P99: ~150ms
缓存命中率: 0%
```

### 优化后（目标）
```
平均响应时间: ~20-30ms
P95: ~30-40ms
P99: < 100ms
缓存命中率: > 80%
```

### 性能收益
- 📊 响应时间：50-75% 改进
- 🚀 吞吐量：3-5x 提升
- 💾 数据库负载：60% 降低

---

## 七、风险和缓解

### 风险 1: 缓存一致性
**描述**: 缓存数据与数据源不一致  
**缓解**: 合理的 TTL 设置、失效策略、版本控制

### 风险 2: 缓存雪崩
**描述**: 大量缓存同时过期导致数据库压力  
**缓解**: 随机化 TTL、缓存预热、加锁机制

### 风险 3: 缓存穿透
**描述**: 查询不存在的数据导致频繁 miss  
**缓解**: 布隆过滤器、空值缓存、黑名单

### 风险 4: 缓存击穿
**描述**: 热键缓存过期导致并发访问数据源  
**缓解**: 互斥锁、逻辑过期、热键识别

---

## 八、测试策略

### 单元测试
- [ ] 缓存 CRUD 操作
- [ ] TTL 过期机制
- [ ] LRU 驱逐策略
- [ ] 并发访问

### 集成测试
- [ ] Redis 连接
- [ ] 缓存预热
- [ ] 缓存失效
- [ ] 多路由缓存

### 性能测试
- [ ] 缓存命中延迟 < 5ms
- [ ] 缓存预热时间 < 2s
- [ ] 内存使用量稳定
- [ ] Redis 内存 < 500MB

### 压力测试
- [ ] 1000 并发缓存访问
- [ ] 100 并发缓存写入
- [ ] 缓存更新期间的性能

---

## 九、交付物清单

### 代码文件
- [ ] `cache/config.py` - 缓存配置 (80 行)
- [ ] `cache/cache.py` - 缓存管理器 (150 行)
- [ ] `cache/memory_cache.py` - 内存缓存 (120 行)
- [ ] `cache/warmer.py` - 缓存预热 (100 行)
- [ ] `cache/invalidation.py` - 缓存失效 (80 行)
- [ ] `cache/metrics.py` - Prometheus 指标 (60 行)

### 测试文件
- [ ] `tests/test_cache_basic.py` - 基础测试 (150 行)
- [ ] `tests/test_cache_integration.py` - 集成测试 (200 行)
- [ ] `tests/test_cache_performance.py` - 性能测试 (180 行)

### 文档
- [ ] 缓存使用指南
- [ ] 缓存配置文档
- [ ] 性能基准报告
- [ ] Grafana 仪表板配置

---

## 十、时间表

### Day 1 (8 小时)
- 09:00-11:00 - 缓存配置和基础类 (Phase 1)
- 11:00-14:00 - 缓存集成到路由 (Phase 2)
- 14:00-17:00 - 缓存预热和失效 (Phase 3)

### Day 2 (8 小时)
- 09:00-12:00 - 性能测试和优化 (Phase 4)
- 12:00-14:00 - Prometheus 集成
- 14:00-17:00 - 文档和报告

---

## 下一步行动

1. **审核计划** - 确认技术方案和时间表
2. **准备环境** - 确保 Redis 可用
3. **开始实施** - Phase 1 缓存基础设施
4. **持续集成** - Phase 2-4 逐步集成

---

**计划版本**: 1.0  
**最后更新**: 2024  
**状态**: ✅ 就绪开始实施
