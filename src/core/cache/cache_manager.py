"""缓存管理器"""
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    expires_at: Optional[datetime]
    created_at: datetime


class CacheManager:
    """缓存管理器 - 简单的内存缓存实现"""
    
    def __init__(self, default_ttl: Optional[timedelta] = None):
        """
        初始化缓存管理器
        
        Args:
            default_ttl: 默认TTL（Time To Live），如果为None则不设置过期时间
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                return None
            
            # 检查是否过期
            if entry.expires_at and datetime.now(timezone.utc) > entry.expires_at:
                del self._cache[key]
                return None
            
            return entry.value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: TTL（Time To Live），如果为None则使用默认TTL
        """
        async with self._lock:
            expires_at = None
            if ttl:
                expires_at = datetime.now(timezone.utc) + ttl
            elif self._default_ttl:
                expires_at = datetime.now(timezone.utc) + self._default_ttl
            
            entry = CacheEntry(
                key=key,
                value=value,
                expires_at=expires_at,
                created_at=datetime.now(timezone.utc)
            )
            
            self._cache[key] = entry
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            是否成功删除
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[timedelta] = None
    ) -> Any:
        """
        获取缓存值，如果不存在则调用factory生成并缓存
        
        Args:
            key: 缓存键
            factory: 生成值的函数（可以是同步或异步）
            ttl: TTL
        
        Returns:
            缓存值或新生成的值
        """
        value = await self.get(key)
        if value is not None:
            return value
        
        # 生成新值
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        await self.set(key, value, ttl)
        return value
    
    async def cleanup_expired(self) -> int:
        """
        清理过期的缓存条目
        
        Returns:
            清理的条目数量
        """
        async with self._lock:
            now = datetime.now(timezone.utc)
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.expires_at and entry.expires_at < now
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        async def _get_stats():
            async with self._lock:
                total_entries = len(self._cache)
                expired_count = sum(
                    1 for entry in self._cache.values()
                    if entry.expires_at and entry.expires_at < datetime.now(timezone.utc)
                )
                
                return {
                    "total_entries": total_entries,
                    "expired_entries": expired_count,
                    "active_entries": total_entries - expired_count
                }
        
        # 同步调用（简化处理）
        return {
            "total_entries": len(self._cache),
            "active_entries": len(self._cache)
        }


# 全局缓存管理器实例
# 对话历史缓存：TTL 5分钟
conversation_cache = CacheManager(default_ttl=timedelta(minutes=5))

# 客户信息缓存：TTL 10分钟
customer_cache = CacheManager(default_ttl=timedelta(minutes=10))

# 配置缓存：TTL 1小时
config_cache = CacheManager(default_ttl=timedelta(hours=1))

# 提示词模板缓存：TTL 1小时
prompt_cache = CacheManager(default_ttl=timedelta(hours=1))

# 默认缓存管理器（无TTL）
cache_manager = CacheManager()

