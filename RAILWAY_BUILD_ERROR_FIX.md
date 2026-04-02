# 🔧 Railway 部署错误修复指南

## 问题诊断

**错误：** `✖ Railpack could not determine how to build the app`  
**原因：** 
1. 缺少 `start.sh` 启动脚本
2. Railway 无法自动识别 monorepo 项目
3. 构建配置不完整

**日志时间：** 2026-04-02 15:38:39 UTC

---

## 🔨 立即执行的修复步骤

### 第 1 步：验证已创建的文件（1 分钟）

```powershell
# 检查 start.sh 是否存在
cd d:\MultiMode\deerflow\deer-flow
Test-Path start.sh    # 应返回 True

# 检查 railway.json 是否更新
Get-Content railway.json | Select-Object -First 20
# 应显示："startCommand": "bash /app/start.sh"
```

**预期结果：**
```
✅ start.sh 文件已创建
✅ railway.json 已更新
✅ 文件格式正确
```

### 第 2 步：修复行尾符（2 分钟）

**重要：** start.sh 必须使用 LF（Linux 格式），不能是 CRLF（Windows 格式）

```powershell
# 方法 1：使用 VS Code（推荐）
# 1. 打开 start.sh
# 2. 右下角显示"CRLF"
# 3. 点击 → 选择"LF"
# 4. Ctrl+S 保存

# 方法 2：使用 PowerShell
$content = Get-Content start.sh -Raw
$content = $content -replace "`r`n", "`n"
Set-Content start.sh $content -NoNewline -Encoding UTF8
```

**验证：**
```powershell
file start.sh
# 应显示：POSIX shell script text executable, ASCII text
```

### 第 3 步：确保 start.sh 可执行（1 分钟）

```powershell
# Windows 中不需要修改权限，但在推送到 Git 时要保留 executable 标志
git add -A
git commit --allow-empty -m "chore: Preserve executable permissions"
```

### 第 4 步：提交和推送（2 分钟）

```powershell
cd d:\MultiMode\deerflow\deer-flow

# 查看改动
git status

# 添加文件
git add start.sh railway.json

# 提交
git commit -m "fix: Add Railway startup script - resolve Railpack build error

- Created start.sh with proper initialization and startup logic
- Updated railway.json with explicit Dockerfile configuration
- Configured startCommand to use bash /app/start.sh
- Added health check configuration
- Includes database migration and multi-tenant initialization"

# 推送到 GitHub
git push origin main
```

**预期输出：**
```
✅ 1 file changed (start.sh)
✅ 1 file changed (railway.json)
✅ Pushing to https://github.com/zyj18860969891-byte/cloud-deerflow.git
```

### 第 5 步：重新部署（15-20 分钟）

```powershell
# 1. 访问 Railway Dashboard
# https://railway.app/dashboard

# 2. 进入 cloud-deerflow 项目

# 3. 进入 Deployments 标签页

# 4. 查看最新的部署日志
# 应该看到：
#   ✅ Git push 已检测
#   ✅ Docker 构建开始
#   ✅ Dockerfile 使用
#   ✅ start.sh 执行
#   ✅ 应用启动

# 5. 监控日志中出现（约 15-20 分钟）
# "INFO: Uvicorn running on 0.0.0.0:8001"
```

---

## ✅ 成功标志

部署修复成功后，应该看到：

```
2026-04-02T15:xx:xxZ [inf] 🚀 开始启动 DeerFlow...
2026-04-02T15:xx:xxZ [inf] ✅ 环境变量已验证
2026-04-02T15:xx:xxZ [inf] 📂 当前目录：/app/backend
2026-04-02T15:xx:xxZ [inf] 📦 使用 uv 安装依赖...
2026-04-02T15:xx:xxZ [inf] ✅ 依赖安装完成
2026-04-02T15:xx:xxZ [inf] 🗄️  运行数据库迁移...
2026-04-02T15:xx:xxZ [inf] ✅ 数据库迁移完成
2026-04-02T15:xx:xxZ [inf] 👥 检查多租户初始化...
2026-04-02T15:xx:xxZ [inf] ✅ 默认租户已存在
2026-04-02T15:xx:xxZ [inf] 🎯 启动 FastAPI 应用...
2026-04-02T15:xx:xxZ [inf]    主机：0.0.0.0
2026-04-02T15:xx:xxZ [inf]    端口：8001
2026-04-02T15:xx:xxZ [inf]    工作进程：4
2026-04-02T15:xx:xxZ [inf] INFO:     Started server process [1]
2026-04-02T15:xx:xxZ [inf] INFO: Uvicorn running on http://0.0.0.0:8001
2026-04-02T15:xx:xxZ [inf] INFO:     Application startup complete
```

---

## 🔍 故障排查

### 问题 1：部署仍然失败 - "Docker build failed"

**检查清单：**
```powershell
# 1. 验证 start.sh 是否有语法错误
bash -n start.sh

# 2. 验证 Dockerfile 路径
# railway.json 中应为："dockerfile": "backend/Dockerfile"

# 3. 检查 backend/Dockerfile 存在
Test-Path backend/Dockerfile

