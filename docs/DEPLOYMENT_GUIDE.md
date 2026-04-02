# DeerFlow 企业级部署指南

## 版本信息

- **文档版本**: v1.0

- **适用DeerFlow版本**: main branch (2026-03-30)

- **目标平台**: 阿里云 ECS / 腾讯云 CVM

- **部署模式**: 单实例多租户

---

## 0. DeerFlow 架构特性详解

### 0.1 核心架构组件

DeerFlow 是一个全栈 "超级代理框架"，包含以下核心组件：

**后端 (Python 3.12 + FastAPI + LangGraph)**：

- **LangGraph + FastAPI 网关**：基于 LangGraph 的代理编排和 FastAPI 的 API 网关

- **沙箱/工具系统**：支持本地执行 (LocalSandbox) 和容器隔离 (AioSandbox)

- **记忆系统**：基于文件的记忆存储，支持多租户隔离

- **MCP 集成**：Model Context Protocol 集成，支持外部工具调用

- **子代理系统**：支持主代理与子代理的协作

**前端 (Next.js 16 + React 19 + TypeScript)**：

- **Web 界面**：基于 Next.js 的现代化前端

- **实时交互**：支持流式响应和实时更新

### 0.2 沙箱系统架构

DeerFlow 提供两种沙箱实现：

**1. LocalSandboxProvider (本地执行)**：

- **原理**：直接在主机上执行命令，无容器隔离

- **适用场景**：开发环境、信任的单用户环境

- **路径映射**：支持容器路径到本地路径的映射

- **安全性**：较低，建议仅在受信任环境中使用

**2. AioSandboxProvider (容器隔离)**：

- **原理**：使用 Docker 容器提供隔离环境

- **适用场景**：生产环境、多租户场景

- **特性**：
  - 支持配置哈希检查，配置变更时自动重建容器
  - 热容器复用 (5分钟内使用的容器)
  - 通过标签管理容器元数据
  - 支持远程/K8s 模式 (通过 provisioner)

### 0.3 记忆系统架构

**记忆存储**：

- **FileMemoryStorage**：基于文件的记忆存储

- **全局共享**：默认所有用户共享同一份记忆数据

- **多租户隔离**：通过配置可实现按租户分文件存储

**记忆注入**：

- **自动注入**：将记忆事实注入到系统提示中

- **Token 限制**：默认 2000 tokens，可配置

- **置信度阈值**：默认 0.7，低于阈值的事实不注入

### 0.4 检查点系统架构

**状态持久化**：

- **InMemorySaver**：内存模式 (默认，重启丢失)

- **SqliteSaver**：SQLite 文件存储

- **PostgresSaver**：PostgreSQL 数据库存储

**线程隔离**：

- **thread_id**：每个对话线程有唯一 ID

- **多租户支持**：通过 thread_id 前缀实现租户隔离

### 0.5 飞书通道架构

**连接机制**：

- **单长连接**：整个 DeerFlow 实例只有一个飞书 WebSocket 长连接

- **消息路由**：通过 chat_id 和 sender_id 路由到对应线程

- **无公网 IP**：WebSocket 模式无需公网 IP

**消息流程**：

1. 用户发送消息 → 飞书服务器 → WebSocket 连接

2. 解析 chat_id, sender_id, msg_id

3. 创建 InboundMessage 发布到 MessageBus

4. 路由到对应 thread_id 的 Agent

5. Agent 处理并回复

6. 通过飞书 API 发送到对应 chat_id

### 0.6 文件读取机制

**文件上传流程**：

1. 客户端上传文件到 `/api/threads/{thread_id}/uploads`

2. Gateway 接收文件并存储到 `.deer-flow/threads/{thread_id}/user-data/uploads/`

3. 返回虚拟路径 `/mnt/user-data/uploads/{filename}`

4. Agent 通过虚拟路径访问文件

**沙箱文件访问**：

- **LocalSandbox**：通过路径映射访问主机文件

- **AioSandbox**：通过 volume 挂载访问容器内文件

**文件权限**：

- **读写权限**：沙箱内进程需要读写权限

- **安全考虑**：建议使用只读挂载，限制写入范围

### 0.7 多租户共享场景

**优势**：

- **Token 节省**：共享记忆减少重复解释

- **知识复用**：团队知识库被所有成员使用

- **算力池化**：容器复用减少资源浪费

- **任务进度共享**：协作项目可共享进度

**劣势**：

- **数据安全**：无租户隔离存在泄露风险

- **资源争抢**：无配额限制可能资源耗尽

- **配置冲突**：全局配置无法定制化

- **记忆污染**：全局记忆可能泄露敏感信息

**推荐方案**：

- **单租户部署**：每个公司独立部署实例

- **多租户改造**：需要修改代码实现租户隔离

### 0.8 部署模式对比

| 特性 | LocalSandbox | AioSandbox | Railway | 云服务器 |
| :--- | :----------- | :--------- | :------ | :------- |
| **隔离级别** | 无隔离 | 容器级 | 无 Docker | 容器级 |
| **Docker 依赖** | 无需 | 必需 | 不支持 | 必需 |
| **部署复杂度** | 低 | 中 | 低 | 中 |
| **资源占用** | 低 | 高 | 中 | 高 |
| **推荐场景** | 开发环境 | 生产环境 | 测试环境 | 生产环境 |

---

## 一、架构概述

### 1.1 部署模式定义

**单实例多租户架构**：

```text
┌─────────────────────────────────────────────────────────────┐
│                      阿里云ECS / 腾讯云CVM                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              DeerFlow 实例 (Docker Compose)          │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │  │
│  │  │  nginx  │ │frontend │ │gateway  │ │langgraph│   │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │  │
│  │       │           │           │           │          │  │
│  │       └───────────┴───────────┴───────────┘          │  │
│  │                                                       │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │          数据持久化目录 (/data/deer-flow)       │ │  │
│  │  │  ┌─────────────┐  ┌─────────────┐             │ │  │
│  │  │  │ .deer-flow/ │  │   threads/  │             │ │  │
│  │  │  │ ├─ memory.json│  │ ├─ tenant-a/│             │ │  │
│  │  │  │ ├─ checkpoints.db│ │ ├─ tenant-b/│             │ │  │
│  │  │  │ └─ config.yaml│  │ └─ ...      │             │ │  │
│  │  │  └─────────────┘  └─────────────┘             │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │
         │ WebSocket (无公网IP需求)
         ↓
    ┌──────────────┐
    │   飞书服务器  │
    └──────────────┘

```text
### 1.2 核心组件说明

| 组件 | 服务名 | 端口 | 说明 |
| :--- | :----- | :--- | :--- |
| Nginx | nginx | 2026 (公网) | 反向代理，统一入口 |
| 前端 | frontend | 3000 (内网) | Next.js 生产服务器 |
| 网关 | gateway | 8001 (内网) | FastAPI Gateway，处理API请求 |
| 图服务 | langgraph | 2024 (内网) | LangGraph 服务器 |
| 沙箱 | sandbox | 动态 | Docker容器（按需创建） |
| 预配器 | provisioner | 8002 (可选) | Kubernetes沙箱预配 |

### 1.3 数据隔离策略

**租户隔离层级**：

1. **Memory（记忆系统）**：按租户分文件存储
   ```text
   .deer-flow/
   ├── memory.json              # 全局共享知识（可选）
   ├── memory-tenant-a.json     # 租户A的私有记忆
   ├── memory-tenant-b.json     # 租户B的私有记忆
   └── memory-tenant-c.json
   ```text
2. **Checkpointer（状态持久化）**：thread_id加租户前缀
   ```text
   checkpoints.db (SQLite)
   └── checkpoint_blobs
       ├── tenant-a:thread-uuid-1
       ├── tenant-a:thread-uuid-2
       ├── tenant-b:thread-uuid-3
       └── ...
   ```text
3. **文件存储**：按租户组织目录
   ```text
   threads/
   ├── tenant-a/
   │   ├── thread-uuid-1/
   │   │   └── user-data/
   │   │       ├── workspace/
   │   │       ├── uploads/
   │   │       └── outputs/
   │   └── thread-uuid-2/
   └── tenant-b/
       └── ...
   ```text
4. **沙箱容器**：按租户前缀命名（可选）
   ```text
   deer-flow-sandbox-tenant-a-xxxx
   deer-flow-sandbox-tenant-b-yyyy
   ```text
---

## 二、环境准备（阿里云ECS / 腾讯云CVM）

### 2.1 服务器选型建议

| 场景 | CPU | 内存 | 磁盘 | 带宽 | 参考价格（月） |
| :--- | :-- | :--- | :--- | :--- | :------------ |
| 小型团队（<20人） | 2核 | 4GB | 100GB SSD | 5Mbps | ¥50-100 |
| 中型团队（20-100人） | 4核 | 8GB | 200GB SSD | 10Mbps | ¥150-300 |
| 大型团队（>100人） | 8核 | 16GB | 500GB SSD | 20Mbps | ¥400-800 |

**推荐配置**：

- 操作系统：Ubuntu 22.04 LTS 或 CentOS 8 Stream

- Docker：20.10+

- 内核：启用cgroup v2（Docker和沙箱需要）

### 2.2 系统初始化

```bash
# 1. 登录服务器

ssh root@your-server-ip

# 2. 更新系统

apt update && apt upgrade -y  # Ubuntu
# 或
yum update -y                # CentOS

# 3. 设置时区

timedatectl set-timezone Asia/Shanghai

# 4. 安装基础工具

apt install -y curl wget git vim htop tree sudo  # Ubuntu
# 或
yum install -y curl wget git vim htop tree sudo  # CentOS

# 5. 配置防火墙（Ubuntu with ufw）

ufw allow 22/tcp    # SSH
ufw allow 2026/tcp  # DeerFlow主端口
ufw enable
ufw status

# 6. 创建部署用户（可选，建议用root简化）

useradd -m -s /bin/bash deploy
echo "deploy ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

```text

### 2.3 安装Docker

```bash
# 使用官方安装脚本（推荐）
curl -fsSL <https://get.docker.com> | sh

# 或手动安装（Ubuntu）
apt install -y docker.io docker-compose-plugin

# 启动Docker
systemctl enable docker
systemctl start docker

# 验证安装
docker --version
docker compose version

# 配置Docker守护进程（镜像加速、数据根目录）
cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "<https://docker.mirrors.ustc.edu.cn>",
    "<https://hub-mirror.c.163.com>",
    "<https://mirror.baidubce.com>"
  ],
  "data-root": "/var/lib/docker",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "exec-opts": ["native.cgroupdriver=systemd"],
  "storage-driver": "overlay2"
}
EOF

systemctl restart docker

# 测试Docker
docker run --rm hello-world

```text

### 2.4 安装Docker Compose

```bash
# Docker Compose v2已包含在docker-compose-plugin中
# 验证
docker compose version

# 如果需单独安装（旧版本）
curl -L "<https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname> -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

```text

### 2.5 安装Node.js和PNPM（可选，用于前端构建）

如果使用生产镜像（前端已构建），可跳过此步。

```bash
# 安装Node.js 22
curl -fsSL <https://deb.nodesource.com/setup_22.x> | bash -
apt install -y nodejs

# 验证
node --version  # 应显示 v22.x
npm --version

# 安装PNPM
corepack enable
corepack install pnpm@10.26.2
pnpm --version

```text

### 2.6 安装Python和UV（可选，用于后端开发）

如果使用生产镜像（后端已构建），可跳过此步。

```bash
# Ubuntu
apt install -y python3 python3-pip python3-venv

# 安装UV（Python包管理器）
curl -LsSf <https://astral.sh/uv/install.sh> | sh
source $HOME/.cargo/env
uv --version

# CentOS可能需要先安装rustc
# yum install -y rustc

```text

---

## 三、目录规划与权限设置

### 3.1 目录结构设计

```text
/data/deer-flow/                    # DEER_FLOW_HOME（主数据目录）
├── .deer-flow/                     # DeerFlow运行时数据
│   ├── config.yaml                 # 配置文件（从/etc/deer-flow/软链接或复制）
│   ├── extensions_config.json      # 扩展配置
│   ├── memory-tenant-a.json        # 租户A记忆数据
│   ├── memory-tenant-b.json        # 租户B记忆数据
│   ├── memory-shared.json          # 全局共享记忆（可选）
│   ├── checkpoints.db              # SQLite状态数据库
│   ├── logs/                       # 日志目录（如果挂载）
│   │   ├── gateway.log
│   │   ├── langgraph.log
│   │   └── frontend.log
│   └── skills/                     # 技能库（只读挂载）
├── tenants/                        # 租户数据隔离（可选扩展）
│   ├── tenant-a/
│   │   ├── threads/               # 线程数据
│   │   └── uploads/               # 上传文件
│   └── tenant-b/
└── backup/                         # 备份目录
    ├── full-20260330.tar.gz
    └── incremental/

```text

### 3.2 创建目录和用户

```bash
# 1. 创建专用用户和组（推荐）

groupadd -r deerflow
useradd -r -g deerflow -d /data/deer-flow -s /sbin/nologin deerflow

# 2. 创建数据目录

mkdir -p /data/deer-flow/.deer-flow/{skills,logs}
mkdir -p /data/deer-flow/tenants
mkdir -p /data/deer-flow/backup

# 3. 设置目录权限

chown -R deerflow:deerflow /data/deer-flow
chmod -R 755 /data/deer-flow

# 4. 设置目录权限（特殊目录）

chmod 700 /data/deer-flow/.deer-flow  # 敏感数据限制访问
chmod 750 /data/deer-flow/tenants     # 组可读

# 5. 将deerflow用户加入docker组（用于DooD模式）

usermod -aG docker deerflow

# 6. 验证权限

ls -ld /data/deer-flow
ls -la /data/deer-flow/.deer-flow/

```text

### 3.3 持久化存储配置

如果使用独立磁盘（如云盘）：

```bash
# 1. 格式化为ext4（首次）

mkfs.ext4 /dev/vdb  # 根据实际设备名调整

# 2. 挂载到/data/deer-flow

mkdir -p /data/deer-flow
mount /dev/vdb /data/deer-flow

# 3. 写入fstab实现开机自动挂载

echo "/dev/vdb /data/deer-flow ext4 defaults,noatime 0 2" >> /etc/fstab

# 4. 设置目录权限（重复3.2步骤）

chown -R deerflow:deerflow /data/deer-flow

```text

---

## 四、配置文件详解

### 4.1 生成初始配置

```bash
# 1. 创建部署目录

mkdir -p /opt/deer-flow
cd /opt/deer-flow

# 2. 克隆仓库

git clone <https://github.com/bytedance/deer-flow.git> .
# 或下载release包
# wget <https://github.com/bytedance/deer-flow/archive/refs/tags/v2.0.0.tar.gz>

# 3. 生成配置文件

make config

# 4. 配置文件位置

#   /opt/deer-flow/config.yaml              # 主配置
#   /opt/deer-flow/extensions_config.example.json  # 扩展配置示例

```text

### 4.2 config.yaml 完整配置示例

```yaml
# ============================================
# DeerFlow 企业部署配置文件
# ============================================

# 1. 日志配置

log_level: info  # debug/info/warning/error

# 2. 沙箱配置（推荐LocalSandboxProvider，更稳定）

sandbox:
  use: deerflow.sandbox.local:LocalSandboxProvider
  # 如果使用Docker沙箱（需要Docker socket）：
  # use: deerflow.community.aio_sandbox:AioSandboxProvider
  # image: enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest
  # replicas: 3                    # 最大并发容器数
  # idle_timeout: 600             # 空闲超时（秒）
  # container_prefix: deer-flow-sandbox
  allow_host_bash: false  # 安全考虑，禁止直接执行bash

# 3. 模型配置（以OpenAI为例）

models:
  - name: gpt-4-turbo
    display_name: GPT-4 Turbo
    use: langchain_openai:ChatOpenAI
    model: gpt-4-turbo-preview
    api_key: ${OPENAI_API_KEY}  # 从环境变量读取
    temperature: 0.7
    max_tokens: 4000
    supports_thinking: false
    supports_vision: true

  - name: claude-3-5-sonnet
    display_name: Claude 3.5 Sonnet
    use: langchain_anthropic:ChatAnthropic
    model: claude-3-5-sonnet-20241022
    api_key: ${ANTHROPIC_API_KEY}
    temperature: 0.7
    max_tokens: 4000
    supports_thinking: true
    supports_vision: true

# 4. 记忆系统配置（多租户关键）

memory:
  enabled: true
  # 存储路径：使用租户隔离的文件名模式
  # 实际路径会在运行时根据tenant_id动态计算
  storage_path: /data/deer-flow/.deer-flow/memory-{tenant}.json
  storage_class: deerflow.agents.memory.storage.FileMemoryStorage
  debounce_seconds: 30
  model_name: null  # 使用默认模型
  max_facts: 100
  fact_confidence_threshold: 0.7
  injection_enabled: true
  max_injection_tokens: 2000

# 5. 检查点配置（状态持久化）

checkpointer:
  type: sqlite
  connection_string: /data/deer-flow/.deer-flow/checkpoints.db
  # 如果使用PostgreSQL（生产推荐）：
  # type: postgres
  # connection_string: postgresql://user:pass@localhost:5432/deerflow

# 6. 技能配置

skills:
  path: /data/deer-flow/.deer-flow/skills  # 技能库路径
  container_path: /mnt/skills

# 7. 通道配置（飞书）

channels:
  langgraph_url: <http://localhost:2024>
  gateway_url: <http://localhost:8001>

  # 飞书通道配置
  feishu:
    enabled: true
    app_id: ${FEISHU_APP_ID}
    app_secret: ${FEISHU_APP_SECRET}
    # verification_token: ${FEISHU_VERIFICATION_TOKEN}  # 可选

  # Slack通道（可选）
  # slack:
  #   enabled: false
  #   bot_token: ${SLACK_BOT_TOKEN}
  #   app_token: ${SLACK_APP_TOKEN}

  # Telegram通道（可选）
  # telegram:
  #   enabled: false
  #   bot_token: ${TELEGRAM_BOT_TOKEN}

  # 会话默认配置
  session:
    assistant_id: lead_agent
    config:
      recursion_limit: 100
    context:
      thinking_enabled: true
      is_plan_mode: false
      subagent_enabled: false

# 8. 工具配置（可选）

tools: []
tool_groups: []

# 9. 标题生成配置

title:
  enabled: true
  max_words: 10
  max_chars: 60

# 10. 摘要配置

summarization:
  enabled: true

# 11. 子代理配置

subagents:
  enabled: true

# 12. MCP配置（在extensions_config.json中）

```text

### 4.3 extensions_config.json 配置

```json
{
  "mcpServers": {},
  "skills": {
    "enabled": true,
    "auto_install": false
  }
}

```text

### 4.4 .env 环境变量文件

```bash
# ============================================
# DeerFlow 生产环境环境变量
# ============================================

# 1. 必需：认证密钥（必须修改！）

BETTER_AUTH_SECRET=your-32-byte-hex-secret-here
# 生成方法：python3 -c 'import secrets; print(secrets.token_hex(32))'

# 2. LLM API Keys

OPENAI_API_KEY=sk-openai-...
ANTHROPIC_API_KEY=sk-ant-...
# 其他...

# 3. 飞书应用凭证

FEISHU_APP_ID=your-feishu-app-id
FEISHU_APP_SECRET=your-feishu-app-secret

# 4. 路径配置（根据实际部署调整）

DEER_FLOW_HOME=/data/deer-flow/.deer-flow
DEER_FLOW_CONFIG_PATH=/opt/deer-flow/config.yaml
DEER_FLOW_EXTENSIONS_CONFIG_PATH=/data/deer-flow/.deer-flow/extensions_config.json
DEER_FLOW_REPO_ROOT=/opt/deer-flow
DEER_FLOW_DOCKER_SOCKET=/var/run/docker.sock

# 5. 网络配置

DEER_FLOW_CHANNELS_LANGGRAPH_URL=<http://langgraph:2024>
DEER_FLOW_CHANNELS_GATEWAY_URL=<http://gateway:8001>

# 6. 可选：镜像加速（国内）

APT_MIRROR=mirrors.aliyun.com
NPM_REGISTRY=<https://registry.npmmirror.com>

# 7. 可选：LangSmith追踪（调试用）

LANGSMITH_TRACING=false
LANGSMITH_API_KEY=

# 8. 端口映射

PORT=2026

# 9. Docker Compose项目名

COMPOSE_PROJECT_NAME=deer-flow

```text

