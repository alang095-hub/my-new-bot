"""Facebook 消息解析器"""
from typing import Dict, Any, Optional
from datetime import datetime
from src.core.database.models import MessageType


class FacebookMessageParser:
    """解析 Facebook Webhook 消息"""
    
    @staticmethod
    def parse_webhook_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析 Webhook 事件
        
        Args:
            event: Facebook Webhook 事件数据
        
        Returns:
            解析后的消息数据，如果无法解析则返回 None
        """
        if "object" not in event or event["object"] != "page":
            return None
        
        entries = event.get("entry", [])
        if not entries:
            return None
        
        parsed_messages = []
        
        for entry in entries:
            # 处理消息事件
            messaging_events = entry.get("messaging", [])
            for messaging_event in messaging_events:
                message_data = FacebookMessageParser._parse_messaging_event(
                    messaging_event, entry.get("id")
                )
                if message_data:
                    parsed_messages.append(message_data)
            
            # 处理评论事件
            comment_events = entry.get("changes", [])
            for change in comment_events:
                if change.get("field") == "feed":
                    comment_data = FacebookMessageParser._parse_comment_event(
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
        
        # 检查是否是页面自己发送的消息（包括 Business Suite 回复）
        # is_echo: true 表示是页面发送的消息，应该跳过
        if message.get("is_echo", False):
            return None
        
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
        if not comment or "message" not in comment:
            return None
        
        post_id = value.get("post_id")
        from_user = value.get("from", {})
        
        return {
            "message_id": comment.get("id"),
            "sender_id": from_user.get("id"),
            "post_id": post_id,
            "page_id": page_id,
            "message_type": MessageType.COMMENT,
            "content": comment.get("message"),
            "timestamp": value.get("created_time"),
            "raw_data": change
        }
    
    @staticmethod
    def parse_ad_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析广告相关事件"""
        # 广告事件通常通过不同的 Webhook 端点接收
        # 这里提供一个基础解析框架
        if event.get("object") != "ad":
            return None
        
        return {
            "message_id": event.get("id"),
            "sender_id": event.get("user_id"),
            "message_type": MessageType.AD,
            "content": event.get("message", ""),
            "timestamp": event.get("created_time"),
            "raw_data": event
        }
    
    @staticmethod
    def extract_user_info(event: Dict[str, Any]) -> Dict[str, Any]:
        """从事件中提取用户信息"""
        sender = event.get("sender", {})
        from_user = event.get("from", {})
        
        user_data = sender if sender else from_user
        
        return {
            "facebook_id": user_data.get("id"),
            "name": user_data.get("name"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name")
        }


