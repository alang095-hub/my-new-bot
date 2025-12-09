"""注册Instagram平台到平台注册器"""
from src.platforms.registry import registry
from src.instagram.api_client import InstagramAPIClient
from src.instagram.message_parser import InstagramMessageParser
from src.instagram.webhook_handler_impl import InstagramWebhookHandler


def register_instagram_platform():
    """注册Instagram平台"""
    registry.register(
        platform_name="instagram",
        client_class=InstagramAPIClient,
        parser_class=InstagramMessageParser,
        handler_class=InstagramWebhookHandler
    )


# 自动注册
register_instagram_platform()







