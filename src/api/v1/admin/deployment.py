"""部署管理API - 用于执行部署后的操作（无需终端）"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.core.database.connection import get_db
from src.core.config import settings
from src.config.page_token_manager import page_token_manager
from src.config.page_settings import page_settings
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/deployment", tags=["deployment"])

# 全局变量跟踪同步状态
_sync_status = {"running": False, "last_result": None}


@router.post("/sync-pages")
async def sync_pages(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
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
                status_code=400,
                detail="FACEBOOK_ACCESS_TOKEN 未配置"
            )
        
        # 检查是否正在运行
        if _sync_status["running"]:
            return {
                "success": False,
                "message": "同步任务正在运行中，请稍后再试",
                "note": "使用 /admin/deployment/status 查看当前状态"
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
                            page_settings.add_page(page_id, auto_reply_enabled=True, name=page_name)
                            enabled_count += 1
                    
                    _sync_status["last_result"] = {
                        "success": True,
                        "pages_synced": count,
                        "pages_enabled": enabled_count
                    }
                    logger.info(f"后台同步完成: {count} 个页面，启用 {enabled_count} 个页面")
                else:
                    _sync_status["last_result"] = {
                        "success": False,
                        "error": "同步失败，未找到任何页面"
                    }
                    logger.warning("同步失败，未找到任何页面")
            except Exception as e:
                _sync_status["last_result"] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"后台同步失败: {str(e)}", exc_info=True)
            finally:
                _sync_status["running"] = False
        
        background_tasks.add_task(sync_task)
        
        return {
            "success": True,
            "message": "页面同步任务已启动，正在后台执行",
            "note": "请稍后查看日志或使用 /admin/deployment/status 检查状态"
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
            db.execute("SELECT 1")
            db_connected = True
        except Exception:
            db_connected = False
        
        return {
            "success": True,
            "status": {
                "database": {
                    "connected": db_connected,
                    "status": "healthy" if db_connected else "unhealthy"
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
                            "auto_reply_enabled": page_settings.is_auto_reply_enabled(page_id)
                        }
                        for page_id in pages.keys()
                    ]
                },
                "token": {
                    "default_token_configured": has_default_token,
                    "token_type": "USER" if has_default_token else "NONE"
                },
                "sync": {
                    "running": _sync_status["running"],
                    "last_result": _sync_status["last_result"]
                }
            }
        }
    except Exception as e:
        logger.error(f"获取部署状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取部署状态失败: {str(e)}")


@router.get("/verify-token")
async def verify_token():
    """
    验证当前Token类型和权限
    
    返回Token验证结果
    """
    try:
        import httpx
        token = settings.facebook_access_token
        
        if not token:
            raise HTTPException(
                status_code=400,
                detail="FACEBOOK_ACCESS_TOKEN 未配置"
            )
        
        # 检查Token类型
        app_id = settings.facebook_app_id
        app_secret = settings.facebook_app_secret
        
        if not app_id or not app_secret:
            raise HTTPException(
                status_code=400,
                detail="FACEBOOK_APP_ID 或 FACEBOOK_APP_SECRET 未配置"
            )
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 检查Token信息
            debug_url = "https://graph.facebook.com/v18.0/debug_token"
            debug_params = {
                "input_token": token,
                "access_token": f"{app_id}|{app_secret}"
            }
            debug_response = await client.get(debug_url, params=debug_params)
            
            if debug_response.status_code != 200:
                return {
                    "success": False,
                    "error": "Token验证失败",
                    "details": debug_response.json()
                }
            
            debug_data = debug_response.json().get("data", {})
            token_type = debug_data.get("type", "未知")
            
            # 尝试获取页面列表
            pages_url = "https://graph.facebook.com/v18.0/me/accounts"
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
                "message": "用户级Token，可以管理多个页面" if can_manage_pages else "页面级Token，只能管理单个页面"
            }
    except Exception as e:
        logger.error(f"验证Token失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"验证Token失败: {str(e)}")

