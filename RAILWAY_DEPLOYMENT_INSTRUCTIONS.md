# 🚀 Railway 部署完整指南

## 第一步：GitHub 推送（手动）

由于网络原因，请按以下步骤手动推送：

### 选项 A：通过 GitHub Desktop（推荐）
1. 打开 GitHub Desktop
2. 打开本地仓库 `d:\MultiMode\deerflow\deer-flow`
3. 点击 "Current Branch" → "main"
4. 查看待推送的更改（左侧面板）
5. 输入提交信息：`feat: Deploy to Railway with Alipay subscription system`
6. 点击 "Commit to main"
7. 点击 "Push origin"

### 选项 B：通过 SSH（如果 HTTPS 持续失败）
```powershell
# 在 PowerShell 中运行
cd d:\MultiMode\deerflow\deer-flow

# 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your-email@example.com"

# 添加 SSH 密钥到 SSH Agent
ssh-add $HOME\.ssh\id_ed25519

# 更新远程仓库为 SSH
git remote set-url origin git@github.com:zyj18860969891-byte/cloud-deerflow.git

# 尝试推送
git push -u origin main
```

## 第二步：Railway 部署

### 2.1 通过 Railway 网页创建项目

1. **访问 Railway.app**
   - 地址：https://railway.app
   - 点击 "Create New Project"

2. **选择部署方式**
   - 选择："Deploy from GitHub repo"
   - 授予 Railway 访问 GitHub 的权限

3. **选择你的仓库**
   - 搜索：`cloud-deerflow`
   - 选择：`zyj18860969891-byte/cloud-deerflow`
   - 分支：`main`

4. **等待自动部署**
   - Railway 会自动：
     - 克隆代码
     - 构建 Docker 镜像
     - 启动服务
   - 预计时间：5-15 分钟

### 2.2 配置环境变量（CRITICAL）

部署完成后，进入 Railway Dashboard：

#### 必须配置的变量：

```
# FastAPI 和 Gateway
DEBUG=false
ENVIRONMENT=production
PORT=8001
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/deerflow
REDIS_URL=redis://[host]:[port]

# 支付宝（Alipay）- 你的凭证
ALIPAY_APPID=2021006138604101
ALIPAY_PRIVATE_KEY=[your-private-key]
ALIPAY_PUBLIC_KEY=[alipay-public-key]
ALIPAY_NOTIFY_URL=[从下方获取]

# Better Auth
BETTER_AUTH_SECRET=[生成新的随机 32 字符]

# LangGraph
LANGGRAPH_URL=http://langgraph:2024
LANGGRAPH_API_KEY=[your-api-key]

# OpenRouter（如果使用）
OPENROUTER_API_KEY=[your-api-key]

# 多租户配置
TENANT_MODE=true
DEFAULT_TENANT_ID=default
```

#### 自动生成的变量（来自 Railway）：
```
RAILWAY_PUBLIC_DOMAIN=https://[your-project].railway.app
```

### 2.3 获取 ALIPAY_NOTIFY_URL

部署完成后：

1. 进入 Railway Dashboard
2. 找到你的项目
3. 点击 "Deployments" 标签页
4. 查找 "Networking" 部分
5. 复制 "Public Domain"

**ALIPAY_NOTIFY_URL 格式：**
```
https://[your-railway-domain]/api/subscription/webhook-alipay
```

例如：
```
https://cloud-deerflow-production.railway.app/api/subscription/webhook-alipay
```

## 第三步：配置支付宝通知

1. **登录支付宝开放平台**
   - 地址：https://open.alipay.com

2. **进入应用设置**
   - 找到你的应用：DeerFlow 订阅系统
   - 点击 "应用信息"
   - 找到 "异步通知 URL"

3. **配置 Webhook URL**
   - 粘贴：`https://[your-railway-domain]/api/subscription/webhook-alipay`
   - 保存设置

4. **验证配置**
   - 支付宝会发送测试通知
   - 查看 Railway 日志确认收到

## 第四步：验证部署

### 4.1 检查服务健康状态

```powershell
# 获取 Railway 域名
$DOMAIN = "https://cloud-deerflow-production.railway.app"

# 检查健康状态
Invoke-WebRequest -Uri "$DOMAIN/health" -SkipHttpsValidation

# 预期响应：200 OK 和 {"status": "healthy"}
```

### 4.2 测试 API 端点

```powershell
# 列出订阅计划
Invoke-WebRequest -Uri "$DOMAIN/api/subscription/plans" -SkipHttpsValidation

# 获取用户信息
Invoke-WebRequest -Uri "$DOMAIN/api/user" -SkipHttpsValidation
```

### 4.3 查看日志

