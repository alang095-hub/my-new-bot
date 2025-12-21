"""Instagram 集成模块"""

# Webhook handler 已移至 src/api/v1/webhooks/instagram.py
# 本模块仅提供API客户端和消息解析器

from .api_client import InstagramAPIClient
from .message_parser import InstagramMessageParser

__all__ = [
    "InstagramAPIClient",
    "InstagramMessageParser",
]