---

## 五、多租户配置实现（已完成）

### 5.1 多租户架构概述

DeerFlow 现已支持完整的多租户功能，提供企业级的数据隔离和租户管理能力。多租户功能已在第9章中完整实现，包括：

- ✅ **TenantMiddleware**: 租户识别中间件，支持多种租户识别方式
- ✅ **MultiTenantCheckpointer**: 多租户检查点存储，确保状态数据隔离
- ✅ **MultiTenantPaths**: 租户感知路径配置，自动生成租户隔离的目录结构
- ✅ **TenantAwareStorage**: 租户感知存储操作，提供文件级数据隔离
- ✅ **多租户API端点**: 更新后的threads路由器支持租户隔离的CRUD操作
- ✅ **完整测试覆盖**: 31个单元测试验证多租户功能

### 5.2 租户识别方式

系统支持多种租户识别方式，按优先级顺序尝试：

1. **HTTP Header**: `X-Tenant-ID` 请求头
2. **Query Parameter**: `tenant_id` 查询参数
3. **Subdomain**: 子域名提取（如 `tenant1.example.com` → `tenant1`）
4. **JWT Token**: JWT令牌中的 `tenant_id` 声明（需要认证中间件）

### 5.3 配置多租户功能

**1. 启用多租户功能**

在 `config.yaml` 中添加以下配置：

```yaml
multi_tenant:
  enabled: true
  
  identification:
    - header: "X-Tenant-ID"
    - query_param: "tenant_id"
    - subdomain: true
    - jwt_claim: "tenant_id"
  
  isolation:
    threads: true
    checkpoints: true
    files: true
    memory: true
  
  storage:
    base_dir: "data/tenants"
    thread_pattern: "threads/{tenant_id}/{thread_id}"
    checkpoint_pattern: "checkpoints/{tenant_id}"
    file_pattern: "files/{tenant_id}"
  
  tenants:
    - id: "tenant1"
      name: "Tenant 1"
      description: "First example tenant"
      config:
        models:
          - name: gpt-4-turbo
            max_tokens: 8192
        allowed_tools: ["file_read", "file_write", "web_search"]
        recursion_limit: 100
    
    - id: "tenant2"
      name: "Tenant 2"
      description: "Second example tenant"
      config:
        models:
          - name: stepfun-3.5-flash
            max_tokens: 16384
        allowed_tools: ["file_read", "web_search"]
        recursion_limit: 150
```

### 2. 环境变量配置

在 `.env.production` 中设置多租户环境变量：

```bash
# 启用多租户
DEER_FLOW_MULTI_TENANT_ENABLED=true
# 隔离级别：data|resource|strict
DEER_FLOW_TENANT_ISOLATION_LEVEL=strict
```

### 3. Docker Compose 配置

生产环境的 `docker-compose.yaml` 已包含多租户支持：

```yaml
environment:
  - DEER_FLOW_MULTI_TENANT_ENABLED=${DEER_FLOW_MULTI_TENANT_ENABLED:-true}
  - DEER_FLOW_TENANT_ISOLATION_LEVEL=${DEER_FLOW_TENANT_ISOLATION_LEVEL:-strict}
```

### 5.4 租户数据隔离

多租户功能提供完整的数据隔离：

**文件系统隔离**:
```text
data/tenants/
├── threads/
│   ├── tenant1/
│   │   └── thread-uuid-1/
│   │       └── user-data/
│   └── tenant2/
│       └── thread-uuid-2/
├── checkpoints/
│   ├── tenant1/
│   └── tenant2/
└── files/
    ├── tenant1/
    └── tenant2/
```

**数据库隔离**:

- 所有数据表包含 `tenant_id` 字段
- 查询自动过滤租户数据
- 跨租户访问被严格阻止

**检查点隔离**:

- 检查点存储按租户分离
- thread_id 自动包含租户前缀
- 租户间检查点完全隔离

### 5.5 租户管理

**创建租户**:

1. 在 `config.yaml` 的 `multi_tenant.tenants` 部分添加租户配置
2. 创建租户特定的数据目录（如果使用文件存储）
3. 为租户分配唯一的 `id` 和 `name`

**租户配置选项**:

- `id`: 租户唯一标识符（必需）
- `name`: 租户显示名称（必需）
- `description`: 租户描述（可选）
- `config`: 租户特定配置（可选）
  - `models`: 租户特定的模型配置覆盖
  - `allowed_tools`: 允许使用的工具列表
  - `recursion_limit`: 递归限制

### 5.6 API使用示例

**创建租户线程**:

```bash
# 方式1: 使用请求头
curl -X POST "http://localhost:2026/api/threads" \
  -H "X-Tenant-ID: tenant1" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# 方式2: 使用查询参数
curl -X POST "http://localhost:2026/api/threads?tenant_id=tenant1" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

**列出租户线程**:

```bash
curl -X GET "http://localhost:2026/api/threads" \
  -H "X-Tenant-ID: tenant1"
```

**租户隔离验证**:

```bash
# tenant1 无法访问 tenant2 的线程
curl -X GET "http://localhost:2026/api/threads/tenant2-thread-uuid" \
  -H "X-Tenant-ID: tenant1"
# 返回 404 或 403
```

### 5.7 生产环境多租户配置检查清单

- [ ] 在 `config.yaml` 中启用 `multi_tenant.enabled: true`
- [ ] 配置合适的租户识别方式（header/query/subdomain/jwt）
- [ ] 设置租户隔离级别（推荐 `strict`）
- [ ] 配置租户存储路径 `multi_tenant.storage.base_dir`
- [ ] 在 `config.yaml` 中定义租户列表 `multi_tenant.tenants`
- [ ] 在 `.env.production` 中设置 `DEER_FLOW_MULTI_TENANT_ENABLED=true`
- [ ] 设置 `DEER_FLOW_TENANT_ISOLATION_LEVEL` 环境变量
- [ ] 确保数据目录有足够的空间和权限
- [ ] 测试租户隔离功能（使用不同租户ID访问API）
- [ ] 配置租户特定的资源限制（可选）
- [ ] 设置租户级别的监控和日志（可选）
- [ ] 制定租户数据备份策略
- [ ] 准备租户创建和管理的自动化脚本

### 5.8 多租户运维注意事项

**数据备份**：

- 按租户组织备份数据
- 支持租户级别的数据恢复
- 定期验证备份完整性

**监控**：

- 监控各租户的资源使用情况
- 设置租户级别的告警阈值
- 记录租户操作日志

**安全**：

- 定期审计租户隔离机制
- 验证跨租户访问控制
- 加密敏感租户数据

**性能**：

- 监控租户数量对性能的影响
- 优化大租户的查询性能
- 考虑租户数据分片策略

---

## 六、部署步骤

### 6.1 一键部署脚本

创建`/opt/deer-flow/deploy.sh`：

```bash
#!/bin/bash
set -e

# ============================================
# DeerFlow 生产环境部署脚本
# ============================================

# 配置变量
REPO_ROOT="/opt/deer-flow"
DATA_DIR="/data/deer-flow"
COMPOSE_FILE="$REPO_ROOT/docker/docker-compose.yaml"
ENV_FILE="$REPO_ROOT/.env"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  DeerFlow 生产部署"
echo "=========================================="
echo ""

# 1. 检查环境

echo -e "${YELLOW}[1/7] 检查环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker未安装${NC}"
    exit 1
fi
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 环境检查通过${NC}"

# 2. 检查配置文件

echo -e "${YELLOW}[2/7] 检查配置文件...${NC}"
if [ ! -f "$REPO_ROOT/config.yaml" ]; then
    echo -e "${RED}✗ config.yaml不存在${NC}"
    echo "请先运行: make config"
    exit 1
fi
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠ .env文件不存在，从.example复制${NC}"
    cp "$REPO_ROOT/.env.example" "$ENV_FILE"
    echo "请编辑 $ENV_FILE 设置必要的环境变量"
fi
echo -e "${GREEN}✓ 配置文件检查通过${NC}"

# 3. 检查数据目录

echo -e "${YELLOW}[3/7] 检查数据目录...${NC}"
if [ ! -d "$DATA_DIR" ]; then
    echo -e "${YELLOW}⚠ 数据目录不存在，创建中...${NC}"
    mkdir -p "$DATA_DIR/.deer-flow"
    chown -R deerflow:deerflow "$DATA_DIR"
fi
echo -e "${GREEN}✓ 数据目录就绪${NC}"

# 4. 生成BETTER_AUTH_SECRET（如果未设置）

if ! grep -q "BETTER_AUTH_SECRET=" "$ENV_FILE" || grep -q "BETTER_AUTH_SECRET=your-" "$ENV_FILE"; then
    echo -e "${YELLOW}[4/7] 生成BETTER_AUTH_SECRET...${NC}"
    SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    sed -i "s/BETTER_AUTH_SECRET=.*/BETTER_AUTH_SECRET=$SECRET/" "$ENV_FILE"
    echo -e "${GREEN}✓ BETTER_AUTH_SECRET已生成${NC}"
else
    echo -e "${GREEN}✓ BETTER_AUTH_SECRET已设置${NC}"
fi

# 5. 检查多租户配置

echo -e "${YELLOW}[5/7] 检查多租户配置...${NC}"
if grep -q "DEER_FLOW_MULTI_TENANT_ENABLED=true" "$ENV_FILE"; then
    echo -e "${GREEN}✓ 多租户功能已启用${NC}"
    
    # 检查租户隔离级别
    if grep -q "DEER_FLOW_TENANT_ISOLATION_LEVEL=strict" "$ENV_FILE"; then
        echo -e "${GREEN}✓ 租户隔离级别: strict${NC}"
    elif grep -q "DEER_FLOW_TENANT_ISOLATION_LEVEL=resource" "$ENV_FILE"; then
        echo -e "${YELLOW}⚠ 租户隔离级别: resource (建议使用 strict)${NC}"
    else
        echo -e "${YELLOW}⚠ 租户隔离级别未设置 (默认: strict)${NC}"
    fi
    
    # 检查config.yaml中的多租户配置
    if [ -f "$REPO_ROOT/config.yaml" ]; then
        if grep -q "multi_tenant:" "$REPO_ROOT/config.yaml"; then
            echo -e "${GREEN}✓ config.yaml 包含多租户配置${NC}"
        else
            echo -e "${YELLOW}⚠ config.yaml 中缺少多租户配置${NC}"
            echo "  建议添加 multi_tenant 配置段"
        fi
    fi
else
    echo -e "${YELLOW}⚠ 多租户功能未启用 (可选)${NC}"
fi

# 6. 预拉取镜像（可选）

echo -e "${YELLOW}[6/8] 预拉取Docker镜像...${NC}"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull || true
echo -e "${GREEN}✓ 镜像拉取完成${NC}"

# 7. 启动服务

echo -e "${YELLOW}[7/8] 启动Docker服务...${NC}"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --remove-orphans
echo -e "${GREEN}✓ 服务启动中...${NC}"

# 8. 等待服务就绪

echo -e "${YELLOW}[8/8] 等待服务就绪...${NC}"
sleep 10

# 检查服务状态
if docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps | grep -q "unhealthy"; then
    echo -e "${RED}✗ 部分服务未健康启动${NC}"
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ DeerFlow部署完成！${NC}"
echo "=========================================="
echo ""
echo "访问地址："
echo "  前端：<http://your-server-ip:2026>"
echo "  API： <http://your-server-ip:2026/api/>"
echo ""
echo "查看日志："
echo "  docker compose -f $COMPOSE_FILE logs -f"
echo ""
echo "停止服务："
echo "  docker compose -f $COMPOSE_FILE down"
echo ""

```text

### 6.2 执行部署

```bash
# 1. 上传部署脚本

scp deploy.sh root@your-server-ip:/opt/deer-flow/
ssh root@your-server-ip "chmod +x /opt/deer-flow/deploy.sh"

# 2. 执行部署

ssh root@your-server-ip "/opt/deer-flow/deploy.sh"

# 3. 验证服务

curl <http://your-server-ip:2026/api/health>  # 如果有健康检查
# 或访问前端页面

```text

### 6.3 使用Docker Compose直接部署

```bash
cd /opt/deer-flow

# 1. 设置环境变量

export $(grep -v '^#' .env | xargs)

# 2. 启动服务

docker compose -f docker/docker-compose.yaml up -d

# 3. 查看状态

docker compose -f docker/docker-compose.yaml ps

# 4. 查看日志

docker compose -f docker/docker-compose.yaml logs -f gateway

```text

---

## 七、飞书通道配置

### 7.1 创建飞书应用

1. **登录飞书开放平台**
   - 访问：<https://open.feishu.cn/>
   - 使用企业管理员账号登录

2. **创建应用**
   - 点击"创建应用" → 选择"自建应用"
   - 应用类型：选择"机器人"
   - 填写应用名称、描述
   - 上传应用图标（可选）

3. **配置应用权限**
   - 在"权限管理"页面，添加以下权限：
     ```text
     必需权限：
     - im:read (读取消息)
     - im:write (发送消息)
     - im:message:send_as_bot (以Bot身份发送)
     
     可选权限（如需文件上传）：
     - drive:read (读取文件)
     - drive:write (上传文件)
     ```text
4. **配置事件订阅**
   - 在"事件订阅"页面：
     - 开启"接收消息"
     - 设置请求URL（暂时留空，后续配置）
     - 设置Token和EncodingAESKey（随机生成）
   

5. **获取App凭证**
   - 在"应用基本信息"页面：
     - 复制 `App ID`
     - 点击"显示"并复制 `App Secret`

6. **发布应用**
   - 在"版本管理与发布"页面
   - 添加版本描述，发布到"测试环境"或"正式环境"
   - 获取安装链接，邀请团队成员使用

### 7.2 配置DeerFlow

编辑 `/opt/deer-flow/.env`：

```bash
# 飞书应用凭证
FEISHU_APP_ID=your-app-id-here
FEISHU_APP_SECRET=your-app-secret-here

```text

编辑 `/opt/deer-flow/config.yaml`：

```yaml
channels:
  feishu:
    enabled: true
    app_id: ${FEISHU_APP_ID}
    app_secret: ${FEISHU_APP_SECRET}

```text

### 7.3 配置事件订阅URL

1. **获取公网访问地址**
   - 确保ECS安全组开放2026端口
   - 域名解析到ECS公网IP（推荐）
   - HTTPS证书（Let's Encrypt免费）

2. **配置飞书事件订阅**
   - 请求URL格式：`<https://your-domain.com/api/channels/feishu/events>`
   - Token：使用飞书后台生成的Token
   - 开启"消息事件"订阅：
     ```text
     im.message.receive_v1  # 接收消息事件
     ```text
3. **验证URL**
   - 飞书会发送GET请求验证URL
   - DeerFlow自动处理验证（使用配置的Token）

### 7.4 飞书Bot使用

1. **邀请Bot到群聊**
   - 在飞书群组中，@你的Bot名称
   - Bot会自动加入群聊

2. **私聊Bot**
   - 在飞书搜索Bot名称，开始私聊

3. **命令支持**
   - `/new` - 新建对话
   - `/status` - 查看状态
   - `/models` - 列出可用模型
   - `/memory` - 查看记忆
   - `/help` - 帮助信息

### 7.5 飞书连接机制详解

**关键结论**：不是每个用户一个长连接，而是整个DeerFlow实例只有一个飞书WebSocket长连接。

**连接架构**：

```text
飞书服务器
    ↓ (WebSocket长连接)
DeerFlow实例 (ECS/CVM)
    ├── FeishuChannel (单例)
    │   └── WebSocket连接 (一个)
    │
    └── MessageBus
        └── 处理所有用户消息

```text

**代码实现**：

- `FeishuChannel`是单例（在整个Gateway进程中只有一个实例）

- 只创建一个`lark.ws.Client`，建立**一个WebSocket长连接**

- 这个连接接收所有飞书用户的消息

**消息路由**：

1. 用户A发送消息 → 飞书服务器 → WebSocket连接 → `_on_message(event)`

2. 解析`chat_id`, `sender_id`

3. 创建`InboundMessage`发布到MessageBus

4. 路由到对应`thread_id`

5. Agent处理

6. 通过`send_card_message`回复

7. 飞书API发送到对应`chat_id`

**多租户场景**：

- **单实例单租户**：每个公司独立部署一个DeerFlow实例

- **单实例多租户**：需要修改代码支持多个飞书应用

- **当前限制**：DeerFlow当前不支持一个实例配置多个飞书应用

**推荐方案**：

- **短期**：每个公司独立部署实例

- **长期**：改造DeerFlow支持多租户，一个实例支持多个飞书应用

---

## 八、多租户用户管理

### 8.1 租户标识方案

#### 方案A：thread_id前缀（推荐）

客户端（前端或飞书Bot）在创建对话时：

```typescript
// 前端示例
const tenantId = "company-a";  // 从用户登录信息获取
const threadId = `${tenantId}:${uuidv4()}`;

// 使用threadId发起请求
await fetch(`/api/threads/${threadId}/chat`, {
  method: "POST",
  body: JSON.stringify({ message: "Hello" })
});

```text

#### 方案B：HTTP请求头

在Gateway层添加中间件自动添加租户前缀：

```python
# backend/app/gateway/middleware/tenant.py
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    # 从认证token或请求头获取租户ID
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    
    # 修改thread_id（如果存在）
    if "thread_id" in request.path_params:
        original_thread = request.path_params["thread_id"]
        if ":" not in original_thread:  # 未加前缀
            request.path_params["thread_id"] = f"{tenant_id}:{original_thread}"
    
    response = await call_next(request)
    return response

```text

### 8.2 租户数据目录结构

```text
/data/deer-flow/
├── .deer-flow/
│   ├── memory-tenant-a.json
│   ├── memory-tenant-b.json
│   ├── checkpoints.db
│   └── config.yaml
├── tenants/
│   ├── tenant-a/
│   │   ├── threads/
│   │   │   ├── tenant-a:uuid-1/
│   │   │   │   └── user-data/
│   │   │   │       ├── workspace/
│   │   │   │       ├── uploads/
│   │   │   │       └── outputs/
│   │   │   └── tenant-a:uuid-2/
│   │   └── uploads/  # 全局上传目录（可选）
│   └── tenant-b/
│       └── threads/
└── backup/

```text

### 8.3 租户配额管理（可选）

在`config.yaml`中添加：

```yaml
# 租户配额配置
tenants:
  tenant-a:
    max_threads: 100
    max_files_per_thread: 50
    max_file_size_mb: 100
    max_tokens_per_day: 100000
    allowed_models: ["gpt-4-turbo", "claude-3-5-sonnet"]
  
  tenant-b:
    max_threads: 50
    max_files_per_thread: 20
    max_file_size_mb: 50
    max_tokens_per_day: 50000
    allowed_models: ["gpt-4-turbo"]

```text

### 8.4 文件读取权限机制

**文件上传流程**：

1. 客户端上传文件到 `/api/threads/{thread_id}/uploads`

2. Gateway 接收文件并存储到 `.deer-flow/threads/{thread_id}/user-data/uploads/`

3. 返回虚拟路径 `/mnt/user-data/uploads/{filename}`

4. Agent 通过虚拟路径访问文件

**沙箱文件访问**：

- **LocalSandbox**: 通过路径映射访问主机文件
  - `_resolve_path()`: 容器路径 → 本地路径
  - `_reverse_resolve_path()`: 本地路径 → 容器路径

- **AioSandbox**: 通过 volume 挂载访问容器内文件
  - 挂载 `/data/deer-flow/.deer-flow/threads/{thread_id}/user-data` 到 `/mnt/user-data`

**文件权限配置**：

```bash
# 创建专用用户和组
groupadd -r deerflow
useradd -r -g deerflow -d /data/deer-flow deerflow

# 设置目录权限
chown -R deerflow:deerflow /data/deer-flow
chmod -R 755 /data/deer-flow

# 将deerflow用户加入docker组（用于DooD模式）
usermod -aG docker deerflow

```text

**安全考虑**：

- **只读挂载**: 对于技能库等只读资源，使用`:ro`挂载

