"""对话Repository"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.core.database.repositories.base import BaseRepository
from src.core.database.models import Conversation, Customer, Platform, MessageType
from src.core.cache.cache_manager import conversation_cache


class ConversationRepository(BaseRepository[Conversation]):
    """对话数据访问层"""
    
    def __init__(self, db: Session):
        super().__init__(db, Conversation)
    
    def get_by_platform_message_id(
        self,
        platform: Platform,
        platform_message_id: str
    ) -> Optional[Conversation]:
        """
        根据平台消息ID获取对话（带缓存）
        
        Args:
            platform: 平台类型
            platform_message_id: 平台消息ID
            
        Returns:
            对话实例或None
        """
        import asyncio
        
        # 生成缓存键
        cache_key = f"conversation:{platform.value}:{platform_message_id}"
        
        # 尝试从缓存获取
        try:
            cached = asyncio.run(conversation_cache.get(cache_key))
            if cached:
                return cached
        except Exception:
            pass  # 缓存失败不影响查询
        
        # 从数据库查询
        result = self.get_by(
            platform=platform,
            platform_message_id=platform_message_id
        )
        
        # 缓存结果（如果存在）
        if result:
            try:
                asyncio.run(conversation_cache.set(
                    cache_key,
                    result,
                    ttl=timedelta(minutes=5)
                ))
            except Exception:
                pass  # 缓存失败不影响返回结果
        
        return result
    
    def create_conversation(
        self,
        customer_id: int,
        platform: Platform,
        platform_message_id: str,
        message_type: MessageType,
        content: str,
        raw_data: Optional[dict] = None,
        **kwargs
    ) -> Conversation:
        """
        创建对话记录
        
        Args:
            customer_id: 客户ID
            platform: 平台类型
            platform_message_id: 平台消息ID
            message_type: 消息类型
            content: 消息内容
            raw_data: 原始数据
            **kwargs: 其他字段
            
        Returns:
            对话实例
        """
        conversation_data = {
            "customer_id": customer_id,
            "platform": platform,
            "platform_message_id": platform_message_id,
            "message_type": message_type,
            "content": content,
            "raw_data": raw_data,
            **kwargs
        }
        
        # 兼容字段：如果是Facebook，也设置facebook_message_id
        if platform == Platform.FACEBOOK:
            conversation_data["facebook_message_id"] = platform_message_id
        
        return self.create(**conversation_data)
    
    def get_customer_conversations(
        self,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        """
        获取客户的所有对话（优化：使用索引）
        
        Args:
            customer_id: 客户ID
            skip: 跳过记录数
            limit: 限制记录数
            
        Returns:
            对话列表
        """
        # 使用索引优化查询：customer_id + received_at
        return self.db.query(self.model)\
            .filter(self.model.customer_id == customer_id)\
            .order_by(self.model.received_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_unreplied_conversations(
        self,
        start_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Conversation]:
        """
        批量获取未回复的对话（优化：使用索引）
        
        Args:
            start_time: 开始时间（可选）
            limit: 限制记录数
            
        Returns:
            未回复的对话列表
        """
        query = self.db.query(self.model)\
            .filter(
                self.model.ai_replied == False,
                self.model.content.isnot(None),
                self.model.content != ""
            )
        
        if start_time:
            query = query.filter(self.model.received_at >= start_time)
        
        # 使用索引：ai_replied + received_at
        return query.order_by(self.model.received_at.asc())\
            .limit(limit)\
            .all()
    
    def bulk_update_ai_reply(
        self,
        conversation_ids: List[int],
        ai_reply_content: str
    ) -> int:
        """
        批量更新AI回复（优化：使用批量操作）
        
        Args:
            conversation_ids: 对话ID列表
            ai_reply_content: AI回复内容
            
        Returns:
            更新的记录数
        """
        from datetime import datetime, timezone
        
        updated = self.db.query(self.model)\
            .filter(self.model.id.in_(conversation_ids))\
            .update({
                "ai_replied": True,
                "ai_reply_content": ai_reply_content,
                "ai_reply_at": datetime.now(timezone.utc)
            }, synchronize_session=False)
        
        self.db.commit()
        return updated
    
    def count_by_time_range(self, start_time: datetime) -> int:
        """
        统计指定时间范围内的对话数量
        
        Args:
            start_time: 开始时间
            
        Returns:
            对话数量
        """
        from sqlalchemy import func
        return self.db.query(func.count(self.model.id))\
            .filter(self.model.created_at >= start_time)\
            .scalar() or 0
    
    def count_ai_replied_by_time_range(self, start_time: datetime) -> int:
        """
        统计指定时间范围内AI已回复的对话数量
        
        Args:
            start_time: 开始时间
            
        Returns:
            AI已回复的对话数量
        """
        from sqlalchemy import func, and_
        return self.db.query(func.count(self.model.id))\
            .filter(
                and_(
                    self.model.created_at >= start_time,
                    self.model.ai_replied == True
                )
            )\
            .scalar() or 0
    
    def count_by_priority_by_time_range(self, start_time: datetime) -> int:
        """
        统计指定时间范围内有优先级的对话数量（通常需要审核）
        
        Args:
            start_time: 开始时间
            
        Returns:
            有优先级的对话数量
        """
        from sqlalchemy import func, and_
        return self.db.query(func.count(self.model.id))\
            .filter(
                and_(
                    self.model.created_at >= start_time,
                    self.model.priority != None
                )
            )\
            .scalar() or 0
    
    def get_customer_ai_replied_conversations(self, customer_id: int) -> List[Conversation]:
        """
        获取客户所有AI已回复的对话
        
        Args:
            customer_id: 客户ID
            
        Returns:
            对话列表
        """
        return self.db.query(self.model)\
            .filter(
                self.model.customer_id == customer_id,
                self.model.ai_replied == True,
                self.model.ai_reply_content.isnot(None)
            )\
            .all()
    
    def get_by_filters(
        self,
        status: Optional[str] = None,
        platform: Optional[Platform] = None,
        skip: int = 0,
        limit: int = 100,
        order_by_desc: bool = True
    ) -> tuple[List[Conversation], int]:
        """
        根据过滤条件获取对话列表
        
        Args:
            status: 状态过滤
            platform: 平台过滤
            skip: 跳过记录数
            limit: 限制记录数
            order_by_desc: 是否按时间倒序
            
        Returns:
            (对话列表, 总数)
        """
        from sqlalchemy import desc
        query = self.db.query(self.model)
        
        if status:
            query = query.filter(self.model.status == status)
        
        if platform:
            query = query.filter(self.model.platform == platform)
        
        total = query.count()
        
        if order_by_desc:
            query = query.order_by(desc(self.model.received_at))
        else:
            query = query.order_by(self.model.received_at)
        
        conversations = query.offset(skip).limit(limit).all()
        
        return conversations, total
    
    def get_by_id_with_relations(self, conversation_id: int) -> Optional[Conversation]:
        """
        根据ID获取对话（包含关联数据，带缓存）
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            对话实例或None
        """
        import asyncio
        
        # 生成缓存键
        cache_key = f"conversation:id:{conversation_id}"
        
        # 尝试从缓存获取
        try:
            cached = asyncio.run(conversation_cache.get(cache_key))
            if cached:
                return cached
        except Exception:
            pass
        
        # 从数据库查询
        result = self.get_by_id(conversation_id)
        
        # 缓存结果（如果存在）
        if result:
            try:
                asyncio.run(conversation_cache.set(
                    cache_key,
                    result,
                    ttl=timedelta(minutes=5)
                ))
            except Exception:
                pass
        
        return result
    
    def count_by_time_range(self, start_time: datetime) -> int:
        """
        统计指定时间范围内的对话数量
        
        Args:
            start_time: 开始时间
            
        Returns:
            对话数量
        """
        from sqlalchemy import func
        return self.db.query(func.count(self.model.id))\
            .filter(self.model.received_at >= start_time)\
            .scalar() or 0
    
    def get_status_stats_by_time_range(self, start_time: datetime) -> List[tuple]:
        """
        按状态统计指定时间范围内的对话
        
        Args:
            start_time: 开始时间
            
        Returns:
            [(status, count), ...] 列表
        """
        from sqlalchemy import func
        return self.db.query(
            self.model.status,
            func.count(self.model.id)
        ).filter(
            self.model.received_at >= start_time
        ).group_by(self.model.status).all()
    
    def get_platform_stats_by_time_range(self, start_time: datetime) -> List[tuple]:
        """
        按平台统计指定时间范围内的对话
        
        Args:
            start_time: 开始时间
            
        Returns:
            [(platform, count), ...] 列表
        """
        from sqlalchemy import func
        return self.db.query(
            self.model.platform,
            func.count(self.model.id)
        ).filter(
            self.model.received_at >= start_time
        ).group_by(self.model.platform).all()
    
    def count_ai_replied_by_time_range(self, start_time: datetime) -> int:
        """
        统计指定时间范围内AI已回复的对话数量
        
        Args:
            start_time: 开始时间
            
        Returns:
            AI已回复的对话数量
        """
        from sqlalchemy import func, and_
        return self.db.query(func.count(self.model.id))\
            .filter(
                and_(
                    self.model.received_at >= start_time,
                    self.model.ai_replied == True
                )
            )\
            .scalar() or 0
    
    def get_ai_replied_with_customer(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Conversation], int]:
        """
        获取AI已回复的对话（包含客户信息）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            skip: 跳过记录数
            limit: 限制记录数
            
        Returns:
            (对话列表, 总数)
        """
        query = self.db.query(self.model)\
            .join(Customer, self.model.customer_id == Customer.id)\
            .filter(
                self.model.ai_replied == True,
                self.model.ai_reply_content.isnot(None)
            )
        
        if start_date:
            query = query.filter(self.model.ai_reply_at >= start_date)
        
        if end_date:
            query = query.filter(self.model.ai_reply_at <= end_date)
        
        total = query.count()
        
        conversations = query\
            .order_by(self.model.ai_reply_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return conversations, total