```bash
# 在 Railway 网页中：
# Dashboard → Deployments → Logs

# 或通过 CLI（如果能连接）：
railway logs --follow
```

## 第五步：测试支付流程

### 测试支付宝支付

1. **进入订阅页面**
   - URL：`https://[your-railway-domain]/subscription`

2. **选择计划**
   - 选择任一订阅计划（如 Professional）

3. **开始支付**
   - 点击 "立即订阅" / "Pay Now"
   - 应跳转到支付宝支付页面

4. **完成支付**
   - 在支付宝沙箱中完成支付
   - 返回应用

5. **验证订阅**
   - 在用户仪表板检查订阅状态
   - 检查发票记录

### 查看支付宝通知日志

在 Railway Dashboard 的日志中，应能看到：
```
[Subscription] Alipay webhook received
[Subscription] Processing order [order_id]
[Subscription] Subscription activated for user [user_id]
```

## 常见问题排查

### 问题 1：部署失败 - Docker 构建错误

**症状：** Railway 显示 "Build failed"

**解决方案：**
1. 进入 Railway Dashboard
2. 点击 "Logs"
3. 查看具体错误信息
4. 常见原因：
   - Python 依赖缺失：检查 `backend/pyproject.toml`
   - 环境变量缺失：配置所有必需变量
   - 数据库未初始化：等待自动迁移完成

### 问题 2：服务无法启动

**症状：** Railway 显示 "Application crashed"

**解决方案：**
1. 查看 Railway 日志
2. 检查环境变量是否完整
3. 检查数据库连接：`DATABASE_URL` 格式正确
4. 检查 `startCommand` 是否正确

### 问题 3：Alipay 通知未送达

**症状：** 支付完成但订阅未激活

**解决方案：**
1. 验证 `ALIPAY_NOTIFY_URL` 配置正确
2. 在支付宝平台重新配置通知 URL
3. 检查 Railway 日志中的 webhook 端点
4. 验证 RSA 密钥配置正确

### 问题 4：无法连接到 LangGraph

**症状：** 错误 "Failed to connect to langgraph service"

**解决方案：**
1. Railway 支持通过 Docker Compose 部署多个服务
2. 在 Railway 中创建两个项目：
   - 项目 1：backend (gateway + langgraph)
   - 项目 2：frontend
3. 配置内部网络通信

## 高级配置

### 使用 Railway 的数据库服务

Railway 提供托管的 PostgreSQL 和 Redis：

1. **创建 PostgreSQL 数据库**
   ```
   Dashboard → Add Service → Databases → PostgreSQL
   ```

2. **获取连接字符串**
   ```
   $DATABASE_URL 自动注入为环境变量
   ```

3. **运行数据库迁移**
   ```
   railway run python -m alembic upgrade head
   ```

### 配置 CI/CD 自动部署

Railway 自动支持 GitHub CI/CD：

1. 每次推送到 `main` 分支时自动部署
2. 自动运行数据库迁移
3. 自动健康检查

### 监控和告警

在 Railway Dashboard 配置：

1. **指标监控**
   - CPU 使用率
   - 内存使用率
   - 请求延迟
   - 错误率

2. **告警规则**
   - CPU > 80% 发送通知
   - 内存 > 90% 发送通知
   - 错误率 > 5% 发送通知

## 完整部署时间表

| 步骤 | 预计时间 | 说明 |
|-----|--------|------|
| GitHub 推送 | 2-5 分钟 | 手动推送或 SSH |
| Railway 初始构建 | 5-10 分钟 | 首次构建时间较长 |
| 环境变量配置 | 3-5 分钟 | 配置关键参数 |
| 数据库初始化 | 2-3 分钟 | 运行迁移脚本 |
| Alipay 配置 | 2-3 分钟 | 配置通知 URL |
| 部署验证 | 5 分钟 | API 测试和健康检查 |
| 支付流程测试 | 5-10 分钟 | 完整支付测试 |
| **总计** | **25-40 分钟** | 从推送到完全就绪 |

## 下一步行动

1. ✅ 通过 GitHub Desktop 或 SSH 推送代码
2. ⏳ 等待 GitHub 推送成功
3. 📝 进入 Railway.app 创建新项目
4. 🔗 连接 GitHub 仓库
5. ⚙️ 配置所有环境变量
6. 📍 获取公共域名和 NOTIFY_URL
7. 🔔 在支付宝平台配置通知
8. ✔️ 运行测试命令验证部署
9. 💳 测试完整支付流程

**祝部署顺利！🎉**

---

需要帮助？查看这些资源：
- Railway 文档：https://docs.railway.app
- 支付宝文档：https://open.alipay.com
- DeerFlow 仓库：https://github.com/zyj18860969891-byte/cloud-deerflow