- **写入限制**: 限制沙箱写入范围，避免系统文件被修改

- **租户隔离**: 每个租户的文件存储在独立目录，避免跨租户访问

---

## 九、安全加固

### 9.1 容器安全

修改`docker/docker-compose.yaml`：

```yaml
services:
  gateway:
    security_opt:
      - no-new-privileges:true
    read_only: true  # 根文件系统只读
    # 需要挂载的目录用volumes明确列出
    volumes:
      - /data/deer-flow/config.yaml:/app/backend/config.yaml:ro
      - /data/deer-flow/.deer-flow:/app/backend/.deer-flow:rw
      # ...
  
  langgraph:
    security_opt:
      - no-new-privileges:true
    read_only: true
    # ...

```text

### 9.2 网络隔离

```yaml
networks:
  deer-flow:
    internal: true  # 仅内部网络，不对外

```text

然后只暴露nginx容器的2026端口。

### 9.3 数据加密

**静态加密**（磁盘加密）：

```bash
# Ubuntu
apt install -y cryptsetup
cryptsetup luksFormat /dev/vdb
cryptsetup open /dev/vdb deerflow-data
mkfs.ext4 /dev/mapper/deerflow-data
mount /dev/mapper/deerflow-data /data/deer-flow

```text

**传输加密**（HTTPS）：

- 使用Nginx容器配置SSL

- 或使用云负载均衡器（阿里云SLB/腾讯云CLB）提供HTTPS终止

### 9.4 访问控制

**API限流**（Nginx配置）：

```nginx
# docker/nginx/nginx.conf 添加
location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass <http://gateway:8001;>
}

http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
}

```text

**认证授权**：

- DeerFlow已集成Better Auth，确保`BETTER_AUTH_SECRET`已设置

- 可集成企业SSO（如LDAP、OAuth2）

---

## 十、监控与运维

### 10.1 日志管理

**查看日志**：

```bash
# 所有服务
docker compose -f /opt/deer-flow/docker/docker-compose.yaml logs -f

# 特定服务
docker compose -f /opt/deer-flow/docker/docker-compose.yaml logs -f gateway
docker compose -f /opt/deer-flow/docker/docker-compose.yaml logs -f langgraph

# 查看日志文件（如果挂载）
tail -f /data/deer-flow/.deer-flow/logs/gateway.log

```text

**日志轮转**（logrotate）：

```bash
# /etc/logrotate.d/deerflow
/data/deer-flow/.deer-flow/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    sharedscripts
    postrotate
        docker compose -f /opt/deer-flow/docker/docker-compose.yaml logs --tail=100 > /dev/null
    endscript
}

```text

### 10.2 资源监控

```bash
# 容器资源使用
docker stats

# 磁盘使用
df -h /data/deer-flow

# 内存使用
free -h

# 进程状态
docker compose -f /opt/deer-flow/docker/docker-compose.yaml ps

# 自定义监控脚本
cat > /usr/local/bin/monitor-deerflow.sh <<'EOF'
#!/bin/bash
ALERT_WEBHOOK="<https://your-alert-webhook>"

# 检查服务状态
if ! docker compose -f /opt/deer-flow/docker/docker-compose.yaml ps | grep -q "Up"; then
    curl -X POST $ALERT_WEBHOOK -d '{"text":"DeerFlow服务异常"}'
fi

# 检查磁盘空间
USAGE=$(df /data/deer-flow | awk 'NR==2 {print $5}' | tr -d '%')
if [ $USAGE -gt 90 ]; then
    curl -X POST $ALERT_WEBHOOK -d "{\"text\":\"磁盘使用率${USAGE}%\"}"
fi
EOF
chmod +x /usr/local/bin/monitor-deerflow.sh

# 添加到crontab
echo "*/5 * * * * /usr/local/bin/monitor-deerflow.sh" >> /etc/crontab

```text

### 10.3 备份策略

**全量备份脚本**：

```bash
#!/bin/bash
# /usr/local/bin/backup-deerflow.sh
BACKUP_DIR="/data/deer-flow/backup"
DATE=$(date +%Y%m%d-%H%M%S)
TARFILE="$BACKUP_DIR/full-$DATE.tar.gz"

# 停止服务（确保数据一致性）
docker compose -f /opt/deer-flow/docker/docker-compose.yaml stop

# 备份数据目录
tar -czf $TARFILE \
  /data/deer-flow/.deer-flow/memory-*.json \
  /data/deer-flow/.deer-flow/checkpoints.db \
  /data/deer-flow/.deer-flow/config.yaml \
  /data/deer-flow/tenants

# 备份数据库（如果使用PostgreSQL）
# pg_dump deerflow > $BACKUP_DIR/postgres-$DATE.sql

# 重启服务
docker compose -f /opt/deer-flow/docker/docker-compose.yaml start

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TARFILE"

```text

**增量备份**（使用rsync）：

```bash
rsync -av --delete \
  /data/deer-flow/.deer-flow/ \
  backup-server:/backup/deerflow/$(date +%Y-%m-%d)/

```text

### 10.4 更新升级

```bash
cd /opt/deer-flow

# 1. 拉取最新代码

git pull origin main

# 2. 更新依赖（如果需要）

# make install

# 3. 更新配置文件（合并更改）

# 手动对比 config.yaml，保留自定义配置

# 4. 重建镜像（如果有更改）

docker compose -f docker/docker-compose.yaml build

# 5. 重启服务

docker compose -f docker/docker-compose.yaml up -d --remove-orphans

# 6. 验证

docker compose -f docker/docker-compose.yaml ps
curl <http://localhost:2026/>

```text

---

## 十一、故障排查

### 11.1 常见问题

#### Q1: 容器无法启动，提示"port is already allocated"

**原因**：端口2026/8001/2024被占用

**解决**：

```bash
# 查看端口占用
netstat -tlnp | grep :2026

# 修改PORT环境变量
export PORT=2027
# 或修改docker-compose.yaml中的端口映射

```text

#### Q2: 飞书消息收不到

**检查清单**：

1. ✅ 飞书应用已发布并安装

2. ✅ 事件订阅URL配置正确（`<https://domain/api/channels/feishu/events>`）

3. ✅ 安全组开放2026端口

4. ✅ HTTPS证书有效

5. ✅ 日志查看：`docker compose logs gateway | grep feishu`

6. ✅ 验证Token和EncodingAESKey配置

#### Q3: 文件上传失败

**原因**：文件权限或磁盘空间

**解决**：

```bash
# 检查磁盘空间
df -h /data/deer-flow

# 检查目录权限
ls -ld /data/deer-flow/.deer-flow/threads/

# 修复权限
chown -R deerflow:deerflow /data/deer-flow

```text

#### Q4: Docker沙箱无法启动

**原因**：Docker socket未挂载或权限不足

**解决**：

```bash
# 检查docker.sock挂载
docker compose exec gateway ls -la /var/run/docker.sock

# 确保deerflow用户在docker组
groups deerflow

# 检查Docker服务
systemctl status docker

```text

#### Q5: Memory不持久化

**原因**：storage_path配置错误或权限不足

**解决**：

```bash
# 检查memory文件
ls -la /data/deer-flow/.deer-flow/memory-*.json

# 检查config.yaml中的storage_path
# 确保路径存在且可写

```text

### 11.2 日志排查命令

```bash
# 查看所有服务日志（最近100行）
docker compose -f /opt/deer-flow/docker/docker-compose.yaml logs --tail=100

# 实时跟踪gateway日志
docker compose -f /opt/deer-flow/docker/docker-compose.yaml logs -f gateway

# 查看特定错误
docker compose -f /opt/deer-flow/docker/docker-compose.yaml logs | grep -i error

# 进入容器调试
docker compose -f /opt/deer-flow/docker/docker-compose.yaml exec gateway bash
# 在容器内查看配置文件、测试网络等

```text

### 11.3 性能调优

**Gateway调优**：

```yaml
# docker/docker-compose.yaml
gateway:
  command: sh -c "cd backend && PYTHONPATH=. uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 --workers 4"
  # 增加workers数量（建议CPU核心数*2+1）
  deploy:
    resources:
      limits:
        memory: 4G
      reservations:
        memory: 2G

```text

**LangGraph调优**：

```yaml
langgraph:
  command: sh -c "cd /app/backend && uv run langgraph dev --no-browser --allow-blocking --no-reload --host 0.0.0.0 --port 2024"
  # 考虑使用langgraph-api（需要license）

```text

---

## 十二、高级配置

### 12.1 使用PostgreSQL（生产推荐）

```bash
# 1. 安装PostgreSQL

apt install -y postgresql postgresql-contrib

# 2. 创建数据库

sudo -u postgres psql
CREATE DATABASE deerflow;
CREATE USER deerflow WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE deerflow TO deerflow;
\q

# 3. 修改config.yaml

checkpointer:
  type: postgres
  connection_string: postgresql://deerflow:your-password@localhost:5432/deerflow

# 4. 重启服务

docker compose -f docker/docker-compose.yaml restart gateway langgraph

```text

### 12.2 使用Redis缓存（可选）

```bash
# 安装Redis
apt install -y redis-server

# 配置Redis持久化
# /etc/redis/redis.conf
appendonly yes
maxmemory 2gb
maxmemory-policy allkeys-lru

systemctl restart redis

# 在DeerFlow中集成Redis（需开发）
# 用于缓存MCP工具、模型列表等

```text

### 12.3 配置HTTPS（Nginx容器）

修改`docker/nginx/nginx.conf`：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 代理配置...
}

```text

挂载SSL证书：

```yaml
nginx:
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - /etc/letsencrypt/live/your-domain.com:/etc/nginx/ssl:ro

```text

### 12.4 使用对象存储（OSS/COS）

修改文件上传配置，将大文件存储到对象存储：

```python
# backend/packages/harness/deerflow/uploads/manager.py
class S3UploadManager:
    def __init__(self, endpoint, bucket, access_key, secret_key):
        # ...
    
    async def upload(self, file_path: str, key: str):
        # 上传到S3/OSS/COS
        pass

```text

---

## 十三、附录

### 13.1 配置文件模板

**config.example.yaml**（完整版）：

```yaml
# DeerFlow 配置文件示例
# 复制为 config.yaml 并修改必要项

log_level: info

sandbox:
  use: deerflow.sandbox.local:LocalSandboxProvider
  allow_host_bash: false

models:
  # OpenAI
  - name: gpt-4-turbo
    display_name: GPT-4 Turbo
    use: langchain_openai:ChatOpenAI
    model: gpt-4-turbo-preview
    api_key: ${OPENAI_API_KEY}
    temperature: 0.7
    max_tokens: 4000
    supports_thinking: false
    supports_vision: true
  
  # Anthropic Claude
  - name: claude-3-5-sonnet
    display_name: Claude 3.5 Sonnet
    use: langchain_anthropic:ChatAnthropic
    model: claude-3-5-sonnet-20241022
    api_key: ${ANTHROPIC_API_KEY}
    temperature: 0.7
    max_tokens: 4000
    supports_thinking: true
    supports_vision: true

memory:
  enabled: true
  storage_path: /data/deer-flow/.deer-flow/memory-{tenant}.json
  storage_class: deerflow.agents.memory.storage.FileMemoryStorage
  debounce_seconds: 30
  max_facts: 100
  fact_confidence_threshold: 0.7
  injection_enabled: true
  max_injection_tokens: 2000

checkpointer:
  type: sqlite
  connection_string: /data/deer-flow/.deer-flow/checkpoints.db

skills:
  path: /data/deer-flow/.deer-flow/skills
  container_path: /mnt/skills

channels:
  langgraph_url: <http://localhost:2024>
  gateway_url: <http://localhost:8001>
  
  feishu:
    enabled: false
    app_id: ${FEISHU_APP_ID}
    app_secret: ${FEISHU_APP_SECRET}

session:
  assistant_id: lead_agent
  config:
    recursion_limit: 100
  context:
    thinking_enabled: true
    is_plan_mode: false
    subagent_enabled: false

title:
  enabled: true
  max_words: 10
  max_chars: 60

summarization:
  enabled: true

subagents:
  enabled: true

```text

### 13.2 环境变量清单

**.env.example**：

```bash
# ==================== 必需 ====================
BETTER_AUTH_SECRET=change-me-please-generate-your-own

# ==================== LLM API Keys ====================
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
# DASHSCOPE_API_KEY=...

# ==================== 飞书 ====================
FEISHU_APP_ID=your-app-id
FEISHU_APP_SECRET=your-app-secret

# ==================== 路径配置 ====================
DEER_FLOW_HOME=/data/deer-flow/.deer-flow
DEER_FLOW_CONFIG_PATH=/opt/deer-flow/config.yaml
DEER_FLOW_EXTENSIONS_CONFIG_PATH=/data/deer-flow/.deer-flow/extensions_config.json
DEER_FLOW_REPO_ROOT=/opt/deer-flow
DEER_FLOW_DOCKER_SOCKET=/var/run/docker.sock

# ==================== 网络 ====================
DEER_FLOW_CHANNELS_LANGGRAPH_URL=<http://langgraph:2024>
DEER_FLOW_CHANNELS_GATEWAY_URL=<http://gateway:8001>

# ==================== 镜像加速（国内） ====================
APT_MIRROR=mirrors.aliyun.com
NPM_REGISTRY=<https://registry.npmmirror.com>

# ==================== 监控（可选） ====================
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=

# ==================== 端口 ====================
PORT=2026

```text

### 13.3 检查清单

**部署前检查**：

- [ ] 服务器系统：Ubuntu 22.04 / CentOS 8

- [ ] Docker已安装并运行

- [ ] Docker Compose已安装

- [ ] 数据目录`/data/deer-flow`已创建

- [ ] 用户`deerflow`已创建并加入docker组

- [ ] 配置文件`config.yaml`已生成并修改

- [ ] 环境变量`.env`已设置（特别是API keys）

- [ ] 安全组开放2026端口

- [ ] 域名解析已配置（可选）

- [ ] SSL证书已准备（可选）

**部署后检查**：

- [ ] 所有容器状态为`Up`

- [ ] 前端页面可访问 (`<http://server:2026>`)

- [ ] API响应正常 (`/api/health`)

- [ ] 飞书Bot在线并响应消息

- [ ] 文件上传功能正常

- [ ] Memory持久化正常（创建thread，重启后数据还在）

- [ ] 日志无错误

### 13.4 常用命令速查

```bash
# 部署目录
cd /opt/deer-flow

# 启动/停止
docker compose -f docker/docker-compose.yaml up -d
docker compose -f docker/docker-compose.yaml down

# 查看状态
docker compose -f docker/docker-compose.yaml ps

# 查看日志
docker compose -f docker/docker-compose.yaml logs -f [service]

# 进入容器
docker compose -f docker/docker-compose.yaml exec gateway bash

# 重建单个服务
docker compose -f docker/docker-compose.yaml up -d --build gateway

# 清理未使用资源
docker system prune -a

# 备份数据
tar -czf /backup/deerflow-$(date +%Y%m%d).tar.gz /data/deer-flow/.deer-flow

# 恢复数据
tar -xzf /backup/deerflow-20260330.tar.gz -C /data/deer-flow/
chown -R deerflow:deerflow /data/deer-flow

```text

---

## 十四、技术支持

### 14.1 资源链接

- **官方文档**：<<https://github.com/bytedance/deer-flow/tree/main/docs>>

- **问题反馈**：<<https://github.com/bytedance/deer-flow/issues>>

- **飞书开放平台**：<<https://open.feishu.cn/>>

### 14.2 联系信息

- 企业技术支持：请联系字节跳动云服务代表

- 社区讨论：GitHub Discussions

---

## 十五、架构特性总结

### 15.1 DeerFlow 核心特性

1. **全栈超级代理框架**
   - 后端：Python 3.12 + FastAPI + LangGraph
   - 前端：Next.js 16 + React 19 + TypeScript
   - 支持本地开发和 Docker 部署

2. **沙箱系统**
   - LocalSandboxProvider：本地执行，无隔离
   - AioSandboxProvider：容器隔离，生产推荐
   - 支持路径映射和文件访问

3. **记忆系统**
   - 基于文件的记忆存储
   - 支持多租户隔离
   - 自动注入到系统提示

4. **检查点系统**
   - 支持内存、SQLite、PostgreSQL
   - 按 thread_id 隔离状态
   - 支持多租户前缀

5. **飞书通道**
   - WebSocket 长连接，无需公网 IP
   - 单实例单长连接
   - 支持多用户消息路由

6. **文件系统**
   - 支持文件上传和访问
   - 虚拟路径映射
   - 租户隔离存储

### 15.2 部署建议

**开发环境**：

- 使用 LocalSandboxProvider

- `make dev` 启动开发服务器

- 热重载支持

**生产环境**：

- 使用 AioSandboxProvider

- 阿里云 ECS / 腾讯云 CVM 部署

- 配置 HTTPS 和安全加固

**多租户场景**：

- 单实例多租户：需要改造代码

- 推荐方案：每个公司独立部署实例

### 15.3 关键配置项

1. **BETTER_AUTH_SECRET**：必须设置，用于认证

2. **API Keys**：配置 LLM 提供商的 API 密钥

3. **飞书凭证**：App ID 和 App Secret

4. **数据目录**：`/data/deer-flow` 持久化存储

5. **端口映射**：2026 端口对外暴露

### 15.4 故障排查要点

1. **容器无法启动**：检查端口占用

2. **飞书消息收不到**：检查事件订阅 URL

3. **文件上传失败**：检查权限和磁盘空间

4. **Docker 沙箱失败**：检查 socket 挂载和权限

5. **Memory 不持久化**：检查 storage_path 配置

---

## 十六、服务提供方快速部署指南

作为服务提供方，您需要为公司/团队快速创建和管理DeerFlow服务实例。本章节提供自动化部署和管理方案。

### 16.1 服务提供方架构设计

**推荐架构**：

```text
服务提供方平台
├── 部署管理控制台 (Web UI)
├── 自动化部署引擎
│   ├── 模板库 (Docker Compose, Kubernetes)
│   ├── 配置生成器
│   └── 部署编排器
├── 租户管理
│   ├── 租户注册/审核
│   ├── 资源配额管理
│   └── 实例生命周期管理
└── 监控运维
    ├── 统一日志收集
    ├── 性能监控
    └── 告警系统

```text

#### 16.1.1 管理控制台功能设计

**核心功能模块**：

| 模块 | 功能 | 说明 |
| :--- | :--- | :--- |
| **仪表盘** | 系统概览 | 显示总租户数、运行实例数、资源使用率、健康状态 |
| **租户管理** | 租户列表 | 查看、搜索、筛选所有租户 |
| | 租户注册 | 创建新租户，填写基本信息 |
| | 租户审核 | 审核租户资质，通过/拒绝 |
| | 租户配置 | 修改租户配置、资源配额 |
| | 租户操作 | 启动、停止、重启、删除实例 |
| **部署管理** | 模板管理 | 管理部署模板（Docker Compose、K8s YAML） |
| | 快速部署 | 选择模板、填写参数、一键部署 |
| | 批量部署 | 上传租户列表，批量创建实例 |
| | 部署历史 | 查看部署记录、回滚操作 |
| **通道管理** | 飞书配置 | 为租户配置飞书 App ID、Secret、事件订阅 |
| | 钉钉配置 | 配置钉钉机器人、加签密钥 |
| | Slack配置 | Slack Bot Token、Signing Secret |
| | 通道测试 | 发送测试消息，验证连接 |
| **监控运维** | 实时日志 | 查看各租户实例的实时日志 |
| | 性能监控 | CPU、内存、磁盘、网络图表 |
| | 告警管理 | 配置告警规则、通知方式 |
| | 备份恢复 | 数据备份、恢复操作 |
| **用户管理** | 平台用户 | 管理平台管理员、运维人员 |
| | 权限控制 | 基于角色的访问控制（RBAC） |
| | 操作审计 | 记录所有操作日志 |

**管理控制台技术栈**：

- **前端**：Next.js 14 + React 18 + TypeScript + Ant Design / shadcn/ui

- **后端**：FastAPI + SQLAlchemy + Celery（异步任务）

- **数据库**：PostgreSQL（主数据）+ Redis（缓存、会话）

- **部署**：Docker Compose / Kubernetes

