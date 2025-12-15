"""Repository基类"""
import time
import logging
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.core.database.connection import Base
from src.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repository基类 - 提供通用的数据访问方法"""
    
    def __init__(self, db: Session, model: Type[ModelType]):
        """
        初始化Repository
        
        Args:
            db: 数据库会话
            model: 数据模型类
        """
        self.db = db
        self.model = model
    
    def _log_query_performance(self, operation: str, duration: float, threshold: float = 1.0):
        """
        记录查询性能（如果超过阈值）
        
        Args:
            operation: 操作名称
            duration: 执行时间（秒）
            threshold: 性能阈值（秒）
        """
        if duration > threshold:
            logger.warning(
                f"Slow query detected: {self.model.__name__}.{operation} "
                f"took {duration:.3f}s (threshold: {threshold}s)"
            )
    
    def get(self, id: int) -> Optional[ModelType]:
        """
        根据ID获取记录
        
        Args:
            id: 记录ID
            
        Returns:
            模型实例或None
        """
        start_time = time.time()
        try:
            result = self.db.query(self.model).filter(self.model.id == id).first()
            duration = time.time() - start_time
            self._log_query_performance("get", duration)
            return result
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get {self.model.__name__}: {str(e)}", operation="get")
    
    def get_by(self, **kwargs) -> Optional[ModelType]:
        """
        根据条件获取单条记录
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            模型实例或None
        """
        try:
            return self.db.query(self.model).filter_by(**kwargs).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get {self.model.__name__}: {str(e)}", operation="get_by")
    
    def get_all(self, skip: int = 0, limit: int = 100, **kwargs) -> List[ModelType]:
        """
        获取多条记录
        
        Args:
            skip: 跳过记录数
            limit: 限制记录数
            **kwargs: 查询条件
            
        Returns:
            模型实例列表
        """
        start_time = time.time()
        try:
            query = self.db.query(self.model)
            if kwargs:
                query = query.filter_by(**kwargs)
            result = query.offset(skip).limit(limit).all()
            duration = time.time() - start_time
            self._log_query_performance("get_all", duration)
            return result
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get all {self.model.__name__}: {str(e)}", operation="get_all")
    
    def create(self, **kwargs) -> ModelType:
        """
        创建新记录
        
        Args:
            **kwargs: 模型字段
            
        Returns:
            创建的模型实例
        """
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create {self.model.__name__}: {str(e)}", operation="create")
    
    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        更新记录
        
        Args:
            id: 记录ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的模型实例或None
        """
        try:
            instance = self.get(id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update {self.model.__name__}: {str(e)}", operation="update")
    
    def delete(self, id: int) -> bool:
        """
        删除记录
        
        Args:
            id: 记录ID
            
        Returns:
            是否删除成功
        """
        try:
            instance = self.get(id)
            if not instance:
                return False
            
            self.db.delete(instance)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete {self.model.__name__}: {str(e)}", operation="delete")
    
    def count(self, **kwargs) -> int:
        """
        统计记录数
        
        Args:
            **kwargs: 查询条件
            
        Returns:
            记录数
        """
        try:
            query = self.db.query(self.model)
            if kwargs:
                query = query.filter_by(**kwargs)
            return query.count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to count {self.model.__name__}: {str(e)}", operation="count")

