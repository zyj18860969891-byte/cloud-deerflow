import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.gateway.config import get_gateway_config
from app.gateway.observability import (
    MetricsMiddleware,
    TracingMiddleware,
    get_metrics,
    get_tracer,
    start_metrics_server,
)
from app.gateway.routers import (
    agents,
    artifacts,
    channels,
    mcp,
    memory,
    models,
    skills,
    suggestions,
    threads,
    uploads,
)
from app.gateway.routes import (
    dashboard,  # 新增仪表板路由
    tenants,
    tools,  # 新增工具管理路由
    subscription,  # 新增订阅管理路由
)

# 直接导入database_optimization以避免循环导入
from app.gateway.routes.database_optimization import router as database_optimization_router
from app.gateway.security import (
    AuditLogger,
    AuditMiddleware,
    CSRFMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from deerflow.config.app_config import get_app_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""

    # Load config and check necessary environment variables at startup
    try:
        get_app_config()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        error_msg = f"Failed to load configuration during gateway startup: {e}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from e
    config = get_gateway_config()
    logger.info(f"Starting API Gateway on {config.host}:{config.port}")

    # Initialize database
    try:
        from deerflow.services.database import get_database_service

        db_service = await get_database_service()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")
        # Database is required for tool management, but we can continue without it
        db_service = None

    # Initialize cache manager
    try:
        from deerflow.cache import get_cache_config, get_cache_manager

        cache_config = get_cache_config()
        cache_manager = await get_cache_manager(cache_config)
        logger.info("Cache manager initialized successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize cache manager: {e}")
        # Cache is optional, so don't raise - just log the error
        cache_manager = None

    # Initialize cache warmer
    try:
        from deerflow.cache import get_cache_config, get_cache_warmer

        if cache_manager is not None:
            cache_config = get_cache_config()
            cache_warmer = await get_cache_warmer(cache_config.warming, cache_manager)

            # 注册预热回调
            try:
                from deerflow.cache.warmup_callbacks import register_all_warmup_callbacks

                await register_all_warmup_callbacks(cache_warmer, cache_manager)
            except ImportError:
                logger.warning("Warmup callbacks not found, skipping registration")

            await cache_warmer.start()
            logger.info("Cache warmer started successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize cache warmer: {e}")

    # Initialize cache metrics
    try:
        from deerflow.cache import get_cache_config, get_cache_metrics

        if cache_manager is not None:
            cache_config = get_cache_config()
            await get_cache_metrics(cache_config.metrics, cache_manager)
            logger.info("Cache metrics initialized successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize cache metrics: {e}")

    # NOTE: MCP tools initialization is NOT done here because:
    # 1. Gateway doesn't use MCP tools - they are used by Agents in the LangGraph Server
    # 2. Gateway and LangGraph Server are separate processes with independent caches
    # MCP tools are lazily initialized in LangGraph Server when first needed

    # Start IM channel service if any channels are configured
    try:
        from app.channels.service import start_channel_service

        channel_service = await start_channel_service()
        logger.info("Channel service started: %s", channel_service.get_status())
    except Exception:
        logger.exception("No IM channels configured or channel service failed to start")

    # Start Prometheus metrics server
    try:
        # Use synchronous start to avoid potential async issues
        metrics = get_metrics()
        metrics.start_server_sync()
        logger.info("Prometheus metrics server started on port %d", metrics.metrics_port)
    except Exception as e:
        logger.exception(f"Failed to start metrics server: {e}")

    yield

    # Shutdown cache metrics
    try:
        from deerflow.cache import shutdown_cache_metrics

        await shutdown_cache_metrics()
        logger.info("Cache metrics shut down successfully")
    except Exception:
        logger.exception("Failed to shutdown cache metrics")

    # Shutdown cache warmer
    try:
        from deerflow.cache import shutdown_cache_warmer

        await shutdown_cache_warmer()
        logger.info("Cache warmer shut down successfully")
    except Exception:
        logger.exception("Failed to shutdown cache warmer")

    # Shutdown cache manager
    try:
        from deerflow.cache import shutdown_cache_manager

        await shutdown_cache_manager()
        logger.info("Cache manager shut down successfully")
    except Exception:
        logger.exception("Failed to shutdown cache manager")

    # Shutdown database
    try:
        from deerflow.services.database import close_db

        await close_db()
        logger.info("Database shut down successfully")
    except Exception:
        logger.exception("Failed to shutdown database")

    # Stop channel service on shutdown
    try:
        from app.channels.service import stop_channel_service

        await stop_channel_service()
    except Exception:
        logger.exception("Failed to stop channel service")
    logger.info("Shutting down API Gateway")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """

    app = FastAPI(
        title="DeerFlow API Gateway",
        description="""
## DeerFlow API Gateway

API Gateway for DeerFlow - A LangGraph-based AI agent backend with sandbox execution capabilities.

### Features

- **Models Management**: Query and retrieve available AI models
- **MCP Configuration**: Manage Model Context Protocol (MCP) server configurations
- **Memory Management**: Access and manage global memory data for personalized conversations
- **Skills Management**: Query and manage skills and their enabled status
- **Artifacts**: Access thread artifacts and generated files
- **Health Monitoring**: System health check endpoints

### Architecture

LangGraph requests are handled by nginx reverse proxy.
This gateway provides custom endpoints for models, MCP configuration, skills, and artifacts.
        """,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "models",
                "description": "Operations for querying available AI models and their configurations",
            },
            {
                "name": "mcp",
                "description": "Manage Model Context Protocol (MCP) server configurations",
            },
            {
                "name": "memory",
                "description": "Access and manage global memory data for personalized conversations",
            },
            {
                "name": "skills",
                "description": "Manage skills and their configurations",
            },
            {
                "name": "artifacts",
                "description": "Access and download thread artifacts and generated files",
            },
            {
                "name": "uploads",
                "description": "Upload and manage user files for threads",
            },
            {
                "name": "threads",
                "description": "Manage DeerFlow thread-local filesystem data",
            },
            {
                "name": "agents",
                "description": "Create and manage custom agents with per-agent config and prompts",
            },
            {
                "name": "suggestions",
                "description": "Generate follow-up question suggestions for conversations",
            },
            {
                "name": "channels",
                "description": "Manage IM channel integrations (Feishu, Slack, Telegram)",
            },
            {
                "name": "tenants",
                "description": "Manage multi-tenant operations and tenant switching",
            },
            {
                "name": "subscription",
                "description": "Subscription management and payment processing",
            },
            {
                "name": "database-optimization",
                "description": "Database performance optimization and monitoring endpoints",
            },
            {
                "name": "health",
                "description": "Health check and system status endpoints",
            },
        ],
    )

    # CORS is handled by nginx - no need for FastAPI middleware

    # Initialize observability components
    metrics = get_metrics()
    tracer = get_tracer()

    # Add observability middlewares (order matters)
    # 1. Tracing - should be first to capture entire request lifecycle
    app.add_middleware(TracingMiddleware, service_name="deerflow-gateway")

    # 2. Metrics - collect HTTP metrics
    app.add_middleware(MetricsMiddleware, metrics=metrics)

    # Load security configuration
    from app.gateway.security.config import security_config

    # Add security middlewares (order matters)
    # 3. Security headers - adds security-related HTTP headers
    if security_config.security_headers_enabled:
        app.add_middleware(
            SecurityHeadersMiddleware,
            hsts_max_age=security_config.hsts_max_age,
            allow_frame=security_config.allow_frame,
            csp_policy=security_config.content_security_policy,
        )

    # 4. Rate limiting - protects against abuse
    if security_config.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            max_requests=security_config.rate_limit_requests,
            window_seconds=security_config.rate_limit_window_seconds,
            exclude_paths=security_config.rate_limit_exclude_paths,
        )

    # 5. CSRF protection - for state-changing operations
    if security_config.csrf_enabled:
        app.add_middleware(
            CSRFMiddleware,
            cookie_name=security_config.csrf_cookie_name,
            header_name=security_config.csrf_header_name,
            cookie_secure=security_config.csrf_cookie_secure,
            cookie_httponly=security_config.csrf_cookie_httponly,
            cookie_samesite=security_config.csrf_cookie_samesite,
            exempt_paths=security_config.csrf_exempt_paths,
        )

    # 6. Audit logging - logs all requests for security monitoring
    if security_config.audit_enabled:
        audit_logger = AuditLogger()
        app.add_middleware(
            AuditMiddleware,
            audit_logger=audit_logger,
            exclude_paths=security_config.audit_exclude_paths,
            log_request_body=security_config.audit_log_request_body,
            log_response_body=security_config.audit_log_response_body,
        )

    # 7. Tenant middleware (must be before routers)
    from app.gateway.middleware.tenant import TenantMiddleware

    app.add_middleware(TenantMiddleware)

    # Include routers
    # Models API is mounted at /api/models
    app.include_router(models.router)

    # MCP API is mounted at /api/mcp
    app.include_router(mcp.router)

    # Memory API is mounted at /api/memory
    app.include_router(memory.router)

    # Skills API is mounted at /api/skills
    app.include_router(skills.router)

    # Artifacts API is mounted at /api/threads/{thread_id}/artifacts
    app.include_router(artifacts.router)

    # Uploads API is mounted at /api/threads/{thread_id}/uploads
    app.include_router(uploads.router)

    # Thread cleanup API is mounted at /api/threads/{thread_id}
    app.include_router(threads.router)

    # Agents API is mounted at /api/agents
    app.include_router(agents.router)

    # Suggestions API is mounted at /api/threads/{thread_id}/suggestions
    app.include_router(suggestions.router)

    # Channels API is mounted at /api/channels
    app.include_router(channels.router)

    # Tenants API is mounted at /api/tenants
    app.include_router(tenants.router, prefix="")

    # Tools API is mounted at /api/tools
    app.include_router(tools.router, prefix="/api")

    # Dashboard API is mounted at /api/dashboard
    app.include_router(dashboard.router)

    # Subscription API is mounted at /api/subscription (router already has prefix)
    app.include_router(subscription.router)

    # Database Optimization API is mounted at /api/v1/database-optimization
    app.include_router(database_optimization_router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        """Health check endpoint.

        Returns:
            Service health status information.
        """
        return {"status": "healthy", "service": "deer-flow-gateway"}

    return app


# Create app instance for uvicorn
app = create_app()
