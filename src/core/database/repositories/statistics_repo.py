"""统计数据Repository"""
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from src.core.database.repositories.base import BaseRepository
from src.core.database.statistics_models import DailyStatistics, CustomerInteraction, FrequentQuestion


class DailyStatisticsRepository(BaseRepository[DailyStatistics]):
    """每日统计数据访问层"""
    
    def __init__(self, db: Session):
        super().__init__(db, DailyStatistics)
    
    def get_by_date(self, target_date: date) -> Optional[DailyStatistics]:
        """根据日期获取统计数据"""
        return self.get_by(date=target_date)
    
    def get_or_create_by_date(self, target_date: date) -> DailyStatistics:
        """获取或创建指定日期的统计数据"""
        stats = self.get_by_date(target_date)
        if not stats:
            stats = self.create(date=target_date)
        return stats


class CustomerInteractionRepository(BaseRepository[CustomerInteraction]):
    """客户交互记录访问层"""
    
    def __init__(self, db: Session):
        super().__init__(db, CustomerInteraction)
    
    def get_by_customer_and_date(
        self,
        customer_id: int,
        target_date: date
    ) -> list[CustomerInteraction]:
        """根据客户ID和日期获取交互记录"""
        return self.get_all(
            customer_id=customer_id,
            date=target_date
        )
    
    def create_interaction(
        self,
        customer_id: int,
        date: date,
        platform: str,
        message_type: str,
        message_summary: str,
        extracted_info: dict,
        ai_replied: bool = False,
        group_invitation_sent: bool = False,
        **kwargs
    ) -> CustomerInteraction:
        """创建客户交互记录"""
        return self.create(
            customer_id=customer_id,
            date=date,
            platform=platform,
            message_type=message_type,
            message_summary=message_summary,
            extracted_info=extracted_info,
            ai_replied=ai_replied,
            group_invitation_sent=group_invitation_sent,
            **kwargs
        )


class FrequentQuestionRepository(BaseRepository[FrequentQuestion]):
    """高频问题访问层"""
    
    def __init__(self, db: Session):
        super().__init__(db, FrequentQuestion)
    
    def get_by_question_text(self, question_text: str) -> Optional[FrequentQuestion]:
        """根据问题文本获取记录"""
        return self.get_by(question_text=question_text)
    
    def increment_occurrence(self, question_text: str) -> FrequentQuestion:
        """增加问题出现次数"""
        question = self.get_by_question_text(question_text)
        if question:
            question = self.update(
                id=question.id,
                occurrence_count=question.occurrence_count + 1
            )
        else:
            question = self.create(question_text=question_text, occurrence_count=1)
        return question

