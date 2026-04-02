#!/usr/bin/env python3
"""Test Gateway API endpoints"""

import json

import requests

BASE_URL = "http://localhost:2024"  # LangGraph API directly


def test_health():
    """Test health endpoint"""
    print("\n🏥 测试健康检查端点...")
    try:
        # Try LangGraph health endpoint
        response = requests.get(f"{BASE_URL}/ok", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health: {response.json()}")
            return True
        else:
            print(f"❌ Health 检查失败: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 LangGraph: {BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_create_thread():
    """Test creating a conversation thread"""
    print("\n💬 测试创建对话线程...")
    try:
        payload = {"metadata": {"test": True}}
        response = requests.post(f"{BASE_URL}/threads", json=payload, timeout=10)
        if response.status_code in (200, 201):
            data = response.json()
            print(f"✅ 线程创建成功: {data.get('id', data)}")
            return data.get("id") or data
        else:
            print(f"⚠️  线程创建响应: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_send_message(thread_id: str | dict):
    """Test sending a message via run creation"""
    print("\n📤 测试发送消息...")

    # Handle both string IDs and dict responses
    if isinstance(thread_id, dict):
        tid = thread_id.get("thread_id") or thread_id.get("id") or json.dumps(thread_id)
    else:
        tid = thread_id

    try:
        payload = {
            "assistant_id": "lead_agent",  # 使用正确的 agent 名称
            "input": {"messages": [{"role": "user", "content": "你好，请介绍一下你自己"}]},
            "metadata": {"test": True},
        }
        response = requests.post(f"{BASE_URL}/threads/{tid}/runs", json=payload, timeout=30)
        if response.status_code in (200, 201):
            data = response.json()
            print("✅ 消息发送成功 (run created)")
            print(f"   Run ID: {data.get('id', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            return data
        else:
            print(f"⚠️  消息响应: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_list_threads():
    """Test listing threads via search"""
    print("\n📋 测试获取线程列表...")
    try:
        # LangGraph uses POST /threads/search for listing
        payload = {"limit": 10}
        response = requests.post(f"{BASE_URL}/threads/search", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get("threads", [])) if isinstance(data, dict) else "未知"
            print(f"✅ 线程列表获取成功: {count} 个线程")
            return True
        else:
            print(f"⚠️  列表响应: {response.status_code}")
            print("   提示: 可能需要不同的查询参数")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    print("=" * 70)
    print("🚀 DeerFlow Gateway API 测试套件")
    print("=" * 70)

    # Test 1: Health check
    if not test_health():
        print("\n⚠️  警告: Gateway 似乎未运行")
        print("   请先运行: make dev 或 python -m deerflow.agents")
        return False

    # Test 2: Create thread
    thread = test_create_thread()
    if not thread:
        print("\n⚠️  线程创建失败，跳过后续测试")
        return False

    # Test 3: Send message
    result = test_send_message(thread)

    # Test 4: List threads
    test_list_threads()

    print("\n" + "=" * 70)
    print("✅ API 测试完成！")
    print("=" * 70)
    print("\n📖 接下来你可以:")
    print("   1. 在前端 UI 中测试完整流程")
    print("   2. 运行 pytest 进行单元测试")
    print("   3. 查看 API 文档: http://localhost:2024/docs")
    print("   4. 检查 LangSmith: https://smith.langchain.com/studio/")

    return True


if __name__ == "__main__":
    main()
