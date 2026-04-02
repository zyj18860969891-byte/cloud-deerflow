# 📚 DeerFlow 资源索引 (2026年4月1日)

**系统状态**: 🟢 **生产就绪**  
**最后更新**: 2026-04-01  
**版本**: main branch

---

## 📖 文档总览

### 🎯 按使用场景分类

#### 新手入门 (按阅读顺序)
1. **[QUICKSTART.md](QUICKSTART.md)** ⭐⭐⭐
   - 快速导航和项目概览
   - 服务运行状态
   - 常用命令速查
   - **🎯 首先读这个**

2. **[COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md)** ⭐⭐⭐⭐⭐
   - 完整的开发指南
   - 项目架构详解
   - API 开发教程
   - 前端开发教程
   - 常见问题解决

3. **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** ⭐⭐⭐
   - 本地开发快速参考
   - 三种启动方式
   - 常见问题

#### 部署和配置
4. **[DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)**
   - 当前部署状态报告
   - 服务运行情况
   - 配置详解
   - 验证清单

5. **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** ⭐⭐⭐⭐
   - 企业级部署指南
   - 阿里云 ECS / 腾讯云 CVM 部署步骤
   - 多租户架构配置
   - 生产环境最佳实践

#### 项目管理
6. **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)**
   - 初始设置完成总结
   - 已安装依赖清单
   - 架构理解总结

7. **[backend/README.md](backend/README.md)**
   - 后端项目文档
   - API 说明
   - 代码组织

8. **[frontend/README.md](frontend/README.md)**
   - 前端项目文档
   - 组件说明
   - 开发指南

#### 参考文档 (在 docs/ 目录)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - 系统架构设计
- **[docs/API.md](docs/API.md)** - API 参考文档
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - 配置说明
- **[docs/MCP_SERVER.md](docs/MCP_SERVER.md)** - MCP 集成指南
- **[docs/MEMORY_IMPROVEMENTS.md](docs/MEMORY_IMPROVEMENTS.md)** - 记忆系统改进

---

## 🔧 工具和脚本

### 启动脚本
- **[start-dev-services.ps1](start-dev-services.ps1)**
  - 一键启动所有服务（推荐）
  - 支持自动验证
  - Windows PowerShell 脚本

### 编译和构建脚本
- **[Makefile](Makefile)** - Linux/Mac 用
- **[scripts/](scripts/)** - 实用工具脚本集合
  - `check.py` - 环境检查
  - `configure.py` - 配置生成
  - `deploy.sh` - 部署脚本

### Docker 相关
- **[docker-compose-dev.yaml](docker-compose-dev.yaml)** - 开发环境 Compose 配置
- **[docker-compose.yaml](docker-compose.yaml)** - 生产环境 Compose 配置
- **[docker/](docker/)** - Docker 配置文件和脚本

---

## 💾 配置文件位置

### 应用配置
| 文件 | 位置 | 说明 |
|-----|-----|------|
| `config.yaml` | `./config.yaml` | ✅ 已创建 - 应用主配置 |
| `config.example.yaml` | `./config.example.yaml` | 配置示例模板 |
| `.env` | `backend/.env` | ✅ 已创建 - 后端环境变量 |
| `.env.local` | `frontend/.env.local` | ✅ 已创建 - 前端环境变量 |
| `langgraph.json` | `backend/langgraph.json` | LangGraph 配置 |

### 项目元数据
| 文件 | 位置 | 说明 |
|-----|-----|------|
| `package.json` | `frontend/package.json` | 前端依赖声明 |
| `pyproject.toml` | `backend/pyproject.toml` | 后端依赖声明 |
| `pnpm-lock.yaml` | `frontend/pnpm-lock.yaml` | 前端依赖锁定 |
| `ruff.toml` | `backend/ruff.toml` | Python Lint 规则 |
| `tsconfig.json` | `frontend/tsconfig.json` | TypeScript 配置 |
| `next.config.js` | `frontend/next.config.js` | Next.js 配置 |
| `eslint.config.js` | `frontend/eslint.config.js` | ESLint 规则 |

---

## 📂 项目目录结构

