"""
工具管理数据模型

定义工具元数据、版本历史、执行记录等数据库表
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""

    pass


class Tool(Base):
    """工具元数据表"""

    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 工具类型和分类
    tool_type: Mapped[str] = mapped_column(String(50), index=True)  # custom, mcp, builtin, etc.
    category: Mapped[str] = mapped_column(String(50), index=True)  # utility, data, agent, etc.
    tags: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # 标签列表

    # 实现信息
    module_path: Mapped[str] = mapped_column(String(200), nullable=False)
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)
    args_schema: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # 参数模式

    # 配置
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否内置工具
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否系统工具（不可删除）

    # 权限和访问
    required_roles: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=list)  # 需要的角色列表
    tenant_scoped: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否租户级别

    # 统计信息（冗余存储，避免频繁聚合）
    total_executions: Mapped[int] = mapped_column(Integer, default=0)
    successful_executions: Mapped[int] = mapped_column(Integer, default=0)
    failed_executions: Mapped[int] = mapped_column(Integer, default=0)
    last_executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    avg_execution_time: Mapped[float | None] = mapped_column(Float, nullable=True)  # 平均执行时间（秒）

    # 版本管理
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    version_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_from_config: Mapped[str | None] = mapped_column(String(200), nullable=True)  # 来源配置文件名

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 软删除

    def __repr__(self) -> str:
        return f"<Tool(id={self.id}, name={self.name}, type={self.tool_type})>"


class ToolExecution(Base):
    """工具执行记录表"""

    __tablename__ = "tool_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tool_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # 执行上下文
    thread_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    tenant_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)

    # 执行参数和结果
    input_params: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    output: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 执行统计
    execution_time: Mapped[float | None] = mapped_column(Float, nullable=True)  # 执行耗时（秒）
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 状态
    status: Mapped[str] = mapped_column(String(20), default="running", index=True)  # running, success, failed, cancelled

    # 其他元数据
    execution_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return f"<ToolExecution(id={self.id}, tool_id={self.tool_id}, status={self.status})>"


class ToolVersion(Base):
    """工具版本历史表"""

    __tablename__ = "tool_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tool_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # 版本信息
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    version_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 变更内容（快照）
    description: Mapped[str] = mapped_column(Text, nullable=False)
    module_path: Mapped[str] = mapped_column(String(200), nullable=False)
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)
    args_schema: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # 谁创建的版本
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ToolVersion(id={self.id}, tool_id={self.tool_id}, version={self.version})>"


class ToolPermission(Base):
    """工具权限表（细粒度控制）"""

    __tablename__ = "tool_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tool_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # 权限配置
    role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 角色名称
    can_execute: Mapped[bool] = mapped_column(Boolean, default=True)
    can_view: Mapped[bool] = mapped_column(Boolean, default=True)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False)

    # 限制条件（可选）
    max_calls_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allowed_tenants: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=list)  # 允许的租户列表

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ToolPermission(id={self.id}, tool_id={self.tool_id}, role={self.role})>"
