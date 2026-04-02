# 快速 Railway 部署检查清单

## 前置条件检查 ✅

- [ ] GitHub 仓库已创建：https://github.com/zyj18860969891-byte/cloud-deerflow
- [ ] Git 代码已推送到 `main` 分支
- [ ] 支付宝凭证已准备：
  - [ ] ALIPAY_APPID: 2021006138604101
  - [ ] ALIPAY_PRIVATE_KEY: [已获取]
  - [ ] ALIPAY_PUBLIC_KEY: [已获取]

## Railway 部署步骤 🚀

### 第 1 步：创建项目（5 分钟）

- [ ] 访问 https://railway.app/dashboard
- [ ] 点击 "Create New Project"
- [ ] 选择 "Deploy from GitHub repo"
- [ ] 授予 Railway 访问 GitHub 权限
- [ ] 选择仓库：`cloud-deerflow`
- [ ] 选择分支：`main`

**预期结果：** Railway 开始自动构建 Docker 镜像

### 第 2 步：配置环境变量（5 分钟）

进入项目后，点击 "Variables" 配置：

#### 必须的 PostgreSQL（如果使用 Railway 数据库）
- [ ] DATABASE_URL: `postgresql://[auto-generated]`

#### 必须的支付宝配置
- [ ] ALIPAY_APPID: `2021006138604101`
- [ ] ALIPAY_PRIVATE_KEY: `[你的私钥]`
- [ ] ALIPAY_PUBLIC_KEY: `[支付宝公钥]`
- [ ] ALIPAY_NOTIFY_URL: `https://[自动生成].railway.app/api/subscription/webhook-alipay`

#### 必须的应用配置
- [ ] ENVIRONMENT: `production`
- [ ] DEBUG: `false`
- [ ] BETTER_AUTH_SECRET: `[生成 32 字符随机值]`

#### 可选的 LangGraph 配置
- [ ] LANGGRAPH_URL: `http://localhost:2024` (如果 LangGraph 在同一项目)
- [ ] LANGGRAPH_API_KEY: `[你的 API 密钥]`

**保存配置后，Railway 会自动重新部署**

### 第 3 步：等待部署完成（10-15 分钟）

在 Railway Dashboard 中：
- [ ] 查看 "Deployments" 标签页
- [ ] 等待状态变为 "Success" (绿色)
- [ ] 查看 "Logs" 确认没有错误

**典型日志输出：**
```
✓ 检查环境变量...
✓ 等待数据库连接...
✅ 数据库已连接
✓ 运行数据库迁移...
✓ 初始化多租户数据...
✅ 初始化完成，启动应用...
INFO: Uvicorn running on 0.0.0.0:8001
```

### 第 4 步：获取公共域名和 Webhook URL（2 分钟）

- [ ] 在 Railway Dashboard 找到 "Networking"
- [ ] 复制 "Public Domain"，例如：`https://cloud-deerflow-production.railway.app`
- [ ] ALIPAY_NOTIFY_URL 应自动更新为：`https://cloud-deerflow-production.railway.app/api/subscription/webhook-alipay`

### 第 5 步：验证部署（5 分钟）

#### 在 PowerShell 中运行验证命令：

```powershell
# 设置域名变量（替换为你的实际域名）
$DOMAIN = "https://cloud-deerflow-production.railway.app"

# 检查 1：健康检查
Write-Host "检查健康状态..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$DOMAIN/health" -SkipHttpsValidation

# 检查 2：API 可用性
Write-Host "检查 API 端点..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$DOMAIN/api/subscription/plans" -SkipHttpsValidation

# 检查 3：用户端点
Write-Host "检查用户端点..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$DOMAIN/api/user" -SkipHttpsValidation
```

**预期结果：** 所有请求返回 HTTP 200 OK

- [ ] ✅ 健康检查返回 200
- [ ] ✅ API 端点返回数据
- [ ] ✅ 用户端点可访问

### 第 6 步：配置支付宝通知（3 分钟）

1. [ ] 登录支付宝开放平台：https://open.alipay.com
2. [ ] 找到应用：`DeerFlow 订阅系统`
3. [ ] 进入 "应用信息"
4. [ ] 找到 "异步通知 URL" 配置项
5. [ ] 更新 URL：`https://[你的域名]/api/subscription/webhook-alipay`
6. [ ] 保存设置
7. [ ] 支付宝会发送测试通知，检查 Railway 日志是否收到

**验证方式：**
查看 Railway 日志，应能看到类似：
```
[Subscription] Alipay webhook received
[Webhook] Processing async notification
✅ Webhook processed successfully
```

- [ ] ✅ 支付宝通知 URL 已配置
- [ ] ✅ 测试通知已接收

## 完整验证流程 🧪

### 测试 1：API 基本功能

```powershell
# 获取订阅计划列表
$response = Invoke-WebRequest -Uri "$DOMAIN/api/subscription/plans" -SkipHttpsValidation
$plans = $response.Content | ConvertFrom-Json
Write-Host "可用计划数：$($plans.Count)" -ForegroundColor Green
```

**预期：** 返回至少 3 个订阅计划（Free, Professional, Enterprise）

