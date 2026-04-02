# DeerFlow 部署快速参考手册

## 📖 快速导航

| 场景 | 文档 | 命令 |
|------|------|------|
| 🚀 快速部署 | 本文 | `./deploy.sh` |
| 📚 详细指南 | DEPLOYMENT_GUIDE.md | - |
| 📓 笔记本教程 | DeerFlow-Deployment-Notebook.ipynb | 在Jupyter中打开 |
| 💻 本地开发 | LOCAL_DEVELOPMENT.md | `make dev` |
| ✅ 安装完成 | SETUP_COMPLETE.md | 查看进度 |

---

## ⚡ 快速启动（5分钟）

### 前提条件

```bash
# 检查基础工具
docker --version       # ✅ 需要 Docker
docker compose version # ✅ 需要 Docker Compose
git --version          # ✅ 需要 Git
```

### 一键部署

```bash
# 1. 克隆仓库
git clone https://github.com/bytedance/deer-flow.git /opt/deer-flow
cd /opt/deer-flow

# 2. 生成配置（首次必须）
make config
# 或手动编辑 config.yaml 和 .env

# 3. 一键启动
./deploy.sh

# 4. 验证
curl http://localhost:2026/
echo "✅ 部署完成！"
```

### 访问应用

- 📱 **前端**：http://localhost:2026
- 🔌 **API 文档**：http://localhost:8001/docs
- 📊 **LangGraph**：http://localhost:2024

---

## 🏗️ 架构简览

```
用户 → Nginx:2026 → Frontend:3000 → Gateway:8001 → LangGraph:2024
         ↓
    飞书/钉钉/Slack（可选）
```

### 核心概念

| 概念 | 解释 | 配置位置 |
|------|------|--------|
| **Thread** | 单个对话线程 | 自动创建 |
| **Tenant** | 租户（多用户隔离）| `memory-{tenant}.json` |
| **Sandbox** | 代码执行环境 | `config.yaml:sandbox` |
| **Memory** | AI学习的知识库 | `.deer-flow/memory-*.json` |
| **Checkpoint** | 对话状态快照 | `.deer-flow/checkpoints.db` |

---

## 📋 配置文件速查

### 最小化配置 (config.yaml)

```yaml
log_level: info
sandbox:
  use: deerflow.sandbox.local:LocalSandboxProvider
memory:
  enabled: true
  storage_path: /data/deer-flow/.deer-flow/memory-{tenant}.json
checkpointer:
  type: sqlite
  connection_string: /data/deer-flow/.deer-flow/checkpoints.db
```

### 环境变量 (.env)

```bash
# 必填
BETTER_AUTH_SECRET=your-generated-secret
OPENAI_API_KEY=sk-...

# 可选
FEISHU_APP_ID=your-app-id
FEISHU_APP_SECRET=your-app-secret
```

---

## 🔧 常用命令

### 部署管理

```bash
# 启动服务
docker compose -f docker/docker-compose.yaml up -d

# 停止服务
docker compose -f docker/docker-compose.yaml down

# 查看状态
docker compose -f docker/docker-compose.yaml ps

# 重启特定服务
docker compose -f docker/docker-compose.yaml restart gateway
```

### 日志查看

```bash
# 实时日志
docker compose logs -f

# 特定服务日志
docker compose logs -f gateway

# 指定行数
docker compose logs --tail=100 gateway
```

### 数据管理

```bash
# 备份数据
tar -czf backup-$(date +%Y%m%d).tar.gz /data/deer-flow/.deer-flow/

# 恢复数据
tar -xzf backup-20260330.tar.gz -C /data/deer-flow/

# 清理容器（谨慎！）
docker system prune -a
```

### 故障排查

```bash
# 进入容器调试
docker compose exec gateway bash

# 检查网络连接
docker compose exec gateway curl http://langgraph:2024

# 查看环境变量
docker compose config | grep -A 20 gateway
```

---

## 🎯 部署清单

### 第1天：环境准备

- [ ] 云服务器已申请（4核8GB+）
- [ ] Ubuntu 22.04 已安装
- [ ] Docker 已安装并启动
- [ ] 数据目录 `/data/deer-flow` 已创建
- [ ] deerflow 用户已创建

```bash
# 快速检查
docker run --rm hello-world && echo "✅ Docker正常"
ls -ld /data/deer-flow && echo "✅ 目录正常"
```

### 第2天：部署配置

- [ ] 代码已克隆到 `/opt/deer-flow`
- [ ] `config.yaml` 已生成
- [ ] `.env` 已编辑并填写 API Keys
- [ ] 配置已验证无语法错误

```bash
# 快速检查
test -f /opt/deer-flow/config.yaml && echo "✅ 配置存在"
grep OPENAI_API_KEY /opt/deer-flow/.env && echo "✅ API Key已填"
```

### 第3天：启动验证

- [ ] 容器已启动（`docker compose ps`）
- [ ] 前端可访问（`curl http://localhost:2026`）
- [ ] API可访问（`curl http://localhost:8001/docs`）
- [ ] 能创建对话线程
- [ ] 能接收并回复消息

```bash
# 快速验证
docker compose ps | grep "Up" && echo "✅ 服务运行中"
curl -s http://localhost:2026/ | head -c 100 && echo "✅ 前端可访问"
```

---

## 📊 性能优化

### 如果响应缓慢

