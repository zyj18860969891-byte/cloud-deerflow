# 🚀 DeerFlow Railway 部署 - 快速参考卡

**最后更新**: 2026年4月2日  
**部署状态**: ✅ 脚本就绪，可立即执行  
**预计用时**: 10-15 分钟 (部署) + 15-20 分钟 (配置和测试)

---

## ⚡ 一行命令启动部署

```powershell
cd d:\MultiMode\deerflow\deer-flow; .\scripts\deploy-railway.ps1
```

---

## 📌 关键信息速查表

| 项目 | 值 | 说明 |
|------|-----|------|
| **Alipay App ID** | 2021006138604101 | 已验证 ✓ |
| **Alipay PID** | 2088380691837603 | 已验证 ✓ |
| **Railway CLI** | 4.27.5 | 已安装 ✓ |
| **部署目标** | Railway.app | 云平台 |
| **应用框架** | FastAPI + LangGraph | 后端 |
| **前端** | Next.js 16 + React 19 | 前端 |
| **数据库** | PostgreSQL | 持久化 |
| **缓存** | Redis | 性能优化 |
| **预计公域** | deerflow-api.railway.app | 自动生成 |
| **NOTIFY_URL** | https://[domain]/api/subscription/webhook-alipay | 自动生成 |

---

## ✅ 执行前检查清单

```
□ Railway CLI 已安装        → railway --version
□ Railway 已登录            → railway whoami  
□ Git 已初始化              → git status
□ 代码已提交                → git log
□ Alipay 凭证已准备         → 4 项全部就绪
□ 网络连接正常              → ping google.com
□ 磁盘空间充足              → 2GB+ 可用空间
```

---

## 🎬 执行步骤 (自动化流程)

```
1️⃣  打开 PowerShell
2️⃣  cd d:\MultiMode\deerflow\deer-flow
3️⃣  .\scripts\deploy-railway.ps1
4️⃣  监控脚本输出 (持续约 10-15 分钟)
5️⃣  获取 ALIPAY_NOTIFY_URL (脚本输出)
6️⃣  配置到支付宝平台 (https://open.alipay.com)
7️⃣  测试支付流程
```

---

## 📊 执行时间分配

| 阶段 | 操作 | 时间 |
|------|------|------|
| 准备 | 环境检查 + 登录 | 2 分钟 |
| 配置 | 变量设置 + 代码推送 | 2 分钟 |
| 构建 | Docker 镜像 + 迁移 | 5 分钟 |
| 启动 | 应用启动 + 验证 | 3 分钟 |
| **总计** | **部署完成** | **10-15 分钟** |

后续:
- 敏感凭证配置 (Dashboard): 5 分钟
- 支付宝平台配置: 5 分钟
- 功能测试: 10 分钟
- **总计**: 30-50 分钟完成整个流程

---

## 🔍 关键命令速查

### 部署相关

```powershell
# 执行部署
.\scripts\deploy-railway.ps1

# 仅验证 (不部署)
.\scripts\deploy-railway.ps1 -Action verify

# 查看日志
.\scripts\deploy-railway.ps1 -Action logs

# 查看应用信息
.\scripts\deploy-railway.ps1 -Action info
```

### Railway 相关

```powershell
# 查看状态
railway status

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

# 查看服务列表
railway service list
```

### 验证相关

```powershell
# 测试健康检查
curl https://deerflow-api.railway.app/health

# 测试 API
curl https://deerflow-api.railway.app/api/subscription/plans

# 查看应用日志
railway logs -n 100

# 连接数据库 (通过 Railway)
railway database connect
```

---

## 🎯 执行后的输出示例

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 部署成功！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 应用信息:
   公域名: https://deerflow-api.railway.app
   
🔔 ALIPAY_NOTIFY_URL:
   https://deerflow-api.railway.app/api/subscription/webhook-alipay

📋 后续步骤:
   1. 登录支付宝: https://open.alipay.com
   2. 配置 NOTIFY_URL 到异步通知字段
   3. 测试支付流程
   4. 监控日志: railway logs --follow
```

---

## ⚠️ 常见问题速解

| 问题 | 解决方案 |
|------|---------|
| **Railway 未登录** | `railway login` 或脚本自动打开 |
| **项目未链接** | 脚本自动链接，或 `railway link` |
| **部署失败** | `railway logs --follow` 查看详情 |
| **无法获取域名** | `railway domains` 或在 Dashboard 查看 |
| **应用启动慢** | 正常，最多 2 分钟，查看 `railway logs` |
| **NOTIFY_URL 获取失败** | 手动构建: `https://[domain]/api/subscription/webhook-alipay` |

---

## 🔐 敏感信息配置

**自动配置** (脚本执行):
- ALIPAY_APP_ID ✓
- ALIPAY_PID ✓  
- ALIPAY_GATEWAY_URL ✓

**手动配置** (Railway Dashboard):
- ALIPAY_APP_PRIVATE_KEY (复制粘贴 RSA 私钥)
- ALIPAY_PUBLIC_KEY (复制粘贴 RSA 公钥)

配置位置:
```
https://railway.app → 项目 → Variables → 添加
```

---

## 📈 部署完成标志

所有以下项目都通过 ✓:

```
✅ 应用状态: Running
✅ Health Check: 200 OK
✅ API 可访问: 返回正确数据
✅ 日志无错误: 显示正常操作
✅ 数据库连接: 正常
✅ Redis 连接: 正常
✅ 公域名: 有效可访问
✅ NOTIFY_URL: 已获得并配置
✅ 支付宝集成: 就绪
✅ 支付流程: 可正常进行
```

---

## 🎓 学习资源

| 资源 | 位置 | 用途 |
|------|------|------|
| 详细部署指南 | RAILWAY_DEPLOYMENT_GUIDE.md | 深入了解 |
| 快速启动 | RAILWAY_DEPLOYMENT_READY.md | 快速参考 |
| 执行手册 | EXECUTE_DEPLOYMENT.md | 详细步骤 |
| 部署脚本 | scripts/deploy-railway.ps1 | 自动化 |
| 凭证验证 | ALIPAY_CREDENTIALS_VERIFICATION.md | 安全性 |

---

## 🆘 需要帮助？

### 立即可用的命令

```powershell
# 诊断脚本
.\scripts\deploy-railway.ps1 -Action verify

# 查看完整日志
railway logs --all --follow

# 获取项目信息
railway project status

# 重新链接项目
railway link
```

### 检查清单

```powershell
# 1. 验证环境
railway --version
git --version
node --version

# 2. 验证登录
railway whoami

# 3. 验证项目
railway status

# 4. 查看日志
railway logs
```

---

## 🚀 现在就开始！

```powershell
# 一条命令启动部署
cd d:\MultiMode\deerflow\deer-flow; .\scripts\deploy-railway.ps1
```

---

## 📞 快速参考

- **部署脚本**: `.\scripts\deploy-railway.ps1`
- **完整指南**: `RAILWAY_DEPLOYMENT_GUIDE.md`
- **快速启动**: `RAILWAY_DEPLOYMENT_READY.md`
- **执行步骤**: `EXECUTE_DEPLOYMENT.md`
- **部署状态**: `DEPLOYMENT_STATUS_FINAL.md`
- **凭证验证**: `ALIPAY_CREDENTIALS_VERIFICATION.md`
- **部署就绪**: `ALIPAY_CREDENTIALS_DEPLOYMENT_READY.md`

---

**准备好了吗?** 开始部署吧! 🎉

```powershell
.\scripts\deploy-railway.ps1
```

预计 10-15 分钟后，您将拥有生产级别的 DeerFlow 应用！
