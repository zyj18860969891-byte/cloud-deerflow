#!/usr/bin/env python3
"""Test OpenRouter API configuration"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


def test_openrouter_config():
    """Test OpenRouter configuration is properly loaded"""

    print("🔍 检查 OpenRouter 配置...")
    print("=" * 60)

    # Check API Key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print(f"✅ OPENROUTER_API_KEY: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("❌ OPENROUTER_API_KEY: 未配置")
        return False

    # Check Model
    model = os.getenv("OPENROUTER_MODEL")
    if model:
        print(f"✅ OPENROUTER_MODEL: {model}")
    else:
        print("❌ OPENROUTER_MODEL: 未配置")
        return False

    # Check Provider
    provider = os.getenv("LLM_PROVIDER")
    if provider == "openrouter":
        print(f"✅ LLM_PROVIDER: {provider}")
    else:
        print(f"❌ LLM_PROVIDER: {provider} (应为 openrouter)")
        return False

    # Check default model
    default_model = os.getenv("DEFAULT_MODEL")
    if default_model:
        print(f"✅ DEFAULT_MODEL: {default_model}")
    else:
        print("❌ DEFAULT_MODEL: 未配置")
        return False

    print("=" * 60)
    print("\n✅ 所有 OpenRouter 配置验证通过！")
    print("\n📋 配置信息汇总:")
    print(f"  • 提供商: {provider}")
    print(f"  • 模型: {model}")
    print(f"  • 温度: {os.getenv('MODEL_TEMPERATURE', '0.7')}")
    print(f"  • 最大令牌: {os.getenv('MODEL_MAX_TOKENS', '2048')}")

    # Try importing LangChain and test basic connectivity
    print("\n🧪 测试 LangChain 模块导入...")
    try:
        from langchain_openai import ChatOpenAI

        print("✅ LangChain ChatOpenAI 导入成功")

        # Test creating a client (won't actually call API without a message)
        client = ChatOpenAI(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1",
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
        )
        print("✅ OpenRouter 客户端初始化成功")
        print(f"   Model: {client.model_name}")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_openrouter_config()
    sys.exit(0 if success else 1)
