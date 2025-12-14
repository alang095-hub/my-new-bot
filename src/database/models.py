"""数据库模型 - 向后兼容导入"""
# 向后兼容：从新位置导入
from src.core.database.models import (
    Customer,
    Conversation,
    Review,
    CollectedData,
    IntegrationLog,
    MessageType,
    ReviewStatus,
    Priority,
    Platform,
)

__all__ = [
    'Customer',
    'Conversation',
    'Review',
    'CollectedData',
    'IntegrationLog',
    'MessageType',
    'ReviewStatus',
    'Priority',
    'Platform',
]
