"""ManyChat API 客户端"""
import httpx
from typing import Dict, Any, Optional
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ManyChatClient:
    """ManyChat API 客户端"""
    
    def __init__(self):
        self.api_key = settings.manychat_api_key
        self.api_url = settings.manychat_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_message(
        self,
        subscriber_id: str,
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        发送消息到 ManyChat
        
        Args:
            subscriber_id: 订阅者 ID
            message: 消息内容
            message_type: 消息类型
        
        Returns:
            API 响应
        """
        if not self.api_key:
            raise ValueError("ManyChat API key not configured")
        
        url = f"{self.api_url}/fb/sending/sendContent"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "subscriber_id": subscriber_id,
            "data": {
                "version": "v2",
                "content": {
                    "messages": [
                        {
                            "type": message_type,
                            "text": message
                        }
                    ]
                }
            }
        }
        
        try:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending ManyChat message: {str(e)}", exc_info=True)
            raise
    
    async def get_subscriber_info(self, subscriber_id: str) -> Dict[str, Any]:
        """
        获取订阅者信息
        
        Args:
            subscriber_id: 订阅者 ID
        
        Returns:
            订阅者信息
        """
        if not self.api_key:
            raise ValueError("ManyChat API key not configured")
        
        url = f"{self.api_url}/subscriber/getInfo"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        params = {
            "subscriber_id": subscriber_id
        }
        
        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting ManyChat subscriber info: {str(e)}", exc_info=True)
            raise
    
    async def set_custom_field(
        self,
        subscriber_id: str,
        field_name: str,
        field_value: Any
    ) -> Dict[str, Any]:
        """
        设置自定义字段
        
        Args:
            subscriber_id: 订阅者 ID
            field_name: 字段名
            field_value: 字段值
        
        Returns:
            API 响应
        """
        if not self.api_key:
            raise ValueError("ManyChat API key not configured")
        
        url = f"{self.api_url}/subscriber/setCustomField"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "subscriber_id": subscriber_id,
            "field_name": field_name,
            "field_value": field_value
        }
        
        try:
            response = await self.client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error setting ManyChat custom field: {str(e)}", exc_info=True)
            raise
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


