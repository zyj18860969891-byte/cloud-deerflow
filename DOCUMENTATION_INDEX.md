# 📚 DeerFlow 项目文档导航

## 🚀 快速开始

### 新手入门
1. **首先阅读**: [`README.md`](./README.md) - 项目概述
2. **快速启动**: [`QUICKSTART.md`](./QUICKSTART.md) - 5 分钟快速指南
3. **开发指南**: [`DEVELOPER_QUICK_START.md`](./DEVELOPER_QUICK_START.md) - 开发环境设置

### 完整文档
- **开发指南**: [`COMPLETE_DEVELOPMENT_GUIDE.md`](./COMPLETE_DEVELOPMENT_GUIDE.md)
- **部署指南**: [`DEPLOYMENT_GUIDE.md`](./docs/DEPLOYMENT_GUIDE.md)
- **项目结构**: [`PROJECT_STRUCTURE_MAP.md`](./PROJECT_STRUCTURE_MAP.md)

## 📊 项目进度

### 当前开发状态
- **总体进度**: P0 完成 ✅ | P1 进行中 🔄
- **详细进度**: [`DEVELOPMENT_PROGRESS.md`](./DEVELOPMENT_PROGRESS.md)

### 最新完成的工作
- **P1 Task 3**: 缓存优化系统
  - 完成报告: [`CACHE_OPTIMIZATION_COMPLETE.md`](./CACHE_OPTIMIZATION_COMPLETE.md)
  - 本次会话报告: [`SESSION_CACHE_OPTIMIZATION_REPORT.md`](./SESSION_CACHE_OPTIMIZATION_REPORT.md)
  - 所有 23 个测试通过 ✅

## 🛠️ 开发工具和命令

### 基本命令
```bash
# 检查环境
make check

# 安装依赖
make install

# 运行后端测试
cd backend && make test

# 后端代码检查
cd backend && make lint

# 启动开发环境
make dev

# 停止开发环境
make stop
```

### 缓存系统命令
```bash
# 运行缓存测试
cd backend && python -m pytest tests/test_cache_basic.py -v

# 验证缓存系统
cd backend && python verify_cache_system.py
```

## 📁 项目结构

```
deerflow/
├── backend/                          # Python FastAPI 网关
│   ├── packages/harness/deerflow/   # 核心 Python 包
│   │   ├── agents/                  # Agent 实现
│   │   ├── tools/                   # 工具库（自定义工具）
│   │   ├── cache/                   # 缓存系统（Redis + 内存）
│   │   ├── mcp/                     # MCP 集成
│   │   └── sandbox/                 # 沙箱执行环境
│   ├── app/gateway/                 # FastAPI 网关应用
│   ├── tests/                       # 后端测试
│   └── Makefile
├── frontend/                         # Next.js 前端应用
│   ├── src/
│   │   ├── app/                     # Next.js 路由
│   │   ├── components/              # React 组件（含租户切换器）
│   │   └── core/                    # 核心逻辑和 API
│   └── package.json
├── docker/                          # Docker 配置
├── docs/                            # 文档
└── skills/                          # 技能包库
```

## 🎯 当前任务优先级

### P1 进行中
1. **P1 Task 3**: 缓存优化 (Phase 1-3 完成 ✅)
   - [x] 配置系统 (304 行)
   - [x] 内存缓存实现 (291 行)
   - [x] 缓存管理器 (323 行)
   - [x] 单元测试 (23 个，100% 通过)
   - [x] 网关集成
   - [ ] Phase 4: 性能基准和监控（下个会话）

2. **P1 Task 4**: 工具管理面板 (下个任务)
   - 预计 3 天
   - 工具列表、详情、参数配置、执行历史

3. **P1 Task 5**: 安全加固
   - 预计 2-3 天

4. **P1 Task 6**: 可观测性增强
   - 预计 2-3 天

### P2 计划中
- **P2 Task 7**: 仪表板开发
- **P2 Task 8**: 数据库优化

## 📈 代码统计

| 任务 | 代码行数 | 测试 | 状态 |
|------|---------|------|------|
| P0 自定义工具库 | 234 | 23 | ✅ |
| P0 多租户 UI | 445 | 16 | ✅ |
| P1 缓存优化 | 1,242 | 23 | ✅ |
| **总计** | **1,921** | **62** | **✅ |

## 🔧 关键特性

### ✅ 已实现
- [x] 自定义工具库（3 个示例工具）
- [x] 多租户 UI 支持
- [x] 双层缓存系统（Redis + 内存）
- [x] LRU 驱逐策略
- [x] TTL 支持
- [x] 并发安全
- [x] 故障转移

