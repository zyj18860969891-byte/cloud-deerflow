"""
工具管理 API 路由

提供工具的 CRUD 操作、执行历史查询、统计等功能
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict

from deerflow.auth import User, get_current_user
from deerflow.services.tool_service import (
    ToolCreate,
    ToolExecutionResponse,
    ToolResponse,
    ToolService,
    ToolUpdate,
    get_tool_service,
)

router = APIRouter(prefix="/tools", tags=["tools"])


# ========== 请求/响应模型 ==========

# 使用服务层定义的模型


class ToolListResponse(BaseModel):
    """工具列表响应"""

    tools: list[ToolResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ToolCreateRequest(ToolCreate):
    """创建工具请求（继承自服务层模型）"""

    pass


class ToolUpdateRequest(ToolUpdate):
    """更新工具请求（继承自服务层模型）"""

    pass


class ToolPermissionResponse(BaseModel):
    """工具权限响应模型"""

    id: int
    tool_id: int
    role: str
    can_execute: bool
    can_view: bool
    can_edit: bool
    can_delete: bool
    max_calls_per_day: int | None = None
    allowed_tenants: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ToolStats(BaseModel):
    """工具统计信息"""

    total_tools: int
    enabled_tools: int
    total_executions: int
    avg_execution_time: float
    success_rate: float
    most_used_tools: list[dict[str, Any]]
    recent_executions: list[ToolExecutionResponse]


# ========== 依赖注入 ==========


async def get_tool_service_with_user(
    current_user: User = Depends(get_current_user),
) -> ToolService:
    """获取工具服务（包含用户信息）"""
    # TODO: 基于用户角色过滤工具
    async for service in get_tool_service():
        return service


# ========== API 端点 ==========


@router.get("", response_model=ToolListResponse)
async def list_tools(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tool_type: str | None = Query(None),
    category: str | None = Query(None),
    enabled: bool | None = Query(None),
    search: str | None = Query(None),
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> ToolListResponse:
    """获取工具列表（支持分页和过滤）"""
    result = await tool_service.list_tools(
        page=page,
        page_size=page_size,
        tool_type=tool_type,
        category=category,
        enabled=enabled,
        search=search,
    )
    return result


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: int,
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> ToolResponse:
    """获取单个工具详情"""
    tool = await tool_service.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool {tool_id} not found")
    return tool


@router.post("", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    request: ToolCreateRequest,
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> ToolResponse:
    """创建新工具"""
    try:
        tool = await tool_service.create_tool(request)
        return tool
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: int,
    request: ToolUpdateRequest,
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> ToolResponse:
    """更新工具"""
    tool = await tool_service.update_tool(tool_id, request)
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool {tool_id} not found")
    return tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: int,
    hard_delete: bool = Query(False, description="是否硬删除（默认软删除）"),
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> None:
    """删除工具（软删除或硬删除）"""
    success = await tool_service.delete_tool(tool_id, hard_delete=hard_delete)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool {tool_id} not found")


@router.post("/{tool_id}/enable")
async def enable_tool(
    tool_id: int,
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> dict[str, Any]:
    """启用工具"""
    success = await tool_service.enable_tool(tool_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool {tool_id} not found")
    return {"message": f"Tool {tool_id} enabled"}


@router.post("/{tool_id}/disable")
async def disable_tool(
    tool_id: int,
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> dict[str, Any]:
    """禁用工具"""
    success = await tool_service.disable_tool(tool_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool {tool_id} not found")
    return {"message": f"Tool {tool_id} disabled"}


# ========== 执行历史 ==========


@router.get("/{tool_id}/executions", response_model=list[ToolExecutionResponse])
async def list_tool_executions(
    tool_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: str | None = Query(None),
    tenant_id: str | None = Query(None),
    status: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> list[ToolExecutionResponse]:
    """获取工具执行历史"""
    executions = await tool_service.list_executions(
        tool_id=tool_id,
        page=page,
        page_size=page_size,
        user_id=user_id,
        tenant_id=tenant_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    return executions


@router.get("/executions/{execution_id}", response_model=ToolExecutionResponse)
async def get_execution(
    execution_id: int,
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> ToolExecutionResponse:
    """获取单个执行记录详情"""
    execution = await tool_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Execution {execution_id} not found")
    return execution


# ========== 统计 ==========


@router.get("/stats/summary", response_model=ToolStats)
async def get_tools_summary(
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> ToolStats:
    """获取工具统计摘要"""
    return await tool_service.get_summary_stats()


@router.get("/stats/execution-trends")
async def get_execution_trends(
    days: int = Query(7, ge=1, le=90),
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> dict[str, Any]:
    """获取执行趋势数据（按天）"""
    trends = await tool_service.get_execution_trends(days=days)
    return {"trends": trends}


# ========== 权限管理 ==========


@router.get("/{tool_id}/permissions", response_model=list[ToolPermissionResponse])
async def list_tool_permissions(
    tool_id: int,
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> list[ToolPermissionResponse]:
    """获取工具权限列表"""
    permissions = await tool_service.list_permissions(tool_id)
    return permissions


@router.post("/{tool_id}/permissions", status_code=status.HTTP_201_CREATED)
async def add_tool_permission(
    tool_id: int,
    role: str = Query(..., description="角色名称"),
    can_execute: bool = Query(True),
    can_view: bool = Query(True),
    can_edit: bool = Query(False),
    can_delete: bool = Query(False),
    max_calls_per_day: int | None = Query(None),
    allowed_tenants: list[str] | None = Query(None),
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> dict[str, Any]:
    """添加工具权限"""
    permission = await tool_service.add_permission(
        tool_id=tool_id,
        role=role,
        can_execute=can_execute,
        can_view=can_view,
        can_edit=can_edit,
        can_delete=can_delete,
        max_calls_per_day=max_calls_per_day,
        allowed_tenants=allowed_tenants,
    )
    return {"message": "Permission added", "permission_id": permission.id}


@router.delete("/{tool_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tool_permission(
    tool_id: int,
    permission_id: int,
    tool_service: ToolService = Depends(get_tool_service_with_user),
) -> None:
    """删除工具权限"""
    success = await tool_service.remove_permission(tool_id, permission_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
