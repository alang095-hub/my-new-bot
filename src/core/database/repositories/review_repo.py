"""审核Repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from src.core.database.repositories.base import BaseRepository
from src.core.database.models import Review, ReviewStatus


class ReviewRepository(BaseRepository[Review]):
    """审核数据访问层"""
    
    def __init__(self, db: Session):
        super().__init__(db, Review)
    
    def get_by_conversation_id(self, conversation_id: int) -> Optional[Review]:
        """根据对话ID获取审核记录"""
        return self.get_by(conversation_id=conversation_id)
    
    def get_by_customer_id(self, customer_id: int) -> List[Review]:
        """根据客户ID获取所有审核记录"""
        return self.get_all(customer_id=customer_id)
    
    def create_review(
        self,
        customer_id: int,
        conversation_id: int,
        status: ReviewStatus = ReviewStatus.PENDING,
        reviewed_by: Optional[str] = None,
        review_notes: Optional[str] = None,
        **kwargs
    ) -> Review:
        """创建审核记录"""
        return self.create(
            customer_id=customer_id,
            conversation_id=conversation_id,
            status=status,
            reviewed_by=reviewed_by,
            review_notes=review_notes,
            **kwargs
        )
    
    def update_review_status(
        self,
        review_id: int,
        status: ReviewStatus,
        reviewed_by: Optional[str] = None,
        review_notes: Optional[str] = None
    ) -> Optional[Review]:
        """更新审核状态"""
        from datetime import datetime, timezone
        return self.update(
            id=review_id,
            status=status,
            reviewed_by=reviewed_by,
            review_notes=review_notes,
            reviewed_at=datetime.now(timezone.utc)
        )

