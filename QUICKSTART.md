# 🚀 DeerFlow 本地开发环境 - 快速导航

**部署时间**: 2026-04-01  
**环境**: Windows 10/11 PowerShell  
**状态**: ✅ 全部就绪

---

## 📋 服务运行状态

| 服务 | 端口 | 地址 | 状态 |
|-----|-----|------|------|
| LangGraph API | 2024 | http://localhost:2024 | ✅ 运行中 |
| Gateway API | 8001 | http://localhost:8001 | ✅ 运行中 |
| Next.js 前端 | 3000 | http://localhost:3000 | ✅ 运行中 |
| API 文档 | 2024 | http://localhost:2024/docs | ✅ 可用 |

---

## 📚 文档导航

### 新手必读
- **[COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md)** ⭐⭐⭐⭐⭐
  - 完整的开发指南，包含快速开始、架构说明、API 开发等
  - **建议首先阅读此文档**
  - 包含所有常见问题的解决方案

### 部署相关
- **[DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)**
  - 当前部署状态的详细报告
  - 已完成的工作清单
  - 服务验证清单

- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)**
  - 企业级部署指南
  - 适用于阿里云 ECS、腾讯云 CVM
  - 多租户配置详解

### 本地开发指南
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)**
  - 本地开发的快速启动方法
  - 三种启动方式对比
  - 常见问题解决

- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)**
  - 初始设置的完成总结
  - 已安装的依赖列表
  - 架构理解总结

### 快速工具
- **[start-dev-services.ps1](start-dev-services.ps1)** ⭐
  - 一键启动所有服务的 PowerShell 脚本
  - 自动化部署验证
  - 使用方法: `.\start-dev-services.ps1`

---

## 🎯 快速开始（3步）

### 1️⃣ 启动服务
```powershell
# 方法 A: 使用自动化脚本（推荐）
.\start-dev-services.ps1

# 方法 B: 手动启动（3个终端）
# 终端1
cd backend
.\.venv\Scripts\python.exe -m langgraph dev

# 终端2
cd backend
$env:OPENAI_API_KEY = "sk-..."
.\.venv\Scripts\python.exe -m uvicorn app.gateway.app:app --port 8001

# 终端3
cd frontend
pnpm dev
```

### 2️⃣ 验证服务
```powershell
# 测试 LangGraph
curl http://localhost:2024/health

# 测试 Gateway
curl http://localhost:8001/health

# 打开前端
Start-Process http://localhost:3000
```

### 3️⃣ 开始开发
- 查看完整指南: [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md)
- 查看 API 文档: http://localhost:2024/docs
- 编辑代码后自动热重载

---

## 📦 项目结构

```
DeerFlow/
├── backend/                          # Python 后端
│   ├── .venv/                       # 虚拟环境 (187 包)
│   ├── app/gateway/                 # FastAPI Gateway API
│   ├── packages/harness/deerflow/   # DeerFlow 核心框架
│   │   ├── agents/                  # Agent 实现
│   │   ├── sandbox/                 # 沙箱执行
│   │   ├── memory/                  # 记忆系统
│   │   └── mcp/                     # MCP 集成
│   ├── tests/                       # 单元测试 (277+ 个)
│   ├── .env                         # 环境变量 (已创建)
│   └── langgraph.json              # LangGraph 配置
│
├── frontend/                         # Next.js 前端
│   ├── node_modules/               # 依赖 (936 包)
│   ├── src/
│   │   ├── app/                    # Next.js 路由
│   │   ├── components/             # React 组件
│   │   └── core/                   # 核心逻辑
│   ├── .env.local                  # 环境变量 (已创建)
│   └── next.config.js             # Next.js 配置
│
├── docs/                           # 文档
│   ├── DEPLOYMENT_GUIDE.md        # 企业级部署
│   ├── ARCHITECTURE.md            # 架构设计
│   └── ...其他文档
│
├── config.yaml                     # 应用配置 (已创建)
├── config.example.yaml            # 配置示例
├── Makefile                        # 构建脚本
├── docker-compose-dev.yaml        # Docker 配置
│
├── 📄 COMPLETE_DEVELOPMENT_GUIDE.md   # ⭐ 完整开发指南
├── 📄 DEPLOYMENT_STATUS.md            # 部署状态报告
├── 📄 LOCAL_DEVELOPMENT.md            # 本地开发指南
├── 📄 SETUP_COMPLETE.md               # 设置完成总结
├── 🔧 start-dev-services.ps1          # 启动脚本
│
└── logs/                           # 日志目录 (已创建)
```

---

## 🔧 常用命令速查

### 启动/停止服务

```powershell
# 启动所有服务（推荐方式）
.\start-dev-services.ps1

# 启动单个服务
cd backend && .\.venv\Scripts\python.exe -m langgraph dev      # LangGraph
cd backend && .\.venv\Scripts\python.exe -m uvicorn ... --port 8001  # Gateway
cd frontend && pnpm dev                                        # Frontend

# 停止服务（Ctrl+C）
```

### 开发和测试

