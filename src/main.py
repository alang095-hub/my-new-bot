"""FastAPI 主应用入口"""
# 标准库导入
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from logging.handlers import RotatingFileHandler

# 第三方库导入
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# 本地模块导入
from src.core.config import settings
from src.core.config.constants import FACEBOOK_GRAPH_API_BASE_URL, LOG_FILE_MAX_BYTES, LOG_FILE_BACKUP_COUNT
from src.core.database.connection import get_db, engine, Base
from src.core.logging.config import LocalTimeFormatter

# API路由导入
from src.api.v1.admin.api import router as admin_router
from src.api.v1.monitoring.api import router as monitoring_router
from src.api.v1.statistics.api import router as statistics_router
from src.api.v1.webhooks.facebook import router as facebook_router
from src.telegram.bot_handler import router as telegram_router

# 可选导入：Instagram模块
try:
    from src.api.v1.webhooks.instagram import router as instagram_router
    INSTAGRAM_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    INSTAGRAM_AVAILABLE = False
    instagram_router = APIRouter()

# 延迟导入的路由（在注册时导入）
from src.api.v1.monitoring.api_usage import router as api_usage_router
from src.api.v1.admin.templates import router as templates_router
from src.api.v1.admin.ab_testing import router as ab_testing_router
from src.api.v1.admin.deployment import router as deployment_router

# 配置日志
project_root = Path(__file__).parent.parent
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)

# 导入敏感信息过滤器
from src.core.logging.config import SensitiveDataFilter