- **监控**：Prometheus + Grafana + Loki

**快速操作流程示例**：

1. **创建租户**：
   - 填写租户基本信息（名称、域名、联系人）
   - 选择套餐（基础版、企业版、定制版）
   - 系统自动生成配置文件和部署脚本
   - 一键部署或加入批量部署队列

2. **配置飞书通道**：
   - 在飞书开放平台创建应用，获取 App ID 和 App Secret
   - 在管理控制台填写凭证，系统自动配置事件订阅 URL
   - 测试消息发送，确保连接正常
   - 租户管理员即可在飞书中使用 DeerFlow

3. **监控与维护**：
   - 查看仪表盘了解系统整体状态
   - 通过日志查看器实时查看租户实例日志
   - 设置告警规则，异常时自动通知
   - 定期备份数据，支持快速恢复

#### 16.1.2 数据库架构设计

**核心数据模型**：

```sql
-- 1. 租户表（tenants）

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    domain VARCHAR(200) UNIQUE,
    plan VARCHAR(50) NOT NULL DEFAULT 'basic',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 资源配额
    max_concurrent_sessions INT DEFAULT 10,
    max_file_uploads_per_day INT DEFAULT 100,
    max_sandbox_containers INT DEFAULT 3,
    storage_quota_gb INT DEFAULT 10,
    api_rate_limit INT DEFAULT 100,
    
    -- 部署信息
    deployment_mode VARCHAR(50) DEFAULT 'docker-compose',
    deployment_config JSONB,
    instance_id VARCHAR(200),
    
    -- 联系信息
    contact_email VARCHAR(200),
    contact_phone VARCHAR(50),
    contact_name VARCHAR(100),
    
    -- 备注
    notes TEXT
);

-- 2. 通道配置表（channel_configs）

CREATE TABLE channel_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(100) NOT NULL REFERENCES tenants(tenant_id),
    channel_type VARCHAR(50) NOT NULL, -- 'feishu', 'dingtalk', 'slack', 'telegram'
    config JSONB NOT NULL, -- 加密存储敏感信息
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, channel_type)
);

-- 3. 部署实例表（deployments）

CREATE TABLE deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(100) NOT NULL REFERENCES tenants(tenant_id),
    deployment_id VARCHAR(200) UNIQUE NOT NULL,
    template_version VARCHAR(50),
    status VARCHAR(50) NOT NULL, -- 'deploying', 'active', 'failed', 'terminated'
    docker_compose_file TEXT,
    kubernetes_yaml TEXT,
    container_ids JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    stopped_at TIMESTAMP,
    logs TEXT,
    error_message TEXT
);

-- 4. 资源使用表（resource_usage）

CREATE TABLE resource_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(100) NOT NULL REFERENCES tenants(tenant_id),
    metric_date DATE NOT NULL,
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_gb DECIMAL(8,2),
    disk_usage_gb DECIMAL(8,2),
    api_requests_count INT DEFAULT 0,
    active_sessions INT DEFAULT 0,
    file_uploads_count INT DEFAULT 0,
    
    UNIQUE(tenant_id, metric_date)
);

-- 5. 操作日志表（audit_logs）

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    tenant_id VARCHAR(100) REFERENCES tenants(tenant_id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. 备份记录表（backups）

CREATE TABLE backups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(100) NOT NULL REFERENCES tenants(tenant_id),
    backup_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'config-only'
    file_path VARCHAR(500) NOT NULL,
    file_size_gb DECIMAL(8,2),
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW(),
    restored_at TIMESTAMP
);

```text

**索引优化**：

```sql
-- 常用查询索引
CREATE INDEX idx_tenants_status ON tenants(status);
CREATE INDEX idx_tenants_plan ON tenants(plan);
CREATE INDEX idx_channel_configs_tenant ON channel_configs(tenant_id);
CREATE INDEX idx_deployments_tenant ON deployments(tenant_id);
CREATE INDEX idx_deployments_status ON deployments(status);
CREATE INDEX idx_resource_usage_tenant_date ON resource_usage(tenant_id, metric_date);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

```text

**敏感信息加密**：

通道配置中的敏感信息（如 App Secret、Bot Token）应加密存储：

```python
# 示例：使用 Fernet 加密
from cryptography.fernet import Fernet
import json

class ConfigEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: dict) -> str:
        json_str = json.dumps(data)
        encrypted = self.cipher.encrypt(json_str.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_str: str) -> dict:
        decrypted = self.cipher.decrypt(encrypted_str.encode())
        return json.loads(decrypted.decode())

```text

**数据迁移脚本**：

```python
# alembic 迁移脚本示例
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 创建 tenants 表
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(100), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('domain', sa.String(200), unique=True),
        sa.Column('plan', sa.String(50), nullable=False, default='basic'),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        # ... 其他字段
    )

def downgrade():
    op.drop_table('tenants')

```text

**部署模式选择**：

| 模式 | 适用场景 | 隔离级别 | 管理复杂度 |
| :--- | :--- | :--- | :--- |
| **独立实例** | 中大型企业 | 完全隔离 | 低 |
| **共享实例** | 中小团队 | 进程级隔离 | 中 |
| **K8s命名空间** | 云原生环境 | 容器级隔离 | 高 |

#### 16.1.3 REST API 设计

**管理控制台 API 规范**：

```text
# 基础信息
Base URL: /api/v1
认证: Bearer Token (JWT)
内容类型: application/json

```text

##### 1. 租户管理 API

```http
# 获取租户列表
GET /tenants
Query Parameters:
  - page (int): 页码，默认 1
  - limit (int): 每页数量，默认 20
  - status (string): 按状态筛选
  - plan (string): 按套餐筛选
  - search (string): 搜索关键词

Response:
{
  "data": [
    {
      "id": "uuid",
      "tenant_id": "acme-corp",
      "name": "Acme 公司",
      "domain": "acme.example.com",
      "plan": "enterprise",
      "status": "active",
      "created_at": "2026-03-30T10:00:00Z",
      "deployment_mode": "docker-compose",
      "instance_id": "instance-123"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20
}

# 创建租户
POST /tenants
Body:
{
  "tenant_id": "acme-corp",
  "name": "Acme 公司",
  "domain": "acme.example.com",
  "plan": "enterprise",
  "contact_email": "admin@acme.com",
  "contact_name": "张三",
  "resources": {
    "max_concurrent_sessions": 100,
    "max_file_uploads_per_day": 1000,
    "storage_quota_gb": 500
  }
}

# 获取租户详情
GET /tenants/{tenant_id}

# 更新租户配置
PUT /tenants/{tenant_id}
Body:
{
  "plan": "enterprise",
  "resources": {...},
  "status": "active"
}

# 删除租户
DELETE /tenants/{tenant_id}

```text

##### 2. 部署管理 API

```http
# 获取部署模板列表
GET /deployments/templates

# 快速部署
POST /deployments/quick
Body:
{
  "tenant_id": "acme-corp",
  "template_id": "docker-compose-v1",
  "parameters": {
    "domain": "acme.example.com",
    "db_password": "generated-secret",
    "better_auth_secret": "generated-secret"
  }
}

# 获取部署状态
GET /deployments/{deployment_id}/status

# 停止/启动/重启实例
POST /deployments/{deployment_id}/actions
Body:
{
  "action": "stop" | "start" | "restart"
}

# 获取部署日志
GET /deployments/{deployment_id}/logs
Query Parameters:
  - lines (int): 返回行数，默认 100
  - follow (bool): 是否实时跟随

```text

##### 3. 通道配置 API

```http
# 获取租户通道配置
GET /tenants/{tenant_id}/channels

# 创建/更新通道配置
POST /tenants/{tenant_id}/channels
Body:
{
  "channel_type": "feishu",
  "config": {
    "app_id": "cli_xxxxx",
    "app_secret": "encrypted-secret",
    "verification_token": "encrypted-token",
    "encryption_key": "encrypted-key"
  }
}

# 测试通道连接
POST /tenants/{tenant_id}/channels/{channel_type}/test

# 删除通道配置
DELETE /tenants/{tenant_id}/channels/{channel_type}

```text

##### 4. 监控数据 API

```http
# 获取租户资源使用情况
GET /tenants/{tenant_id}/metrics
Query Parameters:
  - start_date (date): 开始日期
  - end_date (date): 结束日期
  - metrics (string): cpu,memory,disk,api_requests

# 获取实时日志
GET /tenants/{tenant_id}/logs/realtime
Query Parameters:
  - container (string): 容器名称
  - lines (int): 行数

# 获取告警规则
GET /tenants/{tenant_id}/alerts

# 创建告警规则
POST /tenants/{tenant_id}/alerts
Body:
{
  "name": "CPU 使用率告警",
  "metric": "cpu_usage",
  "threshold": 80,
  "duration": "5m",
  "notifications": ["email", "webhook"]
}

```text

##### 5. 用户和权限 API

```http
# 平台用户管理
GET /admin/users
POST /admin/users
PUT /admin/users/{user_id}
DELETE /admin/users/{user_id}

# 角色管理
GET /admin/roles
POST /admin/roles
PUT /admin/roles/{role_id}

# 权限分配
POST /admin/users/{user_id}/roles
Body:
{
  "role_ids": ["admin", "operator"]
}

# 操作审计
GET /admin/audit-logs
Query Parameters:
  - user_id (string): 用户ID
  - action (string): 操作类型
  - start_date, end_date

```text

#### 16.1.4 前端组件设计

**技术栈**：

- **框架**: Next.js 14 (App Router)

- **UI库**: shadcn/ui + Tailwind CSS

- **状态管理**: Zustand

- **数据获取**: React Query (TanStack Query)

- **表单**: React Hook Form + Zod 验证

- **图表**: Recharts

- **日志查看**: react-terminal-ui

**核心页面组件**：

**1. 仪表盘页面** (`/dashboard`)

```tsx
// app/dashboard/page.tsx
export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">系统概览</h1>
      
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="总租户数" value={totalTenants} trend="+12%" />
        <StatCard title="运行实例" value={activeInstances} trend="+5%" />
        <StatCard title="平均资源使用率" value={avgResourceUsage} unit="%" />
        <StatCard title="健康状态" value={healthyPercentage} unit="%" />
      </div>
      
      {/* 资源使用趋势图 */}
      <ResourceUsageChart />
      
      {/* 最近活动 */}
      <RecentActivity />
    </div>
  )
}

```text

**2. 租户管理页面** (`/tenants`)

```tsx
// app/tenants/page.tsx
export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [filters, setFilters] = useState<FilterState>({})
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">租户管理</h1>
        <Button onClick={() => router.push('/tenants/new')}>
          创建租户
        </Button>
      </div>
      
      {/* 搜索和筛选 */}
      <TenantFilters filters={filters} onFilterChange={setFilters} />
      
      {/* 租户列表 */}
      <TenantTable tenants={tenants} onRowClick={handleRowClick} />
      
      {/* 分页 */}
      <Pagination total={total} page={page} limit={limit} />
    </div>
  )
}

```text

**3. 租户详情页面** (`/tenants/[tenant_id]`)

```tsx
// app/tenants/[tenant_id]/page.tsx
export default function TenantDetailPage({ params }: { params: { tenant_id: string } }) {
  const { data: tenant, isLoading } = useTenant(params.tenant_id)
  
  if (isLoading) return <LoadingSpinner />
  
  return (
    <Tabs defaultValue="overview" className="space-y-6">
      <TabsList>
        <TabsTrigger value="overview">概览</TabsTrigger>
        <TabsTrigger value="deployment">部署</TabsTrigger>
        <TabsTrigger value="channels">通道配置</TabsTrigger>
        <TabsTrigger value="monitoring">监控</TabsTrigger>
        <TabsTrigger value="logs">日志</TabsTrigger>
      </TabsList>
      
      <TabsContent value="overview">
        <TenantOverview tenant={tenant} />
      </TabsContent>
      
      <TabsContent value="deployment">
        <DeploymentManager tenant={tenant} />
      </TabsContent>
      
      <TabsContent value="channels">
        <ChannelConfig tenant={tenant} />
      </TabsContent>
      
      <TabsContent value="monitoring">
        <MonitoringDashboard tenant={tenant} />
      </TabsContent>
      
      <TabsContent value="logs">
        <LogViewer tenant={tenant} />
      </TabsContent>
    </Tabs>
  )
}

```text

**可复用组件**：

```tsx
// components/tenants/tenant-card.tsx
export function TenantCard({ tenant }: { tenant: Tenant }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{tenant.name}</CardTitle>
        <CardDescription>{tenant.domain}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>状态:</span>
            <Badge variant={getStatusVariant(tenant.status)}>
              {tenant.status}
            </Badge>
          </div>
          <div className="flex justify-between">
            <span>套餐:</span>
            <span>{tenant.plan}</span>
          </div>
          <div className="flex justify-between">
            <span>部署模式:</span>
            <span>{tenant.deployment_mode}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button variant="outline" size="sm" onClick={() => router.push(`/tenants/${tenant.id}`)}>
          查看详情
        </Button>
      </CardFooter>
    </Card>
  )
}

// components/deployment/deployment-form.tsx
export function DeploymentForm({ tenantId }: { tenantId: string }) {
  const [template, setTemplate] = useState<Template>()
  const [parameters, setParameters] = useState<Record<string, any>>({})
  
  const handleSubmit = async (data: DeploymentFormData) => {
    const response = await fetch('/api/v1/deployments/quick', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tenant_id: tenantId,
        template_id: template?.id,
        parameters: data
      })
    })
    
    if (response.ok) {
      toast.success('部署已启动')
      router.push(`/tenants/${tenantId}/deployment`)
    }
  }
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <TemplateSelector onSelect={setTemplate} />
        <ParameterInputs template={template} values={parameters} onChange={setParameters} />
        <Button type="submit" disabled={!template}>
          开始部署
        </Button>
      </form>
    </Form>
  )
}

```text

#### 16.1.5 部署引擎实现

**核心部署引擎**：

```python
# backend/deployments/engine.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import subprocess
import yaml
import tempfile
import os
from pathlib import Path

@dataclass
class DeploymentConfig:
    tenant_id: str
    template_type: str  # 'docker-compose' | 'kubernetes'
    parameters: Dict[str, any]
    storage_path: Path

class DeploymentEngine:
    """部署引擎核心类"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.workspace = self._create_workspace()
    
    def _create_workspace(self) -> Path:
        """创建部署工作目录"""
        workspace = Path(f"/tmp/deployments/{self.config.tenant_id}")
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace
    
    def generate_compose_file(self) -> Path:
        """生成 Docker Compose 文件"""
        template_path = Path("templates/docker-compose.deerflow.yml")
        with open(template_path) as f:
            template = yaml.safe_load(f)
        
        # 替换参数
        rendered = self._render_template(template, self.config.parameters)
        
        output_path = self.workspace / "docker-compose.yml"
        with open(output_path, 'w') as f:
            yaml.dump(rendered, f, default_flow_style=False)
        
        return output_path
    
    def generate_kubernetes_yaml(self) -> Path:
        """生成 Kubernetes 部署文件"""
        # 生成 Deployment、Service、ConfigMap、Secret 等
        pass
    
    def deploy(self) -> DeploymentResult:
        """执行部署"""
        if self.config.template_type == 'docker-compose':
            return self._deploy_docker_compose()
        elif self.config.template_type == 'kubernetes':
            return self._deploy_kubernetes()
        else:
            raise ValueError(f"Unsupported template type: {self.config.template_type}")
    
    def _deploy_docker_compose(self) -> DeploymentResult:
        """Docker Compose 部署"""
        compose_file = self.generate_compose_file()
        
        try:
            # 拉取镜像
            subprocess.run(
                ["docker-compose", "-f", str(compose_file), "pull"],
                check=True,
                capture_output=True
            )
            
            # 启动服务
            subprocess.run(
                ["docker-compose", "-f", str(compose_file), "up", "-d"],
                check=True,
                capture_output=True
            )
            
            # 获取容器信息
            result = subprocess.run(
                ["docker-compose", "-f", str(compose_file), "ps", "--format", "json"],
                capture_output=True,
                text=True
            )
            
            return DeploymentResult(
                success=True,
                instance_id=f"docker-{self.config.tenant_id}",
                containers=json.loads(result.stdout)
            )
            
        except subprocess.CalledProcessError as e:
            return DeploymentResult(
                success=False,
                error_message=e.stderr.decode()
            )
    
    def _deploy_kubernetes(self) -> DeploymentResult:
        """Kubernetes 部署"""
        yaml_file = self.generate_kubernetes_yaml()
        
        try:
            # 应用配置
            subprocess.run(
                ["kubectl", "apply", "-f", str(yaml_file)],
                check=True,
                capture_output=True
            )
            
            # 等待部署完成
            self._wait_for_deployment()
            
            return DeploymentResult(
                success=True,
                instance_id=f"k8s-{self.config.tenant_id}"
            )
            
        except subprocess.CalledProcessError as e:
            return DeploymentResult(
                success=False,
                error_message=e.stderr.decode()
            )
    
    def stop(self) -> bool:
        """停止部署实例"""
        try:
            if self.config.template_type == 'docker-compose':
                subprocess.run(
                    ["docker-compose", "-f", "docker-compose.yml", "down"],
                    check=True,
                    capture_output=True
                )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_logs(self, tail: int = 100) -> str:
        """获取部署日志"""
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.yml", "logs", "--tail", str(tail)],
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

```text

**异步任务处理**：

```python
# backend/deployments/tasks.py
from celery import Celery
from datetime import datetime

celery_app = Celery('deployments', broker='redis://localhost:6379/1')

@celery_app.task(bind=True, max_retries=3)
def deploy_tenant(self, tenant_id: str, template_id: str, parameters: dict):
    """异步部署任务"""
    try:
        # 更新状态为 deploying
        update_tenant_status(tenant_id, 'deploying')
        
        # 创建部署引擎
        config = DeploymentConfig(
            tenant_id=tenant_id,
            template_type=template_id,
            parameters=parameters,
            storage_path=Path(f"/data/deer-flow/{tenant_id}")
        )
        
        engine = DeploymentEngine(config)
        result = engine.deploy()
        
        if result.success:
            # 记录部署信息
            save_deployment_record(tenant_id, result)
            update_tenant_status(tenant_id, 'active', result.instance_id)
            return {"status": "success", "instance_id": result.instance_id}
        else:
            update_tenant_status(tenant_id, 'failed')
            raise Exception(result.error_message)
            
    except Exception as exc:
        update_tenant_status(tenant_id, 'failed')
        raise self.retry(exc=exc, countdown=60)

@celery_app.task
def cleanup_old_deployments(days: int = 30):
    """清理旧的部署记录"""
    cutoff_date = datetime.now() - timedelta(days=days)
    # 清理逻辑
    pass

```text

### 16.2 快速部署模板

#### 16.2.1 Docker Compose 模板

创建 `docker-compose.deerflow.yml` 模板：

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "${PUBLIC_PORT:-2026}:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - gateway
      - langgraph
    networks:
      - deerflow-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - NEXT_PUBLIC_API_URL=<http://gateway:8001>
    volumes:
      - ./frontend/.env.local:/app/.env.local
    networks:
      - deerflow-network

  gateway:
    build:
      context: ./backend
      dockerfile: Dockerfile.gateway
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379
      - STORAGE_PATH=/data
    volumes:
      - ./data:/data
    depends_on:
      - postgres
      - redis
    networks:
      - deerflow-network

  langgraph:
    build:
      context: ./backend
      dockerfile: Dockerfile.langgraph
    environment:
      - REDIS_URL=redis://redis:6379
      - STORAGE_PATH=/data
    volumes:
      - ./data:/data
      - /var/run/docker.sock:/var/run/docker.sock  # 沙箱需要
    depends_on:
      - redis
    networks:
      - deerflow-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - deerflow-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - deerflow-network

networks:
  deerflow-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:

```text

#### 16.2.2 Kubernetes 部署模板

创建 `deerflow-deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deerflow
  namespace: ${TENANT_NAMESPACE}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: deerflow
  template:
    metadata:
      labels:
        app: deerflow
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
        - name: ssl
          mountPath: /etc/nginx/ssl
        env:
        - name: PUBLIC_PORT
          value: "80"
      - name: frontend
        image: deerflow/frontend:latest
        env:
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: deerflow-secrets
              key: better-auth-secret
        - name: NEXT_PUBLIC_API_URL
          value: "<http://gateway:8001>"
      # ... 其他容器配置
