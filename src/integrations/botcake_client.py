"""Botcake API 客户端"""
import httpx
from typing import Dict, Any, Optional
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class BotcakeClient:
    """Botcake API 客户端"""
    
    def __init__(self):
        self.api_key = settings.botcake_api_key
        self.api_url = settings.botcake_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_message(
        self,
        user_id: str,
        message: str,
        channel: str = "messenger"
    ) -> Dict[str, Any]:
        """
        发送消息到 Botcake
        
        Args:
            user_id: 用户 ID
            message: 消息内容
            channel: 渠道（messenger, whatsapp等）
        
        Returns:
            API 响应
        """
        if not self.api_key:
            raise ValueError("Botcake API key not configured")
        
        url = f"{self.api_url}/messages/send"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "user_id": user_id,
            "channel": channel,
            "message": {
                "type": "text",
                "text": message
            }
        }
        
        try:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending Botcake message: {str(e)}", exc_info=True)
            raise
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            user_id: 用户 ID
        
        Returns:
            用户信息
        """
        if not self.api_key:
            raise ValueError("Botcake API key not configured")
        
        url = f"{self.api_url}/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting Botcake user info: {str(e)}", exc_info=True)
            raise
    
    async def update_user_attribute(
        self,
        user_id: str,
        attribute_name: str,
        attribute_value: Any
    ) -> Dict[str, Any]:
        """
        更新用户属性
        
        Args:
            user_id: 用户 ID
            attribute_name: 属性名
            attribute_value: 属性值
        
        Returns:
            API 响应
        """
        if not self.api_key:
            raise ValueError("Botcake API key not configured")
        
        url = f"{self.api_url}/users/{user_id}/attributes"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            attribute_name: attribute_value
        }
        
        try:
            response = await self.client.put(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating Botcake user attribute: {str(e)}", exc_info=True)
            raise
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