# 4. 查看完整的构建日志
railway logs --tail 200
```

**解决方案：**
- 如果 start.sh 有语法错误，修复后重新提交
- 如果 Dockerfile 有问题，检查 FROM、RUN、CMD 等指令
- 确保所有文件都推送到 GitHub

### 问题 2：应用启动后立即崩溃

**症状：** "Container exited with code 1"

**检查清单：**
```powershell
# 1. 检查环境变量
railway env
# 应该看到 DATABASE_URL 已设置

# 2. 检查数据库连接
# DATABASE_URL 格式应为：
# postgresql://user:password@host:port/database

# 3. 查看详细错误日志
railway logs --tail 300 | Select-Object -Last 50
```

**解决方案：**
- 验证 DATABASE_URL 格式正确
- 确保数据库服务已启动且可访问
- 检查 Python 依赖是否正确安装

### 问题 3：start.sh 未找到 - "Permission denied"

**症状：** "bash: start.sh: Permission denied"

**解决方案：**
```powershell
# 确保 start.sh 在 Git 中标记为可执行
git update-index --chmod=+x start.sh
git commit -m "chore: Make start.sh executable"
git push origin main
```

### 问题 4：数据库迁移失败

**症状：** Alembic 迁移错误

**解决方案：**
```powershell
# 这通常是非阻塞的 - start.sh 会继续启动应用
# 检查日志中的错误：
# "⚠️ 数据库迁移失败或已完成"

# 如果需要手动修复：
# 1. 连接数据库
# 2. 检查迁移历史
# 3. 手动运行必要的迁移
```

---

## 📊 修复前后对比

### ❌ 修复前（失败）

```
Railpack 0.23.0
Found .dockerignore file
⚠️  Script start.sh not found
✖ Railpack could not determine how to build the app

支持的语言：Python, Node, Golang, ...
无法识别项目类型
```

### ✅ 修复后（成功）

```
使用 Dockerfile 构建
Docker 构建开始 → 完成
容器启动
start.sh 执行
依赖安装
数据库初始化
应用启动：Uvicorn running on 0.0.0.0:8001
✅ 部署完成
```

---

## ⏱️ 总耗时估算

| 步骤 | 耗时 |
|-----|------|
| 1. 验证文件 | 1 分钟 |
| 2. 修复行尾符 | 2 分钟 |
| 3. 设置权限 | 1 分钟 |
| 4. 提交和推送 | 2 分钟 |
| **手动部分小计** | **6 分钟** |
| 5a. GitHub webhook 触发 | 自动（< 1 分钟） |
| 5b. Docker 构建 | 10-15 分钟 |
| 5c. 容器启动和初始化 | 5 分钟 |
| 5d. 应用启动 | 自动（< 1 分钟） |
| **自动部分小计** | **15-20 分钟** |
| **总计** | **21-26 分钟** |

---

## 📋 完整检查清单

### 本地准备（现在做）
- [ ] 验证 start.sh 文件存在
- [ ] 验证 railway.json 已更新
- [ ] 检查行尾符（LF 格式）
- [ ] 提交和推送代码
- [ ] GitHub 已收到推送

### Railway 重新部署（自动）
- [ ] GitHub webhook 已触发
- [ ] Docker 构建已开始
- [ ] Dockerfile 构建完成
- [ ] 容器启动
- [ ] start.sh 执行
- [ ] 依赖安装完成
- [ ] 数据库迁移完成
- [ ] 应用启动

### 验证部署成功
- [ ] Railway 日志显示"Uvicorn running"
- [ ] 公共域名可访问
- [ ] 健康检查返回 200 OK
- [ ] API 端点可响应

---

## 🚀 立即行动

### 第 1 分钟：在 PowerShell 中执行

```powershell
cd d:\MultiMode\deerflow\deer-flow

# 验证文件
Write-Host "✅ 检查 start.sh..." -ForegroundColor Green
Test-Path start.sh
Write-Host ""

Write-Host "✅ 检查 railway.json..." -ForegroundColor Green
Select-String "startCommand" railway.json
Write-Host ""
```

### 第 2-3 分钟：修复行尾符（VS Code）

1. 打开 `start.sh`
2. 右下角点击 "CRLF"
3. 选择 "LF"
4. Ctrl+S 保存

### 第 4-6 分钟：Git 操作

```powershell
git status
git add start.sh railway.json
git commit -m "fix: Add Railway startup script to resolve build error"
git push origin main
```

### 第 7+ 分钟：监控部署

```
1. 打开 https://railway.app/dashboard
2. 进入 cloud-deerflow 项目
3. 点击 Deployments 标签页
4. 查看实时日志
5. 等待看到 "Uvicorn running on 0.0.0.0:8001"
```

---

**预计完成时间：** 约 20-30 分钟内应用将成功部署！ 🎉

---

## 📞 需要更多帮助？

查看 Notebook 第 25 章：`Railway 部署错误诊断和解决方案`

其中包含：
- 详细的错误分析
- start.sh 完整脚本
- Dockerfile 完整配置
- 更多故障排查步骤
- 最佳实践建议