### 测试 2：用户和租户

```powershell
# 创建测试用户（需要认证）
$headers = @{"Authorization" = "Bearer [your-token]"}
Invoke-WebRequest -Uri "$DOMAIN/api/user" -Headers $headers -SkipHttpsValidation
```

**预期：** 返回用户信息和当前租户

### 测试 3：支付宝支付流程

1. [ ] 打开应用：`https://[你的域名]`
2. [ ] 进入订阅页面
3. [ ] 选择订阅计划
4. [ ] 点击 "立即购买" / "Subscribe"
5. [ ] 应跳转到支付宝支付页面
6. [ ] 在沙箱中完成支付
7. [ ] 返回应用，检查订阅状态

**预期：**
- [ ] ✅ 支付页面加载正常
- [ ] ✅ 支付宝支付流程可完成
- [ ] ✅ 支付后订阅状态已激活
- [ ] ✅ Railway 日志显示订阅激活记录

## 故障排查 🔧

### 问题 1：部署失败 - "Build failed"

**查看日志：**
```
Railway Dashboard → Deployments → Logs
```

**常见原因和解决方案：**

1. **Python 依赖错误**
   - [ ] 检查 `backend/pyproject.toml` 语法
   - [ ] 确保所有依赖已列出
   - [ ] 重新提交代码并推送

2. **环境变量缺失**
   - [ ] 检查 `ALIPAY_APPID` 已配置
   - [ ] 检查 `DATABASE_URL` 已配置
   - [ ] 点击 "Redeploy" 重新部署

3. **Dockerfile 错误**
   - [ ] 检查 Dockerfile 路径正确
   - [ ] 检查 base image 可用
   - [ ] 查看完整的构建日志

**解决方案：修复问题后，点击 "Redeploy"**

### 问题 2：应用崩溃 - "Application crashed"

**查看日志：**
```
Railway Dashboard → Logs（查看最近 50 行）
```

**常见原因：**

1. **数据库连接失败**
   - 确保 `DATABASE_URL` 正确
   - 等待数据库服务启动
   - 检查凭证是否正确

2. **环境变量不完整**
   - 检查所有 `ALIPAY_*` 变量已配置
   - 检查 `BETTER_AUTH_SECRET` 已设置

3. **缺少依赖**
   - 查看错误信息中的 `ImportError`
   - 更新 `pyproject.toml`，重新推送

**解决方案：修复后点击 "Redeploy"**

### 问题 3：Alipay 通知未送达

**症状：** 支付完成但订阅未激活

**检查步骤：**

1. [ ] 验证 Railway 日志中是否有 webhook 调用
2. [ ] 检查 `ALIPAY_NOTIFY_URL` 配置正确
3. [ ] 在支付宝平台重新保存通知 URL
4. [ ] 确保 RSA 密钥配置正确

**调试命令：**
```powershell
# 查看 Railway 日志中的 webhook 事件
railway logs --tail 100 | grep -i webhook
```

## 持续部署 ♻️

此后，每次代码更新：

1. [ ] 在本地开发并测试
2. [ ] 提交更改：`git commit -m "feat: [description]"`
3. [ ] 推送到 GitHub：`git push origin main`
4. [ ] Railway 自动监测 GitHub 更新
5. [ ] Railway 自动重新构建和部署
6. [ ] 部署完成后应用自动更新

**无需手动干预！** Railway GitHub 集成完全自动化。

## 回滚和扩展 🔄

### 回滚到上一个版本

1. [ ] Railway Dashboard → Deployments
2. [ ] 找到之前的成功部署
3. [ ] 点击 "Redeploy this version"

### 增加副本数量（高可用）

1. [ ] Railway Dashboard → Variables
2. [ ] 设置 `RAILWAY_REPLICAS=2`（或更多）
3. [ ] 保存，自动部署额外实例

## 完成验证 ✨

所有步骤完成后：

- [ ] ✅ 代码已推送到 GitHub
- [ ] ✅ Railway 项目已创建
- [ ] ✅ 环境变量已配置
- [ ] ✅ 部署已完成（绿色状态）
- [ ] ✅ 健康检查已通过
- [ ] ✅ 支付宝通知已配置
- [ ] ✅ 支付流程已测试
- [ ] ✅ 生产环境已就绪

**🎉 恭喜！DeerFlow 已成功部署到 Railway！**

---

## 快速参考

| 操作 | 位置 | 时间 |
|-----|------|------|
| 创建项目 | railway.app/dashboard | 5 分钟 |
| 配置变量 | 项目 → Variables | 5 分钟 |
| 等待部署 | Deployments 标签页 | 10-15 分钟 |
| 验证健康 | `$DOMAIN/health` | 1 分钟 |
| 配置通知 | alipay.open | 3 分钟 |
| 测试支付 | 应用 → 订阅页面 | 5-10 分钟 |
| **总计** | - | **30-45 分钟** |

需要帮助？查看：
- Railway 文档：https://docs.railway.app
- 支付宝文档：https://open.alipay.com
- DeerFlow 仓库：https://github.com/zyj18860969891-byte/cloud-deerflow
