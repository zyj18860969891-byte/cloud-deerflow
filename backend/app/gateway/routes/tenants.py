"""
租户管理 API 路由
"""

from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.gateway.security.csrf import get_csrf_token_dependency

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


# ==================== 数据模型 ====================


class TenantBase(BaseModel):
    """租户基础模型"""

    name: str = Field(..., description="租户名称")
    description: str | None = Field(None, description="租户描述")


class TenantCreate(TenantBase):
    """创建租户请求"""

    pass


class TenantUpdate(BaseModel):
    """更新租户请求"""

    name: str | None = Field(None, description="租户名称")
    description: str | None = Field(None, description="租户描述")
    status: str | None = Field(None, description="租户状态", pattern="^(active|inactive)$")


class Tenant(TenantBase):
    """租户响应模型"""

    id: str = Field(..., description="租户ID")
    status: str = Field(default="active", description="租户状态")
    created_at: str = Field(..., description="创建时间")
    updated_at: str | None = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class TenantsResponse(BaseModel):
    """租户列表响应"""

    tenants: list[Tenant] = Field(..., description="租户列表")
    total: int = Field(..., description="租户总数")


# ==================== 临时存储（演示用） ====================

# 模拟的租户数据存储
MOCK_TENANTS = {
    "tenant-001": {
        "id": "tenant-001",
        "name": "企业 A",
        "description": "示例企业 A",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
    },
    "tenant-002": {
        "id": "tenant-002",
        "name": "企业 B",
        "description": "示例企业 B",
        "status": "active",
        "created_at": "2024-01-02T00:00:00Z",
    },
    "tenant-003": {
        "id": "tenant-003",
        "name": "企业 C",
        "description": "示例企业 C",
        "status": "inactive",
        "created_at": "2024-01-03T00:00:00Z",
    },
}

# 当前活跃租户（会话级别）
CURRENT_TENANT = "tenant-001"


# ==================== API 端点 ====================


@router.get("", response_model=TenantsResponse)
async def get_all_tenants():
    """
    获取所有租户列表

    Returns:
        TenantsResponse: 租户列表和总数
    """
    tenants = [Tenant(**tenant) for tenant in MOCK_TENANTS.values()]
    return TenantsResponse(tenants=tenants, total=len(tenants))


@router.get("/current", response_model=Tenant)
async def get_current_tenant():
    """
    获取当前活跃租户

    Returns:
        Tenant: 当前租户信息

    Raises:
        HTTPException: 当前租户不存在时
    """
    global CURRENT_TENANT

    if CURRENT_TENANT not in MOCK_TENANTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="当前租户不存在",
        )

    tenant_data = MOCK_TENANTS[CURRENT_TENANT]
    return Tenant(**tenant_data)


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str):
    """
    获取指定租户

    Args:
        tenant_id: 租户ID

    Returns:
        Tenant: 租户信息

    Raises:
        HTTPException: 租户不存在时
    """
    if tenant_id not in MOCK_TENANTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"租户 {tenant_id} 不存在",
        )

    tenant_data = MOCK_TENANTS[tenant_id]
    return Tenant(**tenant_data)


@router.post("/{tenant_id}/switch", response_model=Tenant)
async def switch_tenant(tenant_id: str, csrf_token: str = Depends(get_csrf_token_dependency)):
    """
    切换当前活跃租户

    Args:
        tenant_id: 目标租户ID

    Returns:
        Tenant: 新的当前租户信息

    Raises:
        HTTPException: 租户不存在或状态非活跃时
    """
    global CURRENT_TENANT

    if tenant_id not in MOCK_TENANTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"租户 {tenant_id} 不存在",
        )

    tenant_data = MOCK_TENANTS[tenant_id]

    # 检查租户是否活跃
    if tenant_data.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"租户 {tenant_id} 不可用（状态: {tenant_data.get('status')}）",
        )

    # 切换当前租户
    CURRENT_TENANT = tenant_id

    return Tenant(**tenant_data)


@router.post("", response_model=Tenant)
async def create_tenant(tenant: TenantCreate, csrf_token: str = Depends(get_csrf_token_dependency)):
    """
    创建新租户（仅限管理员）

    Args:
        tenant: 租户创建请求

    Returns:
        Tenant: 新建的租户信息
    """
    # 生成新的租户ID
    tenant_id = f"tenant-{len(MOCK_TENANTS) + 1:03d}"

    # 创建租户数据
    from datetime import datetime

    new_tenant = {
        "id": tenant_id,
        "name": tenant.name,
        "description": tenant.description,
        "status": "active",
        "created_at": datetime.now(UTC).isoformat(),
    }

    # 存储租户
    MOCK_TENANTS[tenant_id] = new_tenant

    return Tenant(**new_tenant)


@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant(tenant_id: str, tenant_update: TenantUpdate, csrf_token: str = Depends(get_csrf_token_dependency)):
    """
    更新租户信息（仅限管理员）

    Args:
        tenant_id: 租户ID
        tenant_update: 租户更新请求

    Returns:
        Tenant: 更新后的租户信息

    Raises:
        HTTPException: 租户不存在时
    """
    if tenant_id not in MOCK_TENANTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"租户 {tenant_id} 不存在",
        )

    # 更新租户数据
    from datetime import datetime

    tenant_data = MOCK_TENANTS[tenant_id]

    if tenant_update.name is not None:
        tenant_data["name"] = tenant_update.name
    if tenant_update.description is not None:
        tenant_data["description"] = tenant_update.description
    if tenant_update.status is not None:
        tenant_data["status"] = tenant_update.status

    tenant_data["updated_at"] = datetime.now(UTC).isoformat()

    return Tenant(**tenant_data)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(tenant_id: str, csrf_token: str = Depends(get_csrf_token_dependency)):
    """
    删除租户（仅限管理员）

    Args:
        tenant_id: 租户ID

    Raises:
        HTTPException: 租户不存在或为当前活跃租户时
    """
    global CURRENT_TENANT

    if tenant_id not in MOCK_TENANTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"租户 {tenant_id} 不存在",
        )

    # 不允许删除当前活跃租户
    if tenant_id == CURRENT_TENANT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除当前活跃租户",
        )

    # 删除租户
    del MOCK_TENANTS[tenant_id]
