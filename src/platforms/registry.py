"""平台注册器"""
from typing import Dict, Type, Optional
from src.platforms.base import PlatformClient, PlatformParser, PlatformWebhookHandler
import logging

logger = logging.getLogger(__name__)


class PlatformRegistry:
    """平台注册管理器"""
    
    _instance = None
    _clients: Dict[str, Type[PlatformClient]] = {}
    _parsers: Dict[str, Type[PlatformParser]] = {}
    _handlers: Dict[str, Type[PlatformWebhookHandler]] = {}
    _instances: Dict[str, Dict[str, any]] = {}
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(PlatformRegistry, cls).__new__(cls)
        return cls._instance
    
    def register(
        self,
        platform_name: str,
        client_class: Type[PlatformClient],
        parser_class: Type[PlatformParser],
        handler_class: Type[PlatformWebhookHandler]
    ):
        """
        注册平台实现
        
        Args:
            platform_name: 平台名称（如 'facebook', 'instagram'）
            client_class: API客户端类
            parser_class: 消息解析器类
            handler_class: Webhook处理器类
        """
        self._clients[platform_name] = client_class
        self._parsers[platform_name] = parser_class
        self._handlers[platform_name] = handler_class
        logger.info(f"Registered platform: {platform_name}")
    
    def get_client_class(self, platform_name: str) -> Optional[Type[PlatformClient]]:
        """获取平台客户端类"""
        return self._clients.get(platform_name)
    
    def get_parser_class(self, platform_name: str) -> Optional[Type[PlatformParser]]:
        """获取平台解析器类"""
        return self._parsers.get(platform_name)
    
    def get_handler_class(self, platform_name: str) -> Optional[Type[PlatformWebhookHandler]]:
        """获取平台处理器类"""
        return self._handlers.get(platform_name)
    
    def create_client(self, platform_name: str, **kwargs) -> Optional[PlatformClient]:
        """
        创建平台客户端实例
        
        Args:
            platform_name: 平台名称
            **kwargs: 客户端初始化参数
        
        Returns:
            平台客户端实例
        """
        client_class = self.get_client_class(platform_name)
        if client_class:
            return client_class(**kwargs)
        logger.warning(f"Client class not found for platform: {platform_name}")
        return None
    
    def create_parser(self, platform_name: str) -> Optional[PlatformParser]:
        """
        创建平台解析器实例
        
        Args:
            platform_name: 平台名称
        
        Returns:
            平台解析器实例
        """
        parser_class = self.get_parser_class(platform_name)
        if parser_class:
            return parser_class()
        logger.warning(f"Parser class not found for platform: {platform_name}")
        return None
    
    def create_handler(
        self,
        platform_name: str,
        client: PlatformClient,
        parser: PlatformParser,
        verify_token: str
    ) -> Optional[PlatformWebhookHandler]:
        """
        创建平台处理器实例
        
        Args:
            platform_name: 平台名称
            client: 平台客户端实例
            parser: 平台解析器实例
            verify_token: 验证令牌
        
        Returns:
            平台处理器实例
        """
        handler_class = self.get_handler_class(platform_name)
        if handler_class:
            return handler_class(client, parser, verify_token)
        logger.warning(f"Handler class not found for platform: {platform_name}")
        return None
    
    def list_platforms(self) -> list:
        """列出所有已注册的平台"""
        return list(self._clients.keys())
    
    def is_registered(self, platform_name: str) -> bool:
        """检查平台是否已注册"""
        return platform_name in self._clients


# 全局注册器实例
registry = PlatformRegistry()







