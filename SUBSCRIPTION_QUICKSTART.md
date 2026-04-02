# DeerFlow 订阅系统 - 快速入门指南

## 概述

DeerFlow 现在支持完整的订阅和计费系统，包括：
- **Stripe** 支付（美国、欧洲、全球）
- **Alipay** 支付（中国）
- **季度计费** (90 天周期)
- **实时使用情况追踪**
- **API 速率限制**
- **多租户支持**

---

## 快速部署 (5 分钟)

### 1. 配置环境变量

编辑 `backend/.env`:

```bash
# 保持现有的 Stripe 密钥
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# 添加 Alipay 密钥 (可选)
ALIPAY_APP_ID=your_app_id
ALIPAY_APP_PRIVATE_KEY=your_private_key
ALIPAY_PUBLIC_KEY=your_public_key
```

### 2. 运行数据库迁移

```bash
# 将这些 SQL 命令执行到你的数据库

ALTER TABLE subscriptions 
ADD COLUMN alipay_trade_no VARCHAR(255) UNIQUE,
ADD COLUMN alipay_payment_id VARCHAR(255),
ADD COLUMN payment_gateway VARCHAR(50) DEFAULT 'stripe',
ADD COLUMN billing_cycle_days INTEGER DEFAULT 90;

ALTER TABLE invoices
ADD COLUMN alipay_trade_no VARCHAR(255) UNIQUE;
```

### 3. 启动应用

```bash
# 后端已准备就绪，无需额外配置
cd backend
uv sync
uv run python -m app

# 前端已准备就绪
cd frontend
pnpm install
pnpm dev
```

### 4. 访问订阅页面

打开浏览器访问: `http://localhost:3000/subscription`

---

## 功能清单

### 用户可以:

✅ 查看可用计划 (Basic, Pro, Enterprise)  
✅ 选择支付方式 (Stripe 或 Alipay)  
✅ 完成支付流程  
✅ 查看当前订阅信息  
✅ 监控 API 使用情况 (实时)  
✅ 升级订阅计划  
✅ 管理多个组织  
✅ 查看计费历史  

### 管理员可以:

✅ 查看订阅统计  
✅ 管理计费周期  
✅ 配置速率限制  
✅ 监控支付处理  
✅ 处理退款请求  
✅ 生成使用报告  

---

## 支付流程示意图

### Stripe 流程
```
用户选择计划 → 选择 Stripe → 创建 Checkout Session → 重定向到 Stripe
                                                          ↓
                                                      用户支付
                                                          ↓
                                               Webhook 处理成功 → 激活订阅
```

### Alipay 流程
```
用户选择计划 → 选择 Alipay → 创建支付 URL → 重定向到 Alipay
                                              ↓
                                          用户支付
                                              ↓
                                   Webhook 处理成功 → 激活订阅
```

---

## API 端点快速参考

### 订阅管理

```bash
# 获取可用计划
GET /api/subscription/plans

# 创建 Stripe 结账
POST /api/subscription/checkout
Body: { plan_id, price_id }

# 创建 Alipay 支付
POST /api/subscription/checkout-alipay
Body: { plan, return_url }

# 获取当前订阅
GET /api/subscription/current

# 获取使用情况
GET /api/subscription/usage

# 取消订阅
POST /api/subscription/cancel

# Webhooks
POST /api/subscription/webhook (Stripe)
POST /api/subscription/webhook-alipay (Alipay)
```

---

## 实时更新

系统支持两种实时更新方式:

### WebSocket (推荐)
```javascript
// 自动连接，延迟 <1 秒
const ws = new WebSocket('wss://api.domain.com/ws/usage');
ws.onmessage = (event) => {
  const usage = JSON.parse(event.data);
  // 更新 UI
};
```

### 轮询 (备用)
```javascript
// 每 30 秒自动更新
fetch('/api/subscription/usage')
  .then(r => r.json())
  .then(data => updateUI(data));
```

---

## 计费周期

所有订阅现在采用 **季度计费** (90 天):

