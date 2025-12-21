"""Webhook路由"""

from .facebook import router as facebook_router

# 可选导入Instagram router（如果模块不可用则不导入）
try:
    from .instagram import router as instagram_router
except ImportError:
    # 如果Instagram模块不可用，创建一个空的router
    from fastapi import APIRouter
    instagram_router = APIRouter()

__all__ = [
    "facebook_router",
    "instagram_router",
]
