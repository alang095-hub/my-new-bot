"""模板管理器"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from src.core.database.models import ReplyTemplate
from src.core.database.repositories.base import BaseRepository
import re
import logging

logger = logging.getLogger(__name__)


class TemplateRepository(BaseRepository[ReplyTemplate]):
    """模板Repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, ReplyTemplate)
    
    def get_active_templates(self, category: Optional[str] = None) -> List[ReplyTemplate]:
        """获取启用的模板"""
        query = self.db.query(self.model).filter(self.model.is_active == True)
        if category:
            query = query.filter(self.model.category == category)
        return query.order_by(self.model.priority.desc(), self.model.created_at.desc()).all()
    
    def get_by_name(self, name: str) -> Optional[ReplyTemplate]:
        """根据名称获取模板"""
        return self.get_by(name=name)


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.template_repo = TemplateRepository(db)
    
    def get_template(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[str]:
        """
        获取模板内容
        
        Args:
            name: 模板名称
            category: 模板分类
        
        Returns:
            模板内容，如果未找到则返回None
        """
        if name:
            template = self.template_repo.get_by_name(name)
        else:
            templates = self.template_repo.get_active_templates(category)
            if not templates:
                return None
            # 选择优先级最高的
            template = templates[0]
        
        if not template or not template.is_active:
            return None
        
        return template.content
    
    def render_template(
        self,
        template_content: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        渲染模板（替换变量）
        
        Args:
            template_content: 模板内容
            variables: 变量字典
        
        Returns:
            渲染后的内容
        """
        result = template_content
        
        # 替换变量：{{variable_name}}
        pattern = r'\{\{(\w+)\}\}'
        
        def replace_var(match):
            var_name = match.group(1)
            value = variables.get(var_name, match.group(0))  # 如果变量不存在，保留原样
            return str(value)
        
        result = re.sub(pattern, replace_var, result)
        
        return result
    
    def get_template_with_variables(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        获取模板并渲染变量
        
        Args:
            name: 模板名称
            category: 模板分类
            variables: 变量字典
        
        Returns:
            渲染后的模板内容
        """
        template_content = self.get_template(name, category)
        if not template_content:
            return None
        
        if variables:
            return self.render_template(template_content, variables)
        
        return template_content
    
    def create_template(
        self,
        name: str,
        content: str,
        category: Optional[str] = None,
        variables: Optional[List[str]] = None,
        description: Optional[str] = None,
        priority: int = 0,
        created_by: Optional[str] = None
    ) -> ReplyTemplate:
        """
        创建模板
        
        Args:
            name: 模板名称
            content: 模板内容
            category: 模板分类
            variables: 可用变量列表
            description: 模板描述
            priority: 优先级
            created_by: 创建人
        
        Returns:
            创建的模板
        """
        return self.template_repo.create(
            name=name,
            content=content,
            category=category,
            variables=variables or [],
            description=description,
            priority=priority,
            created_by=created_by,
            is_active=True
        )
    
    def update_template(
        self,
        template_id: int,
        **kwargs
    ) -> Optional[ReplyTemplate]:
        """
        更新模板
        
        Args:
            template_id: 模板ID
            **kwargs: 要更新的字段
        
        Returns:
            更新后的模板
        """
        return self.template_repo.update(template_id, **kwargs)
    
    def list_templates(
        self,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        列出模板
        
        Args:
            category: 分类过滤
            active_only: 是否只返回启用的
        
        Returns:
            模板列表
        """
        if active_only:
            templates = self.template_repo.get_active_templates(category)
        else:
            templates = self.template_repo.get_all()
            if category:
                templates = [t for t in templates if t.category == category]
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "content": t.content,
                "variables": t.variables or [],
                "is_active": t.is_active,
                "priority": t.priority,
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None
            }
            for t in templates
        ]

