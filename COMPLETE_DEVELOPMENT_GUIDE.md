# DeerFlow 完整开发指南

**最后更新**: 2026-04-01  
**版本**: v1.0  
**适用于**: Windows 10/11 PowerShell 环境

---

## 目录

1. [快速开始](#快速开始)
2. [项目架构](#项目架构)
3. [本地开发](#本地开发)
4. [部署配置](#部署配置)
5. [API 开发](#api-开发)
6. [前端开发](#前端开发)
7. [测试和调试](#测试和调试)
8. [常见问题](#常见问题)

---

## 快速开始

### 一键启动所有服务

```powershell
# 从项目根目录运行
.\start-dev-services.ps1
```

这将在三个独立的 PowerShell 窗口中启动:
- **LangGraph** (端口 2024)
- **Gateway API** (端口 8001)
- **Next.js 前端** (端口 3000)

### 手动启动服务

**终端 1 - LangGraph 服务**:
```powershell
cd backend
.\.venv\Scripts\python.exe -m langgraph dev --no-browser --allow-blocking --no-reload
```

**终端 2 - Gateway API**:
```powershell
cd backend
$env:OPENAI_API_KEY = "your-api-key"
.\.venv\Scripts\python.exe -m uvicorn app.gateway.app:app --host 127.0.0.1 --port 8001
```

**终端 3 - Frontend**:
```powershell
cd frontend
pnpm dev
```

### 验证所有服务运行

```powershell
# 测试 LangGraph
curl http://localhost:2024/health

# 测试 Gateway
curl http://localhost:8001/health

# 访问前端
Start-Process http://localhost:3000
```

---

## 项目架构

### 整体架构

```
┌────────────────────────────────────────────────┐
│           DeerFlow 本地开发环境                 │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  Next.js     │  │   Nginx      │           │
│  │  前端        │  │   反向代理    │           │
│  │ (端口 3000)  │  │  (端口 2026)  │           │
│  └──────┬───────┘  └──────┬───────┘           │
│         │                 │                   │
│         └────────┬────────┘                   │
│                  │                            │
│        ┌─────────▼─────────┐                 │
│        │  FastAPI Gateway  │                 │
│        │  (端口 8001)       │                 │
│        └─────────┬─────────┘                 │
│                  │                            │
│        ┌─────────▼─────────┐                 │
│        │  LangGraph API    │                 │
│        │  (端口 2024)      │                 │
│        └─────────┬─────────┘                 │
│                  │                            │
│   ┌──────────────┴──────────────┐            │
│   │                             │            │
│   ▼                             ▼            │
│ ┌─────────────┐        ┌────────────────┐   │
│ │  Agent      │        │  Sandbox       │   │
│ │  Executor   │        │  (Local)       │   │
│ └─────────────┘        └────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │         Data Persistence             │   │
│  │  ├─ Memory: .deer-flow/memory.json   │   │
│  │  ├─ Checkpoints: .deer-flow/db/      │   │
│  │  └─ File Storage: .deer-flow/threads/│   │
│  └──────────────────────────────────────┘   │
│                                              │
└────────────────────────────────────────────────┘
```

### 核心组件

#### 1. LangGraph (端口 2024)

**功能**:
- Agent 编排和执行
- 对话状态管理
- 工具调用处理
- 流式响应支持

**配置文件**: `backend/langgraph.json`

**核心代码**:
```python
# backend/packages/harness/deerflow/agents/
├── lead_agent.py       # 主 Agent 定义
├── middleware.py       # 中间件链
├── memory.py          # 记忆系统
└── checkpointer/      # 状态持久化
```

#### 2. FastAPI Gateway (端口 8001)

**功能**:
- REST API 提供
- 请求路由和验证
- 文件上传处理
- 后端逻辑编排

**核心端点**:
```
GET/POST  /api/threads                    # 线程管理
GET/POST  /api/threads/{id}/messages      # 消息管理
POST      /api/threads/{id}/uploads       # 文件上传
GET       /api/artifacts                  # 工件查询
GET       /health                         # 健康检查
```

**配置**: `backend/.env`

#### 3. Next.js 前端 (端口 3000)

**功能**:
- Web UI 界面
- 实时消息流式显示
- 文件上传和预览
- API 交互

**核心页面**:
```
src/app/
├── page.tsx                 # 主页
├── threads/[id]/page.tsx    # 对话页面
├── artifacts/page.tsx       # 工件管理
└── api/                     # API 路由
```

**配置**: `frontend/.env.local`

---

## 本地开发

### 开发工作流

#### 1. 后端开发

**启动热重载模式**:
```powershell
cd backend
.\.venv\Scripts\python.exe -m langgraph dev
```

**代码修改会自动重新加载**。修改以下文件后立即生效:
- `backend/packages/harness/deerflow/agents/` - Agent 逻辑
- `backend/app/gateway/` - API 端点
- `backend/langgraph.json` - 配置

#### 2. 前端开发

**启动 Turbopack 开发模式**:
```powershell
cd frontend
pnpm dev
```

**特性**:
- 模块级 HMR (Hot Module Replacement)
- 极快的编译速度
- 内置 TypeScript 支持
- Tailwind CSS 实时编译

#### 3. API 文档

**自动生成的 API 文档**:
- Swagger UI: http://localhost:2024/docs
- ReDoc: http://localhost:2024/redoc

**测试 API**:
```powershell
# 创建对话线程
$body = @{ "user_id" = "test-user" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/threads" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"

# 发送消息
$msg = @{ "content" = "Hello!" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/threads/{thread_id}/messages" `
  -Method POST `
  -Body $msg `
  -ContentType "application/json"
```

---

## 部署配置

### 配置文件说明

#### 1. `config.yaml` (应用配置)

```yaml
config_version: 4
log_level: info

# 模型配置
models:
  - name: gpt-4-turbo
    display_name: GPT-4 Turbo
    use: langchain_openai:ChatOpenAI
    model: gpt-4-turbo
    api_key: $OPENAI_API_KEY
    supports_vision: true

# 沙箱配置 (开发使用 local，生产使用 aio)
sandbox:
  type: local
  
# 记忆配置
memory:
  type: file
  file_path: ./.deer-flow/memory.json
  
# 持久化配置
checkpoint:
  type: sqlite
  db_path: ./.deer-flow/checkpoints.db
```

#### 2. `backend/.env` (后端环境变量)

```env
# API 密钥
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...

# 数据库
DATABASE_URL=sqlite:///./deer-flow.db

# Redis (可选)
REDIS_URL=redis://localhost:6379

# 应用设置
DEBUG=false
LOG_LEVEL=info
PYTHONUNBUFFERED=1
```

#### 3. `frontend/.env.local` (前端环境变量)

```env
# Auth
BETTER_AUTH_SECRET=your-secret-key

# API 地址
NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8001
NEXT_PUBLIC_LANGGRAPH_BASE_URL=http://localhost:2024

# 环境
NODE_ENV=development
```

### 多租户配置

DeerFlow 支持单实例多租户架构。配置方式:

```yaml
# config.yaml
multi_tenancy:
  enabled: true
  tenants:
    - id: tenant-a
      name: Company A
      memory_file: ./.deer-flow/memory-tenant-a.json
    - id: tenant-b
      name: Company B
      memory_file: ./.deer-flow/memory-tenant-b.json
```

---

## API 开发

### 创建新的 API 端点

**位置**: `backend/app/gateway/`

**示例 - 添加自定义端点**:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/custom", tags=["custom"])

class CustomRequest(BaseModel):
    content: str

@router.post("/analyze")
async def analyze_content(request: CustomRequest):
    """分析内容的自定义端点"""
    try:
        # 你的业务逻辑
        result = await process_content(request.content)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**注册端点** - 在 `backend/app/gateway/app.py` 中:

```python
from .routers.custom import router as custom_router

app.include_router(custom_router)
```

### 调用 LangGraph Agent

```python
from deerflow.agents import make_lead_agent

async def call_agent(thread_id: str, message: str):
    agent = make_lead_agent()
    
    input_data = {
        "messages": [{"role": "user", "content": message}],
        "thread_id": thread_id
    }
    
    async for event in agent.astream(input_data):
        yield event
```

---

## 前端开发

### 项目结构

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx            # 主页
│   │   ├── layout.tsx          # 根布局
│   │   ├── threads/
│   │   │   └── [id]/page.tsx   # 对话详情页
│   │   └── api/                # API 路由
│   │
│   ├── components/             # React 组件
│   │   ├── ChatWindow.tsx
│   │   ├── MessageList.tsx
│   │   └── FileUpload.tsx
│   │
│   ├── core/                   # 核心逻辑
│   │   ├── api.ts              # API 客户端
│   │   ├── store.ts            # 状态管理
│   │   └── hooks/              # React Hooks
│   │
│   └── env.js                  # 环境验证
│
├── public/                     # 静态资源
├── tsconfig.json              # TypeScript 配置
└── next.config.js             # Next.js 配置
```

### 创建新组件

```typescript
// src/components/MyComponent.tsx
'use client';

import { useState } from 'react';

interface MyComponentProps {
  title: string;
}

export function MyComponent({ title }: MyComponentProps) {
  const [count, setCount] = useState(0);
  
  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold">{title}</h1>
      <button 
        onClick={() => setCount(count + 1)}
        className="px-4 py-2 bg-blue-500 text-white rounded"
      >
        Count: {count}
      </button>
    </div>
  );
}
```

### 调用后端 API

```typescript
// src/core/api.ts
const API_BASE = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;

export async function createThread(userId: string) {
  const response = await fetch(`${API_BASE}/api/threads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  });
  
  if (!response.ok) throw new Error('Failed to create thread');
  return response.json();
}

export async function sendMessage(threadId: string, content: string) {
  const response = await fetch(
    `${API_BASE}/api/threads/${threadId}/messages`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    }
  );
  
  if (!response.ok) throw new Error('Failed to send message');
  return response.json();
}
```

---

## 测试和调试

### 后端测试

**运行所有测试**:
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

**运行特定测试**:
```powershell
# 运行单个文件
pytest tests/test_artifacts_router.py -v

# 运行特定测试函数
pytest tests/test_artifacts_router.py::test_create_artifact -v

# 运行匹配的测试
pytest tests/ -k "config" -v
```

**调试模式**:
```powershell
# 进入 pdb 调试器
pytest tests/test_file.py -v --pdb

# 显示详细的输出信息
pytest tests/test_file.py -v -s
```

### 前端测试

**TypeScript 检查**:
```powershell
cd frontend
pnpm typecheck
```

**ESLint 检查**:
```powershell
pnpm lint
```

**修复代码格式**:
```powershell
pnpm lint:fix
```

**构建生产版本**:
```powershell
$env:BETTER_AUTH_SECRET = "your-secret"
pnpm build
```

### 调试技巧

#### 后端调试

**查看请求日志**:
```python
# backend/app/gateway/middleware.py
import logging
logger = logging.getLogger(__name__)

logger.info(f"Received request: {request.url}")
logger.debug(f"Request body: {request.body}")
```

**添加断点** (使用 VS Code):
1. 在 Python 代码中添加 `breakpoint()`
2. 在调试终端中运行服务
3. 调试器会在断点处暂停

#### 前端调试

**浏览器开发者工具**:
- F12 打开开发者工具
- Network 标签查看 API 调用
- Console 标签查看日志
- Sources 标签设置断点

**React DevTools**:
- 安装浏览器扩展
- 检查组件树和状态

---

## 常见问题

### Q1: "config.yaml not found" 错误

**原因**: 配置文件不存在  
**解决**:
```powershell
Copy-Item config.example.yaml config.yaml
```

### Q2: 端口被占用

**查找占用进程**:
```powershell
Get-NetTCPConnection -LocalPort 8001 | Select-Object -Property OwningProcess
```

**终止进程**:
```powershell
Stop-Process -Id <PID> -Force
```

### Q3: 模块导入错误

**原因**: PYTHONPATH 未正确设置  
**解决**:
```powershell
$env:PYTHONPATH = "D:\path\to\backend"
```

### Q4: 前端无法连接后端

**检查**:
1. Gateway 是否运行: `curl http://localhost:8001/health`
2. `.env.local` 中的 URL 是否正确
3. CORS 配置是否允许前端域名

### Q5: 测试运行缓慢

**优化**:
```powershell
# 只运行快速测试
pytest tests/ -m "not slow" -v

# 并行运行
pytest tests/ -n auto -v  # 需要 pytest-xdist
```

### Q6: 内存占用过高

**可能原因**:
- LangGraph 缓存太多数据
- 前端包过大
- Node.js 堆大小不足

**解决**:
```powershell
# 增加 Node.js 堆大小
$env:NODE_OPTIONS = "--max-old-space-size=4096"
pnpm dev
```

---

## 性能优化建议

### 后端优化
1. **缓存**: 使用 Redis 缓存频繁查询
2. **异步**: 使用 async/await 处理 I/O
3. **连接池**: 配置数据库连接池
4. **日志级别**: 生产环境使用 WARNING 级别

### 前端优化
1. **代码分割**: Next.js 自动处理
2. **图片优化**: 使用 next/image 组件
3. **缓存**: 配置适当的 Cache-Control
4. **CDN**: 生产环境使用 CDN 加速

---

## 资源链接

- **项目文档**: `docs/`
- **部署指南**: `docs/DEPLOYMENT_GUIDE.md`
- **API 文档**: http://localhost:2024/docs
- **LangGraph 文档**: https://langchain-ai.github.io/langgraph/
- **Next.js 文档**: https://nextjs.org/docs

---

**最后更新**: 2026-04-01  
**维护者**: DeerFlow 团队  
**许可证**: MIT
