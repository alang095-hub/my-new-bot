"""FastAPI 主应用入口"""

# 标准库导入
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict

# 第三方库导入
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 安全中间件导入
from src.api.middleware.security import SecurityMiddleware

# API路由导入
from src.api.v1.admin.api import router as admin_router
from src.api.v1.monitoring.api import router as monitoring_router
from src.api.v1.statistics.api import router as statistics_router
from src.api.v1.webhooks.facebook import router as facebook_router

# 本地模块导入
from src.core.config import settings
from src.core.config.constants import (
    FACEBOOK_GRAPH_API_BASE_URL,
    LOG_FILE_BACKUP_COUNT,
    LOG_FILE_MAX_BYTES,
)
from src.core.database.connection import Base, engine, get_db
from src.core.logging.config import LocalTimeFormatter
from src.telegram.bot_handler import router as telegram_router

# 可选导入：Instagram模块
try:
    from src.api.v1.webhooks.instagram import router as instagram_router

    INSTAGRAM_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    INSTAGRAM_AVAILABLE = False
    instagram_router = APIRouter()

from src.api.v1.admin.ab_testing import router as ab_testing_router
from src.api.v1.admin.ads import router as ads_router
from src.api.v1.admin.deployment import router as deployment_router
from src.api.v1.admin.templates import router as templates_router

# 延迟导入的路由（在注册时导入）
from src.api.v1.monitoring.api_usage import router as api_usage_router

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
console_handler.setFormatter(
    LocalTimeFormatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
)
console_handler.addFilter(sensitive_filter)

# 文件日志处理器（生产环境）
file_handler = RotatingFileHandler(
    logs_dir / "app.log",
    maxBytes=LOG_FILE_MAX_BYTES,
    backupCount=LOG_FILE_BACKUP_COUNT,
    encoding="utf-8",
)
file_handler.setFormatter(
    LocalTimeFormatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
)
file_handler.addFilter(sensitive_filter)

# 配置根日志记录器
# 优化：减少httpx库的详细日志（降低CPU使用）
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])
logger = logging.getLogger(__name__)
logger.info(f"日志文件: {logs_dir / 'app.log'}")

# 创建 FastAPI 应用
app = FastAPI(
    title="多平台客服自动化系统",
    description="支持 Facebook、Instagram 等多平台的自动化客服流程",
    version="2.0.0",
    debug=settings.debug,
)

# 配置 CORS
cors_origins = getattr(settings, "cors_origins", None)
if cors_origins:
    if isinstance(cors_origins, str):
        allowed_origins = [origin.strip() for origin in cors_origins.split(",")]
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