### 🔄 进行中
- [ ] 缓存预热机制
- [ ] 性能基准测试
- [ ] 工具管理面板
- [ ] 安全加固

### ⏳ 计划中
- [ ] Prometheus 监控
- [ ] Grafana 仪表板
- [ ] 分布式追踪
- [ ] 数据库优化

## 📚 核心文件导览

### 后端缓存系统
- **配置**: `backend/packages/harness/deerflow/cache/config.py` (304 行)
- **实现**: `backend/packages/harness/deerflow/cache/memory_cache.py` (291 行)
- **管理**: `backend/packages/harness/deerflow/cache/cache.py` (323 行)
- **导出**: `backend/packages/harness/deerflow/cache/__init__.py` (34 行)
- **测试**: `backend/tests/test_cache_basic.py` (290 行, 23 个测试)

### 后端工具系统
- **实现**: `backend/packages/harness/deerflow/tools/custom_tools.py` (234 行)
- **测试**: `backend/tests/test_tools_custom.py` (23 个测试)

### 前端多租户
- **选择器组件**: `frontend/src/components/TenantSelector.tsx`
- **配置面板**: `frontend/src/components/TenantConfigPanel.tsx`
- **API 钩子**: `frontend/src/core/api/tenants.ts`
- **后端路由**: `backend/app/gateway/routes/tenants.py`

### 配置文件
- **后端依赖**: `backend/pyproject.toml`
- **前端依赖**: `frontend/package.json`
- **pytest 配置**: `backend/pytest.ini`
- **Makefile**: `Makefile`（根目录）

## 🧪 测试执行

### 运行特定测试
```bash
# 缓存测试
cd backend && python -m pytest tests/test_cache_basic.py -v

# 工具测试
cd backend && python -m pytest tests/test_tools_custom.py -v

# 多租户测试
cd backend && python -m pytest tests/test_multi_tenant.py -v

# 所有测试
cd backend && make test
```

### 测试覆盖
```bash
# 生成覆盖报告
cd backend && python -m pytest --cov=deerflow tests/
```

## 🐛 常见问题

### Q: 如何启动开发环境？
```bash
make dev
# 访问 http://localhost:2026
```

### Q: 缓存系统如何工作？
查看 [`CACHE_OPTIMIZATION_COMPLETE.md`](./CACHE_OPTIMIZATION_COMPLETE.md) 的"关键特性"部分。

### Q: 如何添加新工具？
查看 `backend/packages/harness/deerflow/tools/custom_tools.py` 中的 `CustomTool` 基类。

### Q: 如何处理租户？
查看 `frontend/src/components/TenantSelector.tsx` 和相关的 API 钩子。

## 📞 获取帮助

- **文档**: 查看 `docs/` 目录
- **代码注释**: 所有代码都有详细的文档字符串
- **测试**: 查看 `tests/` 目录了解使用示例
- **问题**: GitHub Issues

## 🚀 部署

### 本地开发
```bash
make dev
```

### Docker 开发
```bash
make docker-dev
```

### 完整部署指南
查看 [`docs/DEPLOYMENT_GUIDE.md`](./docs/DEPLOYMENT_GUIDE.md)

## 📝 贡献

1. 阅读 [`CONTRIBUTING.md`](./CONTRIBUTING.md)
2. 创建特性分支
3. 运行测试确保通过
4. 提交 PR

## 📋 检查清单

在提交前：
- [ ] 代码通过 `ruff check`
- [ ] 所有测试通过 `make test`
- [ ] 新代码有类型提示
- [ ] 新代码有文档字符串
- [ ] 添加了相关的单元测试

## 🎓 学习资源

### 官方文档
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Pydantic](https://docs.pydantic.dev/)

### 项目文档
- 架构设计: 查看代码中的顶级注释
- API 文档: 运行 `make dev` 后访问 `/docs`
- 数据模型: 查看 `config.py` 和 `models.py` 文件

## 🔐 安全

- 所有 API 端点都需要认证
- 支持多租户隔离
- 防止跨租户访问
- SQL 注入防护（Pydantic 验证）
- XSS 防护（React 自动转义）

查看 [`SECURITY.md`](./SECURITY.md) 了解更多信息。

## 📅 发布计划

- **v0.1.0**: 基础功能（当前）
- **v0.2.0**: 工具管理面板 + 安全加固
- **v0.3.0**: 仪表板 + 数据库优化
- **v1.0.0**: 生产就绪

---

**最后更新**: 2025-01-21  
**维护者**: GitHub Copilot  
**许可证**: MIT  
**贡献者**: 详见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)

🌟 如果这个项目对你有帮助，请 Star 我们！
