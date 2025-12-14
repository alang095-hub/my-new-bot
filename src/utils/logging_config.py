"""日志配置 - 向后兼容导入"""
# 向后兼容：从新位置导入
from src.core.logging import (
    setup_logging,
    get_logger,
    StructuredFormatter,
)

__all__ = [
    'setup_logging',
    'get_logger',
    'StructuredFormatter',
]
