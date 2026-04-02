"""
认证模块

提供用户认证和授权功能
"""

from pydantic import BaseModel, Field


class User(BaseModel):
    """用户模型"""

    id: str = Field(..., description="用户唯一标识")
    username: str = Field(..., description="用户名")
    email: str | None = Field(None, description="用户邮箱")
    roles: list[str] = Field(default_factory=list, description="用户角色列表")
    tenant_id: str | None = Field(None, description="租户ID")
    is_active: bool = Field(default=True, description="是否激活")

    def has_role(self, role: str) -> bool:
        """检查用户是否拥有指定角色"""
        return role in self.roles

    def has_any_role(self, roles: list[str]) -> bool:
        """检查用户是否拥有任一指定角色"""
        return any(role in self.roles for role in roles)


# 模拟用户数据库（生产环境应该使用真实数据库）
_MOCK_USERS = {
    "admin": User(id="user_001", username="admin", email="admin@deerflow.com", roles=["admin", "user"], tenant_id="tenant_001", is_active=True),
    "user": User(id="user_002", username="user", email="user@deerflow.com", roles=["user"], tenant_id="tenant_001", is_active=True),
}


async def get_current_user() -> User:
    """获取当前用户（依赖注入用）

    注意：这是一个简化实现，生产环境应该：
    1. 从 JWT token 或 session 中解析用户信息
    2. 验证 token 有效性
    3. 从数据库查询用户完整信息
    4. 检查用户状态（是否激活、是否锁定等）
    """
    # 这里简化处理，返回模拟用户
    # 实际实现应该从请求头或 cookie 中提取 token 并验证

    # 为了测试，我们默认返回 admin 用户
    return _MOCK_USERS["admin"]


async def get_current_active_user() -> User:
    """获取当前激活的用户"""
    user = await get_current_user()
    if not user.is_active:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def verify_token(token: str) -> User | None:
    """验证 token 并返回用户（简化实现）"""
    # 这里应该实现真实的 token 验证逻辑
    # 例如：JWT 解码、签名验证、过期检查等

    if token == "admin_token":
        return _MOCK_USERS["admin"]
    elif token == "user_token":
        return _MOCK_USERS["user"]

    return None
