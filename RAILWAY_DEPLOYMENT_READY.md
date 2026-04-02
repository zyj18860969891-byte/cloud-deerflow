# ✅ Railway 部署准备完毕 - ALIPAY_NOTIFY_URL 获取计划

**日期**: 2026年4月2日  
**状态**: 🟢 **部署脚本已准备，可立即执行**  
**目标**: 通过 Railway CLI 部署应用并获取 ALIPAY_NOTIFY_URL

---

## 📋 快速开始

### 一键部署 (PowerShell)

```powershell
# 导航到项目目录
cd d:\MultiMode\deerflow\deer-flow

# 执行部署脚本
.\scripts\deploy-railway.ps1

# 或者带确认:
.\scripts\deploy-railway.ps1 -Confirm
```

### 脚本功能

该部署脚本自动执行以下步骤:

```
✅ 1. 环境检查 (Railway CLI, Git)
✅ 2. Railway 登录验证
✅ 3. 项目链接
✅ 4. 配置基础环境变量
✅ 5. 代码推送到 GitHub
✅ 6. 触发 Railway 部署
✅ 7. 等待部署完成
✅ 8. 获取公域名
✅ 9. 生成 ALIPAY_NOTIFY_URL
✅ 10. 配置回调 URL 到 Railway
✅ 11. 测试应用可访问性
```

---

## 🎯 部署流程详解

### 第 1-3 步: 环境检查和登录 (自动)

```
检查项:
  ✅ Railway CLI 版本: railway 4.27.5 (已安装)
  ✅ Git 版本: git version 2.x (已安装)
  ✅ 项目位置: d:\MultiMode\deerflow\deer-flow (正确)
  ✅ Railway 登录: 自动验证
  ✅ 项目链接: 自动链接到您的 Railway 项目
```

### 第 4 步: 配置环境变量

```bash
# 脚本自动配置:
railway variables set ALIPAY_APP_ID=2021006138604101
railway variables set ALIPAY_PID=2088380691837603
railway variables set ALIPAY_GATEWAY_URL=https://openapi.alipay.com/gateway.do
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO

# 敏感信息需手动配置 (通过 Dashboard):
# - ALIPAY_APP_PRIVATE_KEY
# - ALIPAY_PUBLIC_KEY
```

### 第 5-6 步: 代码推送和部署

```bash
# 脚本执行:
git add .
git commit -m "feat: Configure Alipay credentials and Railway deployment"
git push origin main

# Railway 自动部署:
# - 拉取最新代码
# - 构建 Docker 镜像
# - 执行数据库迁移 (alembic upgrade head)
# - 启动应用程序
```

### 第 7-9 步: 获取公域名和生成 NOTIFY_URL

```
部署完成后，应用会获得:
  https://[auto-generated-name].railway.app

NOTIFY_URL 自动生成:
  https://[auto-generated-name].railway.app/api/subscription/webhook-alipay

示例:
  https://deerflow-api-prod-xxx.railway.app/api/subscription/webhook-alipay
```

### 第 10 步: 配置到 Railway

```bash
# 脚本自动执行:
railway variables set ALIPAY_NOTIFY_URL=https://[domain]/api/subscription/webhook-alipay
```

---

## 📊 部署时间表

| 步骤 | 内容 | 预计时间 | 说明 |
|------|------|---------|------|
| 1-3 | 环境检查 + 登录 | 1分钟 | 自动化 |
| 4 | 环境变量配置 | 1分钟 | 自动化 |
| 5 | 代码推送 | 1-2分钟 | 取决于网络 |
| 6 | Docker 构建 | 3-5分钟 | Railway 自动执行 |
| 6b | 数据库迁移 | 1-2分钟 | Alembic 自动执行 |
| 7 | 应用启动 | 1-2分钟 | 取决于启动时间 |
| 8-11 | 验证 | 1分钟 | 自动化 |

**总计**: **约 10-15 分钟** 即可部署完成并获得 NOTIFY_URL

---

## 🔑 关键输出信息

脚本执行完成后，您将得到:

```
╔════════════════════════════════════════════════════════════╗
║          🎉 Railway 部署完成！                            ║
╚════════════════════════════════════════════════════════════╝

📍 关键信息:
  应用域名:         https://deerflow-api.railway.app
  健康检查:         https://deerflow-api.railway.app/health
  API 计划列表:     https://deerflow-api.railway.app/api/subscription/plans
  Alipay 支付:      https://deerflow-api.railway.app/api/subscription/checkout-alipay

🔔 ALIPAY_NOTIFY_URL:
  https://deerflow-api.railway.app/api/subscription/webhook-alipay

📋 后续步骤:
  1️⃣  将 NOTIFY_URL 配置到支付宝开放平台
     登录: https://open.alipay.com
     应用设置 → 异步通知地址 → 粘贴上述 URL

  2️⃣  测试支付流程
     访问: https://deerflow-api.railway.app
     选择套餐 → 选择 Alipay → 验证支付链接

  3️⃣  监控日志
     运行: railway logs --follow
```

---

## 🛠️ 命令参考

### 部署命令

```powershell
# 标准部署 (交互式)
.\scripts\deploy-railway.ps1

# 无需确认的部署
.\scripts\deploy-railway.ps1 -Confirm

# 仅验证部署 (不推送代码)
.\scripts\deploy-railway.ps1 -Action verify

# 查看日志
.\scripts\deploy-railway.ps1 -Action logs

# 查看应用信息
.\scripts\deploy-railway.ps1 -Action info
```