---
apiVersion: v1
kind: Service
metadata:
  name: deerflow-service
  namespace: ${TENANT_NAMESPACE}
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: deerflow

```text

### 16.3 自动化部署脚本

#### 16.3.1 一键部署脚本

创建 `deploy_tenant.sh`：

```bash
#!/bin/bash

# DeerFlow 租户部署脚本
# 用法: ./deploy_tenant.sh <tenant_id> <domain>

set -e

TENANT_ID=$1
DOMAIN=$2
ENV_FILE=".env.${TENANT_ID}"

if [ -z "$TENANT_ID" ] || [ -z "$DOMAIN" ]; then
    echo "用法: $0 <tenant_id> <domain>"
    echo "示例: $0 acme-corp acme.example.com"
    exit 1
fi

echo "🚀 开始部署租户: $TENANT_ID"
echo "🌐 域名: $DOMAIN"

# 1. 生成环境配置

cat > $ENV_FILE << EOF
# 租户配置
TENANT_ID=$TENANT_ID
PUBLIC_PORT=2026
BETTER_AUTH_SECRET=$(openssl rand -hex 32)
DB_NAME=deerflow_$TENANT_ID
DB_USER=deerflow_$TENANT_ID
DB_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
STORAGE_PATH=/data/deer-flow/$TENANT_ID
EOF

# 2. 创建数据目录

mkdir -p data/$TENANT_ID

# 3. 生成 Nginx 配置

cat > nginx/${TENANT_ID}.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass <http://localhost:2026;>
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# 4. 生成 Docker Compose 文件

envsubst < docker-compose.deerflow.yml > docker-compose.$TENANT_ID.yml

# 5. 启动服务

docker-compose -f docker-compose.$TENANT_ID.yml up -d

# 6. 初始化数据库

sleep 10
docker-compose -f docker-compose.$TENANT_ID.yml exec -T gateway alembic upgrade head

# 7. 创建管理员用户

docker-compose -f docker-compose.$TENANT_ID.yml exec -T gateway python -m deerflow.app.gateway create-admin --email admin@$TENANT_ID.example.com

echo "✅ 部署完成！"
echo "📝 访问地址: <http://$DOMAIN>"
echo "🔑 管理员邮箱: admin@$TENANT_ID.example.com"
echo "⚠️  请保存环境文件: $ENV_FILE"

```text

#### 16.3.2 批量部署脚本

创建 `batch_deploy.py`：

```python
#!/usr/bin/env python3
"""
批量部署 DeerFlow 租户
"""

import os
import sys
import yaml
import subprocess
from datetime import datetime

def load_tenants_config(config_file='tenants.yaml'):
    """加载租户配置"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def deploy_tenant(tenant_config):
    """部署单个租户"""
    tenant_id = tenant_config['tenant_id']
    domain = tenant_config['domain']
    
    print(f"🚀 部署租户: {tenant_id} ({domain})")
    
    # 调用部署脚本
    result = subprocess.run(
        ['./deploy_tenant.sh', tenant_id, domain],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ {tenant_id} 部署成功")
        return True
    else:
        print(f"❌ {tenant_id} 部署失败")
        print(result.stderr)
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = 'tenants.yaml'
    
    tenants = load_tenants_config(config_file)
    
    success_count = 0
    total_count = len(tenants['tenants'])
    
    for tenant in tenants['tenants']:
        if deploy_tenant(tenant):
            success_count += 1
        print()
    
    print(f"📊 部署统计: {success_count}/{total_count} 成功")
    
    # 生成部署报告
    generate_report(tenants['tenants'], success_count)

def generate_report(tenants, success_count):
    """生成部署报告"""
    report_file = f"deployment-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# DeerFlow 批量部署报告\n\n")
        f.write(f"- 部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- 总租户数: {len(tenants)}\n")
        f.write(f"- 成功数: {success_count}\n")
        f.write(f"- 失败数: {len(tenants) - success_count}\n\n")
        
        f.write("## 租户列表\n\n")
        f.write("| 租户ID | 域名 | 状态 | 访问地址 |\n")
        f.write("|--------|------|------|----------|\n")
        
        for tenant in tenants:
            status = "✅ 成功" if tenant.get('deployed', False) else "❌ 失败"
            url = f"<http://{tenant[>'domain']}" if tenant.get('deployed', False) else "-"
            f.write(f"| {tenant['tenant_id']} | {tenant['domain']} | {status} | {url} |\n")
    
    print(f"📄 部署报告已生成: {report_file}")

if __name__ == '__main__':
    main()

```text

#### 16.3.3 租户配置文件示例

创建 `tenants.yaml`：

```yaml
# 租户配置示例
tenants:
  - tenant_id: "acme-corp"
    domain: "acme.example.com"
    plan: "enterprise"  # enterprise, business, basic
    resources:
      cpu: "4"
      memory: "8GB"
      storage: "100GB"
    admin:
      email: "admin@acme-corp.example.com"
      name: "Acme 管理员"
    features:
      enable_sandbox: true
      enable_mcp: true
      max_concurrent_users: 50

  - tenant_id: "tech-startup"
    domain: "tech.example.com"
    plan: "business"
    resources:
      cpu: "2"
      memory: "4GB"
      storage: "50GB"
    admin:
      email: "admin@tech-startup.example.com"
      name: "Tech Startup 管理员"
    features:
      enable_sandbox: true
      enable_mcp: false
      max_concurrent_users: 20

```text

### 16.4 租户生命周期管理

#### 16.4.1 租户注册流程

```mermaid
graph TD
    A[服务申请] --> B[资质审核]
    B --> C{审核通过?}
    C -->|是| D[资源分配]
    C -->|否| E[拒绝通知]
    D --> F[自动部署]
    F --> G[配置初始化]
    G --> H[测试验证]
    H --> I[交付用户]
    I --> J[监控运维]

```text

#### 16.4.2 租户状态管理

| 状态 | 说明 | 操作 |
| :--- | :--- | :--- |
| **pending** | 待审核 | 审核、拒绝 |
| **deploying** | 部署中 | 查看日志、重试 |
| **active** | 运行中 | 暂停、扩容、备份 |
| **suspended** | 已暂停 | 恢复、删除 |
| **terminated** | 已终止 | 归档、删除数据 |

#### 16.4.3 资源配额管理

在 `config.yaml` 中配置租户配额：

```yaml
tenants:
  acme-corp:
    max_concurrent_sessions: 100
    max_file_uploads_per_day: 1000
    max_sandbox_containers: 10
    storage_quota_gb: 500
    api_rate_limit: 1000/hour

  tech-startup:
    max_concurrent_sessions: 50
    max_file_uploads_per_day: 500
    max_sandbox_containers: 5
    storage_quota_gb: 200
    api_rate_limit: 500/hour

```text

### 16.5 监控运维方案

#### 16.5.1 统一日志收集

使用 ELK 或 Loki 收集所有租户日志：

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yml

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./promtail-config.yml:/etc/promtail/config.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana

```text

#### 16.5.2 性能监控指标

| 指标 | 说明 | 告警阈值 |
| :--- | :--- | :--- |
| **CPU 使用率** | 容器 CPU 使用百分比 | > 80% |
| **内存使用率** | 容器内存使用百分比 | > 85% |
| **磁盘使用率** | 数据目录磁盘使用 | > 90% |
| **API 响应时间** | P95 响应时间 | > 2s |
| **错误率** | 5xx 错误比例 | > 1% |
| **飞书消息延迟** | 消息处理延迟 | > 30s |

#### 16.5.3 自动化运维脚本

`maintenance.sh`：

```bash
#!/bin/bash

# 维护操作脚本

case "$1" in
    "backup")
        # 备份所有租户数据
        for tenant in $(ls data); do
            tar -czf backups/${tenant}-$(date +%Y%m%d).tar.gz data/$tenant
        done
        ;;
    "restore")
        # 恢复租户数据
        tar -xzf $2 -C data/
        ;;
    "cleanup")
        # 清理过期日志和缓存
        find logs -name "*.log" -mtime +30 -delete
        find data -name "*.tmp" -delete
        ;;
    "health-check")
        # 健康检查
        for tenant in $(ls data); do
            if [ -f "docker-compose.$tenant.yml" ]; then
                docker-compose -f docker-compose.$tenant.yml ps
            fi
        done
        ;;
    *)
        echo "用法: $0 {backup|restore|cleanup|health-check}"
        exit 1
esac

```text

### 16.6 最佳实践

1. **基础设施即代码**：所有配置使用 Git 管理，通过 CI/CD 自动部署

2. **租户隔离**：每个租户使用独立的数据库、Redis 实例和数据目录

3. **自动化测试**：部署后自动运行健康检查和功能测试

4. **监控告警**：设置关键指标告警，及时发现和处理问题

5. **备份策略**：每日自动备份，保留 30 天

6. **安全加固**：定期更新依赖，使用 HTTPS，限制访问 IP

7. **文档化**：记录所有部署和运维操作，建立知识库

### 16.7 成本优化建议

1. **资源复用**：中小租户可共享基础设施（需评估风险）

2. **弹性伸缩**：根据负载自动调整资源（K8s HPA）

3. **预留实例**：长期租户使用云厂商预留实例节省成本

4. **冷热数据分离**：历史数据归档到对象存储

5. **监控优化**：关闭非必要监控指标，减少资源消耗

---

## 十七、管理控制台完整实现指南

作为服务提供方，管理控制台是整个运营体系的核心。本章节提供从零到一的完整实现和部署指南。

### 17.1 Railway 部署可行性分析

#### 17.1.1 可行性评估

#### Railway 部署管理控制台

✅ **完全可行**

**优势**：

- ✅ 一键部署，无需管理基础设施

- ✅ 自动 HTTPS 和域名配置

- ✅ 内置 PostgreSQL 和 Redis 插件

- ✅ 自动备份和监控

- ✅ 按使用量计费，适合初创阶段

**限制**：

- ⚠️ 免费版有资源限制（512MB RAM, 1GB 磁盘）

- ⚠️ 不支持 Docker Compose 多容器编排

- ⚠️ 需要将多容器应用改造为单容器或使用 Railway 的服务网格

**推荐方案**：

1. **开发/测试环境**：Railway 快速搭建管理控制台

2. **生产环境**：阿里云 ECS / 腾讯云 CVM 部署（性能更稳定）

### 17.2 管理控制台项目结构

```text
deerflow-admin/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── tenants.py          # 租户管理
│   │   │   ├── deployments.py      # 部署管理
│   │   │   ├── channels.py         # 通道配置
│   │   │   ├── monitoring.py       # 监控数据
│   │   │   └── admin.py            # 用户权限
│   │   └── dependencies.py         # 依赖注入
│   ├── core/
│   │   ├── config.py               # 配置管理
│   │   ├── security.py             # 安全相关
│   │   └── encryption.py           # 加密工具
│   ├── models/
│   │   ├── tenant.py
│   │   ├── deployment.py
│   │   ├── channel.py
│   │   └── audit.py
│   ├── schemas/
│   │   ├── tenant.py
│   │   ├── deployment.py
│   │   └── channel.py
│   ├── services/
│   │   ├── deployment_engine.py    # 部署引擎
│   │   ├── monitor_service.py      # 监控服务
│   │   ├── notification_service.py # 通知服务
│   │   └── backup_service.py       # 备份服务
│   ├── utils/
│   │   ├── docker.py               # Docker 操作
│   │   ├── kubernetes.py           # K8s 操作
│   │   ├── fernet_crypto.py        # 加密解密
│   │   └── validators.py           # 数据验证
│   └── main.py                     # FastAPI 应用入口
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── tenants/
│   │   ├── deployments/
│   │   ├── channels/
│   │   ├── monitoring/
│   │   └── settings/
│   ├── components/
│   │   ├── ui/                     # shadcn/ui 组件
│   │   ├── tenants/
│   │   ├── deployments/
│   │   └── charts/
│   ├── lib/
│   │   ├── api.ts                  # API 客户端
│   │   ├── stores.ts               # Zustand 状态
│   │   └── utils.ts
│   └── package.json
├── templates/
│   ├── docker-compose/
│   │   ├── deerflow.yml
│   │   ├── nginx.conf
│   │   └── .env.template
│   └── kubernetes/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       └── secret.yaml
├── scripts/
│   ├── deploy.sh                   # 部署脚本
│   ├── backup.sh                   # 备份脚本
│   ├── restore.sh                  # 恢复脚本
│   └── migrate.sh                  # 数据库迁移
├── tests/
│   ├── test_tenant_api.py
│   ├── test_deployment_engine.py
│   └── test_encryption.py
├── alembic/
│   └── versions/
│       └── 001_create_tables.py
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx/
│       └── nginx.conf
├── .env.example
├── .env.production
├── pyproject.toml
├── requirements.txt
├── package.json
├── docker-compose.yml
├── docker-compose.prod.yml
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── Makefile
├── README.md
└── railway.json                    # Railway 配置

```text

### 17.3 核心服务实现

#### 17.3.1 数据库模型 (models/)

**tenant.py** - 租户模型：

```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    domain = Column(String(200), unique=True, nullable=True)
    plan = Column(String(50), nullable=False, default='basic')
    status = Column(String(50), nullable=False, default='pending', index=True)
    
    # 资源配额
    max_concurrent_sessions = Column(Integer, default=10)
    max_file_uploads_per_day = Column(Integer, default=100)
    max_sandbox_containers = Column(Integer, default=3)
    storage_quota_gb = Column(Integer, default=10)
    api_rate_limit = Column(Integer, default=100)
    
    # 部署信息
    deployment_mode = Column(String(50), default='docker-compose')
    deployment_config = Column(JSON, default=dict)
    instance_id = Column(String(200), nullable=True)
    
    # 联系信息
    contact_email = Column(String(200), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_name = Column(String(100), nullable=True)
    
    # 元数据
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True)
    
    # 关联关系
    deployments = relationship("Deployment", back_populates="tenant")
    channel_configs = relationship("ChannelConfig", back_populates="tenant")

```text

**deployment.py** - 部署模型：

```python
class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(100), ForeignKey("tenants.tenant_id"), nullable=False, index=True)
    deployment_id = Column(String(200), unique=True, nullable=False)
    template_version = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default='pending', index=True)
    
    # 部署文件
    docker_compose_file = Column(Text, nullable=True)
    kubernetes_yaml = Column(Text, nullable=True)
    
    # 容器信息
    container_ids = Column(JSON, default=list)
    
    # 时间戳
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    
    # 日志和错误
    logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # 关联
    tenant = relationship("Tenant", back_populates="deployments")

```text

**channel_config.py** - 通道配置模型：

```python
class ChannelConfig(Base):
    __tablename__ = "channel_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(100), ForeignKey("tenants.tenant_id"), nullable=False, index=True)
    channel_type = Column(String(50), nullable=False)  # 'feishu', 'dingtalk', 'slack'
    config = Column(JSON, nullable=False)  # 加密存储
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('tenant_id', 'channel_type', name='uq_tenant_channel'),
    )
    
    tenant = relationship("Tenant", back_populates="channel_configs")

```text

#### 17.3.2 部署引擎 (services/deployment_engine.py)

```python
import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class DeploymentConfig:
    tenant_id: str
    template_type: str  # 'docker-compose' | 'kubernetes'
    parameters: Dict[str, any]
    storage_path: Path
    network_name: str = "deerflow-network"

@dataclass
class DeploymentResult:
    success: bool
    instance_id: Optional[str] = None
    containers: Optional[List[Dict]] = None
    error_message: Optional[str] = None

class DeploymentEngine:
    """部署引擎核心类"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.workspace = self._create_workspace()
        self.logs = []
    
    def _create_workspace(self) -> Path:
        """创建部署工作目录"""
        workspace = Path(f"/tmp/deployments/{self.config.tenant_id}")
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace
    
    def _render_template(self, template: Dict, parameters: Dict) -> Dict:
        """渲染模板，替换参数"""
        rendered = json.loads(json.dumps(template))
        
        def replace_recursive(obj):
            if isinstance(obj, dict):
                return {k: replace_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_recursive(item) for item in obj]
            elif isinstance(obj, str):
                for key, value in parameters.items():
                    placeholder = f"${{{key}}}"
                    if placeholder in obj:
                        obj = obj.replace(placeholder, str(value))
                return obj
            else:
                return obj
        
        return replace_recursive(rendered)
    
    def generate_compose_file(self) -> Path:
        """生成 Docker Compose 文件"""
        template_path = Path("templates/docker-compose/deerflow.yml")
        with open(template_path) as f:
            template = yaml.safe_load(f)
        
        rendered = self._render_template(template, self.config.parameters)
        
        output_path = self.workspace / "docker-compose.yml"
        with open(output_path, 'w') as f:
            yaml.dump(rendered, f, default_flow_style=False)
        
        return output_path
    
    def generate_kubernetes_yaml(self) -> Path:
        """生成 Kubernetes 部署文件"""
        yaml_files = []
        
        # 生成 Namespace
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {"name": self.config.tenant_id}
        }
        yaml_files.append(namespace)
        
        # 生成 ConfigMap
        configmap = self._generate_configmap()
        yaml_files.append(configmap)
        
        # 生成 Secret
        secret = self._generate_secret()
        yaml_files.append(secret)
        
        # 生成 Deployment
        deployment = self._generate_deployment()
        yaml_files.append(deployment)
        
        # 生成 Service
        service = self._generate_service()
        yaml_files.append(service)
        
        # 生成 Ingress (如果需要)
        if self.config.parameters.get('domain'):
            ingress = self._generate_ingress()
            yaml_files.append(ingress)
        
        output_path = self.workspace / "kubernetes.yaml"
        with open(output_path, 'w') as f:
            yaml.dump_all(yaml_files, f, default_flow_style=False)
        
        return output_path
    
    def deploy(self) -> DeploymentResult:
        """执行部署"""
        try:
            if self.config.template_type == 'docker-compose':
                return self._deploy_docker_compose()
            elif self.config.template_type == 'kubernetes':
                return self._deploy_kubernetes()
            else:
                return DeploymentResult(
                    success=False,
                    error_message=f"Unsupported template type: {self.config.template_type}"
                )
        except Exception as e:
            return DeploymentResult(
                success=False,
                error_message=str(e)
            )
    
    def _deploy_docker_compose(self) -> DeploymentResult:
        """Docker Compose 部署"""
        compose_file = self.generate_compose_file()
        
        try:
            # 创建网络
            subprocess.run(
                ["docker", "network", "create", self.config.network_name],
                check=False,
                capture_output=True
            )
            
            # 拉取镜像
            self._log("正在拉取镜像...")
            subprocess.run(
                ["docker-compose", "-f", str(compose_file), "pull"],
                check=True,
                capture_output=True
            )
            
            # 启动服务
            self._log("正在启动服务...")
            subprocess.run(
                ["docker-compose", "-f", str(compose_file), "up", "-d"],
                check=True,
                capture_output=True
            )
            
            # 获取容器信息
            result = subprocess.run(
                ["docker-compose", "-f", str(compose_file), "ps", "--format", "json"],
                capture_output=True,
                text=True
            )
            
            containers = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        containers.append(json.loads(line))
            
            instance_id = f"docker-{self.config.tenant_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            return DeploymentResult(
                success=True,
                instance_id=instance_id,
                containers=containers
            )
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            self._log(f"部署失败: {error_msg}")
            return DeploymentResult(
                success=False,
                error_message=error_msg
            )
    
    def _deploy_kubernetes(self) -> DeploymentResult:
        """Kubernetes 部署"""
        yaml_file = self.generate_kubernetes_yaml()
        
        try:
            self._log("正在应用 Kubernetes 配置...")
            subprocess.run(
                ["kubectl", "apply", "-f", str(yaml_file)],
                check=True,
                capture_output=True
            )
            
            # 等待部署完成
            self._wait_for_deployment()
            
            instance_id = f"k8s-{self.config.tenant_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            return DeploymentResult(
                success=True,
                instance_id=instance_id
            )
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            self._log(f"K8s 部署失败: {error_msg}")
            return DeploymentResult(
                success=False,
                error_message=error_msg
            )
    
    def _wait_for_deployment(self, timeout=300):
        """等待 K8s 部署完成"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = subprocess.run(
                ["kubectl", "get", "deployments", "-n", self.config.tenant_id, "-o", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data['items']:
                    deployment = data['items'][0]
                    status = deployment['status']
                    
                    if status.get('availableReplicas', 0) >= status.get('replicas', 1):
                        self._log("部署完成")
                        return
            
            time.sleep(5)
        
        raise TimeoutError("部署超时")
    
    def stop(self) -> bool:
        """停止部署实例"""
        try:
            if self.config.template_type == 'docker-compose':
                compose_file = self.workspace / "docker-compose.yml"
                if compose_file.exists():
                    subprocess.run(
                        ["docker-compose", "-f", str(compose_file), "down"],
                        check=True,
                        capture_output=True
                    )
            elif self.config.template_type == 'kubernetes':
                subprocess.run(
                    ["kubectl", "delete", "-f", str(self.workspace / "kubernetes.yaml")],
                    check=True,
                    capture_output=True
                )
            return True
        except subprocess.CalledProcessError as e:
            self._log(f"停止失败: {e.stderr.decode()}")
            return False
    
    def get_logs(self, tail: int = 100) -> str:
        """获取部署日志"""
        try:
            if self.config.template_type == 'docker-compose':
                compose_file = self.workspace / "docker-compose.yml"
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "logs", "--tail", str(tail)],
                    capture_output=True,
                    text=True
                )
                return result.stdout
            else:
                # K8s 日志获取
                logs = []
                pods = self._get_pods()
                for pod in pods:
                    result = subprocess.run(
                        ["kubectl", "logs", pod, "--tail", str(tail), "-n", self.config.tenant_id],
                        capture_output=True,
                        text=True
                    )
                    logs.append(f"=== {pod} ===\n{result.stdout}")
                return "\n".join(logs)
        except subprocess.CalledProcessError as e:
            return f"获取日志失败: {e.stderr.decode()}"
    
    def _get_pods(self) -> List[str]:
        """获取 K8s Pod 列表"""
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", self.config.tenant_id, "-o", "jsonpath={.items[*].metadata.name}"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split() if result.stdout.strip() else []
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

```text

#### 17.3.3 加密服务 (services/encryption.py)

```python
from cryptography.fernet import Fernet
import json
import base64
import os
from typing import Any, Dict

class ConfigEncryption:
    """配置加密服务"""
    
    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
        self.key = key
    
    def encrypt(self, data: Dict[str, Any]) -> str:
        """加密字典数据"""
        json_str = json.dumps(data, ensure_ascii=False)
        encrypted = self.cipher.encrypt(json_str.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_str: str) -> Dict[str, Any]:
        """解密字符串为字典"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_str.encode('utf-8'))
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return json.loads(decrypted.decode('utf-8'))
    
    def encrypt_value(self, value: str) -> str:
        """加密单个字符串值"""
        return self.cipher.encrypt(value.encode('utf-8')).decode('utf-8')
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """解密单个字符串值"""
        return self.cipher.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')
    
    @classmethod
    def generate_key(cls) -> bytes:
        """生成新的加密密钥"""
        return Fernet.generate_key()
    
    @classmethod
    def load_from_env(cls) -> 'ConfigEncryption':
        """从环境变量加载密钥"""
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = cls.generate_key()
            print(f"警告: 未设置 ENCRYPTION_KEY，使用临时密钥: {key.decode()}")
        else:
            key = key.encode('utf-8')
        return cls(key)

