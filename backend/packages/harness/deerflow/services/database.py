"""
数据库服务

提供 SQLAlchemy 异步会话管理和数据库初始化
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from deerflow.models.tool_models import Base


# 避免循环导入，延迟获取配置
def get_app_config():
    from app.gateway.app_config import get_app_config as _get_config

    return _get_config()


logger = logging.getLogger(__name__)

# 全局引擎和会话工厂
_engine = None
_async_session_factory = None


def get_engine():
    """获取或创建数据库引擎"""
    global _engine

    if _engine is None:
        config = get_app_config()
        database_url = config.database.url

        # 确保使用异步驱动
        if "+aiosqlite" not in database_url and database_url.startswith("sqlite"):
            # 如果是 SQLite 且没有指定异步驱动，添加 aiosqlite
            database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        elif "+asyncpg" not in database_url and database_url.startswith("postgresql"):
            # 如果是 PostgreSQL 且没有指定异步驱动，添加 asyncpg
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # 验证 URL 格式
        if not any(dialect in database_url for dialect in ["sqlite+aiosqlite", "postgresql+asyncpg"]):
            raise ValueError(f"Unsupported database URL for async: {database_url}. Use postgresql+asyncpg or sqlite+aiosqlite")

        # 根据数据库类型设置参数
        engine_kwargs = {"echo": config.database.echo}

        if "postgresql" in database_url:
            # PostgreSQL 支持连接池
            engine_kwargs.update(
                {
                    "pool_size": config.database.pool_size,
                    "max_overflow": config.database.max_overflow,
                }
            )
        # SQLite 使用 StaticPool，不需要连接池参数

        _engine = create_async_engine(database_url, **engine_kwargs)
        logger.info(f"Database engine created: {database_url}")

    return _engine


def get_session_factory():
    """获取或创建会话工厂"""
    global _async_session_factory

    if _async_session_factory is None:
        _async_session_factory = sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Async session factory created")

    return _async_session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入用）

    Yields:
        异步会话对象
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库（创建所有表）"""
    engine = get_engine()
    async with engine.begin() as conn:
        # 创建所有表（检查是否已存在）
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True))
        logger.info("Database tables created successfully")


async def drop_db():
    """删除所有表（危险操作）"""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")


async def close_db():
    """关闭数据库连接"""
    global _engine, _async_session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("Database connections closed")


class DatabaseService:
    """数据库服务封装"""

    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def initialize(self):
        """初始化数据库"""
        self.engine = get_engine()
        self.session_factory = get_session_factory()
        await init_db()

    async def shutdown(self):
        """关闭数据库"""
        await close_db()

    def get_session(self):
        """获取会话"""
        return get_session()


# 全局数据库服务实例
_db_service: DatabaseService | None = None


async def get_database_service() -> DatabaseService:
    """获取数据库服务实例"""
    global _db_service

    if _db_service is None:
        _db_service = DatabaseService()
        await _db_service.initialize()

    return _db_service
