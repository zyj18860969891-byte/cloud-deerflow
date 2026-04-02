# DeerFlow 项目完整结构和文档映射

**生成日期**: 2026-04-01  
**更新**: 笔记本完成后

---

## 📁 项目顶级结构

```
deer-flow/
│
├── 📓 Documentation (文档)
│   ├── DeerFlow-Deployment-Notebook.ipynb     ⭐ 主要笔记本 (11章)
│   ├── NOTEBOOK_COMPLETION_SUMMARY.md         新增: 完成总结
│   ├── NOTEBOOK_NAVIGATION.md                 新增: 导航指南
│   ├── QUICKSTART.md                          快速开始指南
│   ├── COMPLETE_DEVELOPMENT_GUIDE.md          完整开发指南
│   ├── DEPLOYMENT_GUIDE.md                    部署指南
│   ├── LOCAL_DEVELOPMENT.md                   本地开发参考
│   ├── RESOURCES_INDEX.md                     资源索引
│   ├── DEPLOYMENT_STATUS.md                   部署状态
│   ├── SETUP_COMPLETE.md                      设置完成报告
│   ├── README.md                              项目主 README
│   ├── README_zh.md                           中文 README
│   ├── README_ja.md                           日语 README
│   ├── README_fr.md                           法语 README
│   ├── README_ru.md                           俄语 README
│   ├── CONTRIBUTING.md                        贡献指南
│   ├── SECURITY.md                            安全政策
│   ├── LICENSE                                许可证
│   └── Install.md                             安装指南
│
├── ⚙️ Configuration (配置)
│   ├── config.yaml                            ✅ 应用配置 (已创建)
│   ├── config.example.yaml                    配置模板
│   ├── extensions_config.example.json         扩展配置模板
│   ├── Makefile                               构建脚本
│   └── docker/                                Docker 相关
│       ├── docker-compose-dev.yaml            开发 Docker Compose
│       ├── docker-compose.yaml                基础 Docker Compose
│       ├── nginx/                             Nginx 配置
│       │   ├── nginx.conf
│       │   └── ssl/
│       └── provisioner/                       配置初始化
│
├── 🔧 Scripts (脚本)
│   ├── start-dev-services.ps1                 ✅ 启动脚本 (已创建)
│   ├── check.sh                               环境检查
│   ├── check.py                               Python 检查
│   ├── deploy.sh                              部署脚本
│   ├── configure.py                           配置脚本
│   ├── cleanup-containers.sh                  清理脚本
│   └── verify-deployment.sh                   验证脚本
│
├── 🐍 Backend (Python 后端)
│   ├── Dockerfile                             后端容器镜像
│   ├── Makefile                               后端构建脚本
│   ├── pyproject.toml                         Python 依赖定义
│   ├── ruff.toml                              代码风格配置
│   ├── uv.lock                                依赖锁定文件
│   ├── langgraph.json                         LangGraph 配置
│   ├── debug.py                               调试脚本
│   │
│   ├── 📂 app/                                应用层
│   │   ├── __init__.py
│   │   ├── gateway/                           FastAPI 网关
│   │   │   ├── app.py                         FastAPI 应用
│   │   │   ├── api/                           API 模块
│   │   │   ├── routers/                       路由定义
│   │   │   ├── middleware/                    中间件
│   │   │   └── models/                        数据模型
│   │   ├── channels/                          通道集成
│   │   └── __pycache__/
│   │
│   ├── 📂 packages/                           核心包
│   │   └── harness/                           核心框架
│   │       └── deerflow/                      主包
│   │           ├── agents/                    Agent 实现 ⭐
│   │           │   ├── lead_agent.py          Lead Agent
│   │           │   ├── middleware.py          中间件
│   │           │   ├── memory.py              内存管理
│   │           │   └── state.py               状态定义
│   │           ├── sandbox/                   沙箱执行 ⭐
│   │           │   ├── local.py               本地沙箱
│   │           │   ├── aio.py                 异步沙箱
│   │           │   └── tools.py               工具定义
│   │           ├── mcp/                       MCP 集成 ⭐
│   │           │   ├── client.py              MCP 客户端
│   │           │   └── tools.py               MCP 工具
│   │           ├── models/                    数据模型
│   │           │   ├── config.py              配置模型
│   │           │   └── state.py               状态模型
│   │           └── checkpoint/                检查点管理 ⭐
│   │               └── multi_tenant.py        多租户检查点
│   │
│   ├── 📂 tests/                              测试套件 (277+ 测试)
│   │   ├── test_agents.py                     Agent 测试
│   │   ├── test_app_config_reload.py          配置重载测试
│   │   ├── test_sandbox.py                    沙箱测试
│   │   ├── test_mcp.py                        MCP 测试
│   │   └── ...
│   │
│   ├── 📂 docs/                               文档
│   │   ├── ARCHITECTURE.md                    架构文档
│   │   ├── API.md                             API 文档
│   │   ├── AGENTS.md                          Agent 设计
│   │   ├── CONFIGURATION.md                   配置说明
│   │   ├── MEMORY_IMPROVEMENTS.md             内存改进
│   │   ├── AUTO_TITLE_GENERATION.md           自动标题
│   │   ├── FILE_UPLOAD.md                     文件上传
│   │   └── ...
│   │
│   ├── 📂 data/                               ✅ 数据目录 (已创建)
│   │   └── .deer-flow/                        应用数据
│   │       ├── checkpoints.db                 SQLite 检查点
│   │       └── memory.json                    记忆数据
│   │
│   ├── 📂 logs/                               ✅ 日志目录 (已创建)
│   │   ├── langgraph.log                      LangGraph 日志
│   │   ├── gateway.log                        Gateway 日志
│   │   └── ...
│   │
│   ├── .env                                   ✅ 环境变量 (已创建)
│   └── README.md                              后端 README
│
├── 🎨 Frontend (Next.js 前端)
│   ├── Dockerfile                             前端容器镜像
│   ├── Makefile                               前端构建脚本
│   ├── package.json                           Node 依赖定义
│   ├── pnpm-lock.yaml                         依赖锁定文件
│   ├── pnpm-workspace.yaml                    工作区配置
│   ├── tsconfig.json                          TypeScript 配置
│   ├── next.config.js                         Next.js 配置
│   ├── eslint.config.js                       ESLint 配置
│   ├── postcss.config.js                      PostCSS 配置
│   ├── prettier.config.js                     Prettier 配置
│   ├── components.json                        组件配置
│   │
│   ├── 📂 src/                                源代码
│   │   ├── app/                               路由和布局
│   │   │   ├── layout.tsx                     根布局
│   │   │   ├── page.tsx                       主页
│   │   │   └── [route]/                       动态路由
│   │   ├── components/                        React 组件
│   │   │   ├── ChatWindow.tsx                 聊天窗口
│   │   │   ├── Sidebar.tsx                    侧边栏
│   │   │   ├── CodeBlock.tsx                  代码块
│   │   │   └── ...
│   │   ├── core/                              核心逻辑
│   │   │   ├── api.ts                         API 客户端
│   │   │   ├── hooks/                         自定义 Hooks
│   │   │   ├── types.ts                       类型定义
│   │   │   └── utils.ts                       工具函数
│   │   ├── styles/                            样式文件
│   │   │   ├── globals.css                    全局样式
│   │   │   └── ...
│   │   └── env.js                             环境验证
│   │
│   ├── 📂 public/                             静态资源
│   │   ├── images/                            图片
│   │   ├── icons/                             图标
│   │   └── ...
│   │
│   ├── 📂 scripts/                            脚本
│   │   └── ...
│   │
│   ├── .env.local                             ✅ 环境变量 (已创建)
│   └── README.md                              前端 README
│
├── 📚 docs/                                   顶级文档
│   ├── DEPLOYMENT_GUIDE.md                    部署指南
│   ├── CODE_CHANGE_SUMMARY_BY_FILE.md         代码变更总结
│   ├── SKILL_NAME_CONFLICT_FIX.md             技能冲突修复
│   └── ...
│
├── 🎯 skills/                                 技能包
│   ├── public/                                公开技能
│   │   ├── basic/
│   │   ├── advanced/
│   │   └── ...
│   └── custom/                                自定义技能
│
├── 🐋 docker/                                 Docker 相关
│   ├── docker-compose-dev.yaml                开发配置
│   ├── docker-compose.yaml                    基础配置
│   └── nginx/                                 Nginx 配置
│
├── 📊 deerflow-subscribe/                     订阅模块
│   └── ...
│
└── 📋 Version Control
    ├── .github/
    │   └── workflows/                         CI/CD 工作流
    │       ├── backend-unit-tests.yml         后端测试
    │       └── ...
    ├── .gitignore
    └── CONTRIBUTING.md
```

