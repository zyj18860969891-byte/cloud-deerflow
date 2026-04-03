#!/usr/bin/env python3
"""
简单的OpenAPI测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gateway.app import app
import uvicorn

if __name__ == "__main__":
    print("启动FastAPI应用测试...")
    print(f"应用标题: {app.title}")
    print(f"应用版本: {app.version}")
    print(f"应用描述: {app.description}")
    
    # 测试OpenAPI文档
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    print(f"\nOpenAPI文档生成成功")
    print(f"标题: {openapi_schema.get('info', {}).get('title', 'N/A')}")
    print(f"版本: {openapi_schema.get('info', {}).get('version', 'N/A')}")
    
    # 检查tags
    tags = openapi_schema.get('tags', [])
    print(f"Tags数量: {len(tags)}")
    
    subscription_tag = None
    for tag in tags:
        if tag.get('name') == 'subscription':
            subscription_tag = tag
            break
    
    if subscription_tag:
        print(f"找到subscription tag: {subscription_tag}")
    else:
        print("未找到subscription tag")
    
    # 检查路径
    paths = openapi_schema.get('paths', {})
    subscription_paths = {k: v for k, v in paths.items() if '/subscription' in k}
    print(f"订阅路径数量: {len(subscription_paths)}")
    
    for path, methods in subscription_paths.items():
        for method, config in methods.items():
            tags = config.get('tags', [])
            print(f"{path} [{method}]: tags={tags}")
    
    # 启动服务器测试
    print("\n启动服务器测试...")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")