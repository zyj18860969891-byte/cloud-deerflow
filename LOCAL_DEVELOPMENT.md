# DeerFlow 本地开发启动指南

## 环境检查状态 ✓

✅ **Python 3.12** - 已验证 (3.12.13)
✅ **Node.js** - 已验证 (v24.12.0)  
✅ **pnpm** - 已安装 (v10.26.2)
✅ **uv** - 已安装 (v0.11.2)

## 依赖安装状态 ✓

✅ **后端依赖** - 已安装 187个包
✅ **前端依赖** - 已安装 936个包

## 环境配置状态 ✓

✅ **后端 (.env)** - 已配置
✅ **前端 (.env.local)** - 已配置
✅ **数据目录** - 已创建 (backend/data)
✅ **日志目录** - 已创建 (backend/logs)

## 前端验证 ✓

✅ **TypeScript 检查** - 通过
✅ **ESLint 检查** - 通过

## 现在可以开始本地开发

### 选项 1: 使用 PowerShell 启动（推荐用于 Windows）

```powershell
# 设置 PATH（如果还没有设置）
$env:Path = "C:\Users\Administrator\.local\bin;$env:Path"

# 启动所有服务
cd d:\MultiMode\deerflow\deer-flow
$env:BETTER_AUTH_SECRET = "local-dev-secret-key"

# 在三个不同的 PowerShell 窗口中分别运行：

# 窗口 1: 启动后端 LangGraph
cd backend
.venv\Scripts\Activate.ps1
python -m langgraph.cli api --host 0.0.0.0 --port 2024

# 窗口 2: 启动后端 Gateway API
cd backend
.venv\Scripts\Activate.ps1
python -m app.gateway.api --host 0.0.0.0 --port 8001

# 窗口 3: 启动前端
cd frontend
pnpm dev
```

### 选项 2: 使用 Docker Compose（推荐用于隔离环境）

```bash
# 从项目根目录
cd d:\MultiMode\deerflow\deer-flow
docker-compose -f docker/docker-compose-dev.yaml up
```

### 选项 3: 使用 Python 脚本启动（一键启动）

```powershell
# 从项目根目录
cd d:\MultiMode\deerflow\deer-flow
python scripts/configure.py  # 如果需要交互式配置
```

## 访问应用

启动所有服务后，可以通过以下地址访问：

- **前端应用**: http://localhost:3000
- **后端 Gateway API**: http://localhost:8001
- **LangGraph 运行时**: http://localhost:2024
- **Nginx 代理** (如配置): http://localhost:2026

## 服务端口映射

| 服务 | 端口 | 说明 |
|------|------|------|
| LangGraph | 2024 | 图执行和代理运行时 |
| Gateway | 8001 | FastAPI 网关和 API |
| 前端 Dev | 3000 | Next.js 开发服务器 |
| Nginx (可选) | 2026 | 反向代理和统一入口 |

## 常见问题

### 1. "uv not found" 错误
解决方案：
```powershell
$env:Path = "C:\Users\Administrator\.local\bin;$env:Path"
```

### 2. 前端构建失败
确保设置了 BETTER_AUTH_SECRET：
```powershell
$env:BETTER_AUTH_SECRET = "dev-secret-key"
pnpm build
```

### 3. 后端找不到依赖
激活虚拟环境：
```powershell
cd backend
.venv\Scripts\Activate.ps1
```

### 4. 端口已被占用
检查并终止占用端口的进程，或在 .env 文件中更改端口号

## 下一步

1. **查看架构文档**: `docs/DEPLOYMENT_GUIDE.md`
2. **查看 API 文档**: `backend/docs/API.md`
3. **查看代理开发**: `backend/AGENTS.md`
4. **查看前端开发**: `frontend/README.md`

## 开发工作流

### 后端开发
```powershell
cd backend
.venv\Scripts\Activate.ps1
# 修改代码后自动重加载
python -m langgraph.cli api --watch
```

### 前端开发
```powershell
cd frontend
pnpm dev
# 访问 http://localhost:3000，支持热重载
```

### 运行测试
```powershell
# 后端单元测试
cd backend
.venv\Scripts\Activate.ps1
make test

# 前端测试（如果配置了）
cd frontend
pnpm test
```

### 代码检查
```powershell
# 后端 lint
cd backend
.venv\Scripts\Activate.ps1
make lint

# 前端 lint
cd frontend
pnpm lint
```

## 需要帮助？

- 查看 `DEPLOYMENT_GUIDE.md` 了解完整的部署指南
- 查看各个模块的 README.md
- 查看 `scripts/` 目录中的辅助脚本

---

**最后更新**: 2026-04-01