---

## 📖 文档交叉映射

### 按功能查找文档

#### 🎓 学习和理解

| 想要 | 文档位置 | 笔记本章节 |
|------|--------|----------|
| 项目概述 | README.md | 第1章 |
| 架构设计 | backend/docs/ARCHITECTURE.md | 第2章 |
| API 文档 | backend/docs/API.md | 第3.3章 |
| 配置说明 | backend/docs/CONFIGURATION.md | 第4章 |
| 快速开始 | QUICKSTART.md | 第7章 |

#### 🛠️ 开发工作

| 想要 | 文档位置 | 笔记本章节 |
|------|--------|----------|
| 设置环境 | Install.md | 第3-5章 |
| 本地开发 | LOCAL_DEVELOPMENT.md | 第8章 |
| 完整指南 | COMPLETE_DEVELOPMENT_GUIDE.md | 第8章 |
| 写测试 | backend/tests/ | 第8.5章 |
| Agent 设计 | AGENTS.md | 第2章 |

#### 🚀 部署和运维

| 想要 | 文档位置 | 笔记本章节 |
|------|--------|----------|
| 部署流程 | DEPLOYMENT_GUIDE.md | 第10章 |
| 生产配置 | docker-compose.prod.yaml | 第10.2章 |
| 监控维护 | DEPLOYMENT_STATUS.md | 第10.4章 |
| 故障排除 | RESOURCES_INDEX.md | 第10.5章 |