# 添加安全中间件（在CORS之后，这样安全头会在所有响应上设置）
app.add_middleware(SecurityMiddleware)

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
app.include_router(ads_router)


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
        verify_token=settings.facebook_verify_token,
    )
    platform_manager.enable_platform("facebook")

    # 初始化Instagram平台（如果配置了）
    instagram_token = (
        getattr(settings, "instagram_access_token", None) or settings.facebook_access_token
    )
    instagram_verify = (
        getattr(settings, "instagram_verify_token", None) or settings.facebook_verify_token
    )
    instagram_user_id = getattr(settings, "instagram_user_id", None)

    if instagram_token:
        try:
            platform_manager.initialize_platform(
                platform_name="instagram",
                access_token=instagram_token,
                verify_token=instagram_verify,
                base_url=FACEBOOK_GRAPH_API_BASE_URL,
            )
            platform_manager.enable_platform("instagram")
            if instagram_user_id:
                logger.info(f"Instagram platform initialized (User ID: {instagram_user_id})")
            else:
                logger.warning(
                    "Instagram platform initialized but INSTAGRAM_USER_ID not configured - sending messages will fail"
                )
        except Exception as e:
            logger.error(f"Failed to initialize Instagram platform: {str(e)}", exc_info=True)

    # 创建数据库表（如果不存在）
    # 注意：在生产环境建议使用 Alembic 迁移
    try:
        from src.core.database import models, statistics_models

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.warning(f"Database table creation skipped (may already exist): {str(e)}")

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
        logger.warning(f"Failed to start summary notification scheduler: {str(e)}")

    # 启动自动回复调度器（每5分钟扫描未回复的产品消息）
    # 检查全局配置，只有 auto_reply.enabled = true 时才启动
    try:
        from src.config.page_settings import page_settings
        
        # 检查全局自动回复配置（不传page_id参数，返回全局配置）
        global_auto_reply_enabled = page_settings.is_auto_reply_enabled(page_id=None)
        
        if global_auto_reply_enabled:
            from src.auto_reply.auto_reply_scheduler import auto_reply_scheduler

            await auto_reply_scheduler.start()
            app.state.auto_reply_scheduler = auto_reply_scheduler
            logger.info(
                "Auto-reply scheduler started (scanning for unreplied product messages every 5 minutes)"
            )
        else:
            logger.info(
                "Auto-reply scheduler disabled (auto_reply.enabled = false in config)"
            )
    except Exception as e:
        logger.warning(f"Failed to check or start auto-reply scheduler: {str(e)}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("Shutting down...")

    # 停止摘要通知调度器
    if hasattr(app.state, "summary_scheduler"):
        try:
            scheduler = app.state.summary_scheduler
            await scheduler.close()
            logger.info("Summary notification scheduler stopped")
        except Exception as e:
            logger.warning(f"Failed to stop summary notification scheduler: {str(e)}")

    # 停止自动回复调度器
    if hasattr(app.state, "auto_reply_scheduler"):
        try:
            scheduler = app.state.auto_reply_scheduler
            await scheduler.stop()
            logger.info("Auto-reply scheduler stopped")
        except Exception as e:
            logger.warning(f"Failed to stop auto-reply scheduler: {str(e)}")


@app.get("/admin")
async def admin_page():
    """管理界面页面 - 同步并配置所有页面"""
    from fastapi.responses import HTMLResponse
    
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>无极项目 - 管理界面</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 28px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
        }
        .btn:active {
            transform: translateY(0);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
            display: none;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
            display: block;
        }
        .status-list {
            list-style: none;
            padding: 0;
        }
        .status-list li {
            padding: 8px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .status-list li.success {
            background: #d4edda;
            color: #155724;
        }
        .status-list li.error {
            background: #f8d7da;
            color: #721c24;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .links {
            margin-top: 20px;
        }
        .links a {
            display: inline-block;
            margin-right: 15px;
            color: #667eea;
            text-decoration: none;
            padding: 8px 16px;
            border: 2px solid #667eea;
            border-radius: 6px;
            transition: all 0.3s;
        }
        .links a:hover {
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 无极项目 - 管理界面</h1>
            <p>Facebook页面同步与配置管理</p>
        </div>

        <div class="section">
            <h2>同步并配置所有页面</h2>
            <p style="margin-bottom: 20px; color: #666;">
                自动同步所有Facebook页面Token，激活页面，并配置Messenger设置（Greeting、Get Started等）
            </p>
            
            <form id="syncForm">
                <div class="form-group">
                    <label for="telegramLink">Telegram链接（可选）</label>
                    <input type="text" id="telegramLink" placeholder="t.me/your_group">
                </div>
                
                <button type="submit" class="btn" id="syncBtn">
                    开始同步并配置
                </button>
            </form>

            <div id="status" class="status"></div>
        </div>

        <div class="section">
            <h2>查看执行状态</h2>
            <button type="button" class="btn" onclick="checkStatus()">刷新状态</button>
            <div id="statusResult" style="margin-top: 20px;"></div>
        </div>

        <div class="section">
            <h2>📋 FAQ配置内容（必须手动设置）</h2>
            <p style="margin-bottom: 20px; color: #666;">
                ⚠️ FAQ无法通过API自动配置，必须在Meta Business Suite中手动设置。<br>
                以下内容可直接复制粘贴到Meta Business Suite → 收件箱 → 自动化 → 常见问题
            </p>
            <button type="button" class="btn" onclick="loadFAQContent()" id="loadFAQBtn">
                加载FAQ内容
            </button>
            <div id="faqContent" style="margin-top: 20px;"></div>
        </div>

        <div class="section">
            <h2>快速链接</h2>
            <div class="links">
                <a href="/docs" target="_blank">API文档 (Swagger)</a>
                <a href="/redoc" target="_blank">API文档 (ReDoc)</a>
                <a href="/health" target="_blank">健康检查</a>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        
        document.getElementById('syncForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('syncBtn');
            const status = document.getElementById('status');
            const telegramLink = document.getElementById('telegramLink').value;
            
            btn.disabled = true;
            btn.innerHTML = '执行中...<span class="loading"></span>';
            status.className = 'status info';
            status.textContent = '任务已启动，正在后台执行...';
            
            try {
                const body = telegramLink ? { telegram_link: telegramLink } : {};
                const response = await fetch(API_BASE + '/admin/deployment/sync-and-setup-pages', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(body)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.className = 'status success';
                    status.innerHTML = `
                        <strong>✅ 任务已启动！</strong><br>
                        ${data.message}<br>
                        <small>${data.note}</small><br><br>
                        <strong>执行步骤：</strong>
                        <ul class="status-list">
                            ${data.steps.map(step => `<li>${step}</li>`).join('')}
                        </ul>
                        <p style="margin-top: 15px;">
                            <strong>提示：</strong> 请稍后点击"刷新状态"查看执行结果
                        </p>
                    `;
                } else {
                    status.className = 'status error';
                    status.innerHTML = `
                        <strong>⚠️ ${data.message || '请求失败'}</strong><br>
                        <small>${data.note || ''}</small>
                    `;
                }
            } catch (error) {
                status.className = 'status error';
                status.innerHTML = `<strong>❌ 错误：</strong> ${error.message}`;
            } finally {
                btn.disabled = false;
                btn.textContent = '开始同步并配置';
            }
        });
        
        async function checkStatus() {
            const resultDiv = document.getElementById('statusResult');
            resultDiv.innerHTML = '<p>检查中...</p>';
            
            try {
                const response = await fetch(API_BASE + '/admin/deployment/status');
                const data = await response.json();
                
                if (data.success && data.status) {
                    const syncStatus = data.status.sync_and_setup || {};
                    const pages = data.status.pages || {};
                    
                    let html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 6px;">';
                    html += '<h3 style="margin-bottom: 15px;">系统状态</h3>';
                    
                    // 同步和配置状态
                    const syncAndSetupStatus = data.status.sync_and_setup || {};
                    if (syncAndSetupStatus.running) {
                        html += '<p style="color: #0c5460;"><strong>🔄 同步和配置任务正在运行中...</strong></p>';
                    } else if (syncAndSetupStatus.last_result) {
                        const result = syncAndSetupStatus.last_result;
                        if (result.success) {
                            html += '<div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 6px; margin-bottom: 15px;">';
                            html += '<h4 style="color: #155724; margin-bottom: 10px;">✅ 同步和配置任务已完成</h4>';
                            html += `<p><strong>同步页面数:</strong> ${result.pages_synced || 0}</p>`;
                            html += `<p><strong>配置页面数:</strong> ${result.pages_configured || 0}</p>`;
                            
                            if (result.messenger_setup) {
                                const setup = result.messenger_setup;
                                html += `<h4 style="margin-top: 15px; margin-bottom: 10px;">Messenger设置结果:</h4>`;
                                html += `<p><strong>成功:</strong> ${setup.success || 0} 个页面</p>`;
                                html += `<p><strong>失败:</strong> ${setup.failed || 0} 个页面</p>`;
                                
                                if (setup.details && setup.details.length > 0) {
                                    html += '<h5 style="margin-top: 15px; margin-bottom: 10px;">详细结果:</h5>';
                                    html += '<table style="width: 100%; border-collapse: collapse; font-size: 13px;">';
                                    html += '<thead><tr style="background: #f8f9fa;"><th style="padding: 8px; border: 1px solid #dee2e6;">页面名称</th><th style="padding: 8px; border: 1px solid #dee2e6;">状态</th><th style="padding: 8px; border: 1px solid #dee2e6;">Greeting</th><th style="padding: 8px; border: 1px solid #dee2e6;">Get Started</th><th style="padding: 8px; border: 1px solid #dee2e6;">详情</th></tr></thead>';
                                    html += '<tbody>';
                                    setup.details.forEach(detail => {
                                        const statusColor = detail.status === 'success' ? '#28a745' : (detail.status === 'partial' ? '#ffc107' : '#dc3545');
                                        const statusIcon = detail.status === 'success' ? '✅' : (detail.status === 'partial' ? '⚠️' : '❌');
                                        const greetingIcon = detail.greeting ? '✅' : '❌';
                                        const getStartedIcon = detail.get_started ? '✅' : '❌';
                                        html += `<tr>`;
                                        html += `<td style="padding: 8px; border: 1px solid #dee2e6;">${detail.page_name || detail.page_id}</td>`;
                                        html += `<td style="padding: 8px; border: 1px solid #dee2e6; color: ${statusColor};">${statusIcon} ${detail.status}</td>`;
                                        html += `<td style="padding: 8px; border: 1px solid #dee2e6;">${greetingIcon}</td>`;
                                        html += `<td style="padding: 8px; border: 1px solid #dee2e6;">${getStartedIcon}</td>`;
                                        html += `<td style="padding: 8px; border: 1px solid #dee2e6; font-size: 12px;">${detail.message || detail.reason || '-'}</td>`;
                                        html += `</tr>`;
                                    });
                                    html += '</tbody></table>';
                                }
                            }
                            html += '</div>';
                        } else {
                            html += '<div style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 6px; margin-bottom: 15px;">';
                            html += '<h4 style="color: #721c24; margin-bottom: 10px;">❌ 同步和配置任务失败</h4>';
                            html += `<p><strong>错误:</strong> ${result.error || '未知错误'}</p>`;
                            html += '</div>';
                        }
                    }
                    
                    if (syncStatus.running) {
                        html += '<p style="color: #0c5460;"><strong>🔄 同步任务正在运行中...</strong></p>';
                    } else if (syncStatus.last_result) {
                        const result = syncStatus.last_result;
                        if (result.success) {
                            html += '<p style="color: #155724;"><strong>✅ 上次执行成功</strong></p>';
                            html += `<ul style="margin: 10px 0; padding-left: 20px;">`;
                            html += `<li>同步页面数: ${result.pages_synced || 0}</li>`;
                            html += `<li>配置页面数: ${result.pages_configured || 0}</li>`;
                            if (result.messenger_setup) {
                                html += `<li>Messenger设置成功: ${result.messenger_setup.success || 0}</li>`;
                                html += `<li>Messenger设置失败: ${result.messenger_setup.failed || 0}</li>`;
                            }
                            html += `</ul>`;
                        } else {
                            html += `<p style="color: #721c24;"><strong>❌ 上次执行失败:</strong> ${result.error || '未知错误'}</p>`;
                        }
                    } else {
                        html += '<p style="color: #666;">暂无执行记录</p>';
                    }
                    
                    // 页面状态
                    html += '<h4 style="margin-top: 20px; margin-bottom: 10px;">页面状态</h4>';
                    html += `<p>总页面数: <strong>${pages.total || 0}</strong></p>`;
                    html += `<p>已启用自动回复: <strong>${pages.enabled || 0}</strong></p>`;
                    html += `<p>已禁用自动回复: <strong>${pages.disabled || 0}</strong></p>`;
                    
                    html += '</div>';
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = '<p style="color: #721c24;">获取状态失败</p>';
                }
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: #721c24;">错误: ${error.message}</p>`;
            }
        }
        
        // 页面加载时自动检查状态
        window.addEventListener('load', () => {
            checkStatus();
        });
        
        // 加载FAQ内容
        async function loadFAQContent() {
            const btn = document.getElementById('loadFAQBtn');
            const contentDiv = document.getElementById('faqContent');
            
            btn.disabled = true;
            btn.textContent = '加载中...';
            contentDiv.innerHTML = '<p>正在加载FAQ内容...</p>';
            
            try {
                const response = await fetch(API_BASE + '/admin/deployment/faq-content');
                const data = await response.json();
                
                if (data.success && data.faqs) {
                    let html = '<div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin-top: 15px;">';
                    html += '<h3 style="margin-bottom: 15px;">📝 FAQ设置说明</h3>';
                    html += '<ol style="margin-bottom: 20px; padding-left: 20px;">';
                    data.instructions.forEach(instruction => {
                        html += `<li style="margin-bottom: 8px;">${instruction}</li>`;
                    });
                    html += '</ol>';
                    
                    html += '<h3 style="margin-bottom: 15px; margin-top: 25px;">📋 FAQ内容（共' + data.total_count + '个）</h3>';
                    data.faqs.forEach(faq => {
                        html += '<div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid #667eea;">';
                        html += `<h4 style="color: #667eea; margin-bottom: 10px;">Q${faq.number}: ${faq.question}</h4>`;
                        html += `<div style="background: #f8f9fa; padding: 12px; border-radius: 4px; margin-bottom: 10px; white-space: pre-wrap; font-family: monospace; font-size: 13px;">${faq.answer}</div>`;
                        html += `<button onclick="copyFAQ(${faq.number - 1})" style="background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 13px;">复制问题和答案</button>`;
                        html += '</div>';
                    });
                    html += '</div>';
                    
                    contentDiv.innerHTML = html;
                    
                    // 保存FAQ数据到全局变量
                    window.faqData = data.faqs;
                } else {
                    contentDiv.innerHTML = '<p style="color: red;">加载失败: ' + (data.message || '未知错误') + '</p>';
                }
            } catch (error) {
                contentDiv.innerHTML = '<p style="color: red;">❌ 加载失败: ' + error.message + '</p>';
            } finally {
                btn.disabled = false;
                btn.textContent = '加载FAQ内容';
            }
        }
        
        // 复制FAQ内容
        function copyFAQ(index) {
            if (window.faqData && window.faqData[index]) {
                const faq = window.faqData[index];
                const textToCopy = `Q${faq.number}: ${faq.question}\n\n${faq.answer}`;
                
                navigator.clipboard.writeText(textToCopy).then(() => {
                    alert('✅ 已复制到剪贴板！\\n\\n现在可以在Meta Business Suite中粘贴了。');
                }).catch(err => {
                    alert('复制失败，请手动复制。');
                    console.error('复制失败:', err);
                });
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


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
        "supported_platforms": platforms,
        "admin_ui": "/admin",
        "api_docs": "/docs",
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
                    "database": {"status": "unhealthy", "message": str(db_error)},
                    "service": {"status": "healthy", "message": "Service is running"},
                },
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Service is running but health check encountered an error",
            "error": str(e),
        }


@app.get("/health/simple", tags=["monitoring"])
async def simple_health_check() -> Dict[str, Any]:
    """简单的健康检查端点（完全不依赖数据库，用于负载均衡器）"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Service is running",
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
            "verify_token_preview": (
                verify_token[:10] + "..."
                if verify_token and len(verify_token) > 10
                else (verify_token or "None")
            ),
        }
    except Exception as e:
        # 生产环境不返回详细错误信息
        logger.error(f"Error in webhook config test: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e) if settings.debug else "Configuration error",
            "error_type": type(e).__name__ if settings.debug else "Error",
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
        return {"status": "ok", "token_length": len(token), "token_preview": token[:10] + "..."}
    except Exception as e:
        # 生产环境不返回详细错误信息
        logger.error(f"Error accessing settings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error" if not settings.debug else str(e),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host=settings.host, port=settings.port, reload=settings.debug)
