# DeerFlow 开发启动指南

**日期**: 2026年4月1日  
**状态**: ✅ **生产就绪**

---

## 🎯 5分钟快速启动

### 第1步: 验证环境
```bash
make check
```
**预期输出**: ✅ 所有必要工具已安装

### 第2步: 安装依赖
```bash
make install
```
**预期输出**: ✅ 192+ Python 包和 936 JavaScript 包已安装

### 第3步: 启动服务
```bash
make dev
```
**预期输出**:
```
✅ LangGraph 运行在 http://localhost:2024
✅ Gateway 运行在 http://localhost:8001
✅ Frontend 运行在 http://localhost:3000
✅ Nginx 运行在 http://localhost:2026
```

### 第4步: 打开应用
在浏览器中打开: **http://localhost:2026**

✅ **完成！** 现在你可以开始开发了！

---

## 📚 选择你的开发路径

### 路径 A: 工具/技能开发 (后端)

**目标**: 为 DeerFlow Agent 创建自定义工具

**时间**: 2-3 天

**步骤**:

1. **理解工具架构**
   ```bash
   cat backend/packages/harness/deerflow/tools/__init__.py
   cat backend/tests/test_tools_*.py
   ```

2. **创建你的工具**
   ```python
   # backend/packages/harness/deerflow/tools/my_tool.py
   from deerflow.tools.base import BaseTool
   
   class MyTool(BaseTool):
       name = "my_tool"
       description = "工具描述"
       
       def invoke(self, input: str) -> str:
           return f"处理结果: {input}"
   ```

3. **编写测试**
   ```python
   # backend/tests/test_my_tool.py
   def test_my_tool():
       tool = MyTool()
       result = tool.invoke("test")
       assert "处理结果" in result
   ```

4. **运行测试**
   ```bash
   cd backend
   pytest tests/test_my_tool.py -v
   ```

5. **在 Agent 中使用**
   ```python
   # backend/packages/harness/deerflow/agents/lead_agent.py
   tools = [..., MyTool(), ...]
   ```

**推荐第一个工具**: 天气查询工具 (调用外部 API)

---

### 路径 B: 前端界面开发

**目标**: 为 DeerFlow 构建现代化的用户界面

**时间**: 3-5 天

**步骤**:

1. **理解前端结构**
   ```bash
   ls -la frontend/src/
   cat frontend/src/app/page.tsx
   ```

2. **开发新页面**
   ```typescript
   // frontend/src/app/tools/page.tsx
   export default function ToolsPage() {
     return (
       <div className="p-8">
         <h1>工具管理</h1>
         {/* 你的内容 */}
       </div>
     );
   }
   ```

3. **使用 API**
   ```typescript
   // frontend/src/core/api/client.ts
   const tools = await client.getTools();
   ```

4. **运行开发服务器**
   ```bash
   cd frontend
   pnpm dev
   ```

5. **访问开发中的页面**
   ```
   http://localhost:3000/tools
   ```

**推荐第一个页面**: 工具浏览页面 (展示所有可用工具)

---

### 路径 C: 多租户功能扩展

**目标**: 增强多租户隔离和管理功能

**时间**: 4-5 天

**步骤**:

1. **理解多租户架构**
   ```bash
   cat backend/packages/harness/deerflow/multi_tenant/middleware.py
   cat backend/tests/test_multi_tenant.py
   ```

2. **添加租户管理 API**
   ```python
   # backend/app/gateway/routes/tenants.py
   @router.get("/tenants/{tenant_id}")
   async def get_tenant(tenant_id: str):
       return {"tenant_id": tenant_id, "status": "active"}
   ```

3. **编写测试**
   ```bash
   cd backend
   pytest tests/test_tenant_api.py -v
   ```

4. **前端集成**
   ```typescript
   // frontend/src/components/TenantManager.tsx
   export function TenantManager() {
     // 实现租户管理 UI
   }
   ```

**推荐第一个功能**: 租户间切换开关

---

### 路径 D: 性能优化

**目标**: 提升 DeerFlow 的性能和响应速度

**时间**: 3-4 天

**步骤**:

1. **基准测试**
   ```bash
   cd backend
   pytest tests/test_performance.py -v --benchmark
   ```

