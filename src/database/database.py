"""数据库连接 - 向后兼容导入"""
# 向后兼容：从新位置导入
from src.core.database.connection import (
    engine,
    SessionLocal,
    Base,
    get_db,
)

__all__ = [
    'engine',
    'SessionLocal',
    'Base',
    'get_db',
]