# 创建敏感信息过滤器
sensitive_filter = SensitiveDataFilter()

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(LocalTimeFormatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
console_handler.addFilter(sensitive_filter)

# 文件日志处理器（生产环境）
file_handler = RotatingFileHandler(
    logs_dir / "app.log",
    maxBytes=LOG_FILE_MAX_BYTES,
    backupCount=LOG_FILE_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setFormatter(LocalTimeFormatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
file_handler.addFilter(sensitive_filter)

# 配置根日志记录器
# 优化：减少httpx库的详细日志（降低CPU使用）
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger(__name__)
logger.info(f"日志文件: {logs_dir / 'app.log'}")

# 创建 FastAPI 应用
app = FastAPI(
    title="多平台客服自动化系统",
    description="支持 Facebook、Instagram 等多平台的自动化客服流程",
    version="2.0.0",
    debug=settings.debug
)

# 配置 CORS
cors_origins = getattr(settings, 'cors_origins', None)
if cors_origins:
    if isinstance(cors_origins, str):
        allowed_origins = [origin.strip() for origin in cors_origins.split(',')]
    else:
        allowed_origins = cors_origins
else:
    if settings.debug:
        allowed_origins = ["*"]
        logger.info("CORS允许所有来源 (*)，仅用于开发环境")
    else:
        allowed_origins = []
        logger.info(
            "生产环境未配置CORS_ORIGINS，将拒绝所有跨域请求。"
            "如果只有Webhook服务（无前端界面），可以忽略此提示。"
            "如果有前端管理界面，请通过环境变量CORS_ORIGINS配置允许的域名（逗号分隔）。"
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 注册路由
app.include_router(facebook_router)  # Facebook Webhook (兼容路由: /webhook)
if INSTAGRAM_AVAILABLE:
    app.include_router(instagram_router)  # Instagram Webhook (/instagram/webhook)
app.include_router(telegram_router)
app.include_router(statistics_router)
app.include_router(monitoring_router)
app.include_router(api_usage_router)
app.include_router(admin_router)
app.include_router(templates_router)
app.include_router(ab_testing_router)
app.include_router(deployment_router)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("Starting Multi-Platform Customer Service Automation System...")

    # 初始化平台管理器
    from src.platforms.manager import platform_manager

    # 初始化Facebook平台
    platform_manager.initialize_platform(
        platform_name="facebook",
        access_token=settings.facebook_access_token,
        verify_token=settings.facebook_verify_token
    )
    platform_manager.enable_platform("facebook")

    # 初始化Instagram平台（如果配置了）
    instagram_token = getattr(
        settings, 'instagram_access_token', None) or settings.facebook_access_token
    instagram_verify = getattr(
        settings, 'instagram_verify_token', None) or settings.facebook_verify_token
    instagram_user_id = getattr(settings, 'instagram_user_id', None)

    if instagram_token:
        try:
            platform_manager.initialize_platform(
                platform_name="instagram",
                access_token=instagram_token,
                verify_token=instagram_verify,
                base_url=FACEBOOK_GRAPH_API_BASE_URL
            )
            platform_manager.enable_platform("instagram")
            if instagram_user_id:
                logger.info(
                    f"Instagram platform initialized (User ID: {instagram_user_id})")
            else:
                logger.warning(
                    "Instagram platform initialized but INSTAGRAM_USER_ID not configured - sending messages will fail")
        except Exception as e:
            logger.error(
                f"Failed to initialize Instagram platform: {str(e)}", exc_info=True)

    # 创建数据库表（如果不存在）
    # 注意：在生产环境建议使用 Alembic 迁移
    try:
        from src.core.database import models
        from src.core.database import statistics_models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.warning(
            f"Database table creation skipped (may already exist): {str(e)}")

    # 列出已注册的平台（如果可用）
    try:
        from src.platforms.registry import registry
        logger.info(f"Registered platforms: {registry.list_platforms()}")
    except (ImportError, AttributeError):
        logger.info("Platform registry not available")

    # 启动摘要通知调度器
    try:
        from src.telegram.summary_scheduler import SummaryScheduler
        db = next(get_db())
        summary_scheduler = SummaryScheduler(db)
        summary_scheduler.start()
        app.state.summary_scheduler = summary_scheduler
        logger.info("Summary notification scheduler started")
    except Exception as e:
        logger.warning(
            f"Failed to start summary notification scheduler: {str(e)}")

    # 启动自动回复调度器（每5分钟扫描未回复的产品消息）
    try:
        from src.auto_reply.auto_reply_scheduler import auto_reply_scheduler
        await auto_reply_scheduler.start()
        app.state.auto_reply_scheduler = auto_reply_scheduler
        logger.info(
            "Auto-reply scheduler started (scanning for unreplied product messages every 5 minutes)")
    except Exception as e:
        logger.warning(
            f"Failed to start auto-reply scheduler: {str(e)}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("Shutting down...")

    # 停止摘要通知调度器
    if hasattr(app.state, 'summary_scheduler'):
        try:
            scheduler = app.state.summary_scheduler
            await scheduler.close()
            logger.info("Summary notification scheduler stopped")
        except Exception as e:
            logger.warning(
                f"Failed to stop summary notification scheduler: {str(e)}")

    # 停止自动回复调度器
    if hasattr(app.state, 'auto_reply_scheduler'):
        try:
            scheduler = app.state.auto_reply_scheduler
            await scheduler.stop()
            logger.info("Auto-reply scheduler stopped")
        except Exception as e:
            logger.warning(f"Failed to stop auto-reply scheduler: {str(e)}")


@app.get("/")
async def root() -> Dict[str, Any]:
    """根路径"""
    try:
        from src.platforms.registry import registry
        platforms = registry.list_platforms()
    except (ImportError, AttributeError):
        platforms = ["facebook"]

    return {
        "message": "多平台客服自动化系统",
        "version": "2.0.0",
        "status": "running",
        "supported_platforms": platforms
    }


@app.get("/health", tags=["monitoring"])
async def health_check() -> Dict[str, Any]:
    """增强的健康检查端点（不强制依赖数据库，避免502错误）"""
    try:
        from src.monitoring.health import health_checker
        try:
            db = next(get_db())
            return await health_checker.check_health(db)
        except Exception as db_error:
            logger.warning(f"Database connection failed in health check: {db_error}")
            return {
                "status": "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Service is running but database connection failed",
                "checks": {
                    "database": {
                        "status": "unhealthy",
                        "message": str(db_error)
                    },
                    "service": {
                        "status": "healthy",
                        "message": "Service is running"
                    }
                }
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Service is running but health check encountered an error",
            "error": str(e)
        }


@app.get("/health/simple", tags=["monitoring"])
async def simple_health_check() -> Dict[str, Any]:
    """简单的健康检查端点（完全不依赖数据库，用于负载均衡器）"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Service is running"
    }


@app.get("/metrics", tags=["monitoring"])
async def get_metrics() -> Dict[str, Any]:
    """获取性能指标"""
    from src.monitoring.health import health_checker
    return health_checker.get_metrics()


@app.get("/test/webhook-config", tags=["testing"])
async def test_webhook_config() -> Dict[str, Any]:
    """测试端点 - 检查 Webhook 配置（用于诊断）"""
    try:
        verify_token = settings.facebook_verify_token
        return {
            "status": "ok",
            "verify_token_configured": True,
            "verify_token_length": len(verify_token) if verify_token else 0,
            "verify_token_preview": verify_token[:10] + "..." if verify_token and len(verify_token) > 10 else (verify_token or "None")
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


@app.get("/test/simple", tags=["testing"])
async def test_simple():
    """最简单的测试端点"""
    return {"status": "ok", "message": "Simple test endpoint works"}


@app.get("/test/settings", tags=["testing"])
async def test_settings():
    """测试 settings 访问"""
    try:
        token = settings.facebook_verify_token
        return {
            "status": "ok",
            "token_length": len(token),
            "token_preview": token[:10] + "..."
        }
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