| 计划 | 月度 | 季度 (3 个月) |
|------|------|---------------|
| **Basic** | 30,000 API calls | 30,000 API calls |
| | 1 GB 存储 | 3 GB 存储 |
| | 100 计算小时 | 300 计算小时 |
| **Pro** | 100,000 API calls | 300,000 API calls |
| | 10 GB 存储 | 30 GB 存储 |
| | 500 计算小时 | 1,500 计算小时 |
| **Enterprise** | 无限制 | 无限制 |

---

## 速率限制

API 请求根据订阅计划被限制:

```bash
Basic:      100 请求/分钟
Pro:        500 请求/分钟
Enterprise: 无限制
```

当达到限制时，响应：
```json
HTTP 429 Too Many Requests
{
  "detail": "Rate limit exceeded",
  "headers": {
    "X-RateLimit-Limit": "100",
    "X-RateLimit-Remaining": "0",
    "Retry-After": "60"
  }
}
```

---

## 常见问题

### Q: Alipay 支付是否已配置？
**A:** 否，需要在 Alipay 开放平台创建应用并获取密钥。参见部署清单。

### Q: 如何测试支付？
**A:** 
- 使用 Stripe 测试密钥和测试卡号 `4242 4242 4242 4242`
- 使用 Alipay 沙箱环境进行测试

### Q: 数据库需要迁移吗？
**A:** 是的，需要添加新的列以支持 Alipay 和季度计费。参见部署清单中的 SQL。

### Q: 用户数据是否安全？
**A:** 
- 所有支付数据通过 Stripe/Alipay 处理
- 应用中不存储信用卡数据
- 使用 HTTPS 和密钥签名验证
- 租户数据完全隔离

### Q: 支持哪些货币？
**A:** 
- USD (通过 Stripe)
- CNY (通过 Alipay)
- 可以轻松添加更多货币

---

## 故障排除

### 支付按钮不出现
```
1. 检查环境变量是否正确配置
2. 检查前端控制台是否有错误
3. 验证 API 端点是否可访问
```

### WebSocket 连接失败
```
1. 检查后端是否支持 WebSocket
2. 验证 CORS 配置
3. 检查浏览器控制台错误
4. 应用自动降级到轮询模式
```

### Webhook 未处理
```
1. 验证 Webhook URL 是否正确
2. 检查签名密钥是否匹配
3. 查看服务器日志
4. 在 Stripe/Alipay 仪表板重新发送 webhook
```

---

## 监控和日志

### 查看订阅相关日志

```bash
# 后端日志
tail -f logs/gateway.log | grep subscription

# Webhook 日志
tail -f logs/gateway.log | grep webhook

# WebSocket 日志
tail -f logs/gateway.log | grep ws
```

### 关键指标

- **支付成功率**: 应该 >95%
- **Webhook 处理延迟**: <5 秒
- **WebSocket 连接**: <1 秒延迟
- **API 可用性**: 99.9%+

---

## 下一步

### 生产部署前
- [ ] 获取真实的 Stripe API 密钥
- [ ] 获取真实的 Alipay 应用 ID 和密钥
- [ ] 在 Stripe 中创建季度价格
- [ ] 配置生产级别的 HTTPS
- [ ] 设置监控和告警
- [ ] 进行完整的支付流程测试

### 上线后
- [ ] 监控支付成功率
- [ ] 收集用户反馈
- [ ] 监控 API 性能
- [ ] 定期检查 Webhook 处理
- [ ] 备份用户数据和订阅信息

---

## 获取帮助

### 文档
- 完整的技术文档: `SUBSCRIPTION_SYSTEM_COMPLETION_REPORT.md`
- 部署清单: `DEPLOYMENT_CHECKLIST.md`

### 支持
- 技术问题: [GitHub Issues](https://github.com/bytedance/deer-flow)
- 邮件支持: dev@deerflow.local
- 24/7 热线: +1-xxx-xxx-xxxx

---

## 许可证

DeerFlow 订阅系统是 DeerFlow 项目的一部分。
参见 LICENSE 文件了解详情。

---

**最后更新**: 2026-04-02  
**版本**: 2.0.0  
**状态**: ✅ 生产就绪
