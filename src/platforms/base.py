"""平台抽象基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import httpx


class PlatformClient(ABC):
    """平台API客户端抽象基类"""
    
    def __init__(self, access_token: str, base_url: str = None):
        """
        初始化平台客户端
        
        Args:
            access_token: 平台访问令牌
            base_url: API基础URL（可选）
        """
        self.access_token = access_token
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def send_message(
        self,
        recipient_id: str,
        message: str,
        message_type: str = "RESPONSE"
    ) -> Dict[str, Any]:
        """
        发送消息到平台
        
        Args:
            recipient_id: 接收者ID
            message: 消息内容
            message_type: 消息类型
        
        Returns:
            API响应
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息字典
        """
        pass
    
    @abstractmethod
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
        pass
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


class PlatformParser(ABC):
    """平台消息解析器抽象基类"""
    
    @abstractmethod
    def parse_webhook_event(self, event: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        解析Webhook事件
        
        Args:
            event: Webhook事件数据
        
        Returns:
            解析后的消息数据列表，如果无法解析则返回None
        """
        pass
    
    @abstractmethod
    def extract_user_info(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        从事件中提取用户信息
        
        Args:
            event: Webhook事件数据
        
        Returns:
            用户信息字典
        """
        pass


class PlatformWebhookHandler(ABC):
    """平台Webhook处理器抽象基类"""
    
    def __init__(self, client: PlatformClient, parser: PlatformParser, verify_token: str):
        """
        初始化Webhook处理器
        
        Args:
            client: 平台API客户端
            parser: 平台消息解析器
            verify_token: Webhook验证令牌
        """
        self.client = client
        self.parser = parser
        self.verify_token = verify_token
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def handle(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        处理Webhook事件
        
        Args:
            event_data: Webhook事件数据
        
        Returns:
            解析后的消息数据列表
        """
        pass







