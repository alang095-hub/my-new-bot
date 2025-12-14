"""缓存模块"""
from .cache_manager import (
    CacheManager,
    cache_manager,
    conversation_cache,
    customer_cache,
    config_cache,
    prompt_cache
)

__all__ = [
    "CacheManager",
    "cache_manager",
    "conversation_cache",
    "customer_cache",
    "config_cache",
    "prompt_cache"
]

