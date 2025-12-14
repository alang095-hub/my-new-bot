"""对话上下文管理"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.core.database.models import Conversation, Customer, Platform, MessageType
from src.core.database.connection import get_db
from src.core.database.repositories import CustomerRepository, ConversationRepository


class ConversationManager:
    """管理对话上下文和历史记录"""
    
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.conversation_repo = ConversationRepository(db)
    
    async def get_conversation_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史（带缓存）
        
        Args:
            customer_id: 客户 ID
            limit: 返回的最大消息数
        
        Returns:
            对话历史列表
        """
        # 尝试从缓存获取
        from src.core.cache import conversation_cache
        
        cache_key = f"conversation_history:{customer_id}:{limit}"
        cached_history = await conversation_cache.get(cache_key)
        if cached_history is not None:
            return cached_history
        
        # 使用Repository获取对话历史
        conversations = self.conversation_repo.get_customer_conversations(
            customer_id=customer_id,
            skip=0,
            limit=limit
        )
        # 按时间倒序排列
        conversations = sorted(conversations, key=lambda x: x.created_at, reverse=True)
        
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
        
        # 缓存结果
        await conversation_cache.set(cache_key, history)
        
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
        
        # 转换message_type字符串为枚举
        message_type_enum = None
        if message_type:
            try:
                message_type_enum = MessageType[message_type.upper()] if isinstance(message_type, str) else message_type
            except (KeyError, AttributeError):
                message_type_enum = MessageType.MESSAGE  # 默认值
        
        # 使用Repository创建对话
        conversation = self.conversation_repo.create_conversation(
            customer_id=customer_id,
            platform=platform_enum,
            platform_message_id=msg_id,
            message_type=message_type_enum or MessageType.MESSAGE,
            content=content or "",
            raw_data=raw_data
        )
        
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
        # 使用Repository更新对话
        from datetime import datetime, timezone
        conversation = self.conversation_repo.update(
            id=conversation_id,
            ai_replied=True,
            ai_reply_content=reply_content,
            ai_reply_at=datetime.now(timezone.utc)
        )
        
        return conversation
    
    async def get_or_create_customer(
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
        
        # 尝试从缓存获取
        from src.core.cache import customer_cache
        
        cache_key = f"customer:{platform_enum.value}:{user_id}"
        cached_customer = await customer_cache.get(cache_key)
        if cached_customer is not None:
            # 如果提供了新名称且客户名称为空，更新并清除缓存
            if name and not cached_customer.name:
                cached_customer = self.customer_repo.update(
                    id=cached_customer.id,
                    name=name
                )
                await customer_cache.set(cache_key, cached_customer)
            return cached_customer
        
        # 使用Repository获取或创建客户
        customer = self.customer_repo.get_or_create(
            platform=platform_enum,
            platform_user_id=user_id,
            name=name,
            facebook_id=facebook_id or user_id  # 兼容字段
        )
        
        # 如果客户已存在但信息不完整，更新信息
        if name and not customer.name:
            customer = self.customer_repo.update(
                id=customer.id,
                name=name
            )
        
        # 缓存客户信息
        await customer_cache.set(cache_key, customer)
        
        return customer


