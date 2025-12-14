"""Instagram 消息解析器"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.core.database.models import MessageType


class InstagramMessageParser:
    """解析 Instagram Webhook 消息"""
    
    @staticmethod
    def parse_webhook_event(event: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        解析 Webhook 事件
        
        Args:
            event: Instagram Webhook 事件数据
        
        Returns:
            解析后的消息数据列表，如果无法解析则返回 None
        """
        if "object" not in event or event["object"] != "instagram":
            return None
        
        entries = event.get("entry", [])
        if not entries:
            return None
        
        parsed_messages = []
        
        for entry in entries:
            # 处理消息事件
            messaging_events = entry.get("messaging", [])
            for messaging_event in messaging_events:
                message_data = InstagramMessageParser._parse_messaging_event(
                    messaging_event, entry.get("id")
                )
                if message_data:
                    parsed_messages.append(message_data)
            
            # 处理评论事件
            comment_events = entry.get("changes", [])
            for change in comment_events:
                if change.get("field") == "comments":
                    comment_data = InstagramMessageParser._parse_comment_event(
                        change, entry.get("id")
                    )
                    if comment_data:
                        parsed_messages.append(comment_data)
        
        return parsed_messages if parsed_messages else None
    
    @staticmethod
    def _parse_messaging_event(
        event: Dict[str, Any],
        page_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """解析私信事件"""
        sender = event.get("sender", {})
        recipient = event.get("recipient", {})
        message = event.get("message", {})
        
        if not message or "text" not in message:
            return None
        
        return {
            "message_id": message.get("mid"),
            "sender_id": sender.get("id"),
            "recipient_id": recipient.get("id"),
            "page_id": page_id,
            "message_type": MessageType.MESSAGE,
            "content": message.get("text"),
            "timestamp": event.get("timestamp"),
            "raw_data": event
        }
    
    @staticmethod
    def _parse_comment_event(
        change: Dict[str, Any],
        page_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """解析评论事件"""
        value = change.get("value", {})
        
        # 只处理新评论
        if value.get("verb") != "add":
            return None
        
        comment = value.get("comment", {})
        if not comment or "text" not in comment:
            return None
        
        media_id = value.get("media_id")
        from_user = value.get("from", {})
        
        return {
            "message_id": comment.get("id"),
            "sender_id": from_user.get("id"),
            "media_id": media_id,
            "page_id": page_id,
            "message_type": MessageType.COMMENT,
            "content": comment.get("text"),
            "timestamp": value.get("created_time"),
            "raw_data": change
        }
    
    @staticmethod
    def extract_user_info(event: Dict[str, Any]) -> Dict[str, Any]:
        """从事件中提取用户信息"""
        sender = event.get("sender", {})
        from_user = event.get("from", {})
        
        user_data = sender if sender else from_user
        
        return {
            "instagram_id": user_data.get("id"),
            "username": user_data.get("username"),
            "name": user_data.get("name")
        }

