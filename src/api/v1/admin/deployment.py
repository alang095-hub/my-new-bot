"""部署管理API - 用于执行部署后的操作（无需终端）"""

import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.middleware.auth import AuthMiddleware
from src.config.page_settings import page_settings
from src.config.page_token_manager import page_token_manager
from src.core.config import settings
from src.core.database.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/deployment", tags=["deployment"])


class PageStatusUpdate(BaseModel):
    """页面状态更新请求"""

    page_id: str
    auto_reply_enabled: bool
    page_name: Optional[str] = None


class BatchPageStatusUpdate(BaseModel):
    """批量页面状态更新请求"""

    page_ids: List[str]
    auto_reply_enabled: bool


# 全局变量跟踪同步状态
_sync_status = {"running": False, "last_result": None}
_sync_and_setup_status = {"running": False, "last_result": None}


@router.post("/sync-pages")
async def sync_pages(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    同步所有页面Token（后台执行）

    这会：
    - 使用用户级Token自动获取所有页面的Token
    - 保存到 .page_tokens.json 文件
    - 自动为所有页面启用自动回复
    """
    try:
        user_token = settings.facebook_access_token

        if not user_token:
            raise HTTPException(
                status_code=400, detail="FACEBOOK_ACCESS_TOKEN 未配置")

        # 检查是否正在运行
        if _sync_status["running"]:
            return {
                "success": False,
                "message": "同步任务正在运行中，请稍后再试",
                "note": "使用 /admin/deployment/status 查看当前状态",
            }

        # 在后台执行同步（避免阻塞请求）
        async def sync_task():
            global _sync_status
            _sync_status["running"] = True
            try:
                count = await page_token_manager.sync_from_user_token(user_token)

                if count > 0:
                    # 自动为所有同步的页面启用自动回复
                    pages = page_token_manager.list_pages()
                    enabled_count = 0
                    for page_id, info in pages.items():
                        page_name = info.get("name", "未知")
                        if not page_settings.get_page_config(page_id).get("auto_reply_enabled"):
                            page_settings.add_page(
                                page_id, auto_reply_enabled=True, name=page_name)
                            enabled_count += 1

                    _sync_status["last_result"] = {
                        "success": True,
                        "pages_synced": count,
                        "pages_enabled": enabled_count,
                    }
                    logger.info(f"后台同步完成: {count} 个页面，启用 {enabled_count} 个页面")
                else:
                    _sync_status["last_result"] = {
                        "success": False,
                        "error": "同步失败，未找到任何页面",
                    }
                    logger.warning("同步失败，未找到任何页面")
            except Exception as e:
                _sync_status["last_result"] = {
                    "success": False, "error": str(e)}
                logger.error(f"后台同步失败: {str(e)}", exc_info=True)
            finally:
                _sync_status["running"] = False

        background_tasks.add_task(sync_task)

        return {
            "success": True,
            "message": "页面同步任务已启动，正在后台执行",
            "note": "请稍后查看日志或使用 /admin/deployment/status 检查状态",
        }
    except Exception as e:
        logger.error(f"启动同步任务失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启动同步任务失败: {str(e)}")


@router.get("/status")
async def get_deployment_status(db: Session = Depends(get_db)):
    """
    获取部署状态

    返回：
    - 页面配置状态
    - Token配置状态
    - 数据库连接状态
    """
    try:
        # 检查页面配置
        pages = page_token_manager.list_pages()
        page_count = len(pages)

        # 检查自动回复状态
        enabled_pages = []
        disabled_pages = []
        for page_id in pages.keys():
            if page_settings.is_auto_reply_enabled(page_id):
                enabled_pages.append(page_id)
            else:
                disabled_pages.append(page_id)

        # 检查Token配置
        has_default_token = page_token_manager.get_token() is not None

        # 检查数据库连接
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db_connected = True
        except Exception as e:
            logger.warning(f"Database connection check failed: {str(e)}")
            db_connected = False

        return {
            "success": True,
            "status": {
                "database": {
                    "connected": db_connected,
                    "status": "healthy" if db_connected else "unhealthy",
                },
                "pages": {
                    "total": page_count,
                    "enabled": len(enabled_pages),
                    "disabled": len(disabled_pages),
                    "pages": [
                        {
                            "id": page_id,
                            "name": pages[page_id].get("name", "未知"),
                            "token_configured": page_token_manager.get_token(page_id) is not None,
                            "auto_reply_enabled": page_settings.is_auto_reply_enabled(page_id),
                        }
                        for page_id in pages.keys()
                    ],
                },
                "token": {
                    "default_token_configured": has_default_token,
                    "token_type": "USER" if has_default_token else "NONE",
                },
                "sync": {
                    "running": _sync_status["running"],
                    "last_result": _sync_status["last_result"],
                },
                "sync_and_setup": {
                    "running": _sync_and_setup_status["running"],
                    "last_result": _sync_and_setup_status["last_result"],
                },
            },
        }
    except Exception as e:
        logger.error(f"获取部署状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取部署状态失败: {str(e)}")


@router.get("/pages/{page_id}")
async def get_page_config(page_id: str, db: Session = Depends(get_db)):
    """
    获取单个页面的详细配置信息

    返回：
    - 页面基本信息
    - Token配置状态
    - 自动回复配置
    - Messenger设置状态
    """
    try:
        # 检查页面是否存在
        pages = page_token_manager.list_pages()
        if page_id not in pages:
            raise HTTPException(
                status_code=404, detail=f"页面 {page_id} 未找到，请先同步页面")

        page_info = pages[page_id]
        page_name = page_info.get("name", "未知")

        # 获取Token配置
        page_token = page_token_manager.get_token(page_id)
        token_configured = page_token is not None

        # 获取页面设置
        page_config = page_settings.get_page_config(page_id)
        auto_reply_enabled = page_settings.is_auto_reply_enabled(page_id)
        default_reply = page_settings.get_page_default_reply(page_id)

        # 尝试获取Messenger配置（如果Token可用）
        messenger_config = {}
        if page_token:
            try:
                import httpx
                from src.core.config.constants import FACEBOOK_GRAPH_API_BASE_URL

                # 使用 me 端点查询Messenger配置
                url = f"{FACEBOOK_GRAPH_API_BASE_URL}/me/messenger_profile"
                params = {
                    "access_token": page_token,
                    "fields": "get_started,persistent_menu,greeting,whitelisted_domains"
                }

                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        messenger_config = response.json()
                    else:
                        # 如果失败，尝试使用页面ID
                        url2 = f"{FACEBOOK_GRAPH_API_BASE_URL}/{page_id}/messenger_profile"
                        response2 = await client.get(url2, params=params)
                        if response2.status_code == 200:
                            messenger_config = response2.json()
            except Exception as e:
                logger.warning(f"获取页面 {page_id} 的Messenger配置失败: {str(e)}")
                messenger_config = {"error": str(e)}

        # 获取配置管理器中的配置信息（如果存在）
        config_info = {}
        try:
            from src.project.wuji.config_manager import config_manager

            config_info = config_manager.get_config_info(page_id) or {}
        except Exception:
            pass

        return {
            "success": True,
            "page": {
                "id": page_id,
                "name": page_name,
                "token_configured": token_configured,
                "token_exists": bool(page_token),
                "auto_reply": {
                    "enabled": auto_reply_enabled,
                    "default_reply": default_reply,
                },
                "page_settings": page_config,
                "messenger_config": {
                    "greeting": messenger_config.get("greeting", []),
                    "get_started": messenger_config.get("get_started", {}),
                    "persistent_menu": messenger_config.get("persistent_menu", []),
                    "whitelisted_domains": messenger_config.get("whitelisted_domains", []),
                },
                "config_status": config_info.get("status", "unknown"),
                "last_updated": page_info.get("updated_at"),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取页面配置失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取页面配置失败: {str(e)}")


@router.put("/pages/{page_id}/enable")
async def enable_page(
    page_id: str,
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    启用指定页面的自动回复

    Args:
        page_id: 页面ID
    """
    try:
        pages = page_token_manager.list_pages()
        if page_id not in pages:
            raise HTTPException(
                status_code=404, detail=f"页面 {page_id} 未找到，请先同步页面")

        page_name = pages[page_id].get("name", "未知")
        page_settings.add_page(
            page_id, auto_reply_enabled=True, name=page_name)

        logger.info(f"通过API启用页面自动回复: {page_id} ({page_name})")

        return {
            "success": True,
            "message": f"页面 {page_name} (ID: {page_id}) 的自动回复已启用",
            "page_id": page_id,
            "page_name": page_name,
            "auto_reply_enabled": True,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启用页面自动回复失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启用页面自动回复失败: {str(e)}")


@router.put("/pages/{page_id}/disable")
async def disable_page(
    page_id: str,
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    禁用指定页面的自动回复

    Args:
        page_id: 页面ID
    """
    try:
        pages = page_token_manager.list_pages()
        if page_id not in pages:
            raise HTTPException(
                status_code=404, detail=f"页面 {page_id} 未找到，请先同步页面")

        page_name = pages[page_id].get("name", "未知")
        page_settings.add_page(
            page_id, auto_reply_enabled=False, name=page_name)

        logger.info(f"通过API禁用页面自动回复: {page_id} ({page_name})")

        return {
            "success": True,
            "message": f"页面 {page_name} (ID: {page_id}) 的自动回复已禁用",
            "page_id": page_id,
            "page_name": page_name,
            "auto_reply_enabled": False,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"禁用页面自动回复失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"禁用页面自动回复失败: {str(e)}")


@router.put("/pages/{page_id}/toggle")
async def toggle_page(
    page_id: str,
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    切换指定页面的自动回复状态（启用↔禁用）

    Args:
        page_id: 页面ID
    """
    try:
        pages = page_token_manager.list_pages()
        if page_id not in pages:
            raise HTTPException(
                status_code=404, detail=f"页面 {page_id} 未找到，请先同步页面")

        page_name = pages[page_id].get("name", "未知")
        current_status = page_settings.is_auto_reply_enabled(page_id)
        new_status = not current_status

        page_settings.add_page(
            page_id, auto_reply_enabled=new_status, name=page_name)

        status_text = "启用" if new_status else "禁用"
        logger.info(
            f"通过API切换页面自动回复状态: {page_id} ({page_name}) -> {status_text}")

        return {
            "success": True,
            "message": f"页面 {page_name} (ID: {page_id}) 的自动回复已{status_text}",
            "page_id": page_id,
            "page_name": page_name,
            "auto_reply_enabled": new_status,
            "previous_status": current_status,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换页面自动回复状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"切换页面自动回复状态失败: {str(e)}")


@router.put("/pages/batch-update")
async def batch_update_pages(
    update: BatchPageStatusUpdate,
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    批量更新多个页面的自动回复状态

    Args:
        update: 批量更新请求，包含页面ID列表和目标状态
    """
    try:
        pages = page_token_manager.list_pages()
        results = []
        success_count = 0
        failed_count = 0

        for page_id in update.page_ids:
            if page_id not in pages:
                results.append(
                    {"page_id": page_id, "success": False, "error": "页面未找到"})
                failed_count += 1
                continue

            try:
                page_name = pages[page_id].get("name", "未知")
                page_settings.add_page(
                    page_id, auto_reply_enabled=update.auto_reply_enabled, name=page_name
                )
                results.append(
                    {
                        "page_id": page_id,
                        "page_name": page_name,
                        "success": True,
                        "auto_reply_enabled": update.auto_reply_enabled,
                    }
                )
                success_count += 1
            except Exception as e:
                results.append(
                    {"page_id": page_id, "success": False, "error": str(e)})
                failed_count += 1

        status_text = "启用" if update.auto_reply_enabled else "禁用"
        logger.info(
            f"通过API批量{status_text}页面自动回复: 成功 {success_count} 个，失败 {failed_count} 个"
        )

        return {
            "success": True,
            "message": f"批量{status_text}完成：成功 {success_count} 个，失败 {failed_count} 个",
            "total": len(update.page_ids),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results,
        }
    except Exception as e:
        logger.error(f"批量更新页面状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量更新页面状态失败: {str(e)}")


@router.put("/pages/enable-all")
async def enable_all_pages(
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    启用所有页面的自动回复
    """
    try:
        pages = page_token_manager.list_pages()
        if not pages:
            return {"success": False, "message": "未找到任何页面，请先同步页面"}

        enabled_count = 0
        for page_id, info in pages.items():
            page_name = info.get("name", "未知")
            if not page_settings.is_auto_reply_enabled(page_id):
                page_settings.add_page(
                    page_id, auto_reply_enabled=True, name=page_name)
                enabled_count += 1

        logger.info(
            f"通过API启用所有页面自动回复: 共 {len(pages)} 个页面，新启用 {enabled_count} 个"
        )

        return {
            "success": True,
            "message": f"已启用所有页面的自动回复（共 {len(pages)} 个页面，新启用 {enabled_count} 个）",
            "total_pages": len(pages),
            "newly_enabled": enabled_count,
            "already_enabled": len(pages) - enabled_count,
        }
    except Exception as e:
        logger.error(f"启用所有页面自动回复失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启用所有页面自动回复失败: {str(e)}")


@router.put("/pages/disable-all")
async def disable_all_pages(
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    禁用所有页面的自动回复
    """
    try:
        pages = page_token_manager.list_pages()
        if not pages:
            return {"success": False, "message": "未找到任何页面，请先同步页面"}

        disabled_count = 0
        for page_id, info in pages.items():
            page_name = info.get("name", "未知")
            if page_settings.is_auto_reply_enabled(page_id):
                page_settings.add_page(
                    page_id, auto_reply_enabled=False, name=page_name)
                disabled_count += 1

        logger.info(
            f"通过API禁用所有页面自动回复: 共 {len(pages)} 个页面，新禁用 {disabled_count} 个"
        )

        return {
            "success": True,
            "message": f"已禁用所有页面的自动回复（共 {len(pages)} 个页面，新禁用 {disabled_count} 个）",
            "total_pages": len(pages),
            "newly_disabled": disabled_count,
            "already_disabled": len(pages) - disabled_count,
        }
    except Exception as e:
        logger.error(f"禁用所有页面自动回复失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"禁用所有页面自动回复失败: {str(e)}")


@router.get("/verify-token")
async def verify_token(
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    验证当前Token类型和权限

    返回Token验证结果
    """
    try:
        import httpx

        token = settings.facebook_access_token

        if not token:
            raise HTTPException(
                status_code=400, detail="FACEBOOK_ACCESS_TOKEN 未配置")

        # 检查Token类型
        app_id = settings.facebook_app_id
        app_secret = settings.facebook_app_secret

        if not app_id or not app_secret:
            raise HTTPException(
                status_code=400, detail="FACEBOOK_APP_ID 或 FACEBOOK_APP_SECRET 未配置"
            )

        from src.core.config.constants import FACEBOOK_DEBUG_TOKEN_URL, FACEBOOK_ME_ACCOUNTS_URL

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 检查Token信息
            debug_url = FACEBOOK_DEBUG_TOKEN_URL
            debug_params = {"input_token": token,
                            "access_token": f"{app_id}|{app_secret}"}
            debug_response = await client.get(debug_url, params=debug_params)

            if debug_response.status_code != 200:
                return {
                    "success": False,
                    "error": "Token验证失败",
                    "details": debug_response.json(),
                }

            debug_data = debug_response.json().get("data", {})
            token_type = debug_data.get("type", "未知")

            # 尝试获取页面列表
            pages_url = FACEBOOK_ME_ACCOUNTS_URL
            pages_params = {"access_token": token}
            pages_response = await client.get(pages_url, params=pages_params)

            pages_count = 0
            can_manage_pages = False

            if pages_response.status_code == 200:
                pages_data = pages_response.json()
                pages_count = len(pages_data.get("data", []))
                can_manage_pages = True

            return {
                "success": True,
                "token_type": token_type,
                "can_manage_pages": can_manage_pages,
                "pages_count": pages_count,
                "is_user_token": token_type == "USER",
                "message": (
                    "用户级Token，可以管理多个页面"
                    if can_manage_pages
                    else "页面级Token，只能管理单个页面"
                ),
            }
    except Exception as e:
        logger.error(f"验证Token失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"验证Token失败: {str(e)}")


class SyncAndSetupRequest(BaseModel):
    """同步并配置所有页面请求"""
    telegram_link: Optional[str] = None


@router.post("/sync-and-setup-pages")
async def sync_and_setup_pages(
    request: SyncAndSetupRequest = Body(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    同步所有页面Token并配置Messenger设置（后台执行）

    这会：
    - 同步所有Facebook页面Token
    - 激活所有页面（auto_reply_enabled=false，但页面已激活）
    - 配置所有页面的Messenger设置（Greeting Message、Get Started Button）
    - 为Meta Business Suite自动回复做准备

    请求参数（可选）:
    - telegram_link: Telegram群组链接（用于Persistent Menu）
    """
    try:
        user_token = settings.facebook_access_token

        if not user_token:
            raise HTTPException(
                status_code=400, detail="FACEBOOK_ACCESS_TOKEN 未配置")

        # 检查是否正在运行
        if _sync_and_setup_status["running"]:
            return {
                "success": False,
                "message": "同步和配置任务正在运行中，请稍后再试",
                "note": "使用 /admin/deployment/status 查看当前状态",
            }

        telegram_link = request.telegram_link if request else None

        # 在后台执行同步和配置（避免阻塞请求）
        async def sync_and_setup_task():
            global _sync_and_setup_status
            _sync_and_setup_status["running"] = True
            try:
                from src.core.config.loader import load_yaml_config
                from src.core.facebook.messenger_setup import (
                    set_greeting_message,
                    set_get_started_button,
                    set_greeting_and_get_started,
                )

                # 步骤1: 同步所有页面
                logger.info("开始同步所有页面Token...")
                count = await page_token_manager.sync_from_user_token(user_token)

                if count == 0:
                    _sync_and_setup_status["last_result"] = {
                        "success": False,
                        "error": "同步失败，未找到任何页面",
                        "step": "sync",
                    }
                    logger.warning("同步失败，未找到任何页面")
                    return

                logger.info(f"成功同步 {count} 个页面Token")

                # 步骤2: 激活所有页面（auto_reply_enabled=false）
                pages = page_token_manager.list_pages()
                configured_count = 0
                for page_id, info in pages.items():
                    page_name = info.get("name", "未知")
                    if not page_settings.get_page_config(page_id):
                        page_settings.add_page(
                            page_id, auto_reply_enabled=False, name=page_name)
                        configured_count += 1

                logger.info(f"已为 {configured_count} 个页面添加配置（自动回复已禁用，页面已激活）")

                # 步骤3: 配置所有页面的Messenger设置
                # 读取合规配置
                try:
                    config = load_yaml_config(
                        "config/config_philippines_iphone_loan_compliant.yaml")
                    three_step_config = config.get("three_step_flow", {})
                except Exception as e:
                    logger.warning(f"无法读取合规配置: {str(e)}，使用默认配置")
                    three_step_config = {}

                # 获取问候语（简短版本）
                def get_greeting_message(config: dict) -> str:
                    # 优先使用greeting_text字段（新格式，简短版本）
                    if "greeting_text" in config:
                        greeting_text = config["greeting_text"]
                        if isinstance(greeting_text, str):
                            return greeting_text.strip()
                    # 默认值
                    return "Hello 👋\nThanks for contacting our Page.\nWe provide general loan information only."

                greeting_message = get_greeting_message(three_step_config)

                # 配置每个页面
                setup_success = 0
                setup_failed = 0
                setup_details = []

                for page_id, info in pages.items():
                    page_name = info.get("name", "未知")
                    page_token = page_token_manager.get_token(page_id)

                    if not page_token:
                        setup_failed += 1
                        setup_details.append(
                            {"page_id": page_id, "page_name": page_name, "status": "failed", "reason": "未找到Token"})
                        continue

                    try:
                        logger.info(
                            f"开始配置页面 {page_name} (ID: {page_id}) 的Messenger设置...")

                        # 同时设置Greeting Message和Get Started Button（Facebook API要求：设置greeting时必须同时设置至少一个其他参数）
                        greeting_and_get_started_result = await set_greeting_and_get_started(
                            page_id, page_token, greeting_message, "GET_STARTED"
                        )
                        if isinstance(greeting_and_get_started_result, tuple):
                            greeting_success, greeting_error = greeting_and_get_started_result
                        else:
                            # 向后兼容：如果返回bool，则没有错误详情
                            greeting_success = greeting_and_get_started_result
                            greeting_error = None

                        # 两者同时设置，结果相同
                        get_started_success = greeting_success

                        logger.info(
                            f"页面 {page_name} - Greeting Message和Get Started Button设置结果: {greeting_success}")
                        if greeting_error:
                            logger.warning(
                                f"页面 {page_name} - Greeting Message和Get Started Button错误详情: {greeting_error}")

                        # 详细记录结果
                        if greeting_success and get_started_success:
                            setup_success += 1
                            setup_details.append({
                                "page_id": page_id,
                                "page_name": page_name,
                                "status": "success",
                                "greeting": True,
                                "get_started": True,
                                "message": "Greeting和Get Started都已成功设置"
                            })
                            logger.info(f"✅ 页面 {page_name} - Messenger设置完成")
                        elif greeting_success or get_started_success:
                            setup_success += 1
                            failed_items = []
                            error_details_list = []
                            if not greeting_success:
                                failed_items.append("Greeting Message")
                                if greeting_error:
                                    error_msg = greeting_error.get(
                                        'message', '未知错误')
                                    error_code = greeting_error.get('code', 0)
                                    error_details_list.append(
                                        f"Greeting Message: {error_msg} (错误码: {error_code})")
                            if not get_started_success:
                                failed_items.append("Get Started Button")

                            error_message = f"部分成功，失败的项: {', '.join(failed_items)}"
                            if error_details_list:
                                error_message += f" | 错误详情: {'; '.join(error_details_list)}"

                            setup_details.append({
                                "page_id": page_id,
                                "page_name": page_name,
                                "status": "partial",
                                "greeting": greeting_success,
                                "get_started": get_started_success,
                                "message": error_message,
                                "greeting_error": greeting_error if not greeting_success else None
                            })
                            logger.warning(
                                f"⚠️ 页面 {page_name} - Messenger设置部分成功: {failed_items} 失败, 错误: {error_details_list}")
                        else:
                            setup_failed += 1
                            setup_details.append({
                                "page_id": page_id,
                                "page_name": page_name,
                                "status": "failed",
                                "greeting": False,
                                "get_started": False,
                                "reason": "Greeting Message和Get Started Button都设置失败，请检查Token权限或API响应"
                            })
                            logger.error(f"❌ 页面 {page_name} - Messenger设置全部失败")
                    except Exception as e:
                        setup_failed += 1
                        error_msg = str(e)
                        setup_details.append({
                            "page_id": page_id,
                            "page_name": page_name,
                            "status": "failed",
                            "reason": f"异常错误: {error_msg}",
                            "error_type": type(e).__name__
                        })
                        logger.error(
                            f"❌ 配置页面 {page_id} ({page_name}) 失败: {str(e)}", exc_info=True)

                _sync_and_setup_status["last_result"] = {
                    "success": True,
                    "pages_synced": count,
                    "pages_configured": configured_count,
                    "messenger_setup": {
                        "success": setup_success,
                        "failed": setup_failed,
                        "details": setup_details,
                    },
                    "telegram_link": telegram_link,
                }
                logger.info(
                    f"后台同步和配置完成: {count} 个页面同步，{configured_count} 个页面配置，"
                    f"{setup_success} 个页面Messenger设置成功"
                )
            except Exception as e:
                _sync_and_setup_status["last_result"] = {
                    "success": False, "error": str(e)}
                logger.error(f"后台同步和配置失败: {str(e)}", exc_info=True)
            finally:
                _sync_and_setup_status["running"] = False

        background_tasks.add_task(sync_and_setup_task)

        return {
            "success": True,
            "message": "同步和配置任务已启动，正在后台执行",
            "note": "请稍后查看日志或使用 /admin/deployment/status 检查状态",
            "steps": [
                "同步所有Facebook页面Token",
                "激活所有页面（auto_reply_enabled=false，使用Meta自动回复）",
                "配置所有页面的Messenger设置（Greeting、Get Started - 通过API自动设置）",
                "显示Instant Reply和FAQ设置说明（需在Meta Business Suite手动配置）",
            ],
            "note": "Instant Reply和FAQ必须在Meta Business Suite中手动配置，系统无法通过API自动设置",
        }
    except Exception as e:
        logger.error(f"启动同步和配置任务失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启动同步和配置任务失败: {str(e)}")


@router.get("/faq-content")
async def get_faq_content(
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    获取FAQ配置内容（用于复制粘贴到Meta Business Suite）

    注意：FAQ必须手动在Meta Business Suite中设置，无法通过API自动配置
    """
    try:
        from src.core.config.loader import load_yaml_config

        # 读取FAQ配置
        try:
            faq_config = load_yaml_config("config/facebook_faqs.yaml")
            questions = faq_config.get(
                "facebook_faqs", {}).get("questions", [])
        except Exception as e:
            logger.warning(f"无法读取FAQ配置: {str(e)}，使用默认配置")
            # 使用默认FAQ内容
            questions = [
                {
                    "question": "What is this page about?",
                    "answer": "This page provides general information related to loan application services.\nWe offer guidance and FAQs only.\nApproval is subject to individual review."
                },
                {
                    "question": "Do you guarantee loan approval?",
                    "answer": "No. Loan approval is not guaranteed.\nAll applications are reviewed individually by the provider."
                },
                {
                    "question": "Are there any fees to get information here?",
                    "answer": "No fees are required to receive information on this page.\nPlease do not send money to anyone claiming otherwise."
                },
                {
                    "question": "Who is eligible to learn more?",
                    "answer": "Generally, information is available for users who are 18 years old or above\nand currently located in the Philippines."
                },
                {
                    "question": "How can I proceed or get assistance?",
                    "answer": "If you wish to proceed, you may continue the conversation here\nor choose to use our Telegram assistant for optional self-service guidance."
                }
            ]

        # 格式化FAQ内容
        formatted_faqs = []
        for idx, qa in enumerate(questions, 1):
            formatted_faqs.append({
                "number": idx,
                "question": qa.get("question", ""),
                "answer": qa.get("answer", ""),
                "copy_text": f"Q{idx}: {qa.get('question', '')}\n\n{qa.get('answer', '')}"
            })

        return {
            "success": True,
            "note": "FAQ必须手动在Meta Business Suite中设置，无法通过API自动配置",
            "instructions": [
                "1. 访问 https://business.facebook.com",
                "2. 进入 收件箱 → 自动化 → 常见问题",
                "3. 点击'添加常见问题'",
                "4. 复制以下问题和答案，逐一添加",
                "5. 保存并启用FAQ"
            ],
            "faqs": formatted_faqs,
            "total_count": len(formatted_faqs)
        }
    except Exception as e:
        logger.error(f"获取FAQ内容失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取FAQ内容失败: {str(e)}")
