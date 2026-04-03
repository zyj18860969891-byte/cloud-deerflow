#!/usr/bin/env python3
"""
调试OpenAPI文档生成问题
检查订阅路由是否正确包含在OpenAPI文档中
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.gateway.app import app
from fastapi.openapi.utils import get_openapi
import json

def debug_openapi_generation():
    print("=== OpenAPI文档生成调试 ===")
    
    # 1. 检查路由注册
    print("\n1. 检查路由注册:")
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods - {'HEAD', 'OPTIONS'}),
                'name': getattr(route, 'name', 'N/A')
            })
    
    subscription_routes = [r for r in routes if '/subscription' in r['path']]
    print(f"找到 {len(subscription_routes)} 个订阅路由:")
    for route in subscription_routes:
        print(f"  - {route['path']} [{', '.join(route['methods'])}]")
    
    # 2. 检查OpenAPI文档生成
    print("\n2. 检查OpenAPI文档生成:")
    try:
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        print(f"OpenAPI文档生成成功")
        print(f"标题: {openapi_schema.get('title', 'N/A')}")
        print(f"版本: {openapi_schema.get('version', 'N/A')}")
        print(f"描述: {openapi_schema.get('description', 'N/A')}")
        
        # 3. 检查tags
        print("\n3. 检查OpenAPI Tags:")
        tags = openapi_schema.get('tags', [])
        print(f"找到 {len(tags)} 个tags:")
        for tag in tags:
            print(f"  - {tag.get('name', 'N/A')}: {tag.get('description', 'N/A')}")
        
        # 4. 检查订阅相关的路径
        print("\n4. 检查订阅相关的路径:")
        paths = openapi_schema.get('paths', {})
        subscription_paths = {k: v for k, v in paths.items() if '/subscription' in k}
        
        print(f"在OpenAPI文档中找到 {len(subscription_paths)} 个订阅路径:")
        for path, methods in subscription_paths.items():
            print(f"  - {path}: {list(methods.keys())}")
        
        # 5. 检查是否有订阅tag的引用
        print("\n5. 检查订阅tag的引用:")
        subscription_tag_found = any(tag.get('name') == 'subscription' for tag in tags)
        print(f"订阅tag在tags中: {'是' if subscription_tag_found else '否'}")
        
        # 6. 检查每个订阅路径是否有正确的tag
        print("\n6. 检查订阅路径的tag:")
        for path, methods in subscription_paths.items():
            for method, config in methods.items():
                tags = config.get('tags', [])
                print(f"  - {path} [{method}]: tags={tags}")
        
        # 7. 保存完整的OpenAPI文档用于分析
        with open('openapi_full.json', 'w', encoding='utf-8') as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
        print(f"\n完整OpenAPI文档已保存到: openapi_full.json")
        
        # 8. 检查app的router配置
        print("\n8. 检查app的router配置:")
        print(f"app.router.routes数量: {len(app.router.routes)}")
        
        for route in app.router.routes:
            if hasattr(route, 'path') and '/subscription' in route.path:
                print(f"  路由: {route.path}")
                if hasattr(route, 'include_router'):
                    print(f"    include_router: {route.include_router}")
                if hasattr(route, 'prefix'):
                    print(f"    prefix: {getattr(route, 'prefix', 'N/A')}")
                if hasattr(route, 'tags'):
                    print(f"    tags: {getattr(route, 'tags', 'N/A')}")
        
    except Exception as e:
        print(f"OpenAPI文档生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_openapi_generation()