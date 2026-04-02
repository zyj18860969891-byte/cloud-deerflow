# DeerFlow OpenRouter API 快速参考

## 🔑 API 配置

**提供商**: OpenRouter  
**模型**: stepfun/step-3.5-flash  
**API Key**: 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  
**Base URL**: https://openrouter.ai/api/v1  

## 🚀 服务状态

| 服务 | 地址 | 状态 |
|------|------|------|
| Frontend | http://localhost:3000 | ✅ 运行中 |
| Gateway | http://localhost:8001 | ✅ 运行中 |
| LangGraph | http://localhost:2024 | ✅ 运行中 |

## 📋 关键配置文件

1. **backend/.env** - 环境变量
```
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=stepfun/step-3.5-flash
LLM_PROVIDER=openrouter
DEFAULT_MODEL=stepfun/step-3.5-flash
MODEL_TEMPERATURE=0.7
MODEL_MAX_TOKENS=2048
```

2. **config.yaml** - 模型定义
```yaml
models:
  - name: stepfun-3.5-flash
    use: langchain_openai:ChatOpenAI
    model: stepfun/step-3.5-flash
    api_key: $OPENROUTER_API_KEY
    base_url: https://openrouter.ai/api/v1
```

3. **frontend/.env.local** - 前端配置
```
BETTER_AUTH_SECRET=local-dev-secret-key
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:2024
```

## 🧪 快速测试命令

```bash
# 1. 验证 API 配置
cd backend
python test_openrouter_config.py

# 2. 测试 Gateway API
python test_gateway_api.py

# 3. 运行单元测试
pytest tests/ -v

# 4. 测试前端
打开 http://localhost:3000
```

## 📈 API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /threads | 创建新线程 |
| GET | /threads | 列出所有线程 |
| GET | /threads/{id} | 获取线程详情 |
| POST | /threads/{id}/messages | 发送消息 |
| GET | /threads/{id}/messages | 获取消息历史 |
| GET | /health | 健康检查 |

## 🔧 常用命令

```bash
# 启动服务
cd backend
uv run --with langgraph-cli langgraph dev --config langgraph.json &
uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 &
cd ../frontend && pnpm dev

# 停止服务
pkill -f "langgraph"
pkill -f "uvicorn"
pkill -f "pnpm"

# 查看日志
tail -f logs/langgraph.log
tail -f logs/gateway.log

# 检查端口
netstat -ano | findstr :2024
netstat -ano | findstr :8001
netstat -ano | findstr :3000
```

## 📚 资源链接

- [OpenRouter API 文档](https://openrouter.ai/docs)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [部署笔记本](./DeerFlow-Deployment-Notebook.ipynb) (第 12 章)
- [完整开发指南](./COMPLETE_DEVELOPMENT_GUIDE.md)

## ⚡ 故障排查

**问题**: LangGraph 不启动
```
解决: cd backend && uv run --with langgraph-cli langgraph dev \
     --config $(pwd)/langgraph.json
```

**问题**: Gateway 无法导入 app 模块
```
解决: cd backend && $env:PYTHONPATH="." && uv run uvicorn ...
```

**问题**: 模型配置错误
```
解决: 检查 config.yaml 中的模型定义
     验证 OPENROUTER_API_KEY 环境变量
     确认 base_url 为 https://openrouter.ai/api/v1
```

---

**最后更新**: 2026-04-01  
**系统状态**: ✅ 生产就绪