```text

#### 17.3.4 监控服务 (services/monitor_service.py)

```python
import psutil
import docker
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class MonitorService:
    """监控服务"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
    
    def get_system_metrics(self) -> Dict:
        """获取系统整体指标"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total_gb': memory.total / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'percent': disk.percent
            }
        }
    
    def get_container_metrics(self, container_name: str) -> Optional[Dict]:
        """获取容器指标"""
        try:
            container = self.docker_client.containers.get(container_name)
            stats = container.stats(stream=False)
            
            # 计算 CPU 使用率
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100
            
            # 计算内存使用
            memory_usage = stats['memory_stats']['usage'] / (1024**3)
            memory_limit = stats['memory_stats']['limit'] / (1024**3)
            memory_percent = (memory_usage / memory_limit) * 100
            
            return {
                'container_id': container.id[:12],
                'container_name': container.name,
                'cpu_percent': round(cpu_percent, 2),
                'memory_gb': round(memory_usage, 2),
                'memory_limit_gb': round(memory_limit, 2),
                'memory_percent': round(memory_percent, 2),
                'network_rx': stats['networks'].get('eth0', {}).get('rx_bytes', 0),
                'network_tx': stats['networks'].get('eth0', {}).get('tx_bytes', 0)
            }
        except docker.errors.NotFound:
            return None
    
    def get_tenant_containers(self, tenant_id: str) -> List[Dict]:
        """获取租户的所有容器"""
        containers = []
        for container in self.docker_client.containers.list(all=True):
            if tenant_id in container.name:
                containers.append({
                    'id': container.id[:12],
                    'name': container.name,
                    'status': container.status,
                    'image': container.image.tags[0] if container.image.tags else container.image.id[:20]
                })
        return containers
    
    def check_health(self, tenant_id: str) -> Dict:
        """检查租户健康状态"""
        containers = self.get_tenant_containers(tenant_id)
        
        if not containers:
            return {'status': 'error', 'message': '未找到容器'}
        
        unhealthy = []
        for container in containers:
            if container['status'] != 'running':
                unhealthy.append(f"{container['name']} 状态: {container['status']}")
        
        if unhealthy:
            return {
                'status': 'unhealthy',
                'message': '; '.join(unhealthy),
                'containers': containers
            }
        
        return {
            'status': 'healthy',
            'message': '所有容器运行正常',
            'containers': containers
        }

```text

### 17.4 Railway 部署配置

**railway.json** - Railway 配置文件：

```json
{
  "$schema": "<https://railway.app/railway.schema.json>",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "docker/Dockerfile.backend"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicy": {
      "type": "ON_FAILURE"
    },
    "waitFor": [
      "postgresql",
      "redis"
    ]
  },
  "variables": {
    "ENVIRONMENT": "production",
    "DATABASE_URL": "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}",
    "REDIS_URL": "redis://${REDIS_HOST}:${REDIS_PORT}"
  },
  "services": [
    {
      "name": "postgresql",
      "type": "postgresql",
      "plan": "shared-cpu-2x",
      "envVars": {
        "POSTGRES_DB": "deerflow_admin",
        "POSTGRES_USER": "deerflow",
        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}"
      }
    },
    {
      "name": "redis",
      "type": "redis",
      "plan": "shared-cpu-2x"
    }
  ]
}

```text

**Dockerfile.backend** - 后端 Dockerfile：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 运行数据库迁移
RUN alembic upgrade head

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

```text

**Dockerfile.frontend** - 前端 Dockerfile：

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM nginx:alpine

COPY --from=builder /app/.next/static /usr/share/nginx/html/static
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

```text

### 17.5 从零到一部署流程

#### 阶段 1: 环境准备 (1-2 天)

1. **选择部署平台**
   - 开发环境: Railway (快速验证)
   - 生产环境: 阿里云 ECS / 腾讯云 CVM

2. **准备服务器**
   ```bash
   # 登录服务器
   ssh root@your-server-ip
   
   # 更新系统
   apt update && apt upgrade -y
   
   # 安装 Docker & Docker Compose
   curl -fsSL <https://get.docker.com> -o get-docker.sh
   sh get-docker.sh
   curl -L "<https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname> -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   chmod +x /usr/local/bin/docker-compose
   
   # 安装 Python 3.12
   apt install -y python3.12 python3.12-venv python3.12-dev
   
   # 安装 Node.js 18+
   curl -fsSL <https://deb.nodesource.com/setup_18.x> | bash -
   apt install -y nodejs
   
   # 安装 pnpm
   npm install -g pnpm
   ```text
3. **配置域名和 SSL**
   ```bash
   # 购买域名并解析到服务器 IP
   # 使用 Let's Encrypt 获取 SSL 证书
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d admin.yourdomain.com
   ```text
#### 阶段 2: 数据库初始化 (0.5 天)

1. **创建数据库**
   ```sql
   CREATE DATABASE deerflow_admin;
   CREATE USER deerflow_admin WITH PASSWORD 'strong-password';
   GRANT ALL PRIVILEGES ON DATABASE deerflow_admin TO deerflow_admin;
   ```text
2. **运行迁移**
   ```bash
   cd deerflow-admin
   alembic upgrade head
   ```text
3. **创建管理员用户**
   ```bash
   python -m app.cli create-admin --email admin@yourdomain.com --password 'admin-password'
   ```text
#### 阶段 3: 部署管理控制台 (1 天)

1. **克隆和配置**
   ```bash
   git clone <your-repo>
   cd deerflow-admin
   
   # 复制环境配置
   cp .env.example .env
   # 编辑 .env 文件，填入数据库、Redis、加密密钥等
   ```text
2. **构建和启动**
   ```bash
   # 使用 Docker Compose
   docker-compose -f docker-compose.prod.yml up -d
   
   # 或使用 Makefile
   make prod-build
   make prod-up
   ```text
3. **验证部署**
   ```bash
   # 检查服务状态
   docker-compose ps
   
   # 查看日志
   docker-compose logs -f
   
   # 测试 API
   curl <https://admin.yourdomain.com/api/v1/health>
   ```text
#### 阶段 4: 配置管理控制台 (0.5 天)

1. **登录管理控制台**
   - 访问 <https://admin.yourdomain.com>
   - 使用管理员账号登录

2. **配置系统设置**
   - 设置邮件服务器 (SMTP)
   - 配置告警通知 (Webhook/邮件)
   - 上传部署模板 (Docker Compose/K8s YAML)
   - 设置备份策略

3. **创建第一个租户**
   - 点击"创建租户"
   - 填写租户信息 (名称、域名、联系人)
   - 选择套餐 (basic/enterprise)
   - 点击"部署"按钮
   - 等待部署完成 (约 5-10 分钟)

#### 阶段 5: 配置租户通道 (0.5 天)

1. **为租户配置飞书通道**
   - 在租户详情页，进入"通道配置"标签
   - 点击"添加飞书通道"
   - 填写飞书 App ID、App Secret、Encryption Key
   - 点击"测试连接"
   - 保存配置

2. **验证消息收发**
   - 在飞书中发送消息到 Bot
   - 确认管理控制台收到消息
   - 确认 DeerFlow 实例回复消息

#### 阶段 6: 监控和运维 (持续)

1. **设置监控告警**
   ```bash
   # 配置 Prometheus 抓取指标
   # 配置 Grafana 仪表盘
   # 设置告警规则 (CPU > 80%, 内存 > 85%, 磁盘 > 90%)
   ```text
2. **定期备份**
   ```bash
   # 自动备份脚本
   0 2 * * * /path/to/backup.sh
   ```text
3. **日志管理**
   ```bash
   # 使用 Loki 收集日志
   # 配置日志保留策略 (30天)
   ```text
4. **性能优化**
   - 定期清理未使用的镜像
   - 优化数据库查询
   - 调整容器资源限制

### 17.6 大小场景覆盖

#### 场景 1: 单租户小规模 (个人/小团队)

**需求**：1-5 个用户，轻量使用

**部署方案**：

- Railway 部署管理控制台 (免费版)

- 单服务器部署 DeerFlow 实例 (1核2G)

- 使用 LocalSandboxProvider (开发模式)

**成本**：~$5-10/月

**配置示例**：

```yaml
# docker-compose.simple.yml
version: '3.8'
services:
  deerflow:
    image: deerflow/all-in-one:latest
    ports:
      - "2026:2026"
    environment:
      - BETTER_AUTH_SECRET=${SECRET}
      - SANDBOX_PROVIDER=local
      - MEMORY_STORAGE_PATH=/data
    volumes:
      - ./data:/data

```text

#### 场景 2: 中型企业 (50-200 用户)

**需求**：多部门使用，需要隔离

**部署方案**：

- 阿里云 ECS 部署管理控制台 (4核8G)

- 每个租户独立 Docker Compose 实例

- 使用 AioSandboxProvider (生产模式)

- PostgreSQL + Redis 独立实例

**成本**：~$200-500/月

**配置示例**：

```yaml
# docker-compose.enterprise.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
  
  frontend:
    image: deerflow/frontend:latest
    environment:
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
  
  gateway:
    image: deerflow/gateway:latest
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379
      - STORAGE_PATH=/data
  
  langgraph:
    image: deerflow/langgraph:latest
    environment:
      - REDIS_URL=redis://redis:6379
      - STORAGE_PATH=/data
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:

```text

#### 场景 3: 大型企业 (500+ 用户，多租户)

**需求**：完全隔离，高可用，弹性伸缩

**部署方案**：

- K8s 集群部署管理控制台 (K8s Deployment)

- 每个租户独立 K8s Namespace

- 使用 K8s HPA 自动伸缩

- 云数据库 (RDS/TDSQL)

- 对象存储 (OSS/COS)

- 全球多区域部署

**成本**：~$1000+/月

**K8s 配置示例**：

```yaml
# k8s/tenant-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-${TENANT_ID}
  labels:
    tenant: ${TENANT_ID}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deerflow
  namespace: tenant-${TENANT_ID}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: deerflow
  template:
    metadata:
      labels:
        app: deerflow
    spec:
      containers:
      - name: deerflow
        image: deerflow/all-in-one:latest
        ports:
        - containerPort: 2026
        env:
        - name: TENANT_ID
          value: ${TENANT_ID}
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: deerflow-data-pvc
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: deerflow-hpa
  namespace: tenant-${TENANT_ID}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: deerflow
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

```text
### 17.7 故障排查和最佳实践

#### 常见问题

1. **Railway 部署失败**
   - 检查 `railway.json` 配置
   - 查看构建日志: `railway logs`
   - 确保环境变量正确设置

2. **数据库连接失败**
   - 检查 DATABASE_URL 格式
   - 确认数据库服务运行正常
   - 验证网络连通性

3. **Docker 权限问题**
   - 将用户加入 docker 组: `sudo usermod -aG docker $USER`
   - 重启会话生效

4. **端口冲突**
   - 检查端口占用: `netstat -tlnp`
   - 修改 docker-compose.yml 中的端口映射

5. **磁盘空间不足**
   - 清理未使用的 Docker 镜像: `docker image prune -a`
   - 清理未使用的 Docker 卷: `docker volume prune`

#### 最佳实践

1. **安全**
   - 使用强密码和随机密钥
   - 定期更新依赖和基础镜像
   - 启用 HTTPS 和防火墙
   - 限制数据库访问 IP

2. **性能**
   - 使用 Redis 缓存频繁访问的数据
   - 配置数据库连接池
   - 启用 Gzip 压缩
   - 使用 CDN 加速静态资源

3. **可靠性**
   - 配置健康检查和自动重启
   - 设置日志轮转和保留策略
   - 定期备份数据库和文件
   - 使用监控告警系统

4. **可维护性**
   - 使用版本控制管理所有配置
   - 编写部署和运维文档
   - 建立 CI/CD 流水线
   - 定期进行故障演练

---

## 十八、Railway快速部署管理控制台原型

作为服务提供方，您可以使用Railway快速搭建管理控制台原型，验证业务逻辑和用户体验。本章节提供完整的Railway部署指南。

### 18.1 项目准备

#### 18.1.1 创建独立仓库

管理控制台应该是一个独立的Git仓库，与DeerFlow核心代码分离：

```bash
# 创建新仓库
mkdir deerflow-admin
cd deerflow-admin

# 初始化Git
git init
git remote add origin <your-git-repo>

# 创建基础目录结构
mkdir -p app/api/v1 app/core app/models app/schemas app/services app/utils
mkdir -p frontend/app frontend/components frontend/lib
mkdir -p templates/docker-compose templates/kubernetes
mkdir -p scripts tests docker k8s
```text
#### 18.1.2 初始化项目文件

**pyproject.toml** - Python依赖：

```toml
[project]
name = "deerflow-admin"
version = "0.1.0"
description = "DeerFlow Management Console"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "psycopg2-binary>=2.9.0",
    "redis>=5.0.0",
    "cryptography>=41.0.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "celery>=5.3.0",
    "docker>=6.1.0",
    "kubernetes>=28.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 88
target-version = ['py312']

[tool.ruff]
target-version = "py312"
line-length = 88
select = ["E", "F", "B", "I"]
```text
**package.json** - 前端依赖：

```json
{
  "name": "deerflow-admin-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.8.0",
    "zustand": "^4.4.0",
    "react-hook-form": "^7.47.0",
    "zod": "^3.22.0",
    "shadcn-ui": "^0.4.0",
    "tailwindcss": "^3.3.0",
    "lucide-react": "^0.292.0",
    "recharts": "^2.8.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "14.0.4"
  }
}
```text
### 18.2 Railway 配置详解

#### 18.2.1 railway.json 配置

创建 `railway.json` 在项目根目录：

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "nixpacksPlan": {
      "providers": ["python", "nodejs"],
      "phases": {
        "build": {
          "cmds": [
            "cd frontend && npm install -g pnpm && pnpm install --frozen-lockfile",
            "cd frontend && pnpm build"
          ]
        }
      }
    }
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/v1/health",
    "restartPolicy": {
      "type": "ON_FAILURE",
      "maxRetries": 3
    },
    "waitFor": [
      "postgresql",
      "redis"
    ]
  },
  "variables": {
    "ENVIRONMENT": "production",
    "PYTHON_VERSION": "3.12",
    "NODE_VERSION": "18",
    "DATABASE_URL": "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}",
    "REDIS_URL": "redis://${REDIS_HOST}:${REDIS_PORT}",
    "BETTER_AUTH_SECRET": "${BETTER_AUTH_SECRET}",
    "ENCRYPTION_KEY": "${ENCRYPTION_KEY}"
  },
  "services": [
    {
      "name": "postgresql",
      "type": "postgresql",
      "plan": "shared-cpu-2x",
      "envVars": {
        "POSTGRES_DB": "deerflow_admin",
        "POSTGRES_USER": "deerflow",
        "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD}"
      }
    },
    {
      "name": "redis",
      "type": "redis",
      "plan": "shared-cpu-2x"
    }
  ]
}
```text
#### 18.2.2 环境变量配置

在Railway控制台设置以下环境变量：

```bash
# 必需变量
BETTER_AUTH_SECRET=your-random-secret-here
ENCRYPTION_KEY=your-fernet-key-here
POSTGRES_PASSWORD=your-db-password

# 可选变量（用于订阅功能）
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_PRICE_ID=price_xxx  # 季度订阅价格ID

# 邮件配置（用于通知）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# 监控配置
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
```text
**生成加密密钥**：

```bash
# 生成 BETTER_AUTH_SECRET
openssl rand -hex 32

# 生成 ENCRYPTION_KEY (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```text
#### 18.2.3 目录结构调整

Railway 使用 Nixpacks 自动检测，需要调整目录结构：

```text
deerflow-admin/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── api/
│   │   └── ...
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/                   # 前端代码
│   ├── app/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── next.config.js
│   └── ...
├── railway.json                # Railway 配置
├── .env.example
└── README.md
```text
**requirements.txt**（Railway需要）：

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
cryptography==41.0.7
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
celery==5.3.4
docker==6.1.3
kubernetes==28.1.0
```text
### 18.3 部署步骤

#### 18.3.1 首次部署

#### 步骤 1: 推送代码到Git仓库

```bash
cd deerflow-admin
git add .
git commit -m "Initial commit: Management Console"
git push origin main
```text
#### 步骤 2: 在Railway创建项目

- 登录 [Railway.app](https://railway.app)
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 选择你的 `deerflow-admin` 仓库
- Railway 自动检测并开始构建

#### 步骤 3: 添加插件

在项目设置中添加：
- PostgreSQL (计划: shared-cpu-2x)
- Redis (计划: shared-cpu-2x)

#### 步骤 4: 设置环境变量

在项目 Settings → Variables 中添加：
```text
BETTER_AUTH_SECRET=your-secret
ENCRYPTION_KEY=your-key
POSTGRES_PASSWORD=your-password
```text
#### 步骤 5: 等待部署完成

- Railway 自动运行构建脚本
- 自动执行数据库迁移（如果配置了）
- 部署完成后获得公网URL

#### 步骤 6: 初始化数据库

```bash
# 通过Railway CLI或SSH进入容器
railway ssh