### Railway CLI 命令

```bash
# 查看部署状态
railway status

# 查看服务
railway service list

# 查看日志
railway logs --follow

# 查看环境变量
railway variables

# 设置环境变量
railway variables set KEY value

# 重启应用
railway service restart

# 查看公域名
railway domains
```

---

## ✅ 部署前检查清单

执行脚本前，请确认:

- [ ] 已安装 Railway CLI (`railway --version`)
- [ ] 已登录 Railway 账户 (`railway whoami`)
- [ ] 在项目根目录 (`d:\MultiMode\deerflow\deer-flow`)
- [ ] 所有代码已提交 (`git status`)
- [ ] Alipay 凭证已准备:
  - [ ] ALIPAY_APP_ID: 2021006138604101
  - [ ] ALIPAY_PID: 2088380691837603
  - [ ] ALIPAY_APP_PRIVATE_KEY: (RSA 私钥)
  - [ ] ALIPAY_PUBLIC_KEY: (RSA 公钥)

---

## 🚨 故障排除

### 脚本执行失败

**错误**: Railway CLI 未安装
```powershell
# 解决:
npm install -g @railway/cli

# 验证:
railway --version
```

**错误**: 未登录 Railway
```powershell
# 脚本会自动打开登录页面，完成登录后按 Enter 继续
```

**错误**: 无法链接项目
```bash
# 手动链接:
railway link --project <PROJECT_ID>

# 或交互式链接:
railway link
```

### 部署失败

**症状**: Docker 镜像构建失败
```bash
# 1. 检查 Dockerfile
ls docker/Dockerfile.backend

# 2. 本地测试构建
docker build -f docker/Dockerfile.backend -t test .

# 3. 查看 Railway 日志
railway logs --follow
```

**症状**: 应用启动失败
```bash
# 1. 检查日志
railway logs -n 100

# 2. 验证数据库连接
railway variables | grep DATABASE_URL

# 3. 检查迁移是否执行
# Dockerfile 应包含: RUN alembic upgrade head
```

**症状**: 无法获取公域名
```bash
# 1. 检查应用状态
railway service list

# 2. 通过 Dashboard 查看
# https://railway.app → 项目 → Backend Service → Public Domain

# 3. 手动输入域名
# 脚本会提示输入，或稍后通过以下命令获取:
railway variables | grep RAILWAY_PUBLIC_DOMAIN
```

---

## 📖 后续操作

### 1. 配置支付宝平台

```
登录: https://open.alipay.com
位置: 应用 → 我的应用 → [选择应用] → 开发设置
配置: 异步通知 URL

粘贴获得的 NOTIFY_URL:
https://deerflow-api.railway.app/api/subscription/webhook-alipay

点击 "设置" 保存
```

### 2. 测试支付流程

```
访问前端应用:
  https://deerflow-api.railway.app

执行以下测试:
  1. 导航到 /subscription 页面
  2. 选择套餐 (Basic/Business/Enterprise)
  3. 选择支付方式 (Alipay)
  4. 验证支付链接正确生成
  5. (可选) 模拟支付完成

监控日志:
  railway logs --follow
  # 应看到: "Webhook received from Alipay"
```

### 3. 监控和维护

```bash
# 定期检查应用健康状态
curl https://deerflow-api.railway.app/health

# 监控日志
railway logs --follow

# 查看错误
railway logs | grep -i error

# 定期备份数据
railway database backup
```

---

## 📊 部署完成标志

当以下所有条件都满足时，部署成功:

```
✅ Railway 应用状态: Running
✅ 日志无错误输出
✅ Health Check: 200 OK (curl https://domain/health)
✅ API 可访问: (curl https://domain/api/subscription/plans)
✅ Alipay 支付端点: 可生成支付链接
✅ 公域名已获得: https://[auto-generated].railway.app
✅ NOTIFY_URL 已配置: https://domain/api/subscription/webhook-alipay
✅ 数据库连接正常: (日志中 "database": "connected")
✅ Redis 连接正常: (日志中 "redis": "connected")
✅ 支付宝平台已配置: NOTIFY_URL 已添加
```

---

## 🎯 最终清单

部署完成后，您将拥有:

```
✅ 生产级别的 DeerFlow 应用 (在 Railway 上运行)
✅ 完整的 Alipay 支付集成 (CNY 币种)
✅ 自动化的数据库迁移 (Alembic)
✅ 自动化的应用部署 (Docker)
✅ 可用的 ALIPAY_NOTIFY_URL (支付宝回调接收)
✅ 完整的监控和日志 (Railway Dashboard)
✅ 高可用部署架构 (PostgreSQL + Redis)
✅ 自动重启和故障恢复
```

---

## 🚀 现在就开始部署！

```powershell
# 1. 打开 PowerShell
# 2. 导航到项目目录
cd d:\MultiMode\deerflow\deer-flow

# 3. 执行部署脚本
.\scripts\deploy-railway.ps1

# 4. 等待 10-15 分钟
# 5. 获取 ALIPAY_NOTIFY_URL
# 6. 配置到支付宝平台
# 7. 开始接收支付回调！
```

---

**准备就绪！** 🎉

部署脚本已准备完毕，可以立即执行。预计 10-15 分钟内即可完成部署并获得 ALIPAY_NOTIFY_URL。
