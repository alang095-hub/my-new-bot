"""数据访问层 - Repository模式"""
from .base import BaseRepository
from .customer_repo import CustomerRepository
from .conversation_repo import ConversationRepository
from .statistics_repo import (
    DailyStatisticsRepository,
    CustomerInteractionRepository,
    FrequentQuestionRepository
)
from .collected_data_repo import CollectedDataRepository
from .review_repo import ReviewRepository

__all__ = [
    'BaseRepository',
    'CustomerRepository',
    'ConversationRepository',
    'DailyStatisticsRepository',
    'CustomerInteractionRepository',
    'FrequentQuestionRepository',
    'CollectedDataRepository',
    'ReviewRepository',
]