# 运行迁移
cd backend
alembic upgrade head

# 创建管理员用户
python -m app.cli create-admin --email admin@yourdomain.com --password 'secure-password'
```text
#### 18.3.2 持续部署

Railway 自动配置了 CI/CD：
- 每次推送到 main 分支自动触发部署
- 自动运行测试（如果配置了）
- 自动构建和部署

**配置分支部署**：
- 在 Railway 项目设置中
- 添加 "Preview Deployments"
- 每个 PR 都会生成预览环境

### 18.4 管理控制台使用

#### 18.4.1 登录和初始配置

1. **访问管理控制台**
   - 打开 Railway 提供的 URL
   - 使用管理员账号登录

2. **配置系统设置**
   - 设置邮件服务器（SMTP）
   - 配置告警通知（Webhook/邮件）
   - 上传DeerFlow部署模板
   - 设置备份策略

3. **创建第一个租户**
   - 点击"创建租户"
   - 填写租户信息
   - 选择套餐
   - 点击"部署"按钮

#### 18.4.2 监控和运维

- **仪表盘**：查看系统概览、资源使用率、健康状态
- **租户管理**：查看、搜索、管理所有租户
- **部署管理**：查看部署历史、执行操作（启动/停止/重启）
- **通道配置**：为租户配置飞书/钉钉等通道
- **监控日志**：实时查看各租户日志

### 18.5 从原型到生产

当原型验证完成后，迁移到生产环境：

1. **选择生产平台**
   - 阿里云 ECS / 腾讯云 CVM
   - 配置更高的资源（4核8G起步）
   - 独立的数据库和Redis实例

2. **数据迁移**
   ```bash
   # 导出Railway数据库
   pg_dump -h <railway-host> -U deerflow deerflow_admin > backup.sql
   
   # 导入到生产数据库
   psql -h <prod-host> -U deerflow deerflow_admin < backup.sql
   ```text
3. **更新DNS**
   - 将域名从Railway CNAME 指向生产服务器IP
   - 配置SSL证书

4. **更新环境变量**
   - 更新数据库连接字符串
   - 更新Redis连接
   - 更新加密密钥（保持数据可解密）

5. **验证部署**
   - 测试所有功能
   - 验证数据完整性
   - 检查监控告警

---

## 十九、季度订阅机制实现

作为服务提供方，需要实现订阅机制来管理租户的付费周期和访问权限。

### 19.1 订阅模型设计

#### 19.1.1 数据库表扩展

在 `tenants` 表中添加订阅相关字段：

```sql
ALTER TABLE tenants ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'trial';
ALTER TABLE tenants ADD COLUMN subscription_plan VARCHAR(50) DEFAULT 'basic';
ALTER TABLE tenants ADD COLUMN subscription_start_date TIMESTAMP;
ALTER TABLE tenants ADD COLUMN subscription_end_date TIMESTAMP;
ALTER TABLE tenants ADD COLUMN trial_end_date TIMESTAMP;
ALTER TABLE tenants ADD COLUMN billing_cycle VARCHAR(20) DEFAULT 'monthly'; -- monthly, quarterly, yearly
ALTER TABLE tenants ADD COLUMN stripe_customer_id VARCHAR(200);
ALTER TABLE tenants ADD COLUMN stripe_subscription_id VARCHAR(200);
```text
创建 `subscriptions` 表：

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(100) NOT NULL REFERENCES tenants(tenant_id),
    stripe_subscription_id VARCHAR(200) UNIQUE NOT NULL,
    stripe_price_id VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL, -- trialing, active, past_due, canceled, unpaid
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_tenant ON subscriptions(tenant_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_end_date ON subscriptions(current_period_end);
```text
创建 `invoices` 表：

```sql
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(100) NOT NULL REFERENCES tenants(tenant_id),
    stripe_invoice_id VARCHAR(200) UNIQUE NOT NULL,
    stripe_payment_intent_id VARCHAR(200),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50) NOT NULL, -- draft, open, paid, uncollectible, void
    hosted_invoice_url TEXT,
    invoice_pdf_url TEXT,
    due_date TIMESTAMP,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX idx_invoices_status ON invoices(status);
```text
#### 19.1.2 订阅状态枚举

```python
# app/models/subscription.py
from enum import Enum

class SubscriptionStatus(str, Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class SubscriptionPlan(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
```text
### 19.2 Stripe 集成

#### 19.2.1 Stripe 配置

1. **创建Stripe账户**
   - 注册 [Stripe](https://stripe.com)
   - 获取 API 密钥（Secret Key 和 Publishable Key）
   - 配置 Webhook 端点

2. **创建产品和服务**

在Stripe Dashboard创建：
- **产品**：DeerFlow Management Console
  - Basic: ￥2999/季度
  - Professional: ￥12999/季度
  - Enterprise: ￥48000/季度
- **价格**：为每个产品创建季度和年度价格

3. **配置Webhook**

在Stripe Dashboard → Developers → Webhooks：
- 端点URL: `https://admin.yourdomain.com/api/v1/webhooks/stripe`
- 选择事件：
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.paid`
  - `invoice.payment_failed`

#### 19.2.2 Stripe服务封装

```python
# app/services/stripe_service.py
import stripe
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeService:
    """Stripe 服务封装"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_customer(self, tenant_id: str, email: str, name: str) -> stripe.Customer:
        """创建Stripe客户"""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                "tenant_id": tenant_id
            }
        )
        return customer
    
    def create_subscription(
        self, 
        customer_id: str, 
        price_id: str,
        trial_days: int = 14
    ) -> stripe.Subscription:
        """创建订阅"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            trial_period_days=trial_days,
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
        )
        return subscription
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> stripe.Subscription:
        """取消订阅"""
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=at_period_end
        )
        return subscription
    
    def reactivate_subscription(self, subscription_id: str) -> stripe.Subscription:
        """重新激活订阅"""
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=False
        )
        return subscription
    
    def update_subscription_quantity(self, subscription_id: str, quantity: int) -> stripe.Subscription:
        """更新订阅数量（如用户数）"""
        subscription = stripe.Subscription.modify(
            subscription_id,
            items=[{
                "id": self.get_subscription_items(subscription_id)[0].id,
                "quantity": quantity
            }]
        )
        return subscription
    
    def get_subscription_items(self, subscription_id: str) -> list:
        """获取订阅项目"""
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription["items"]["data"]
    
    def create_checkout_session(
        self, 
        customer_id: str, 
        price_id: str,
        success_url: str,
        cancel_url: str
    ) -> stripe.checkout.Session:
        """创建结账会话"""
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            allow_promotion_codes=True,
        )
        return session
    
    def handle_webhook(self, payload: Dict[str, Any], signature: str) -> Optional[stripe.Event]:
        """处理Stripe Webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, os.getenv("STRIPE_WEBHOOK_SECRET")
            )
            return event
        except ValueError:
            # 无效的payload
            return None
        except stripe.error.SignatureVerificationError:
            # 无效的签名
            return None
    
    def sync_subscription_from_webhook(self, event: stripe.Event):
        """从Webhook同步订阅状态到数据库"""
        event_type = event["type"]
        data = event["data"]["object"]
        
        if event_type == "customer.subscription.created":
            self._create_or_update_subscription(data)
        elif event_type == "customer.subscription.updated":
            self._create_or_update_subscription(data)
        elif event_type == "customer.subscription.deleted":
            self._delete_subscription(data["id"])
        elif event_type == "invoice.paid":
            self._handle_invoice_paid(data)
        elif event_type == "invoice.payment_failed":
            self._handle_invoice_payment_failed(data)
    
    def _create_or_update_subscription(self, stripe_subscription: Dict[str, Any]):
        """创建或更新订阅记录"""
        from app.models.subscription import Subscription as DBSubscription
        
        # 获取租户信息
        customer = stripe.Customer.retrieve(stripe_subscription["customer"])
        tenant_id = customer.metadata.get("tenant_id")
        
        if not tenant_id:
            return
        
        # 查找或创建订阅记录
        db_sub = self.db.query(DBSubscription).filter(
            DBSubscription.stripe_subscription_id == stripe_subscription["id"]
        ).first()
        
        if not db_sub:
            db_sub = DBSubscription(
                tenant_id=tenant_id,
                stripe_subscription_id=stripe_subscription["id"]
            )
            self.db.add(db_sub)
        
        # 更新字段
        db_sub.stripe_price_id = stripe_subscription["items"]["data"][0]["price"]["id"]
        db_sub.status = stripe_subscription["status"]
        db_sub.current_period_start = datetime.fromtimestamp(stripe_subscription["current_period_start"])
        db_sub.current_period_end = datetime.fromtimestamp(stripe_subscription["current_period_end"])
        db_sub.cancel_at_period_end = stripe_subscription.get("cancel_at_period_end", False)
        db_sub.canceled_at = (
            datetime.fromtimestamp(stripe_subscription["canceled_at"]) 
            if stripe_subscription.get("canceled_at") 
            else None
        )
        db_sub.updated_at = datetime.now()
        
        # 同步到租户表
        tenant = self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if tenant:
            tenant.subscription_status = stripe_subscription["status"]
            tenant.subscription_end_date = db_sub.current_period_end
            tenant.stripe_subscription_id = stripe_subscription["id"]
        
        self.db.commit()
    
    def _delete_subscription(self, stripe_subscription_id: str):
        """删除订阅记录"""
        from app.models.subscription import Subscription as DBSubscription
        
        db_sub = self.db.query(DBSubscription).filter(
            DBSubscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if db_sub:
            self.db.delete(db_sub)
            self.db.commit()
    
    def _handle_invoice_paid(self, invoice: Dict[str, Any]):
        """处理发票支付成功"""
        # 更新租户状态为 active
        subscription = self.db.query(DBSubscription).filter(
            DBSubscription.stripe_subscription_id == invoice["subscription"]
        ).first()
        
        if subscription:
            tenant = self.db.query(Tenant).filter(
                Tenant.tenant_id == subscription.tenant_id
            ).first()
            
            if tenant:
                tenant.subscription_status = "active"
                tenant.subscription_start_date = subscription.current_period_start
                tenant.subscription_end_date = subscription.current_period_end
                
                # 根据价格确定套餐
                price = stripe.Price.retrieve(invoice["lines"]["data"][0]["price"]["id"])
                if price.product == "prod_xxx":  # Basic
                    tenant.subscription_plan = "basic"
                elif price.product == "prod_yyy":  # Professional
                    tenant.subscription_plan = "professional"
                elif price.product == "prod_zzz":  # Enterprise
                    tenant.subscription_plan = "enterprise"
            
            self.db.commit()
    
    def _handle_invoice_payment_failed(self, invoice: Dict[str, Any]):
        """处理发票支付失败"""
        subscription = self.db.query(DBSubscription).filter(
            DBSubscription.stripe_subscription_id == invoice["subscription"]
        ).first()
        
        if subscription:
            tenant = self.db.query(Tenant).filter(
                Tenant.tenant_id == subscription.tenant_id
            ).first()
            
            if tenant:
                tenant.subscription_status = "past_due"
            
            self.db.commit()
```text
#### 19.2.3 Webhook 端点

```python
# app/api/v1/webhooks.py
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stripe_service import StripeService
import stripe
import hmac
import hashlib

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Stripe Webhook 端点"""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    
    stripe_service = StripeService(db)
    
    try:
        event = stripe_service.handle_webhook(payload, signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not event:
        raise HTTPException(status_code=400, detail="Invalid webhook")
    
    # 处理事件
    stripe_service.sync_subscription_from_webhook(event)
    
    return JSONResponse(content={"status": "success"})
```text
### 19.3 订阅管理 API

#### 19.3.1 创建订阅会话

```python
# app/api/v1/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.services.stripe_service import StripeService
from app.models.tenant import Tenant

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

class CreateSubscriptionRequest(BaseModel):
    tenant_id: str
    email: str
    name: str
    price_id: str
    success_url: str
    cancel_url: str

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateSubscriptionRequest,
    db: Session = Depends(get_db)
):
    """创建订阅结账会话"""
    stripe_service = StripeService(db)
    
    # 检查租户是否存在
    tenant = db.query(Tenant).filter(Tenant.tenant_id == request.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # 检查是否已有客户
    if tenant.stripe_customer_id:
        customer_id = tenant.stripe_customer_id
    else:
        # 创建新客户
        customer = stripe_service.create_customer(
            tenant_id=request.tenant_id,
            email=request.email,
            name=request.name
        )
        customer_id = customer.id
        tenant.stripe_customer_id = customer_id
        db.commit()
    
    # 创建结账会话
    try:
        session = stripe_service.create_checkout_session(
            customer_id=customer_id,
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "session_id": session.id,
        "checkout_url": session.url
    }
```text
#### 19.3.2 订阅状态查询

```python
class SubscriptionResponse(BaseModel):
    status: str
    plan: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    trial_end: Optional[datetime]

@router.get("/{tenant_id}")
async def get_subscription(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """获取租户订阅状态"""
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == tenant_id,
        Subscription.status.in_(["active", "trialing"])
    ).first()
    
    if not subscription:
        return {
            "status": tenant.subscription_status,
            "plan": tenant.subscription_plan,
            "current_period_start": None,
            "current_period_end": None,
            "cancel_at_period_end": False,
            "trial_end": tenant.trial_end_date
        }
    
    return {
        "status": subscription.status,
        "plan": tenant.subscription_plan,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "trial_end": None
    }
```text
#### 19.3.3 取消订阅

```python
class CancelSubscriptionRequest(BaseModel):
    tenant_id: str
    at_period_end: bool = True  # True: 当前周期结束后取消, False: 立即取消

@router.post("/cancel")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    db: Session = Depends(get_db)
):
    """取消订阅"""
    tenant = db.query(Tenant).filter(Tenant.tenant_id == request.tenant_id).first()
    if not tenant or not tenant.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    stripe_service = StripeService(db)
    
    try:
        subscription = stripe_service.cancel_subscription(
            subscription_id=tenant.stripe_subscription_id,
            at_period_end=request.at_period_end
        )
        
        # 更新数据库
        db_sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == tenant.stripe_subscription_id
        ).first()
        
        if db_sub:
            db_sub.cancel_at_period_end = request.at_period_end
            db_sub.canceled_at = datetime.now() if not request.at_period_end else None
            db.commit()
        
        return {
            "status": "success",
            "message": f"Subscription will be canceled {'at period end' if request.at_period_end else 'immediately'}",
            "subscription_status": subscription.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```text
#### 19.3.4 重新激活订阅

```python
@router.post("/reactivate")
async def reactivate_subscription(
    tenant_id: str,
    db: Session = Depends(get_db)
):
    """重新激活已取消的订阅"""
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant or not tenant.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    stripe_service = StripeService(db)
    
    try:
        subscription = stripe_service.reactivate_subscription(
            subscription_id=tenant.stripe_subscription_id
        )
        
        # 更新数据库
        db_sub = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == tenant.stripe_subscription_id
        ).first()
        
        if db_sub:
            db_sub.cancel_at_period_end = False
            db_sub.canceled_at = None
            db.commit()
        
        return {
            "status": "success",
            "message": "Subscription reactivated",
            "subscription_status": subscription.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```text
### 19.4 订阅验证中间件

在管理控制台中，需要验证租户订阅状态才能执行某些操作（如部署新实例）。

```python
# app/api/dependencies.py
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.tenant import Tenant
from app.services.stripe_service import StripeService

class SubscriptionRequired:
    """订阅验证依赖"""
    
    def __init__(self, require_active: bool = True):
        self.require_active = require_active
    
    def __call__(self, request: Request, db: Session = Depends(get_db)):
        # 从请求中获取 tenant_id（通过 header 或 token）
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant-ID header required")
        
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # 检查订阅状态
        if self.require_active:
            if tenant.subscription_status not in ["active", "trialing"]:
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "subscription_required",
                        "message": "Active subscription required",
                        "subscription_status": tenant.subscription_status,
                        "upgrade_url": f"/billing?tenant_id={tenant_id}"
                    }
                )
            
            # 检查是否过期
            if tenant.subscription_end_date and tenant.subscription_end_date < datetime.now():
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "subscription_expired",
                        "message": "Subscription has expired",
                        "renewal_url": f"/billing/renew?tenant_id={tenant_id}"
                    }
                )
        
        return tenant

# 使用示例
@router.post("/deployments")
async def create_deployment(
    request: DeploymentRequest,
    tenant: Tenant = Depends(SubscriptionRequired(require_active=True)),
    db: Session = Depends(get_db)
):
    """创建部署（需要有效订阅）"""
    # 只有活跃订阅的租户才能部署
    ...
```text
### 19.5 前端订阅管理界面

#### 19.5.1 账单页面

```tsx
// frontend/app/billing/page.tsx
'use client'

import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatCurrency } from '@/lib/utils'
import { useToast } from '@/components/ui/use-toast'

