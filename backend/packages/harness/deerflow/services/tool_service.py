"""
工具管理服务

处理工具 CRUD、执行记录、统计等业务逻辑
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from deerflow.models.tool_models import (
    Tool,
    ToolExecution,
    ToolPermission,
    ToolVersion,
)
from deerflow.services.database import get_session as get_db_session

logger = logging.getLogger(__name__)


# ========== Pydantic 请求/响应模型 ==========


class ToolCreate(BaseModel):
    """创建工具请求模型"""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    tool_type: str = Field(..., pattern="^(custom|mcp|builtin|agent)$")
    category: str = Field(..., min_length=1, max_length=50)
    tags: dict[str, Any] | None = None
    module_path: str = Field(..., min_length=1)
    class_name: str = Field(..., min_length=1)
    args_schema: dict[str, Any] | None = None
    enabled: bool = True
    tenant_scoped: bool = False
    required_roles: list[str] | None = None
    version: str = "1.0.0"
    version_notes: str | None = None
    created_from_config: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ToolUpdate(BaseModel):
    """更新工具请求模型"""

    description: str | None = None
    tags: dict[str, Any] | None = None
    args_schema: dict[str, Any] | None = None
    enabled: bool | None = None
    tenant_scoped: bool | None = None
    required_roles: list[str] | None = None
    version: str | None = None
    version_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ToolResponse(BaseModel):
    """工具响应模型"""

    id: int
    name: str
    description: str
    tool_type: str
    category: str
    tags: dict[str, Any] | None = None
    enabled: bool
    is_builtin: bool
    is_system: bool
    version: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    last_executed_at: datetime | None = None
    avg_execution_time: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ToolExecutionResponse(BaseModel):
    """工具执行记录响应模型"""

    id: int
    tool_id: int
    tool_name: str
    thread_id: str | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    input_params: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    error: str | None = None
    execution_time: float | None = None
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    execution_metadata: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class ToolService:
    """工具管理服务"""

    def __init__(self, session: AsyncSession):
        """初始化服务

        Args:
            session: 数据库会话
        """
        self.session = session

    async def list_tools(
        self,
        page: int = 1,
        page_size: int = 20,
        tool_type: str | None = None,
        category: str | None = None,
        enabled: bool | None = None,
        search: str | None = None,
        include_deleted: bool = False,
    ) -> dict[str, Any]:
        """获取工具列表（分页和过滤）

        Args:
            page: 页码（从1开始）
            page_size: 每页大小
            tool_type: 工具类型过滤
            category: 分类过滤
            enabled: 启用状态过滤
            search: 搜索关键词（匹配名称和描述）
            include_deleted: 是否包含已删除的工具

        Returns:
            分页结果字典
        """
        # 构建查询
        stmt = select(Tool).where(Tool.deleted_at.is_(None) if not include_deleted else True)

        # 应用过滤条件
        if tool_type:
            stmt = stmt.where(Tool.tool_type == tool_type)
        if category:
            stmt = stmt.where(Tool.category == category)
        if enabled is not None:
            stmt = stmt.where(Tool.enabled == enabled)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where((Tool.name.ilike(search_pattern)) | (Tool.description.ilike(search_pattern)))

        # 总数查询
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self.session.scalar(count_stmt) or 0

        # 分页查询
        stmt = stmt.order_by(desc(Tool.created_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        tools = result.scalars().all()

        # 转换为响应模型
        tool_responses = [self._tool_to_response(tool) for tool in tools]

        return {
            "tools": tool_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_tool(self, tool_id: int) -> Tool | None:
        """获取单个工具详情

        Args:
            tool_id: 工具 ID

        Returns:
            Tool 对象或 None
        """
        stmt = select(Tool).where(Tool.id == tool_id, Tool.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_tool(self, request: Any) -> Tool:
        """创建新工具

        Args:
            request: 创建工具请求（Pydantic 模型）

        Returns:
            创建的 Tool 对象
        """
        # 检查名称是否已存在
        existing = await self.session.execute(select(Tool).where(Tool.name == request.name, Tool.deleted_at.is_(None)))
        if existing.scalar_one_or_none():
            raise ValueError(f"Tool with name '{request.name}' already exists")

        # 创建工具记录
        tool = Tool(
            name=request.name,
            description=request.description,
            tool_type=request.tool_type,
            category=request.category,
            tags=request.tags,
            module_path=request.module_path,
            class_name=request.class_name,
            args_schema=request.args_schema,
            enabled=request.enabled,
            tenant_scoped=request.tenant_scoped,
            required_roles=request.required_roles or [],
            version=request.version,
            version_notes=request.version_notes,
            created_from_config=request.created_from_config,
        )

        self.session.add(tool)
        await self.session.flush()

        # 创建初始版本记录
        await self._create_version(tool, getattr(request, "created_by", None))

        await self.session.commit()
        await self.session.refresh(tool)

        logger.info(f"Created tool: {tool.name} (id={tool.id})")
        return tool

    async def update_tool(self, tool_id: int, request: Any) -> Tool | None:
        """更新工具

        Args:
            tool_id: 工具 ID
            request: 更新请求（Pydantic 模型）

        Returns:
            更新后的 Tool 对象或 None（如果不存在）
        """
        tool = await self.get_tool(tool_id)
        if not tool:
            return None

        # 更新字段
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tool, field, value)

        tool.updated_at = datetime.now(UTC)

        # 如果有版本变更，创建版本记录
        if any(field in update_data for field in ["description", "args_schema", "module_path", "class_name"]):
            await self._create_version(tool, getattr(request, "created_by", None))

        await self.session.commit()
        await self.session.refresh(tool)

        logger.info(f"Updated tool: {tool.name} (id={tool.id})")
        return tool

    async def delete_tool(self, tool_id: int, hard_delete: bool = False) -> bool:
        """删除工具（软删除或硬删除）

        Args:
            tool_id: 工具 ID
            hard_delete: 是否硬删除

        Returns:
            是否成功删除
        """
        tool = await self.get_tool(tool_id)
        if not tool:
            return False

        if tool.is_system:
            raise ValueError("System tools cannot be deleted")

        if hard_delete:
            await self.session.delete(tool)
        else:
            tool.deleted_at = datetime.now(UTC)
            tool.enabled = False

        await self.session.commit()
        logger.info(f"Deleted tool: {tool.name} (id={tool.id}, hard={hard_delete})")
        return True

    async def enable_tool(self, tool_id: int) -> bool:
        """启用工具"""
        tool = await self.get_tool(tool_id)
        if not tool:
            return False

        tool.enabled = True
        tool.updated_at = datetime.now(UTC)
        await self.session.commit()
        return True

    async def disable_tool(self, tool_id: int) -> bool:
        """禁用工具"""
        tool = await self.get_tool(tool_id)
        if not tool:
            return False

        tool.enabled = False
        tool.updated_at = datetime.now(UTC)
        await self.session.commit()
        return True

    async def list_executions(
        self,
        tool_id: int,
        page: int = 1,
        page_size: int = 50,
        user_id: str | None = None,
        tenant_id: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[ToolExecution]:
        """获取工具执行历史"""
        stmt = select(ToolExecution).where(ToolExecution.tool_id == tool_id)

        if user_id:
            stmt = stmt.where(ToolExecution.user_id == user_id)
        if tenant_id:
            stmt = stmt.where(ToolExecution.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(ToolExecution.status == status)
        if start_date:
            stmt = stmt.where(ToolExecution.started_at >= start_date)
        if end_date:
            stmt = stmt.where(ToolExecution.started_at <= end_date)

        stmt = stmt.order_by(desc(ToolExecution.started_at))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_execution(self, execution_id: int) -> ToolExecution | None:
        """获取执行记录详情"""
        stmt = select(ToolExecution).where(ToolExecution.id == execution_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def record_execution(
        self,
        tool_id: int,
        input_params: dict[str, Any] | None = None,
        output: dict[str, Any] | None = None,
        error: str | None = None,
        status: str = "success",
        execution_time: float | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        thread_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ToolExecution:
        """记录工具执行

        Args:
            tool_id: 工具 ID
            input_params: 输入参数
            output: 输出结果
            error: 错误信息
            status: 执行状态
            execution_time: 执行耗时（秒）
            user_id: 用户 ID
            tenant_id: 租户 ID
            thread_id: 线程 ID
            metadata: 其他元数据

        Returns:
            创建的 ToolExecution 对象
        """
        execution = ToolExecution(
            tool_id=tool_id,
            input_params=input_params,
            output=output,
            error=error,
            status=status,
            execution_time=execution_time,
            user_id=user_id,
            tenant_id=tenant_id,
            thread_id=thread_id,
            metadata=metadata or {},
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC) if status in ["success", "failed", "cancelled"] else None,
        )

        self.session.add(execution)

        # 更新工具的统计信息
        tool = await self.get_tool(tool_id)
        if tool:
            tool.total_executions += 1
            if status == "success":
                tool.successful_executions += 1
            elif status == "failed":
                tool.failed_executions += 1
            tool.last_executed_at = datetime.now(UTC)

            # 更新平均执行时间
            if execution_time is not None:
                if tool.avg_execution_time is None:
                    tool.avg_execution_time = execution_time
                else:
                    # 移动平均
                    n = tool.total_executions
                    tool.avg_execution_time = (tool.avg_execution_time * (n - 1) + execution_time) / n

        await self.session.commit()
        await self.session.refresh(execution)

        return execution

    async def get_summary_stats(self) -> dict[str, Any]:
        """获取工具统计摘要"""
        # 工具总数
        total_tools = await self.session.scalar(select(func.count()).select_from(Tool).where(Tool.deleted_at.is_(None))) or 0

        # 启用工具数
        enabled_tools = await self.session.scalar(select(func.count()).select_from(Tool).where(Tool.deleted_at.is_(None), Tool.enabled == True)) or 0

        # 总执行次数
        total_executions = await self.session.scalar(select(func.count()).select_from(ToolExecution)) or 0

        # 成功率
        success_count = await self.session.scalar(select(func.count()).select_from(ToolExecution).where(ToolExecution.status == "success")) or 0
        success_rate = success_count / total_executions if total_executions > 0 else 0.0

        # 平均执行时间
        avg_time = await self.session.scalar(select(func.avg(ToolExecution.execution_time)).select_from(ToolExecution)) or 0.0

        # 最常用工具
        most_used_stmt = (
            select(Tool.id, Tool.name, Tool.description, func.count(ToolExecution.id).label("execution_count"))
            .join(ToolExecution, Tool.id == ToolExecution.tool_id)
            .where(Tool.deleted_at.is_(None))
            .group_by(Tool.id, Tool.name, Tool.description)
            .order_by(desc("execution_count"))
            .limit(10)
        )
        result = await self.session.execute(most_used_stmt)
        most_used = [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "execution_count": row.execution_count,
            }
            for row in result.all()
        ]

        # 最近执行
        recent_stmt = select(ToolExecution).order_by(desc(ToolExecution.started_at)).limit(10)
        result = await self.session.execute(recent_stmt)
        recent_executions = result.scalars().all()

        return {
            "total_tools": total_tools,
            "enabled_tools": enabled_tools,
            "total_executions": total_executions,
            "avg_execution_time": float(avg_time) if avg_time else None,
            "success_rate": success_rate,
            "most_used_tools": most_used,
            "recent_executions": recent_executions,
        }

    async def get_execution_trends(self, days: int = 7) -> list[dict[str, Any]]:
        """获取执行趋势数据（按天）

        Args:
            days: 查询天数

        Returns:
            按天聚合的执行数据列表
        """
        start_date = datetime.now(UTC) - timedelta(days=days)

        stmt = (
            select(
                func.date(ToolExecution.started_at).label("date"),
                func.count().label("total"),
                func.sum(func.case((ToolExecution.status == "success", 1), else_=0)).label("success"),
                func.sum(func.case((ToolExecution.status == "failed", 1), else_=0)).label("failed"),
            )
            .where(ToolExecution.started_at >= start_date)
            .group_by(func.date(ToolExecution.started_at))
            .order_by("date")
        )

        result = await self.session.execute(stmt)
        trends = []
        for row in result.all():
            total = row.total or 0
            success = row.success or 0
            trends.append(
                {
                    "date": row.date.isoformat(),
                    "total": total,
                    "success": success,
                    "failed": row.failed or 0,
                    "success_rate": success / total if total > 0 else 0.0,
                }
            )

        return trends

    async def list_permissions(self, tool_id: int) -> list[ToolPermission]:
        """获取工具权限列表"""
        stmt = select(ToolPermission).where(ToolPermission.tool_id == tool_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_permission(
        self,
        tool_id: int,
        role: str,
        can_execute: bool = True,
        can_view: bool = True,
        can_edit: bool = False,
        can_delete: bool = False,
        max_calls_per_day: int | None = None,
        allowed_tenants: list[str] | None = None,
    ) -> ToolPermission:
        """添加工具权限"""
        # 检查是否已存在
        existing = await self.session.execute(
            select(ToolPermission).where(
                ToolPermission.tool_id == tool_id,
                ToolPermission.role == role,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Permission for role '{role}' already exists")

        permission = ToolPermission(
            tool_id=tool_id,
            role=role,
            can_execute=can_execute,
            can_view=can_view,
            can_edit=can_edit,
            can_delete=can_delete,
            max_calls_per_day=max_calls_per_day,
            allowed_tenants=allowed_tenants or [],
        )

        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)

        return permission

    async def remove_permission(self, tool_id: int, permission_id: int) -> bool:
        """删除工具权限"""
        stmt = select(ToolPermission).where(
            ToolPermission.id == permission_id,
            ToolPermission.tool_id == tool_id,
        )
        result = await self.session.execute(stmt)
        permission = result.scalar_one_or_none()

        if not permission:
            return False

        await self.session.delete(permission)
        await self.session.commit()
        return True

    # ========== 私有辅助方法 ==========

    def _tool_to_response(self, tool: Tool) -> dict[str, Any]:
        """将 Tool 模型转换为响应字典"""
        return {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "tool_type": tool.tool_type,
            "category": tool.category,
            "tags": tool.tags,
            "enabled": tool.enabled,
            "is_builtin": tool.is_builtin,
            "is_system": tool.is_system,
            "version": tool.version,
            "total_executions": tool.total_executions,
            "successful_executions": tool.successful_executions,
            "failed_executions": tool.failed_executions,
            "last_executed_at": tool.last_executed_at,
            "avg_execution_time": tool.avg_execution_time,
            "created_at": tool.created_at,
            "updated_at": tool.updated_at,
        }

    async def _create_version(self, tool: Tool, created_by: str | None = None) -> ToolVersion:
        """创建工具版本快照"""
        version = ToolVersion(
            tool_id=tool.id,
            version=tool.version,
            version_notes=tool.version_notes,
            description=tool.description,
            module_path=tool.module_path,
            class_name=tool.class_name,
            args_schema=tool.args_schema,
            created_by=created_by,
        )

        self.session.add(version)
        return version


# ========== 依赖注入 ==========


async def get_tool_service():
    """获取工具服务实例（依赖注入工厂）

    这是一个异步生成器，用于FastAPI依赖注入。
    会自动处理会话的获取和关闭。
    """
    async for session in get_db_session():
        yield ToolService(session)
