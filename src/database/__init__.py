"""数据库模块 - 向后兼容导入"""
# 向后兼容：从新位置导入
from src.core.database import (
    engine,
    SessionLocal,
    Base,
    get_db,
    Customer,
    Conversation,
    Review,
    MessageType,
    ReviewStatus,
    Priority,
    Platform,
)

__all__ = [
    'engine',
    'SessionLocal',
    'Base',
    'get_db',
    'Customer',
    'Conversation',
    'Review',
    'MessageType',
    'ReviewStatus',
    'Priority',
    'Platform',
]
