"""Webhook路由"""
from .facebook import router as facebook_router
from .instagram import router as instagram_router

__all__ = [
    'facebook_router',
    'instagram_router',
]

