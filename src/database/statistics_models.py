"""统计数据模型 - 向后兼容导入"""
# 向后兼容：从新位置导入
from src.core.database.statistics_models import (
    DailyStatistics,
    CustomerInteraction,
    FrequentQuestion,
)

__all__ = [
    'DailyStatistics',
    'CustomerInteraction',
    'FrequentQuestion',
]