```powershell
# 后端测试
cd backend
pytest tests/ -v                    # 运行所有测试
pytest tests/test_file.py -v       # 运行特定文件
pytest tests/ -k "keyword" -v      # 运行匹配的测试

# 前端检查
cd frontend
pnpm typecheck                      # TypeScript 检查
pnpm lint                          # ESLint 检查
pnpm lint:fix                      # 修复代码格式

# 前端构建
pnpm build                         # 生产构建（需要 BETTER_AUTH_SECRET）
```

### 工具和工作流

```powershell
# 查看 API 文档
Start-Process http://localhost:2024/docs

# 查看 LangGraph Studio
Start-Process https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

# 访问前端
Start-Process http://localhost:3000

# 查看日志
Get-Content logs/langgraph.log
Get-Content logs/gateway.log
Get-Content logs/frontend.log
```

---

## 🎓 学习路径

### 第一天 - 基础
1. 阅读 [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) 的快速开始部分
2. 启动所有服务
3. 访问 http://localhost:3000 看看前端
4. 浏览 http://localhost:2024/docs 了解 API

### 第二天 - 后端开发
1. 理解 LangGraph Agent 架构
2. 尝试修改 `backend/packages/harness/deerflow/agents/` 中的代码
3. 查看热重载效果
4. 运行后端单元测试

### 第三天 - 前端开发
1. 理解 Next.js 项目结构
2. 修改 `frontend/src/components/` 中的组件
3. 查看 Turbopack 热重载
4. 测试 API 集成

### 第四天 - 集成和部署
1. 完整阅读 [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
2. 配置多租户设置
3. 学习部署到云服务器的流程
4. 规划生产环境架构

---

## 🐛 故障排查

### 常见问题

**问题**: 服务无法启动  
**解决**: 
1. 检查端口是否被占用: `Get-NetTCPConnection -LocalPort 8001`
2. 检查 config.yaml 是否存在
3. 查看错误日志

**问题**: 前端无法连接后端  
**解决**:
1. 检查 Gateway 是否运行: `curl http://localhost:8001/health`
2. 检查 `.env.local` 中的 URL
3. 检查浏览器控制台的 CORS 错误

**问题**: 测试运行失败  
**解决**:
1. 确保虚拟环境激活: `.\.venv\Scripts\Activate.ps1`
2. 更新依赖: `uv sync`
3. 运行特定测试查看详细错误

更多问题请查看 [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) 的常见问题部分。

---

## 📊 项目统计

- **后端代码行数**: 10,000+
- **前端代码行数**: 5,000+
- **文档行数**: 10,000+
- **测试数量**: 277+ 单元测试
- **依赖数量**: 
  - Python: 187 个包
  - Node.js: 936 个包

---

## 🔐 安全提示

⚠️ **本地开发注意事项**:

1. **API 密钥管理**:
   - 不要将真实的 API 密钥提交到 Git
   - 使用 `.env` 和 `.env.local` 文件（已在 .gitignore）
   - 生产环境使用环境变量或密钥管理系统

2. **CORS 配置**:
   - 开发环境已配置 `localhost:3000` CORS
   - 生产环境更改为实际域名
   - 不要使用 `*` 作为 CORS 来源

3. **数据库**:
   - 本地开发使用 SQLite（自动创建）
   - 生产环境配置 PostgreSQL
   - 定期备份数据库

4. **沙箱隔离**:
   - 开发环境使用 LocalSandbox（无隔离）
   - 生产环境使用 AioSandbox（Docker 隔离）
   - 配置适当的权限和资源限制

---

## 📞 获取帮助

1. **查看本地文档**:
   - [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) - 常见问题和解决方案
   - [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - 详细的部署信息
   - `backend/README.md` - 后端文档
   - `frontend/README.md` - 前端文档

2. **查看官方资源**:
   - [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
   - [Next.js 文档](https://nextjs.org/docs)
   - [FastAPI 文档](https://fastapi.tiangolo.com/)

3. **获取技术支持**:
   - 检查 GitHub Issues
   - 查看项目的 CONTRIBUTING.md
   - 联系开发团队

---

## 📝 版本信息

- **DeerFlow 版本**: main branch (2026-03-30)
- **部署文档版本**: v1.0
- **最后更新**: 2026-04-01
- **Python 版本**: 3.12.13
- **Node.js 版本**: v24.12.0

---

## ✨ 我们已为你准备好一切！

现在你有了：
- ✅ 完整的本地开发环境
- ✅ 所有依赖已安装
- ✅ 三个服务正在运行
- ✅ 完善的文档和指南
- ✅ 自动化启动脚本
- ✅ 故障排查指南

**让我们开始构建伟大的东西吧！** 🚀

---

**快速链接**:
- 🌐 [访问前端](http://localhost:3000)
- 📚 [查看 API 文档](http://localhost:2024/docs)
- 📖 [阅读完整开发指南](COMPLETE_DEVELOPMENT_GUIDE.md)
- 📋 [查看部署状态](DEPLOYMENT_STATUS.md)