#### ❓ 问题和参考

| 想要 | 文档位置 | 笔记本章节 |
|------|--------|----------|
| 常见问题 | NOTEBOOK_NAVIGATION.md | 第11.3章 |
| 命令参考 | 本文件 | 第11.1章 |
| 环境变量 | config.example.yaml | 第11.4章 |
| 性能优化 | docs/DEPLOYMENT_GUIDE.md | 第11.5章 |

---

## 🔑 关键文件和功能地图

### 核心应用文件

```
后端核心 (backend/packages/harness/deerflow/)
├── agents/lead_agent.py          Lead Agent 实现
├── agents/middleware.py           中间件链
├── agents/memory.py               内存管理系统
├── sandbox/local.py               本地沙箱 (开发)
├── sandbox/aio.py                 异步沙箱 (生产)
├── mcp/client.py                  MCP 集成
├── models/config.py               配置管理
└── checkpoint/multi_tenant.py     多租户检查点 ⭐ (新增)

前端核心 (frontend/src/)
├── app/page.tsx                   主页
├── components/ChatWindow.tsx       聊天窗口
├── core/api.ts                    API 调用
├── core/hooks/                    自定义 Hooks
└── core/types.ts                  类型定义

网关 (backend/app/gateway/)
├── app.py                         FastAPI 应用
├── api/                           API 端点
├── routers/                       路由模块
└── middleware/tenant.py           多租户中间件 ⭐ (新增)
```

### 配置文件

```
config.yaml                 ✅ 应用配置 (已创建)
├── app                     应用设置
├── model                   模型配置
├── sandbox                 沙箱配置
├── memory                  内存设置
└── checkpoint              检查点设置

.env (backend/)             ✅ 环境变量 (已创建)
├── OPENAI_API_KEY
├── DATABASE_URL
├── REDIS_URL
└── ...

.env.local (frontend/)      ✅ 环境变量 (已创建)
├── NEXT_PUBLIC_BACKEND_BASE_URL
└── BETTER_AUTH_SECRET
```

### Docker 文件

```
docker-compose-dev.yaml     开发环境
├── langgraph 服务          (端口 2024)
├── gateway 服务            (端口 8001)
└── frontend 服务           (端口 3000)

docker-compose.prod.yaml    ⭐ 生产环境 (新增)
├── postgres 数据库
├── redis 缓存
├── backend 服务
├── frontend 服务
└── nginx 负载均衡
```

