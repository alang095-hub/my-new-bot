"""Facebook Webhook处理器实现"""
from typing import Dict, Any, List, Optional
from src.platforms.base import PlatformWebhookHandler, PlatformClient, PlatformParser
from src.config import settings


class FacebookWebhookHandler(PlatformWebhookHandler):
    """Facebook Webhook处理器"""
    
    async def verify(
        self,
        mode: str,
        token: str,
        challenge: str
    ) -> Optional[str]:
        """
        验证Webhook
        
        Args:
            mode: 验证模式
            token: 验证令牌
            challenge: 挑战字符串
        
        Returns:
            如果验证成功返回challenge，否则返回None
        """
        return await self.client.verify_webhook(mode, token, challenge)
    
    async def handle(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理Webhook事件
        
        Args:
            event_data: Webhook事件数据
        
        Returns:
            解析后的消息数据列表
        """
        parsed_messages = self.parser.parse_webhook_event(event_data)
        return parsed_messages if parsed_messages else []







