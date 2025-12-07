"""实时监控 - 使用 Server-Sent Events (SSE) 推送实时数据"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from collections import deque
import asyncio
import json
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class RealtimeMonitor:
    """实时监控器 - 跟踪AI回复和系统状态"""
    
    def __init__(self, max_history: int = 100):
        """
        初始化实时监控器
        
        Args:
            max_history: 保留的最大历史记录数
        """
        self.max_history = max_history
        self.recent_replies: deque = deque(maxlen=max_history)
        self.active_connections: List[Dict[str, Any]] = []
        self.stats_cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    async def record_ai_reply(
        self,
        customer_id: int,
        customer_name: Optional[str],
        platform: str,
        user_message: str,
        ai_reply: str,
        timestamp: Optional[datetime] = None
    ):
        """
        记录AI回复事件
        
        Args:
            customer_id: 客户ID
            customer_name: 客户姓名
            platform: 平台名称
            user_message: 用户消息
            ai_reply: AI回复
            timestamp: 时间戳
        """
        if timestamp is None:
            # 使用UTC时间，确保时区信息正确
            timestamp = datetime.now(timezone.utc)
        elif timestamp.tzinfo is None:
            # 如果没有时区信息，假设为UTC
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        
        event = {
            "type": "ai_reply",
            "timestamp": timestamp.isoformat(),  # ISO格式包含时区信息
            "data": {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "platform": platform,
                "user_message": user_message[:200],  # 限制长度
                "ai_reply": ai_reply,
                "reply_length": len(ai_reply)
            }
        }
        
        self.recent_replies.append(event)
        
        # 更新统计缓存
        await self._update_stats_cache()
        
        # 推送给所有连接的客户端
        await self._broadcast_event(event)
    
    async def record_system_event(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        记录系统事件
        
        Args:
            event_type: 事件类型（如 'error', 'warning', 'info'）
            message: 事件消息
            data: 额外数据
        """
        event = {
            "type": "system_event",
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),  # 使用UTC时间
            "message": message,
            "data": data or {}
        }
        
        await self._broadcast_event(event)
    
    async def get_recent_replies(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取最近的AI回复记录
        
        Args:
            limit: 返回的记录数
            
        Returns:
            最近的回复记录列表
        """
        return list(self.recent_replies)[-limit:]
    
    async def get_live_stats(self, db: Session) -> Dict[str, Any]:
        """
        获取实时统计数据
        
        Args:
            db: 数据库会话
            
        Returns:
            实时统计数据
        """
        from datetime import date, timedelta
        from src.database.models import Conversation
        from sqlalchemy import func
        
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today + timedelta(days=1), datetime.min.time())
        
        # 今日统计
        today_stats = db.query(
            func.count(Conversation.id).label('total_replies'),
            func.count(func.distinct(Conversation.customer_id)).label('unique_customers')
        ).filter(
            Conversation.ai_replied == True,
            Conversation.ai_reply_at >= today_start,
            Conversation.ai_reply_at < today_end
        ).first()
        
        # 最近1小时统计
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_stats = db.query(
            func.count(Conversation.id).label('recent_replies')
        ).filter(
            Conversation.ai_replied == True,
            Conversation.ai_reply_at >= one_hour_ago
        ).first()
        
        # 平台分布
        platform_stats = db.query(
            Conversation.platform,
            func.count(Conversation.id).label('count')
        ).filter(
            Conversation.ai_replied == True,
            Conversation.ai_reply_at >= today_start,
            Conversation.ai_reply_at < today_end
        ).group_by(Conversation.platform).all()
        
        return {
            "today": {
                "total_replies": today_stats.total_replies or 0,
                "unique_customers": today_stats.unique_customers or 0
            },
            "last_hour": {
                "replies": recent_stats.recent_replies or 0
            },
            "platform_distribution": {
                platform.value if platform else "unknown": count
                for platform, count in platform_stats
            },
            "cache_updated_at": self.stats_cache.get("updated_at")
        }
    
    async def _update_stats_cache(self):
        """更新统计缓存"""
        async with self._lock:
            self.stats_cache = {
                "total_replies": len(self.recent_replies),
                "updated_at": datetime.now().isoformat()
            }
    
    async def _broadcast_event(self, event: Dict[str, Any]):
        """向所有连接的客户端广播事件"""
        if not self.active_connections:
            return
        
        message = f"data: {json.dumps(event)}\n\n"
        disconnected = []
        
        for conn in self.active_connections:
            try:
                await conn["queue"].put(message)
            except Exception as e:
                logger.warning(f"Failed to send event to client: {e}")
                disconnected.append(conn)
        
        # 移除断开的连接
        for conn in disconnected:
            self.active_connections.remove(conn)
    
    async def add_connection(self, connection_id: str) -> asyncio.Queue:
        """
        添加新的SSE连接
        
        Args:
            connection_id: 连接ID
            
        Returns:
            消息队列
        """
        queue = asyncio.Queue()
        self.active_connections.append({
            "id": connection_id,
            "queue": queue,
            "connected_at": datetime.now()
        })
        logger.info(f"New monitoring connection: {connection_id}")
        return queue
    
    async def remove_connection(self, connection_id: str):
        """移除连接"""
        self.active_connections = [
            conn for conn in self.active_connections
            if conn["id"] != connection_id
        ]
        logger.info(f"Removed monitoring connection: {connection_id}")


# 全局监控实例
realtime_monitor = RealtimeMonitor()

