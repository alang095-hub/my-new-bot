"""平台注册表 - 管理平台客户端、解析器和处理器的注册"""

import logging
from typing import Any, Dict, Optional, Type

logger = logging.getLogger(__name__)


class PlatformRegistry:
    """平台注册表 - 管理所有平台的注册信息"""

    def __init__(self):
        """初始化注册表"""
        self._clients: Dict[str, Type] = {}
        self._parsers: Dict[str, Type] = {}
        self._webhook_handlers: Dict[str, Any] = {}

    def register_platform(
        self,
        platform_name: str,
        client_class: Optional[Type] = None,
        parser_class: Optional[Type] = None,
        webhook_handler: Optional[Any] = None,
    ):
        """
        注册平台

        Args:
            platform_name: 平台名称
            client_class: 客户端类
            parser_class: 解析器类
            webhook_handler: Webhook处理器
        """
        if client_class:
            self._clients[platform_name] = client_class
        if parser_class:
            self._parsers[platform_name] = parser_class
        if webhook_handler:
            self._webhook_handlers[platform_name] = webhook_handler

        logger.info(f"Platform {platform_name} registered")

    def get_client_class(self, platform_name: str) -> Optional[Type]:
        """获取平台客户端类"""
        return self._clients.get(platform_name)

    def create_client(self, platform_name: str, **kwargs) -> Optional[Any]:
        """
        创建平台客户端实例

        Args:
            platform_name: 平台名称
            **kwargs: 客户端初始化参数（会被忽略，因为客户端从 settings 读取配置）

        Returns:
            客户端实例，如果平台未注册则返回 None
        """
        client_class = self.get_client_class(platform_name)
        if not client_class:
            logger.error(f"Platform {platform_name} is not registered")
            return None

        try:
            # 检查客户端类的初始化签名
            import inspect

            sig = inspect.signature(client_class.__init__)
            params = sig.parameters

            # 构建初始化参数
            init_kwargs = {}

            # 如果客户端需要 db 参数
            if "db" in params:
                init_kwargs["db"] = kwargs.get("db", None)

            # FacebookAPIClient 和 InstagramAPIClient 不接受 access_token 参数
            # 它们直接从 settings 读取配置，所以忽略 kwargs 中的 access_token

            return client_class(**init_kwargs)
        except Exception as e:
            logger.error(
                f"Failed to create client for platform {platform_name}: {str(e)}", exc_info=True
            )
            return None

    def get_parser_class(self, platform_name: str) -> Optional[Type]:
        """获取平台解析器类"""
        return self._parsers.get(platform_name)

    def get_webhook_handler(self, platform_name: str) -> Optional[Any]:
        """获取平台Webhook处理器"""
        return self._webhook_handlers.get(platform_name)

    def list_platforms(self) -> list:
        """列出所有已注册的平台"""
        platforms = set()
        platforms.update(self._clients.keys())
        platforms.update(self._parsers.keys())
        platforms.update(self._webhook_handlers.keys())
        return list(platforms)


# 全局注册表实例
registry = PlatformRegistry()

# 注册Facebook平台
try:
    from src.facebook.api_client import FacebookAPIClient
    from src.facebook.message_parser import FacebookMessageParser
    from src.api.v1.webhooks.facebook import router as facebook_webhook_handler

    registry.register_platform(
        platform_name="facebook",
        client_class=FacebookAPIClient,
        parser_class=FacebookMessageParser,
        webhook_handler=facebook_webhook_handler,
    )
except ImportError as e:
    logger.warning(f"Failed to register Facebook platform: {e}")

# 注册Instagram平台
try:
    from src.instagram.api_client import InstagramAPIClient
    from src.instagram.message_parser import InstagramMessageParser
    from src.api.v1.webhooks.instagram import router as instagram_webhook_handler

    registry.register_platform(
        platform_name="instagram",
        client_class=InstagramAPIClient,
        parser_class=InstagramMessageParser,
        webhook_handler=instagram_webhook_handler,
    )
except ImportError as e:
    logger.warning(f"Failed to register Instagram platform: {e}")
