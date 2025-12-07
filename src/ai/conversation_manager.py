"""对话上下文管理"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.database.models import Conversation, Customer, Platform
from src.database.database import get_db


class ConversationManager:
    """管理对话上下文和历史记录"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_conversation_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        Args:
            customer_id: 客户 ID
            limit: 返回的最大消息数
        
        Returns:
            对话历史列表
        """
        conversations = self.db.query(Conversation)\
            .filter(Conversation.customer_id == customer_id)\
            .order_by(Conversation.created_at.desc())\
            .limit(limit)\
            .all()
        
        from datetime import timezone
        
        history = []
        for conv in reversed(conversations):  # 按时间正序
            # 确保时间有时区信息
            received_at = conv.received_at
            if received_at and received_at.tzinfo is None:
                received_at = received_at.replace(tzinfo=timezone.utc)
            
            history.append({
                "role": "user",
                "content": conv.content,
                "timestamp": received_at.isoformat() if received_at else None
            })
            
            if conv.ai_replied and conv.ai_reply_content:
                ai_reply_at = conv.ai_reply_at
                if ai_reply_at and ai_reply_at.tzinfo is None:
                    ai_reply_at = ai_reply_at.replace(tzinfo=timezone.utc)
                
                history.append({
                    "role": "assistant",
                    "content": conv.ai_reply_content,
                    "timestamp": ai_reply_at.isoformat() if ai_reply_at else None
                })
        
        return history
    
    def save_conversation(
        self,
        customer_id: int,
        platform_message_id: str = None,
        facebook_message_id: str = None,
        platform: str = "facebook",
        message_type: str = None,
        content: str = None,
        raw_data: Dict[str, Any] = None
    ) -> Conversation:
        """
        保存对话记录
        
        Args:
            customer_id: 客户 ID
            platform_message_id: 平台消息 ID（新字段，优先使用）
            facebook_message_id: Facebook 消息 ID（兼容字段）
            platform: 平台名称（facebook, instagram等）
            message_type: 消息类型
            content: 消息内容
            raw_data: 原始数据
        
        Returns:
            创建的对话记录
        """
        # 使用platform_message_id或facebook_message_id
        msg_id = platform_message_id or facebook_message_id
        
        # 转换platform字符串为枚举
        platform_enum = None
        try:
            platform_enum = Platform[platform.upper()] if platform else Platform.FACEBOOK
        except (KeyError, AttributeError):
            platform_enum = Platform.FACEBOOK  # 默认值
        
        conversation = Conversation(
            customer_id=customer_id,
            platform_message_id=msg_id,
            facebook_message_id=facebook_message_id or msg_id,  # 兼容字段
            platform=platform_enum,
            message_type=message_type,
            content=content,
            raw_data=raw_data
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def update_ai_reply(
        self,
        conversation_id: int,
        reply_content: str
    ) -> Conversation:
        """
        更新 AI 回复
        
        Args:
            conversation_id: 对话 ID
            reply_content: 回复内容
        
        Returns:
            更新的对话记录
        """
        conversation = self.db.query(Conversation)\
            .filter(Conversation.id == conversation_id)\
            .first()
        
        if conversation:
            conversation.ai_replied = True
            conversation.ai_reply_content = reply_content
            from datetime import datetime, timezone
            conversation.ai_reply_at = datetime.now(timezone.utc)  # 使用UTC时区
            
            self.db.commit()
            self.db.refresh(conversation)
        
        return conversation
    
    def get_or_create_customer(
        self,
        platform_user_id: str = None,
        facebook_id: str = None,
        platform: str = "facebook",
        name: str = None
    ) -> Customer:
        """
        获取或创建客户
        
        Args:
            platform_user_id: 平台用户 ID（新字段，优先使用）
            facebook_id: Facebook 用户 ID（兼容字段）
            platform: 平台名称（facebook, instagram等）
            name: 客户姓名
        
        Returns:
            客户对象
        """
        # 使用platform_user_id或facebook_id
        user_id = platform_user_id or facebook_id
        
        # 转换platform字符串为枚举
        platform_enum = None
        try:
            platform_enum = Platform[platform.upper()] if platform else Platform.FACEBOOK
        except (KeyError, AttributeError):
            platform_enum = Platform.FACEBOOK  # 默认值
        
        # 查询客户（根据平台和用户ID）
        customer = self.db.query(Customer)\
            .filter(
                Customer.platform == platform_enum,
                Customer.platform_user_id == user_id
            )\
            .first()
        
        # 如果没有找到，尝试通过facebook_id查找（向后兼容）
        if not customer and facebook_id:
            customer = self.db.query(Customer)\
                .filter(Customer.facebook_id == facebook_id)\
                .first()
        
        if not customer:
            customer = Customer(
                platform=platform_enum,
                platform_user_id=user_id,
                facebook_id=facebook_id or user_id,  # 兼容字段
                name=name
            )
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)
        elif name and not customer.name:
            customer.name = name
            # 更新平台相关字段（如果之前没有设置）
            if not customer.platform:
                customer.platform = platform_enum
            if not customer.platform_user_id:
                customer.platform_user_id = user_id
            self.db.commit()
            self.db.refresh(customer)
        
        return customer


