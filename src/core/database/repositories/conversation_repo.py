"""对话Repository"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from src.core.database.repositories.base import BaseRepository
from src.core.database.models import Conversation, Customer, Platform, MessageType


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
        根据平台消息ID获取对话
        
        Args:
            platform: 平台类型
            platform_message_id: 平台消息ID
            
        Returns:
            对话实例或None
        """
        return self.get_by(
            platform=platform,
            platform_message_id=platform_message_id
        )
    
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

