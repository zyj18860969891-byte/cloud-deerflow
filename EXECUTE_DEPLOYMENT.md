# 🚀 执行 Railway 部署 - 完整指南

**准备状态**: ✅ 所有部署文件已准备完毕  
**执行时间**: 约 10-15 分钟  
**目标**: 获取 ALIPAY_NOTIFY_URL 并完成支付宝集成

---

## 📋 执行前准备 (5 分钟)

### 第一步: 打开 PowerShell 窗口

```powershell
# 在 Windows 中打开 PowerShell 5.1+
# 快捷键: Win + R → PowerShell
```

### 第二步: 导航到项目目录

```powershell
cd d:\MultiMode\deerflow\deer-flow

# 验证位置
pwd
# 应显示: d:\MultiMode\deerflow\deer-flow
```

### 第三步: 验证 Railway CLI

```powershell
railway --version
# 应显示: railway 4.27.5 (或更新版本)

railway whoami
# 应显示: 您的 Railway 账户信息
```

如果出现 **未安装** 或 **未登录** 的错误:

```powershell
# 安装 Railway CLI (如需)
npm install -g @railway/cli

# 登录 Railway (如需)
railway login
# 会自动打开浏览器，完成登录后返回终端
```

### 第四步: 验证凭证

```powershell
# 确认以下环境变量已设置 (如果您已在本地配置)
echo $env:ALIPAY_APP_ID           # 应显示: 2021006138604101
echo $env:ALIPAY_PID              # 应显示: 2088380691837603
```

如果未显示，脚本会在 Railway 平台上自动配置。

---

## 🎬 执行部署脚本

### 步骤 1: 运行部署脚本

```powershell
.\scripts\deploy-railway.ps1

# 或使用以下选项:
# .\scripts\deploy-railway.ps1 -Confirm          # 需要确认每一步
# .\scripts\deploy-railway.ps1 -Action verify    # 仅验证，不部署
# .\scripts\deploy-railway.ps1 -Action logs      # 查看部署日志
```

### 步骤 2: 监控执行过程

脚本会依次执行以下操作，每一步都会显示进度:

```
✅ 1. 环境检查 (Railway CLI, Git)
   → 验证安装和版本
   
✅ 2. 登录验证
   → 确保 Railway 已登录
   
✅ 3. 项目链接
   → 将本地项目链接到 Railway 账户
   → 如果是首次，需要选择项目或创建新项目
   
✅ 4. 配置环境变量
   → ALIPAY_APP_ID=2021006138604101
   → ALIPAY_PID=2088380691837603
   → ALIPAY_GATEWAY_URL=https://openapi.alipay.com/gateway.do
   → ENVIRONMENT=production
   → LOG_LEVEL=INFO
   
✅ 5. 代码推送
   → git add .
   → git commit -m "feat: Configure Alipay credentials"
   → git push origin main
   
✅ 6. 触发部署
   → Railway 开始构建 Docker 镜像
   → 执行数据库迁移
   → 启动应用程序
   
✅ 7. 等待部署
   → 等待 30 秒让应用完全启动
   → 监控部署状态
   
✅ 8. 获取公域名
   → 从 Railway 获取自动分配的域名
   → 示例: https://deerflow-api-xxxx.railway.app
   
✅ 9. 生成 NOTIFY_URL
   → 自动构建回调 URL
   → 格式: https://[domain]/api/subscription/webhook-alipay
   
✅ 10. 配置回调 URL
    → 将 NOTIFY_URL 保存到 Railway 环境变量
    
✅ 11. 验证应用
    → 测试 Health Check 端点
    → 验证应用可访问
```

---

## 🔍 执行示例

### 完整执行输出示例

```
[ℹ️]  Railway CLI 部署脚本 - DeerFlow 应用
[ℹ️]  版本: 1.0
[ℹ️]  日期: 2026年4月2日

[Step] 检查环境...
[✅] Railway CLI: railway 4.27.5
[✅] Git 已安装: git version 2.46.0.windows.1

[Step] 验证 Railway 登录...
[✅] Railway 登录成功: your-account@email.com

[Step] 链接 Railway 项目...
[ℹ️]  正在链接项目...
[✅] 项目已链接: deerflow (project-id: xxx)

[Step] 配置环境变量...
[✅] ALIPAY_APP_ID set to: 2021006138604101
[✅] ALIPAY_PID set to: 2088380691837603
[✅] ALIPAY_GATEWAY_URL set to: https://openapi.alipay.com/gateway.do
[✅] ENVIRONMENT set to: production
[✅] LOG_LEVEL set to: INFO

[Step] 代码推送到 GitHub...
[✅] 代码已提交并推送

[Step] 触发 Railway 部署...
[✅] 部署已触发
[ℹ️]  等待应用启动... (最多 30 秒)

[Step] 获取公域名...
[✅] 公域名: https://deerflow-api.railway.app

[Step] 生成 ALIPAY_NOTIFY_URL...
[✅] NOTIFY_URL: https://deerflow-api.railway.app/api/subscription/webhook-alipay

[Step] 配置回调 URL...
[✅] ALIPAY_NOTIFY_URL 已配置到 Railway

[Step] 验证应用...
[✅] Health Check 通过 (200 OK)

╔════════════════════════════════════════════════════════════╗
║          🎉 部署成功！                                     ║
╚════════════════════════════════════════════════════════════╝

📍 应用信息:
   应用域名:    https://deerflow-api.railway.app
   Health:     https://deerflow-api.railway.app/health
   API:        https://deerflow-api.railway.app/api

🔔 Alipay 回调 URL:
   https://deerflow-api.railway.app/api/subscription/webhook-alipay

📋 后续步骤:
   1. 登录支付宝开放平台: https://open.alipay.com
   2. 应用设置 → 异步通知 URL
   3. 粘贴上述 NOTIFY_URL
   4. 保存配置
   5. 开始测试支付流程
```

