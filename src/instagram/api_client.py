"""Instagram Graph API 客户端"""
import httpx
from typing import Dict, Any, Optional
from src.core.config import settings


class InstagramAPIClient:
    """Instagram Graph API 客户端封装"""
    
    def __init__(self):
        self.access_token = getattr(settings, 'instagram_access_token', None) or settings.facebook_access_token
        self.base_url = "https://graph.instagram.com/v18.0"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_message(
        self,
        recipient_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        发送消息到 Instagram
        
        Args:
            recipient_id: 接收者 Instagram ID
            message: 消息内容
        
        Returns:
            API 响应
        """
        url = f"{self.base_url}/{recipient_id}/messages"
        params = {"access_token": self.access_token}
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": message}
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
            "fields": "id,username,account_type"
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def comment_on_media(
        self,
        media_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        在媒体下评论
        
        Args:
            media_id: 媒体 ID
            message: 评论内容
        
        Returns:
            API 响应
        """
        url = f"{self.base_url}/{media_id}/comments"
        params = {"access_token": self.access_token}
        data = {"message": message}
        
        response = await self.client.post(url, params=params, json=data)
        response.raise_for_status()
        return response.json()
    
    async def verify_webhook(
        self,
        mode: str,
        token: str,
        challenge: str
    ) -> Optional[str]:
        """
        验证 Webhook 订阅
        
        Args:
            mode: 验证模式
            token: 验证令牌
            challenge: 挑战字符串
        
        Returns:
            如果验证成功返回 challenge，否则返回 None
        """
        verify_token = getattr(settings, 'instagram_verify_token', None) or settings.facebook_verify_token
        if mode == "subscribe" and token == verify_token:
            return challenge
        return None
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()

