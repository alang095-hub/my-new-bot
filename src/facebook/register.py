"""注册Facebook平台到平台注册器"""
from src.platforms.registry import registry
from src.facebook.api_client import FacebookAPIClient
from src.facebook.message_parser import FacebookMessageParser
from src.facebook.webhook_handler_impl import FacebookWebhookHandler


def register_facebook_platform():
    """注册Facebook平台"""
    registry.register(
        platform_name="facebook",
        client_class=FacebookAPIClient,
        parser_class=FacebookMessageParser,
        handler_class=FacebookWebhookHandler
    )


# 自动注册
register_facebook_platform()