export default function BillingPage() {
  const { toast } = useToast()
  const tenantId = useTenantId() // 从上下文获取
  
  // 获取订阅信息
  const { data: subscription, isLoading } = useQuery({
    queryKey: ['subscription', tenantId],
    queryFn: () => fetch(`/api/v1/subscriptions/${tenantId}`).then(r => r.json())
  })
  
  // 创建结账会话
  const checkoutMutation = useMutation({
    mutationFn: async (priceId: string) => {
      const response = await fetch('/api/v1/subscriptions/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenantId,
          email: user.email,
          name: user.name,
          price_id: priceId,
          success_url: `${window.location.origin}/billing?success=true`,
          cancel_url: `${window.location.origin}/billing?canceled=true`
        })
      })
      return response.json()
    },
    onSuccess: (data) => {
      window.location.href = data.checkout_url
    }
  })
  
  const plans = [
    {
      id: 'price_monthly_basic',
      name: 'Basic',
      price: 29,
      period: 'month',
      features: ['10 users', '100 file uploads/day', 'Email support']
    },
    {
      id: 'price_quarterly_basic',
      name: 'Basic (Quarterly)',
      price: 78,  // 10% discount
      period: 'quarter',
      features: ['10 users', '100 file uploads/day', 'Email support', 'Quarterly billing']
    },
    {
      id: 'price_monthly_pro',
      name: 'Professional',
      price: 99,
      period: 'month',
      features: ['50 users', '1000 file uploads/day', 'Priority support', 'Advanced analytics']
    },
    {
      id: 'price_quarterly_pro',
      name: 'Professional (Quarterly)',
      price: 267,  // 10% discount
      period: 'quarter',
      features: ['50 users', '1000 file uploads/day', 'Priority support', 'Advanced analytics', 'Quarterly billing']
    }
  ]
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Billing & Subscription</h1>
        <p className="text-muted-foreground">
          Manage your subscription and billing information
        </p>
      </div>
      
      {/* 当前订阅状态 */}
      <Card>
        <CardHeader>
          <CardTitle>Current Subscription</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div>Loading...</div>
          ) : subscription ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{subscription.plan}</p>
                  <p className="text-sm text-muted-foreground">
                    {subscription.status} • {formatCurrency(subscription.amount)}/{subscription.billing_cycle}
                  </p>
                </div>
                <Badge variant={subscription.status === 'active' ? 'default' : 'secondary'}>
                  {subscription.status}
                </Badge>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Current Period</p>
                  <p>{new Date(subscription.current_period_start).toLocaleDateString()} - {new Date(subscription.current_period_end).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Auto-renewal</p>
                  <p>{subscription.cancel_at_period_end ? 'Disabled' : 'Enabled'}</p>
                </div>
              </div>
              
              {subscription.status === 'past_due' && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800">
                    Your payment has failed. Please update your payment method to avoid service interruption.
                  </p>
                  <Button 
                    variant="destructive" 
                    className="mt-2"
                    onClick={() => window.location.href = '/billing/update-payment'}
                  >
                    Update Payment Method
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <p>No active subscription. Choose a plan below to get started.</p>
          )}
        </CardContent>
      </Card>
      
      {/* 升级/更改计划 */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {plans.map((plan) => (
            <Card key={plan.id} className={subscription?.plan === plan.name ? 'border-primary' : ''}>
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <CardDescription>
                  <span className="text-3xl font-bold">{formatCurrency(plan.price)}</span>
                  <span className="text-muted-foreground">/{plan.period}</span>
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 mb-4">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center">
                      <CheckIcon className="mr-2 h-4 w-4 text-green-500" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Button 
                  className="w-full"
                  onClick={() => checkoutMutation.mutate(plan.id)}
                  disabled={subscription?.plan === plan.name}
                >
                  {subscription?.plan === plan.name ? 'Current Plan' : 'Subscribe'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      
      {/* 发票历史 */}
      <Card>
        <CardHeader>
          <CardTitle>Invoice History</CardTitle>
        </CardHeader>
        <CardContent>
          {/* 发票列表 */}
        </CardContent>
      </Card>
    </div>
  )
}
```text
#### 19.5.2 订阅状态徽章组件

```tsx
// frontend/components/subscription-status-badge.tsx
import { Badge } from '@/components/ui/badge'

export function SubscriptionStatusBadge({ status }: { status: string }) {
  const variants = {
    active: 'default',
    trialing: 'secondary',
    past_due: 'destructive',
    canceled: 'outline',
    unpaid: 'destructive',
    incomplete: 'warning'
  }
  
  const labels = {
    active: 'Active',
    trialing: 'Trial',
    past_due: 'Past Due',
    canceled: 'Canceled',
    unpaid: 'Unpaid',
    incomplete: 'Incomplete'
  }
  
  return (
    <Badge variant={variants[status as keyof typeof variants] || 'outline'}>
      {labels[status as keyof typeof labels] || status}
    </Badge>
  )
}
```text
### 19.6 订阅验证和限制

#### 19.6.1 资源配额检查

在部署引擎中检查租户订阅配额：

```python
# app/services/quota_service.py
from sqlalchemy.orm import Session
from app.models.tenant import Tenant

class QuotaService:
    """配额服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_deployment_quota(self, tenant_id: str) -> Dict[str, Any]:
        """检查部署配额"""
        tenant = self.db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if not tenant:
            return {"allowed": False, "reason": "Tenant not found"}
        
        # 检查订阅状态
        if tenant.subscription_status not in ["active", "trialing"]:
            return {
                "allowed": False, 
                "reason": "subscription_required",
                "message": "Active subscription required to deploy"
            }
        
        # 检查当前部署数量
        current_deployments = self._count_active_deployments(tenant_id)
        max_deployments = self._get_max_deployments(tenant.subscription_plan)
        
        if current_deployments >= max_deployments:
            return {
                "allowed": False,
                "reason": "deployment_limit_reached",
                "message": f"Maximum {max_deployments} deployments allowed for {tenant.subscription_plan} plan",
                "current": current_deployments,
                "limit": max_deployments
            }
        
        return {
            "allowed": True,
            "current": current_deployments,
            "limit": max_deployments
        }
    
    def _count_active_deployments(self, tenant_id: str) -> int:
        """统计活跃部署数量"""
        from app.models.deployment import Deployment
        return self.db.query(Deployment).filter(
            Deployment.tenant_id == tenant_id,
            Deployment.status == "active"
        ).count()
    
    def _get_max_deployments(self, plan: str) -> int:
        """根据套餐获取最大部署数量"""
        limits = {
            "basic": 3,
            "professional": 10,
            "enterprise": 50
        }
        return limits.get(plan, 1)
```text
#### 19.6.2 中间件集成

```python
# app/api/deployments.py
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import SubscriptionRequired
from app.services.quota_service import QuotaService

router = APIRouter(prefix="/deployments", tags=["deployments"])

@router.post("/")
async def create_deployment(
    request: DeploymentRequest,
    tenant: Tenant = Depends(SubscriptionRequired(require_active=True)),
    db: Session = Depends(get_db)
):
    """创建新部署"""
    # 检查配额
    quota_service = QuotaService(db)
    quota_check = quota_service.check_deployment_quota(tenant.tenant_id)
    
    if not quota_check["allowed"]:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "quota_exceeded",
                "message": quota_check["message"],
                "current": quota_check.get("current"),
                "limit": quota_check.get("limit")
            }
        )
    
    # 执行部署逻辑
    ...
```text
### 19.7 自动化续费和通知

#### 19.7.1 续费提醒

使用Celery定时任务检查即将到期的订阅：

```python
# app/tasks/subscription_tasks.py
from celery import Celery
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.services.email_service import EmailService

celery_app = Celery('subscription_tasks', broker='redis://localhost:6379/1')

@celery_app.task
def check_expiring_subscriptions():
    """检查即将到期的订阅"""
    db = SessionLocal()
    
    try:
        # 查找7天内到期的活跃订阅
        cutoff_date = datetime.now() + timedelta(days=7)
        tenants = db.query(Tenant).filter(
            Tenant.subscription_status == "active",
            Tenant.subscription_end_date <= cutoff_date,
            Tenant.subscription_end_date >= datetime.now()
        ).all()
        
        email_service = EmailService()
        
        for tenant in tenants:
            days_left = (tenant.subscription_end_date - datetime.now()).days
            
            # 发送续费提醒
            email_service.send_subscription_renewal_reminder(
                tenant=tenant,
                days_left=days_left,
                renewal_url=f"https://admin.yourdomain.com/billing/renew?tenant_id={tenant.tenant_id}"
            )
            
    finally:
        db.close()

# 配置Celery Beat定时任务
# 每天运行一次
celery_app.conf.beat_schedule = {
    'check-expiring-subscriptions': {
        'task': 'app.tasks.subscription_tasks.check_expiring_subscriptions',
        'schedule': 86400.0,  # 24 hours
    },
}
```text
#### 19.7.2 支付失败处理

```python
# app/tasks/payment_tasks.py
@celery_app.task
def handle_payment_failure(tenant_id: str, invoice_id: str):
    """处理支付失败"""
    db = SessionLocal()
    
    try:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if tenant:
            # 更新订阅状态
            tenant.subscription_status = "past_due"
            db.commit()
            
            # 发送通知
            email_service = EmailService()
            email_service.send_payment_failed_notification(
                tenant=tenant,
                invoice_id=invoice_id,
                update_url=f"https://admin.yourdomain.com/billing/update-payment?tenant_id={tenant_id}"
            )
            
            # 记录审计日志
            audit_log = AuditLog(
                user_id="system",
                tenant_id=tenant_id,
                action="payment_failed",
                resource_type="invoice",
                resource_id=invoice_id
            )
            db.add(audit_log)
            db.commit()
            
    finally:
        db.close()
```text
### 19.8 前端订阅集成

#### 19.8.1 订阅状态检查Hook

```tsx
// frontend/hooks/use-subscription.ts
import { useQuery } from '@tanstack/react-query'

export function useSubscription(tenantId: string) {
  return useQuery({
    queryKey: ['subscription', tenantId],
    queryFn: async () => {
      const response = await fetch(`/api/v1/subscriptions/${tenantId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch subscription')
      }
      return response.json()
    },
    staleTime: 60000, // 1 minute
  })
}

export function useSubscriptionRequirement() {
  const { tenantId } = useTenant()
  const { data: subscription, isLoading } = useSubscription(tenantId)
  
  const isActive = subscription?.status === 'active' || subscription?.status === 'trialing'
  const isExpired = subscription?.current_period_end && new Date(subscription.current_period_end) < new Date()
  
  return {
    subscription,
    isLoading,
    isActive,
    isExpired,
    requiresUpgrade: !isActive || isExpired
  }
}
```text
#### 19.8.2 受保护路由

```tsx
// frontend/components/subscription-gated.tsx
'use client'

import { useSubscriptionRequirement } from '@/hooks/use-subscription'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'

export function SubscriptionGated({ children, feature }: { children: React.ReactNode, feature: string }) {
  const { isActive, isExpired, isLoading } = useSubscriptionRequirement()
  const router = useRouter()
  
  if (isLoading) {
    return <div>Loading...</div>
  }
  
  if (!isActive || isExpired) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
        <h2 className="text-2xl font-bold mb-4">Subscription Required</h2>
        <p className="text-muted-foreground mb-6">
          An active subscription is required to access {feature}.
          {isExpired && " Your subscription has expired."}
        </p>
        <Button onClick={() => router.push('/billing')}>
          {isExpired ? 'Renew Subscription' : 'Upgrade Now'}
        </Button>
      </div>
    )
  }
  
  return children
}
```text
### 19.9 测试订阅流程

#### 19.9.1 Stripe测试模式

1. **启用测试模式**
   - 在Stripe Dashboard切换到测试模式
   - 使用测试API密钥

2. **测试卡号**
   - 成功支付: `4242 4242 4242 4242`
   - 支付失败: `4000 0000 0000 0002`
   - 需要3D Secure: `4000 0025 0000 3155`

3. **自动化测试**

```python
# tests/test_subscriptions.py
import pytest
from app.services.stripe_service import StripeService

@pytest.fixture
def stripe_service(db_session):
    return StripeService(db_session)

def test_create_subscription(stripe_service):
    """测试创建订阅"""
    # 创建测试客户
    customer = stripe_service.create_customer(
        tenant_id="test-tenant",
        email="test@example.com",
        name="Test User"
    )
    
    assert customer.id is not None
    assert customer.email == "test@example.com"
    
    # 创建订阅
    subscription = stripe_service.create_subscription(
        customer_id=customer.id,
        price_id="price_test_xxx",
        trial_days=7
    )
    
    assert subscription.status == "trialing"
    assert subscription.trial_end is not None
```text
### 19.10 监控和报表

#### 19.10.1 订阅指标

在管理控制台仪表盘添加订阅指标：

```python
# app/services/analytics_service.py
class AnalyticsService:
    """分析服务"""
    
    def get_subscription_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """获取订阅指标"""
        db = SessionLocal()
        
        try:
            # 总租户数
            total_tenants = db.query(Tenant).count()
            
            # 活跃订阅数
            active_subscriptions = db.query(Tenant).filter(
                Tenant.subscription_status == "active",
                Tenant.subscription_end_date >= datetime.now()
            ).count()
            
            # 试用租户数
            trial_tenants = db.query(Tenant).filter(
                Tenant.subscription_status == "trialing"
            ).count()
            
            # 过期租户数
            expired_tenants = db.query(Tenant).filter(
                Tenant.subscription_status == "past_due"
            ).count()
            
            # MRR (Monthly Recurring Revenue)
            mrr = self._calculate_mrr(db)
            
            # 按套餐统计
            plan_distribution = self._get_plan_distribution(db)
            
            return {
                "total_tenants": total_tenants,
                "active_subscriptions": active_subscriptions,
                "trial_tenants": trial_tenants,
                "expired_tenants": expired_tenants,
                "mrr": mrr,
                "plan_distribution": plan_distribution,
                "conversion_rate": active_subscriptions / total_tenants if total_tenants > 0 else 0
            }
            
        finally:
            db.close()
```text
#### 19.10.2 订阅报表

```sql
-- 月度收入报表
SELECT 
    DATE_TRUNC('month', current_period_start) as month,
    COUNT(*) as subscriber_count,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
    AVG(EXTRACT(DAY FROM (current_period_end - current_period_start))) as avg_cycle_days
FROM subscriptions
GROUP BY DATE_TRUNC('month', current_period_start)
ORDER BY month DESC;

-- 套餐分布
SELECT 
    t.subscription_plan,
    COUNT(*) as count,
    SUM(CASE WHEN s.status = 'active' THEN 1 ELSE 0 END) as active_count
FROM tenants t
LEFT JOIN subscriptions s ON t.tenant_id = s.tenant_id
GROUP BY t.subscription_plan
ORDER BY count DESC;
```text
### 19.11 最佳实践

1. **安全**
   - 永远不要在前端暴露Stripe Secret Key
   - 验证Webhook签名
   - 使用环境变量存储敏感信息
   - 定期轮换API密钥

2. **可靠性**
   - 实现幂等的Webhook处理
   - 设置重试机制
   - 记录所有订阅事件
   - 定期对账（Stripe vs 数据库）

3. **用户体验**
   - 提供清晰的订阅状态提示
   - 在订阅到期前发送提醒
   - 支持自助升级/降级
   - 提供优雅的降级体验（试用期结束后限制功能而非立即停用）

4. **合规性**
   - 明确显示价格和计费周期
   - 提供取消订阅的简单方式
   - 遵守Stripe的使用条款
   - 保留完整的账单历史

---

## 二十、计费方案设计

基于业务需求，设计阶梯式计费方案，不支持按量付费，不够只能升级套餐。

### 20.1 计费核心原则

1. **用户数 = 通道数**：每个用户对应一个通道，一一对应关系
2. **阶梯式套餐**：固定数量，不支持按量付费
3. **不够只能升级**：达到上限后必须升级到更高套餐
4. **不限制消息数量**：包含在套餐中
5. **存储空间**：按实际使用收费（超出部分）

### 20.2 套餐设计（季度订阅）

| 套餐 | 基础价格（季度） | 用户/通道数量 | 存储包含 | 云资源规格 | 适用场景 |
|------|----------------|-------------|---------|-----------|---------|
| **Basic** | ¥2,999 | 10个 | 50GB | 共享规格 | 小型团队、试用 |
| **Business** | ¥12,999 | 50个 | 200GB | 独享规格 | 中型企业、正式使用 |
| **Enterprise** | ¥48000 | 200个 | 1TB | 集群+CDN | 大型企业、高可用 |

### 20.3 套餐详情

#### Basic套餐（¥2,999/季度）

**包含资源**：
- 用户/通道数量：10个
- 存储空间：50GB
- 消息数量：不限制
- 云资源规格：
  - RDS PostgreSQL：共享规格（2核1GB）
  - Redis：共享规格（1GB）
  - OSS：标准存储（50GB）

**适用场景**：
- 小型团队（1-10人）
- 试用期项目
- 低并发场景

**升级条件**：
- 用户数达到10个时，必须升级到Business套餐

#### Business套餐（¥12,999/季度）

**包含资源**：
- 用户/通道数量：50个
- 存储空间：200GB
- 消息数量：不限制
- 云资源规格：
  - RDS PostgreSQL：独享规格（4核8GB）
  - Redis：独享规格（4GB）
  - OSS：标准存储（200GB）

**适用场景**：
- 中型企业（11-50人）
- 正式使用项目
- 中等并发场景

**升级条件**：
- 用户数达到50个时，必须升级到Enterprise套餐

#### Enterprise套餐（¥48000/季度）

**包含资源**：
- 用户/通道数量：200个
- 存储空间：1TB
- 消息数量：不限制
- 云资源规格：
  - RDS PostgreSQL：集群版（主从复制，8核16GB）
  - Redis：集群版（哨兵模式，8GB）
  - OSS：标准存储（1TB）+ CDN加速

**适用场景**：
- 大型企业（51-200人）
- 高可用要求项目
- 高并发场景

**升级条件**：
- 用户数达到200个时，需要联系销售定制方案

### 20.4 存储费用

**超出存储收费**：
- 超出套餐包含的存储空间后，按 ¥0.12/GB/月 收费
- 按实际使用量计费，每月结算

**存储升级**：
- 可以单独升级存储空间，不影响套餐
- 升级后按新存储规格收费

### 20.5 升级规则

```python
class SubscriptionManager:
    """订阅管理器"""
    
    def check_upgrade_needed(self, tenant_id: str) -> Dict:
        """检查是否需要升级"""
        tenant = self.tenant_repo.find_by_id(tenant_id)
        subscription = tenant.subscription
        
        # 获取当前套餐限制
        plan_limits = self.get_plan_limits(subscription.plan)
        max_users = plan_limits['max_users']
        
        # 获取当前使用量
        current_users = self.get_active_user_count(tenant_id)
        
        # 检查是否达到上限
        if current_users >= max_users:
            return {
                "need_upgrade": True,
                "current_plan": subscription.plan,
                "current_users": current_users,
                "max_users": max_users,
                "recommended_plan": self.get_next_plan(subscription.plan),
                "message": f"当前用户数({current_users})已达到套餐上限({max_users})，请升级套餐"
            }
        else:
            return {
                "need_upgrade": False,
                "current_plan": subscription.plan,
                "current_users": current_users,
                "max_users": max_users,
                "remaining": max_users - current_users
            }
    
    def get_next_plan(self, current_plan: str) -> str:
        """获取下一个套餐"""
        plans = ["basic", "business", "enterprise"]
        current_index = plans.index(current_plan)
        if current_index < len(plans) - 1:
            return plans[current_index + 1]
        else:
            return None  # 已经是最高套餐
```

### 20.6 升级流程

1. **监控使用量**：系统实时监控用户/通道数量
2. **达到上限提醒**：当用户数达到套餐上限的80%时，发送提醒
3. **达到上限限制**：当用户数达到套餐上限时，禁止新增用户/通道
4. **升级套餐**：用户在管理控制台选择升级套餐
5. **自动扩容**：升级后自动调整云资源规格

### 20.7 计费计算示例

```python
class BillingCalculator:
    """计费计算器"""
    
    def calculate_quarterly_fee(self, tenant_id: str) -> Dict:
        """计算季度费用"""
        tenant = self.tenant_repo.find_by_id(tenant_id)
        subscription = tenant.subscription
        
        # 基础套餐费用
        plan_fee = self.get_plan_fee(subscription.plan)
        
        # 检查是否需要升级
        upgrade_check = self.subscription_manager.check_upgrade_needed(tenant_id)
        
        # 存储费用（按实际使用）
        storage_usage = self.get_storage_usage(tenant_id)
        included_storage = self.get_plan_storage(subscription.plan)
        
        if storage_usage > included_storage:
            extra_storage = storage_usage - included_storage
            storage_fee = extra_storage * 0.12  # ¥0.12/GB/月
        else:
            storage_fee = 0
        
        total_fee = plan_fee + storage_fee
        
        return {
            "plan_fee": plan_fee,
            "storage_fee": storage_fee,
            "total_fee": total_fee,
            "currency": "CNY",
            "upgrade_check": upgrade_check
        }
```

### 20.8 推荐配置策略

#### 场景1：小型团队（1-10个用户/通道）

**推荐套餐**：Basic

**配置**：

- 10个用户/通道
- 50GB存储
- 共享云资源（RDS共享规格、Redis共享规格）

**优势**：成本低，部署快，满足基本需求

#### 场景2：中型企业（11-50个用户/通道）

**推荐套餐**：Business

**配置**：

- 50个用户/通道
- 200GB存储
- 独享云资源（RDS独享规格、Redis独享规格）

**优势**：性能稳定，扩展性好，性价比高

#### 场景3：大型企业（51-200个用户/通道）

**推荐套餐**：Enterprise

**配置**：

- 200个用户/通道
- 1TB存储
- 集群+CDN（RDS集群、Redis集群、CDN加速）

**优势**：最高性能，完全隔离，专属支持

### 20.9 多用户隔离确认

**重要确认**：上述所有套餐方案**完全不影响**初始设计的多用户隔离DeerFlow架构。

**隔离机制保持不变**：

1. **数据库隔离**：每个租户独立数据库（不同数据库名或Schema）
2. **Redis隔离**：每个租户独立Redis实例或DB索引
3. **文件存储隔离**：每个租户独立OSS Bucket或目录
4. **容器隔离**：每个租户独立DeerFlow实例（Docker容器/K8s Pod）

**套餐差异仅体现在资源规格**：

- **Basic**：共享规格（多个租户共享云资源，但数据完全隔离）
- **Business**：独享规格（每个租户独占云资源，数据完全隔离）
- **Enterprise**：集群规格（高可用架构，数据完全隔离）

**所有套餐都保证**：

- ✅ 数据完全隔离（不会互相访问）
- ✅ 安全性相同（都使用独立数据库、独立存储）
- ✅ 功能相同（都支持完整的DeerFlow功能）
- ✅ 隔离级别相同（都是租户级隔离）

### 20.10 成本透明度

**用户可以看到**：

- 当前套餐和限制
- 已使用量和剩余量
- 存储使用情况
- 升级提醒和建议

**管理控制台提供**：

- 实时使用量仪表盘
- 费用预估和账单
- 升级路径建议
- 历史使用趋势

---

## 版本历史

| 版本 | 日期 | 说明 |
| :--- | :--- | :--- |
| v1.0 | 2026-03-30 | 初始版本，基于DeerFlow main分支 |







