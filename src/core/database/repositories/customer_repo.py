"""客户Repository"""
from typing import Optional, List
from sqlalchemy.orm import Session
from src.core.database.repositories.base import BaseRepository
from src.core.database.models import Customer, Platform


class CustomerRepository(BaseRepository[Customer]):
    """客户数据访问层"""
    
    def __init__(self, db: Session):
        super().__init__(db, Customer)
    
    def get_by_platform_user_id(
        self, 
        platform: Platform, 
        platform_user_id: str
    ) -> Optional[Customer]:
        """
        根据平台用户ID获取客户
        
        Args:
            platform: 平台类型
            platform_user_id: 平台用户ID
            
        Returns:
            客户实例或None
        """
        return self.get_by(
            platform=platform,
            platform_user_id=platform_user_id
        )
    
    def get_or_create(
        self,
        platform: Platform,
        platform_user_id: str,
        name: Optional[str] = None,
        **kwargs
    ) -> Customer:
        """
        获取或创建客户
        
        Args:
            platform: 平台类型
            platform_user_id: 平台用户ID
            name: 客户名称
            **kwargs: 其他客户字段
            
        Returns:
            客户实例
        """
        customer = self.get_by_platform_user_id(platform, platform_user_id)
        
        if not customer:
            # 创建新客户
            customer_data = {
                "platform": platform,
                "platform_user_id": platform_user_id,
                **kwargs
            }
            if name:
                customer_data["name"] = name
            
            # 兼容字段：如果是Facebook，也设置facebook_id
            if platform == Platform.FACEBOOK:
                customer_data["facebook_id"] = platform_user_id
            
            customer = self.create(**customer_data)
        
        return customer