2. **识别瓶颈**
   ```bash
   python -m cProfile -s cumulative scripts/profile_api.py
   ```

3. **添加缓存**
   ```python
   # backend/packages/harness/deerflow/cache/redis_cache.py
   class RedisCache:
       async def get(self, key: str) -> Optional[str]:
           return await self.redis.get(key)
   ```

4. **验证性能提升**
   ```bash
   pytest tests/test_performance.py -v --benchmark
   ```

**推荐第一个优化**: 查询缓存

---

## 🔧 日常开发命令

### 启动和停止

```bash
# 启动所有服务
make dev

# 停止所有服务
make stop

# 重启所有服务
make stop && make dev
```

### 后端工作流

```bash
cd backend

# 运行所有测试
make test

# 运行特定测试
pytest tests/test_my_feature.py -v

# 代码检查和修复
make lint
ruff check . --fix

# 添加新的 Python 包
uv add package_name
```

### 前端工作流

```bash
cd frontend

# 热重载开发
pnpm dev

# 运行测试
pnpm test

# 代码检查和修复
pnpm lint --fix

# 类型检查
pnpm typecheck
```

### 数据库操作

```bash
cd backend

# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 日志查看

```bash
# 查看所有日志
tail -f logs/*.log

# 查看特定服务日志
tail -f logs/gateway.log
tail -f logs/langgraph.log
tail -f logs/frontend.log

# 实时日志监控
docker-compose logs -f
```

---

## 📊 每日检查清单

### 每天开始

- [ ] `make check` - 验证环境
- [ ] `git pull` - 获取最新代码
- [ ] `make dev` - 启动服务
- [ ] 查看 `logs/` - 确保无错误

### 开发过程中

- [ ] 定期运行 `make test` - 确保测试通过
- [ ] 提交前运行 `make lint` - 检查代码风格
- [ ] 查看文档 - 了解相关代码
- [ ] 保持代码简洁 - 定期重构

### 提交前

- [ ] 所有测试通过 ✅
- [ ] lint 检查通过 ✅
- [ ] 类型检查通过 ✅
- [ ] 代码审查完成 ✅
- [ ] 提交信息清晰 ✅

### 每天结束

- [ ] `git status` - 检查未提交的文件
- [ ] `git commit` - 提交日常工作
- [ ] `git push` - 推送到远程
- [ ] 记录完成的工作

---

## 💡 最佳实践

### 代码风格

```python
# ✅ 好的做法
def calculate_total(items: List[Item]) -> float:
    """计算项目总价。"""
    return sum(item.price for item in items)

# ❌ 不好的做法
def calc(items):
    return sum([i.price for i in items])
```

### 测试编写

```python
# ✅ 好的做法
def test_calculate_total_with_multiple_items():
    """测试多个项目的总价计算。"""
    items = [Item(price=10), Item(price=20)]
    assert calculate_total(items) == 30

# ❌ 不好的做法
def test_calc():
    assert calc([Item(10), Item(20)]) == 30
```

### Git 提交

```bash
# ✅ 好的做法
git commit -m "feat: 添加工具管理页面

- 实现工具列表展示
- 添加工具详情页
- 集成工具执行

Closes #123"

# ❌ 不好的做法
git commit -m "update"
```

### 代码审查

- 至少 1 人审查
- 至少 2 个通过测试
- 更新相关文档
- 更新 CHANGELOG

---

## 🐛 调试技巧

### 后端调试

```python
# 添加调试输出
import logging
logger = logging.getLogger(__name__)
logger.debug(f"变量值: {value}")

# 使用 debugger
import pdb; pdb.set_trace()

# 或者使用现代调试器
import ipdb; ipdb.set_trace()
```

### 前端调试

```typescript
// 浏览器开发者工具
console.log("调试信息:", value);

// 设置断点
debugger;

// VS Code 调试
// 添加 .vscode/launch.json 配置
```

### 数据库调试

```bash
# 连接到 PostgreSQL
psql -h localhost -U deerflow -d deerflow_db

# 查看表结构
\dt

# 查询数据
SELECT * FROM threads LIMIT 10;

# 查看日志
docker logs deerflow_postgres
```

### API 调试

```bash
# 测试 API 端点
curl -X GET http://localhost:8001/api/health

# 使用 HTTPie (更友好)
http GET localhost:8001/api/health

# 使用 Postman 或 Insomnia GUI 工具
```

---

## 📈 常见任务指南

### 添加新的 API 端点

**步骤**:

1. 创建路由模块
   ```python
   # backend/app/gateway/routes/my_route.py
   from fastapi import APIRouter, Depends
   
   router = APIRouter(prefix="/my", tags=["my"])
   
   @router.get("/endpoint")
   async def my_endpoint():
       return {"status": "ok"}
   ```

2. 在主应用中注册
   ```python
   # backend/app/gateway/app.py
   from .routes.my_route import router
   app.include_router(router)
   ```

3. 编写测试
   ```python
   # backend/tests/test_my_route.py
   def test_my_endpoint():
       response = client.get("/api/my/endpoint")
       assert response.status_code == 200
   ```

4. 测试
   ```bash
   pytest tests/test_my_route.py -v
   ```

### 添加新的数据模型

**步骤**:

1. 定义 Pydantic 模型
   ```python
   # backend/app/models/my_model.py
   from pydantic import BaseModel
   
   class MyModel(BaseModel):
       id: str
       name: str
       created_at: datetime
   ```

2. 创建数据库表
   ```python
   # backend/app/database/models.py
   class MyModelDB(Base):
       __tablename__ = "my_model"
       id = Column(String, primary_key=True)
       name = Column(String)
   ```

3. 创建迁移
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add my_model table"
   alembic upgrade head
   ```

4. 编写 CRUD 操作
   ```python
   # backend/app/crud/my_crud.py
   async def create_model(db: Session, model: MyModel):
       db_model = MyModelDB(**model.dict())
       db.add(db_model)
       db.commit()
       return db_model
   ```

---

## 🚀 下一步建议

### 立即开始 (今天)

1. 运行 `make dev` 启动服务
2. 打开 http://localhost:2026 探索应用
3. 查看笔记本的第 1-3 章了解基础
4. 运行一个简单的测试: `cd backend && pytest tests/test_multi_tenant.py::TestTenantMiddleware::test_extract_from_header -v`

### 本周目标

选择一条路径并完成第一个功能:
- **路径 A**: 创建第一个自定义工具
- **路径 B**: 开发第一个前端页面
- **路径 C**: 添加租户管理功能
- **路径 D**: 实现一个性能优化

### 本月目标

- 完成 5 个新工具或功能
- 提交 10+ 个 PR
- 达到 80%+ 测试覆盖率
- 部署到开发环境

---

## 📞 需要帮助？

### 常见问题

**Q: 如何添加新的 Python 包？**
```bash
cd backend
uv add package_name
```

**Q: 如何修复代码风格问题？**
```bash
cd backend
ruff check . --fix
```

**Q: 如何查看应用日志？**
```bash
tail -f logs/gateway.log
```

**Q: 如何重新初始化数据库？**
```bash
docker-compose down -v
make dev
```

### 查阅资源

- 📖 **笔记本**: `DeerFlow-Deployment-Notebook.ipynb` (17,000+ 行文档)
- 📚 **开发指南**: `NEXT_STEPS_DEVELOPMENT.md` (详细计划)
- 🔍 **验证报告**: `VERIFICATION_REPORT.md` (系统状态)
- 📋 **检查清单**: `verification-checklist.md` (验证步骤)

### 更多帮助

- 查看 `backend/docs/` 获取技术文档
- 查看 `frontend/README.md` 获取前端指南
- 查看 `skills/public/` 获取示例实现
- 提交 GitHub Issue 报告问题

---

## ✅ 开发准备检查表

在开始开发前，请确认:

- [ ] 已运行 `make check` ✅
- [ ] 已运行 `make install` ✅
- [ ] 已运行 `make dev` ✅
- [ ] 已打开 http://localhost:2026 ✅
- [ ] 已查看笔记本第 1-3 章 ✅
- [ ] 已选择开发路径 ✅
- [ ] 已阅读相关文档 ✅

---

## 🎉 准备好了？

```bash
# 启动服务
make dev

# 打开应用
# http://localhost:2026

# 选择一个任务开始编码！
```

**祝你开发愉快！** 🚀

---

**生成日期**: 2026-04-01  
**状态**: ✅ 生产就绪  
**下一步**: 运行 `make dev` 并开始开发！
