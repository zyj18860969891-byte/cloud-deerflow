#!/usr/bin/env python3
"""
测试Alipay配置是否正确读取
"""
import os
import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_alipay_config():
    """测试Alipay配置"""
    print("=" * 60)
    print("Alipay 配置验证测试")
    print("=" * 60)
    
    # 检查环境变量
    print("\n[1] 检查环境变量:")
    print("-" * 30)
    
    alipay_app_id = os.getenv("ALIPAY_APP_ID")
    alipay_pid = os.getenv("ALIPAY_PID")
    alipay_gateway_url = os.getenv("ALIPAY_GATEWAY_URL")
    alipay_private_key = os.getenv("ALIPAY_PRIVATE_KEY")
    alipay_public_key = os.getenv("ALIPAY_PUBLIC_KEY")
    
    print(f"ALIPAY_APP_ID: {'✅ 已设置' if alipay_app_id else '❌ 未设置'}")
    print(f"ALIPAY_PID: {'✅ 已设置' if alipay_pid else '❌ 未设置'}")
    print(f"ALIPAY_GATEWAY_URL: {'✅ 已设置' if alipay_gateway_url else '❌ 未设置'}")
    print(f"ALIPAY_PRIVATE_KEY: {'✅ 已设置' if alipay_private_key else '❌ 未设置'}")
    print(f"ALIPAY_PUBLIC_KEY: {'✅ 已设置' if alipay_public_key else '❌ 未设置'}")
    
    # 验证必要字段
    print("\n[2] 验证必要字段:")
    print("-" * 30)
    
    required_fields = {
        "ALIPAY_APP_ID": alipay_app_id,
        "ALIPAY_PID": alipay_pid,
        "ALIPAY_GATEWAY_URL": alipay_gateway_url,
        "ALIPAY_PRIVATE_KEY": alipay_private_key,
        "ALIPAY_PUBLIC_KEY": alipay_public_key
    }
    
    all_set = all(required_fields.values())
    
    if all_set:
        print("✅ 所有必要字段都已设置")
        print(f"   - APP_ID: {alipay_app_id}")
        print(f"   - PID: {alipay_pid}")
        print(f"   - GATEWAY_URL: {alipay_gateway_url}")
        print(f"   - PRIVATE_KEY: {'已设置' if alipay_private_key else '未设置'}")
        print(f"   - PUBLIC_KEY: {'已设置' if alipay_public_key else '未设置'}")
    else:
        print("❌ 部分必要字段未设置")
        missing = [k for k, v in required_fields.items() if not v]
        print(f"   缺少字段: {', '.join(missing)}")
    
    # 测试Alipay服务初始化
    print("\n[3] 测试Alipay服务初始化:")
    print("-" * 30)
    
    try:
        # 添加backend路径到Python路径
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'harness', 'deerflow'))
        
        from services.alipay_service import AlipayService
        
        # 创建Alipay服务实例
        alipay_service = AlipayService()
        
        if alipay_service.client:
            print("✅ Alipay服务初始化成功")
            print(f"   - APP_ID: {alipay_service.client.app_id}")
            print(f"   - GATEWAY_URL: {alipay_service.client.gateway_url}")
            print(f"   - SIGN_TYPE: {alipay_service.client.sign_type}")
        else:
            print("❌ Alipay服务初始化失败")
            
    except ImportError as e:
        print(f"❌ 导入Alipay服务失败: {e}")
    except Exception as e:
        print(f"❌ Alipay服务测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_alipay_config()