---

## ⏱️ 时间分配

| 步骤 | 预计时间 | 说明 |
|------|---------|------|
| 环境检查 | 1 分钟 | 自动验证 |
| 登录验证 | 1 分钟 | 可能需要浏览器确认 |
| 项目链接 | 1 分钟 | 自动化 |
| 变量配置 | 1 分钟 | 网络 API 调用 |
| 代码推送 | 1-2 分钟 | 取决于网络速度 |
| Docker 构建 | 3-5 分钟 | Railway 后台执行 |
| 迁移执行 | 1-2 分钟 | Alembic 自动执行 |
| 应用启动 | 1-2 分钟 | 取决于启动时间 |
| 域名获取 | 1 分钟 | 自动化 |
| 验证测试 | 1 分钟 | 最后的健康检查 |

**总计**: **约 10-15 分钟**

---

## 🚨 常见问题和解决方案

### Q1: "Railway 未登录"

```powershell
# 解决:
railway login
# 会打开浏览器，完成登录后按 Enter
```

### Q2: "项目未链接"

```powershell
# 解决方式 1: 使用脚本自动链接
# 脚本会提示选择或创建项目

# 解决方式 2: 手动链接
railway link
# 交互式地选择项目
```

### Q3: "部署失败 - Docker 构建错误"

```powershell
# 1. 查看详细日志
railway logs --follow

# 2. 检查 Dockerfile 是否正确
Test-Path docker/Dockerfile.backend

# 3. 本地测试构建
docker build -f docker/Dockerfile.backend -t test-build .

# 4. 重新触发部署
git push origin main
```

### Q4: "无法获取公域名"

```powershell
# 解决方式 1: 通过命令获取
railway domains

# 解决方式 2: 通过 Dashboard 查看
# https://railway.app → 项目 → Backend Service → Networking

# 解决方式 3: 检查应用状态
railway status
```

### Q5: "获不到 NOTIFY_URL"

```powershell
# 如果脚本自动生成失败，手动构建:
$domain = "您从上面获得的域名"
$notifyUrl = "https://$domain/api/subscription/webhook-alipay"
echo $notifyUrl

# 然后手动设置:
railway variables set ALIPAY_NOTIFY_URL=$notifyUrl
```

---

## ✅ 部署成功标志

执行完成后，验证以下事项:

```powershell
# 1. 应用可访问
curl https://deerflow-api.railway.app/health
# 应返回: 200 OK

# 2. API 端点正常
curl https://deerflow-api.railway.app/api/subscription/plans
# 应返回: JSON 格式的套餐列表

# 3. 查看应用日志
railway logs -n 50
# 应看到: "Application started successfully"

# 4. 查看环境变量
railway variables
# 应包含所有 ALIPAY_* 变量和 ALIPAY_NOTIFY_URL
```

---

## 🎯 部署后的下一步 (15 分钟)

### 步骤 1: 配置支付宝平台 (5 分钟)

```
1. 登录: https://open.alipay.com
2. 进入: 应用 → 我的应用 → [选择应用]
3. 点击: 开发设置
4. 找到: 异步通知 URL
5. 粘贴: https://deerflow-api.railway.app/api/subscription/webhook-alipay
6. 点击: 保存或更新
```

### 步骤 2: 测试支付流程 (10 分钟)

```
1. 访问前端: https://deerflow-api.railway.app
2. 导航: /subscription 页面
3. 选择: 任意套餐 (Basic/Business/Enterprise)
4. 选择: Alipay 支付
5. 验证: 生成正确的支付链接
6. (可选) 模拟支付过程

监控日志:
  railway logs --follow
  应看到: "Webhook received from Alipay" 或类似消息
```

---

## 📞 获取帮助

如果遇到问题:

```powershell
# 查看完整日志
railway logs --all --follow

# 查看错误日志
railway logs | Select-String -Pattern "error|Error|ERROR"

# 查看应用配置
railway service list

# 查看数据库状态
railway service list
# 应显示 PostgreSQL 和 Redis 的状态

# 重启应用
railway service restart

# 查看项目信息
railway status
```

---

## 🎉 开始部署！

现在您已准备好了，按照以下步骤执行:

```powershell
# 1. 打开 PowerShell
# 2. cd d:\MultiMode\deerflow\deer-flow
# 3. .\scripts\deploy-railway.ps1
# 4. 等待 10-15 分钟
# 5. 获取 ALIPAY_NOTIFY_URL
# 6. 配置到支付宝
# 7. 开始测试支付！
```

**准备就绪！祝部署顺利！** 🚀

---

## 📊 部署检查清单

执行前:
- [ ] Railway CLI 已安装和登录
- [ ] 项目代码已提交到 Git
- [ ] Alipay 凭证已准备 (APP_ID, PID, 密钥)
- [ ] 网络连接正常

执行中:
- [ ] 脚本正常运行，无错误
- [ ] Docker 镜像成功构建
- [ ] 数据库迁移成功
- [ ] 应用成功启动

执行后:
- [ ] 获得公域名
- [ ] 获得 NOTIFY_URL
- [ ] Health Check 通过
- [ ] 日志无错误
- [ ] 已配置到 Railway

---

**最后一步**: 执行以下命令开始部署！

```powershell
.\scripts\deploy-railway.ps1
```

**预计 10-15 分钟后，您将获得可用的 ALIPAY_NOTIFY_URL！** ✨
