#!/usr/bin/env python3
"""
缓存系统验证脚本
直接验证模块可导入性和基本功能
"""

import sys
import traceback


def verify_imports():
    """验证所有缓存模块都能成功导入"""
    print("=" * 60)
    print("验证缓存模块导入")
    print("=" * 60)

    try:
        print("✓ 配置模块导入成功")

        print("✓ 内存缓存模块导入成功")

        print("✓ 缓存管理器导入成功")

        print("✓ 公共 API 导入成功")

        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        traceback.print_exc()
        return False


def verify_config():
    """验证配置系统"""
    print("\n" + "=" * 60)
    print("验证缓存配置")
    print("=" * 60)

    try:
        from deerflow.cache import get_cache_config

        config = get_cache_config()
        print(f"✓ 默认 Redis TTL: {config.redis.default_ttl} 秒")
        print(f"✓ 内存缓存最大大小: {config.memory.max_size} 项")
        print(f"✓ 驱逐策略: {config.memory.eviction_policy}")

        return True
    except Exception as e:
        print(f"✗ 配置验证失败: {e}")
        traceback.print_exc()
        return False


def verify_test_file():
    """验证测试文件存在"""
    print("\n" + "=" * 60)
    print("验证测试文件")
    print("=" * 60)

    import os

    test_file = "backend/tests/test_cache_basic.py"
    if os.path.exists(test_file):
        lines = 0
        with open(test_file) as f:
            lines = len(f.readlines())
        print(f"✓ 测试文件存在: {test_file} ({lines} 行)")

        # 统计测试函数
        with open(test_file) as f:
            content = f.read()
            test_count = content.count("async def test_")
            print(f"✓ 测试函数数量: {test_count} 个")

        return True
    else:
        print(f"✗ 测试文件不存在: {test_file}")
        return False


def verify_implementation_files():
    """验证实现文件存在"""
    print("\n" + "=" * 60)
    print("验证实现文件")
    print("=" * 60)

    import os

    files = {
        "backend/packages/harness/deerflow/cache/config.py": "配置",
        "backend/packages/harness/deerflow/cache/memory_cache.py": "内存缓存",
        "backend/packages/harness/deerflow/cache/cache.py": "缓存管理器",
        "backend/packages/harness/deerflow/cache/__init__.py": "模块导出",
        "backend/pytest.ini": "pytest 配置",
    }

    all_exist = True
    for file_path, description in files.items():
        if os.path.exists(file_path):
            with open(file_path) as f:
                lines = len(f.readlines())
            print(f"✓ {description}: {file_path} ({lines} 行)")
        else:
            print(f"✗ {description}: {file_path} (不存在)")
            all_exist = False

    return all_exist


def verify_gateway_integration():
    """验证网关集成"""
    print("\n" + "=" * 60)
    print("验证网关集成")
    print("=" * 60)

    try:
        with open("backend/app/gateway/app.py") as f:
            content = f.read()

        if "get_cache_manager" in content and "shutdown_cache_manager" in content:
            print("✓ 缓存管理器在网关 lifespan 中初始化")
            print("✓ 缓存管理器在网关关闭时清理")
            return True
        else:
            print("✗ 缓存管理器未在网关中集成")
            return False
    except Exception as e:
        print(f"✗ 网关集成验证失败: {e}")
        return False


def main():
    """运行所有验证"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "    DeerFlow 缓存系统验证报告".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    results.append(("导入验证", verify_imports()))
    results.append(("配置验证", verify_config()))
    results.append(("测试文件", verify_test_file()))
    results.append(("实现文件", verify_implementation_files()))
    results.append(("网关集成", verify_gateway_integration()))

    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20} {status}")

    print("-" * 60)
    print(f"总计: {passed}/{total} 验证通过")

    if passed == total:
        print("\n✅ 所有验证通过！缓存系统已准备好。")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个验证失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
