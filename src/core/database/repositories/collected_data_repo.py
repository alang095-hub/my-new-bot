"""收集数据Repository"""
from typing import Optional
from sqlalchemy.orm import Session
from src.core.database.repositories.base import BaseRepository
from src.core.database.models import CollectedData


class CollectedDataRepository(BaseRepository[CollectedData]):
    """收集数据访问层"""
    
    def __init__(self, db: Session):
        super().__init__(db, CollectedData)
    
    def get_by_conversation_id(self, conversation_id: int) -> Optional[CollectedData]:
        """根据对话ID获取收集数据"""
        return self.get_by(conversation_id=conversation_id)
    
    def create_collected_data(
        self,
        conversation_id: int,
        data: dict,
        is_validated: bool = False,
        validation_errors: Optional[dict] = None
    ) -> CollectedData:
        """创建收集数据记录"""
        return self.create(
            conversation_id=conversation_id,
            data=data,
            is_validated=is_validated,
            validation_errors=validation_errors
        )

