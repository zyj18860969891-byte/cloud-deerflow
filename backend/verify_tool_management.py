#!/usr/bin/env python3
"""
工具管理功能验证脚本
"""

import asyncio

from deerflow.services.database import close_db, get_session, init_db
from deerflow.services.tool_service import ToolCreate, ToolService, ToolUpdate


async def main():
    """验证工具管理功能"""
    print("=" * 60)
    print("工具管理功能验证")
    print("=" * 60)

    session = None
    try:
        # 1. 初始化数据库
        print("\n1. 初始化数据库...")
        await init_db()
        print("   ✓ 数据库初始化成功")

        # 2. 获取数据库会话
        print("\n2. 获取数据库会话...")
        session_gen = get_session()
        session = await session_gen.__anext__()
        print("   ✓ 数据库会话获取成功")

        # 3. 创建工具服务
        print("\n3. 创建工具服务...")
        service = ToolService(session)
        print("   ✓ 工具服务创建成功")

        # 4. 创建测试工具
        print("\n4. 创建测试工具...")
        tool_data = ToolCreate(name="验证工具", description="这是一个验证工具", tool_type="custom", category="utility", module_path="deerflow.tools.custom_tools", class_name="CalculatorTool", enabled=True, version="1.0.0")
        tool = await service.create_tool(tool_data)
        print(f"   ✓ 创建工具成功: {tool.name} (ID: {tool.id})")

        # 5. 查询工具
        print("\n5. 查询工具...")
        retrieved = await service.get_tool(tool.id)
        assert retrieved is not None, "工具不存在"
        assert retrieved.name == tool_data.name, "工具名称不匹配"
        print(f"   ✓ 查询工具成功: {retrieved.name}")

        # 6. 更新工具
        print("\n6. 更新工具...")
        update_data = ToolUpdate(description="更新后的描述", enabled=False)
        updated = await service.update_tool(tool.id, update_data)
        assert updated.description == "更新后的描述", "更新失败"
        assert updated.enabled == False, "启用状态未更新"
        print("   ✓ 更新工具成功")

        # 7. 记录执行
        print("\n7. 记录工具执行...")
        execution = await service.record_execution(tool_id=tool.id, input_params={"expression": "1+1"}, output={"result": 2}, status="success", execution_time=0.05, user_id="test_user", thread_id="test_thread")
        print(f"   ✓ 记录执行成功: ID={execution.id}, 状态={execution.status}")

        # 8. 查询执行历史
        print("\n8. 查询执行历史...")
        executions = await service.list_executions(tool_id=tool.id)
        assert len(executions) > 0, "没有执行记录"
        print(f"   ✓ 查询执行历史成功: {len(executions)} 条记录")

        # 9. 获取统计
        print("\n9. 获取统计信息...")
        stats = await service.get_summary_stats()
        print(f"   ✓ 统计信息: 总工具数={stats['total_tools']}, 总执行数={stats['total_executions']}")

        # 10. 删除工具
        print("\n10. 删除工具...")
        success = await service.delete_tool(tool.id, hard_delete=True)
        assert success, "删除失败"
        print("   ✓ 删除工具成功")

        # 11. 关闭数据库
        print("\n11. 关闭数据库连接...")
        await close_db()
        print("   ✓ 数据库连接已关闭")

        print("\n" + "=" * 60)
        print("✅ 所有验证通过！工具管理功能正常工作")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        # 确保会话关闭
        if session is not None:
            try:
                await session.close()
            except:
                pass

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
