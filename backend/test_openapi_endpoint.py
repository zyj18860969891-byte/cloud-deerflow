#!/usr/bin/env python3
"""
测试OpenAPI端点
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gateway.app import app
import requests
import json

def test_openapi_endpoint():
    print("=== 测试OpenAPI端点 ===")
    
    # 启动服务器
    import uvicorn
    import threading
    import time
    
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8002, log_level="warning")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(5)
    
    try:
        # 测试OpenAPI文档端点
        print("\n1. 测试 /openapi.json 端点:")
        response = requests.get("http://127.0.0.1:8002/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            print(f"OpenAPI文档获取成功")
            print(f"标题: {openapi_data.get('info', {}).get('title', 'N/A')}")
            print(f"版本: {openapi_data.get('info', {}).get('version', 'N/A')}")
            
            # 检查tags
            tags = openapi_data.get('tags', [])
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
            paths = openapi_data.get('paths', {})
            subscription_paths = {k: v for k, v in paths.items() if '/subscription' in k}
            print(f"订阅路径数量: {len(subscription_paths)}")
            
            for path, methods in subscription_paths.items():
                for method, config in methods.items():
                    tags = config.get('tags', [])
                    print(f"{path} [{method}]: tags={tags}")
            
        else:
            print(f"OpenAPI文档获取失败: {response.status_code}")
        
        # 测试 /docs 端点
        print("\n2. 测试 /docs 端点:")
        response = requests.get("http://127.0.0.1:8002/docs")
        if response.status_code == 200:
            print(f"Swagger UI页面获取成功")
        else:
            print(f"Swagger UI页面获取失败: {response.status_code}")
        
        # 测试 /redoc 端点
        print("\n3. 测试 /redoc 端点:")
        response = requests.get("http://127.0.0.1:8002/redoc")
        if response.status_code == 200:
            print(f"ReDoc页面获取成功")
        else:
            print(f"ReDoc页面获取失败: {response.status_code}")
        
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        # 测试健康检查端点
        print("\n4. 测试 /health 端点:")
        try:
            response = requests.get("http://127.0.0.1:8002/health")
            if response.status_code == 200:
                print(f"健康检查成功: {response.json()}")
            else:
                print(f"健康检查失败: {response.status_code}")
        except Exception as e:
            print(f"健康检查失败: {e}")

if __name__ == "__main__":
    test_openapi_endpoint()