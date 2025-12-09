"""Instagram Graph API 客户端"""
from typing import Dict, Any, Optional
from src.platforms.base import PlatformClient


class InstagramAPIClient(PlatformClient):
    """Instagram Graph API 客户端封装"""
    
    def __init__(self, access_token: str = None, base_url: str = None, ig_user_id: str = None):
        """
        初始化Instagram API客户端
        
        Args:
            access_token: Instagram访问令牌（如果为None，从配置读取）
            base_url: API基础URL（如果为None，使用默认值）
            ig_user_id: Instagram用户ID（用于发送消息）
        """
        from src.config import settings
        
        if access_token is None:
            access_token = getattr(settings, 'instagram_access_token', None) or settings.facebook_access_token
        
        if base_url is None:
            base_url = "https://graph.facebook.com/v18.0"
        
        super().__init__(access_token, base_url)
        self.ig_user_id = ig_user_id or getattr(settings, 'instagram_user_id', None)
    
    async def send_message(
        self,
        recipient_id: str,
        message: str,
        message_type: str = "RESPONSE"
    ) -> Dict[str, Any]:
        """
        发送消息到Instagram
        
        Args:
            recipient_id: 接收者Instagram ID
            message: 消息内容
            message_type: 消息类型 (RESPONSE, UPDATE, MESSAGE_TAG)
        
        Returns:
            API响应
        """
        if not self.ig_user_id:
            raise ValueError("Instagram user ID is required for sending messages")
        
        url = f"{self.base_url}/{self.ig_user_id}/messages"
        params = {"access_token": self.access_token}
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": message},
            "messaging_type": message_type
        }
        
        response = await self.client.post(url, params=params, json=data)
        response.raise_for_status()
        return response.json()
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            user_id: Instagram 用户 ID
        
        Returns:
            用户信息
        """
        url = f"{self.base_url}/{user_id}"
        params = {
            "access_token": self.access_token,
            "fields": "id,username"
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def verify_webhook(
        self,
        mode: str,
        token: str,
        challenge: str
    ) -> Optional[str]:
        """
        验证Webhook订阅
        
        Args:
            mode: 验证模式
            token: 验证令牌
            challenge: 挑战字符串
        
        Returns:
            如果验证成功返回challenge，否则返回None
        """
        from src.config import settings
        verify_token = getattr(settings, 'instagram_verify_token', None) or settings.facebook_verify_token
        
        if mode == "subscribe" and token == verify_token:
            return challenge
        return None







