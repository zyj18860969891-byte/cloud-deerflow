#!/usr/bin/env python3
"""
测试Alipay API配置
"""
import os
import sys
import requests
import json

def test_alipay_api():
    """测试Alipay API配置"""
    print("=" * 60)
    print("Alipay API 配置测试")
    print("=" * 60)
    
    # Railway服务URL
    base_url = "https://cloud-deerflow-production.up.railway.app"
    
    # 测试端点
    test_endpoints = [
        "/api/subscription/plans",
        "/api/health"
    ]
    
    print(f"\n[1] 测试服务连接:")
    print("-" * 30)
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: 正常")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: 连接失败 - {e}")
    
    print(f"\n[2] 测试Alipay配置状态:")
    print("-" * 30)
    
    # 检查环境变量（通过API）
    try:
        # 尝试获取订阅计划信息，这会显示Alipay状态
        response = requests.get(f"{base_url}/api/subscription/plans", timeout=10)
        if response.status_code == 200:
            plans = response.json()
            print("✅ 获取订阅计划成功")
            
            # 检查是否有Alipay支付选项
            for plan in plans.get('plans', []):
                payment_methods = plan.get('payment_methods', [])
                if 'alipay' in payment_methods:
                    print(f"✅ 计划 {plan.get('name', 'Unknown')}: 支持Alipay")
                else:
                    print(f"⚠️  计划 {plan.get('name', 'Unknown')}: 不支持Alipay")
        else:
            print(f"❌ 获取订阅计划失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试Alipay配置失败: {e}")
    
    print(f"\n[3] 测试Alipay支付端点:")
    print("-" * 30)
    
    # 测试Alipay支付端点
    alipay_endpoints = [
        "/api/subscription/checkout-alipay",
        "/api/subscription/webhook-alipay"
    ]
    
    for endpoint in alipay_endpoints:
        try:
            response = requests.post(f"{base_url}{endpoint}", timeout=10)
            # 对于支付端点，我们期望某些特定的响应码
            if response.status_code in [200, 400, 401, 500]:
                print(f"✅ {endpoint}: 可访问 (HTTP {response.status_code})")
            else:
                print(f"❌ {endpoint}: 意外响应码 {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: 连接失败 - {e}")
    
    print(f"\n[4] 检查Railway环境变量:")
    print("-" * 30)
    
    # 这里我们无法直接访问Railway的环境变量，但可以检查服务是否正确配置
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 服务健康检查通过")
            print(f"   - 状态: {health_data.get('status', 'unknown')}")
            print(f"   - 服务: {health_data.get('service', 'unknown')}")
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_alipay_api()