```bash
# 1. 检查资源使用
docker stats

# 2. 增加 Gateway 工作进程
# 在 docker-compose.yaml 中修改：
gateway:
  command: "uvicorn app.gateway.app:app --workers 4"

# 3. 启用 Redis 缓存
# 在 docker-compose.yaml 中添加 redis 服务

# 4. 使用 PostgreSQL 替代 SQLite
# 修改 config.yaml checkpointer 配置
```

### 如果磁盘不足

```bash
# 1. 检查磁盘使用
df -h /data/deer-flow

# 2. 清理Docker镜像
docker image prune -a

# 3. 清理日志文件
find /data/deer-flow/logs -type f -delete

# 4. 归档旧数据
tar -czf archive-$(date +%Y%m).tar.gz /data/deer-flow/backup/old-threads/
```

---

## 🚨 常见问题速解

### Q: Docker 容器启动失败？

**A: 检查日志并修复**

```bash
docker compose logs gateway  # 查看具体错误

# 常见原因：
# 1. 端口已占用 → 修改 docker-compose.yaml 端口
# 2. 权限不足 → 运行 sudo
# 3. 配置错误 → 检查 config.yaml 语法
```

### Q: 前端访问 404？

**A: 检查 Nginx 配置**

```bash
docker compose exec nginx nginx -t  # 验证配置
docker compose restart nginx        # 重启 Nginx
```

### Q: API 返回 500 错误？

**A: 查看 Gateway 日志**

```bash
docker compose logs -f gateway | grep ERROR
# 根据错误信息修复对应代码或配置
```

### Q: 飞书消息收不到？

**A: 逐项检查**

```bash
# 1. 检查飞书应用是否已发布
# 2. 检查事件订阅 URL 是否正确
# 3. 检查 Webhook Token 是否配置
# 4. 查看日志：docker compose logs -f gateway | grep feishu
```

---

## 📈 生产检查清单

### 安全

- [ ] BETTER_AUTH_SECRET 已修改（不是默认值）
- [ ] HTTPS 已配置
- [ ] API 限流已启用
- [ ] 防火墙规则已设置

### 性能

- [ ] CPU 占用率 < 80%
- [ ] 内存占用率 < 85%
- [ ] 磁盘占用率 < 90%
- [ ] API 响应时间 < 2s (P95)

### 可靠性

- [ ] 每天自动备份已设置
- [ ] 告警通知已配置
- [ ] 日志轮转已设置
- [ ] 容器自动重启已启用

### 合规

- [ ] 数据加密已启用
- [ ] 审计日志已配置
- [ ] 用户协议已展示
- [ ] 隐私政策已公布

---

## 📚 学习资源

### 快速上手

1. **5分钟快速启动**（本文）
2. **本地开发指南**：`LOCAL_DEVELOPMENT.md`
3. **完整笔记本**：`DeerFlow-Deployment-Notebook.ipynb`

### 深入学习

1. **部署完整指南**：`DEPLOYMENT_GUIDE.md`（20,000+ 行）
2. **架构文档**：`docs/ARCHITECTURE.md`
3. **API 文档**：Swagger UI（http://localhost:8001/docs）

### 问题反馈

- **GitHub Issues**：https://github.com/bytedance/deer-flow/issues
- **官方Wiki**：https://github.com/bytedance/deer-flow/wiki

---

## 🔄 日常维护

### 日常检查（每天）

```bash
# 服务健康状态
docker compose ps

# 最近错误
docker compose logs --since 1h | grep ERROR

# 资源使用
docker stats --no-stream
```

### 周期检查（每周）

```bash
# 备份检查
ls -lh /data/deer-flow/backup/ | head -5

# 磁盘使用
du -sh /data/deer-flow/*

# 日志大小
du -sh /data/deer-flow/.deer-flow/logs/
```

### 月度检查（每月）

```bash
# 清理旧日志
find /data/deer-flow/logs -type f -mtime +30 -delete

# 更新依赖
cd /opt/deer-flow && git pull origin main

# 灾难恢复演练
# 1. 备份当前数据
# 2. 模拟故障场景
# 3. 执行恢复流程
# 4. 验证数据完整性
```

---

## 🎓 下一步

### 刚完成安装？

→ 阅读 `LOCAL_DEVELOPMENT.md` 了解如何开发

### 需要深入理解架构？

→ 打开 `DeerFlow-Deployment-Notebook.ipynb` 

### 遇到问题？

→ 查阅 `DEPLOYMENT_GUIDE.md` 第11章"故障排查"

### 准备生产部署？

→ 完成本文所有清单项目

---

## 📞 快速支持

| 问题类型 | 查阅位置 | 命令 |
|---------|--------|------|
| 部署问题 | DEPLOYMENT_GUIDE.md | `./deploy.sh` |
| 开发问题 | LOCAL_DEVELOPMENT.md | `make dev` |
| 概念理解 | DeerFlow-Deployment-Notebook.ipynb | Jupyter |
| 代码错误 | GitHub Issues | - |
| 架构设计 | docs/ARCHITECTURE.md | - |

---

## ✨ 提示

💡 **Pro Tip**：保存此文档的链接在浏览器书签中，部署时随时查阅！

---

*最后更新：2026年3月30日*

*DeerFlow 版本：main branch*

*推荐环境：Ubuntu 22.04 LTS + Docker 20.10+ + 4核8GB以上*