```
d:\MultiMode\deerflow\deer-flow\
│
├── 📄 文档根目录
│   ├── QUICKSTART.md                    ← 开始这里！
│   ├── COMPLETE_DEVELOPMENT_GUIDE.md    ← 完整指南
│   ├── DEPLOYMENT_STATUS.md             ← 部署状态
│   ├── LOCAL_DEVELOPMENT.md             ← 本地开发
│   ├── SETUP_COMPLETE.md                ← 设置总结
│   ├── README.md                        ← 项目首页
│   ├── CONTRIBUTING.md                  ← 贡献指南
│   ├── config.yaml                      ← 应用配置 ✅
│   └── config.example.yaml              ← 配置示例
│
├── 🔧 start-dev-services.ps1            ← 启动脚本
│
├── backend/                             ← Python 后端
│   ├── .venv/                          ← 虚拟环境 (187 包)
│   ├── app/
│   │   ├── gateway/                    ← FastAPI 网关
│   │   ├── channels/                   ← 通道集成
│   │   └── __init__.py
│   ├── packages/harness/deerflow/
│   │   ├── agents/                     ← Agent 实现
│   │   ├── sandbox/                    ← 沙箱执行
│   │   ├── memory/                     ← 记忆系统
│   │   ├── mcp/                        ← MCP 集成
│   │   ├── models/                     ← LLM 模型
│   │   └── config/                     ← 配置管理
│   ├── tests/                          ← 单元测试 (277+)
│   ├── data/                           ← 数据存储 ✅
│   ├── logs/                           ← 日志目录 ✅
│   ├── .env                            ← 环境变量 ✅
│   ├── langgraph.json                  ← LangGraph 配置
│   ├── pyproject.toml                  ← 依赖声明
│   ├── Makefile                        ← 构建脚本
│   └── README.md                       ← 后端文档
│
├── frontend/                            ← Next.js 前端
│   ├── node_modules/                   ← 依赖 (936 包)
│   ├── src/
│   │   ├── app/                        ← Next.js 路由
│   │   ├── components/                 ← React 组件
│   │   ├── core/                       ← 核心逻辑
│   │   │   ├── api.ts                 ← API 客户端
│   │   │   ├── hooks/                 ← React Hooks
│   │   │   └── types.ts               ← 类型定义
│   │   ├── styles/                    ← 样式文件
│   │   └── env.js                     ← 环境验证
│   ├── public/                         ← 静态资源
│   ├── .env.local                      ← 环境变量 ✅
│   ├── package.json                    ← 依赖声明
│   ├── pnpm-lock.yaml                  ← 依赖锁定
│   ├── tsconfig.json                   ← TypeScript 配置
│   ├── next.config.js                  ← Next.js 配置
│   ├── eslint.config.js                ← ESLint 规则
│   ├── Makefile                        ← 构建脚本
│   └── README.md                       ← 前端文档
│
├── docs/                                ← 详细文档
│   ├── DEPLOYMENT_GUIDE.md             ← 企业级部署
│   ├── ARCHITECTURE.md                 ← 系统架构
│   ├── API.md                          ← API 参考
│   ├── CONFIGURATION.md                ← 配置说明
│   ├── MCP_SERVER.md                   ← MCP 集成
│   ├── MEMORY_IMPROVEMENTS.md          ← 记忆系统
│   ├── FILE_UPLOAD.md                  ← 文件上传
│   ├── GUARDRAILS.md                   ← 安全栏杆
│   └── 其他技术文档...
│
├── docker/                              ← Docker 配置
│   ├── docker-compose-dev.yaml         ← 开发环境
│   ├── docker-compose.yaml             ← 生产环境
│   ├── nginx/                          ← Nginx 配置
│   └── provisioner/                    ← K8s 预配置
│
├── skills/                              ← 技能库
│   └── public/                         ← 内置技能
│
├── scripts/                             ← 工具脚本
│   ├── check.py                        ← 环境检查
│   ├── configure.py                    ← 配置生成
│   ├── deploy.sh                       ← 部署脚本
│   └── 其他工具脚本
│
├── logs/                                ← 日志目录 ✅
│
├── .github/                             ← GitHub 配置
│   └── workflows/                      ← CI/CD 流程
│
└── Makefile                             ← 根构建脚本
```

---

## 🎯 功能导航

### 我想... 应该看什么文档？