---

## 📊 统计信息

### 代码量

| 组件 | 文件数 | 代码行数 | 语言 |
|------|--------|---------|------|
| 后端 | 150+ | 15,000+ | Python |
| 前端 | 80+ | 8,000+ | TypeScript/JSX |
| 测试 | 40+ | 5,000+ | Python |
| 文档 | 30+ | 25,000+ | Markdown |
| 配置 | 15+ | 2,000+ | YAML/JSON |

### 依赖

| 类型 | 数量 | 备注 |
|------|------|------|
| Python 包 | 187 | 通过 uv 管理 |
| Node 包 | 936 | 通过 pnpm 管理 |
| 系统依赖 | 5+ | Python, Node, Nginx 等 |

### 测试覆盖

| 类型 | 数量 | 覆盖率 |
|------|------|--------|
| 单元测试 | 250+ | 80%+ |
| 集成测试 | 27+ | 核心功能 |
| 端到端测试 | 可选 | - |

---

## 🔄 文件更新历史

### 新创建 (2026-04-01)

✅ `config.yaml` - 应用配置  
✅ `backend/.env` - 后端环境变量  
✅ `frontend/.env.local` - 前端环境变量  
✅ `start-dev-services.ps1` - 启动脚本  
✅ `QUICKSTART.md` - 快速开始  
✅ `COMPLETE_DEVELOPMENT_GUIDE.md` - 完整指南  
✅ `DEPLOYMENT_STATUS.md` - 部署状态  
✅ `LOCAL_DEVELOPMENT.md` - 本地开发  
✅ `RESOURCES_INDEX.md` - 资源索引  
✅ `SETUP_COMPLETE.md` - 设置报告  
✅ `backend/data/` - 数据目录  
✅ `backend/logs/` - 日志目录  

### 笔记本新增章节 (2026-04-01)

✅ 第8章 - 本地开发进阶指南 (1000+ 行)  
✅ 第9章 - 多租户实现指南 (1200+ 行)  
✅ 第10章 - 生产部署指南 (1500+ 行)  
✅ 第11章 - 快速参考和 FAQ (1200+ 行)  

### 新增导航文档 (2026-04-01)

✅ `NOTEBOOK_COMPLETION_SUMMARY.md` - 完成总结  
✅ `NOTEBOOK_NAVIGATION.md` - 导航指南  
✅ `PROJECT_STRUCTURE_MAP.md` - 本文件  

---

## ⚡ 快速访问命令

### 打开重要文件

```powershell
# 打开笔记本
code .\DeerFlow-Deployment-Notebook.ipynb

# 打开配置
code .\config.yaml
code .\backend\.env
code .\frontend\.env.local

# 打开快速参考
code .\QUICKSTART.md
code .\NOTEBOOK_NAVIGATION.md
```

### 查看目录

```powershell
# 列出所有文档
Get-ChildItem *.md

# 列出后端文件
Get-ChildItem .\backend -Recurse -Filter "*.py" | Select-Object FullName

# 列出前端文件
Get-ChildItem .\frontend\src -Recurse -Filter "*.tsx" | Select-Object FullName
```

### 启动服务

```powershell
# 使用启动脚本
.\start-dev-services.ps1

# 或手动启动
make dev
```

---

## 📚 推荐阅读顺序

1. 📄 本文件（项目结构）
2. 📄 NOTEBOOK_NAVIGATION.md（导航指南）
3. 📓 DeerFlow-Deployment-Notebook.ipynb（主笔记本）
4. 📄 QUICKSTART.md（快速开始）
5. 📄 COMPLETE_DEVELOPMENT_GUIDE.md（完整指南）

---

## 🎯 下一步

根据你的角色选择：

**我想快速启动项目**
→ 执行 `.\start-dev-services.ps1`

**我想学习开发**
→ 打开笔记本，阅读第8章

**我想实现多租户**
→ 打开笔记本，阅读第9章

**我想部署到生产**
→ 打开笔记本，阅读第10章

**我遇到问题**
→ 查看笔记本第11章的 FAQ

---

**生成日期**: 2026-04-01  
**版本**: 1.0  
**更新者**: DeerFlow 团队