| 我想... | 应该看... |
|---------|----------|
| 快速了解项目 | [QUICKSTART.md](QUICKSTART.md) |
| 学习如何开发 | [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) |
| 启动本地开发 | [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) 或 `start-dev-services.ps1` |
| 部署到云服务器 | [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) |
| 了解系统架构 | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 或 [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) |
| 查看 API 文档 | http://localhost:2024/docs (启动后) |
| 运行测试 | [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) 的测试部分 |
| 配置应用 | [docs/CONFIGURATION.md](docs/CONFIGURATION.md) 或 `config.yaml` |
| 集成 MCP | [docs/MCP_SERVER.md](docs/MCP_SERVER.md) |
| 上传文件 | [docs/FILE_UPLOAD.md](docs/FILE_UPLOAD.md) |
| 安全性 | [docs/GUARDRAILS.md](docs/GUARDRAILS.md) 或 [SECURITY.md](SECURITY.md) |

---

## 🌐 在线资源

### 官方文档
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **Python 官方**: https://docs.python.org/3.12/
- **Node.js 官方**: https://nodejs.org/docs/

### 社区资源
- **LangChain 社区**: https://github.com/langchain-ai/langchain
- **FastAPI 讨论**: https://github.com/tiangolo/fastapi/discussions
- **Next.js 讨论**: https://github.com/vercel/next.js/discussions

---

## 📊 快速数据

### 依赖统计
```
后端依赖:  187 个 Python 包
前端依赖:  936 个 Node.js 包
总计:      1,123 个包
```

### 代码统计
```
后端代码:  10,000+ 行
前端代码:  5,000+ 行
测试代码:  3,000+ 行
文档:      10,000+ 行
总计:      28,000+ 行
```

### 测试覆盖
```
单元测试:  277+ 个
集成测试:  持续中
E2E 测试:  计划中
```

---

## 🔐 安全资源

- **[SECURITY.md](SECURITY.md)** - 安全政策和责任披露
- **[docs/GUARDRAILS.md](docs/GUARDRAILS.md)** - 安全栏杆和限制

---

## 📝 贡献指南

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - 贡献规则
- **[backend/CONTRIBUTING.md](backend/CONTRIBUTING.md)** - 后端贡献指南
- **[frontend/README.md](frontend/README.md)** - 前端贡献指南

---

## 📞 获取帮助

1. **检查文档**：首先查看 [QUICKSTART.md](QUICKSTART.md) 和 [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md)
2. **查看常见问题**：[COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md) 包含常见问题解决方案
3. **查看示例代码**：在 `tests/` 目录中找到示例
4. **读取源代码注释**：代码中有详细的中文注释
5. **查看日志**：使用 `logs/` 目录中的日志文件调试

---

## ✅ 检查清单

启动开发之前：
- [ ] 已阅读 [QUICKSTART.md](QUICKSTART.md)
- [ ] 已运行 `start-dev-services.ps1` 或手动启动三个服务
- [ ] 已验证 http://localhost:3000 能访问
- [ ] 已查看 http://localhost:2024/docs 的 API 文档
- [ ] 已阅读 [COMPLETE_DEVELOPMENT_GUIDE.md](COMPLETE_DEVELOPMENT_GUIDE.md)

开始开发之前：
- [ ] 已了解项目结构
- [ ] 已了解代码组织方式
- [ ] 已了解开发工作流
- [ ] 已配置编辑器 (VS Code 推荐)
- [ ] 已设置 Git commit hooks (可选)

---

## 🎓 学习路径

**第一周**: 理解项目  
→ QUICKSTART.md → COMPLETE_DEVELOPMENT_GUIDE.md → 启动服务

**第二周**: 后端开发  
→ 后端架构 → 修改代码 → 运行测试 → 调试

**第三周**: 前端开发  
→ 前端架构 → 修改组件 → 测试功能 → 优化性能

**第四周**: 部署学习  
→ DEPLOYMENT_GUIDE.md → Docker 配置 → 云服务器部署

---

**最后更新**: 2026-04-01  
**文档版本**: v1.0  
**项目版本**: main branch (2026-03-30)

---

## 📞 联系方式

- **项目首页**: [README.md](README.md)
- **安全报告**: [SECURITY.md](SECURITY.md)
- **许可证**: [LICENSE](LICENSE)

---

✨ **现在你已经有了所有需要的信息。祝你开发愉快！** 🚀
