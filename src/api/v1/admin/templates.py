"""模板管理API"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.middleware.auth import AuthMiddleware
from src.core.database.connection import get_db
from src.core.templates.template_manager import TemplateManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["admin"])


class TemplateCreate(BaseModel):
    """创建模板请求"""

    name: str
    content: str
    category: Optional[str] = None
    variables: Optional[List[str]] = None
    description: Optional[str] = None
    priority: int = 0
    created_by: Optional[str] = None


class TemplateUpdate(BaseModel):
    """更新模板请求"""

    name: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    variables: Optional[List[str]] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    updated_by: Optional[str] = None


class TemplateRender(BaseModel):
    """渲染模板请求"""

    template_name: Optional[str] = None
    category: Optional[str] = None
    variables: Dict[str, Any]


@router.get("")
async def list_templates(
    category: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    列出所有模板

    Args:
        category: 分类过滤
        active_only: 是否只返回启用的
        db: 数据库会话

    Returns:
        模板列表
    """
    try:
        manager = TemplateManager(db)
        templates = manager.list_templates(category=category, active_only=active_only)

        return {"success": True, "data": templates, "count": len(templates)}
    except Exception as e:
        logger.error(f"Failed to list templates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    获取单个模板

    Args:
        template_id: 模板ID
        db: 数据库会话

    Returns:
        模板信息
    """
    try:
        manager = TemplateManager(db)
        template = manager.template_repo.get(template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        return {
            "success": True,
            "data": {
                "id": template.id,
                "name": template.name,
                "category": template.category,
                "content": template.content,
                "variables": template.variables or [],
                "is_active": template.is_active,
                "priority": template.priority,
                "description": template.description,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    创建新模板

    Args:
        template: 模板信息
        db: 数据库会话

    Returns:
        创建的模板
    """
    try:
        manager = TemplateManager(db)

        # 检查名称是否已存在
        existing = manager.template_repo.get_by_name(template.name)
        if existing:
            raise HTTPException(status_code=400, detail="Template name already exists")

        created_template = manager.create_template(
            name=template.name,
            content=template.content,
            category=template.category,
            variables=template.variables,
            description=template.description,
            priority=template.priority,
            created_by=template.created_by,
        )

        return {
            "success": True,
            "data": {
                "id": created_template.id,
                "name": created_template.name,
                "category": created_template.category,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}")
async def update_template(
    template_id: int,
    template: TemplateUpdate,
    db: Session = Depends(get_db),
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    更新模板

    Args:
        template_id: 模板ID
        template: 更新信息
        db: 数据库会话

    Returns:
        更新后的模板
    """
    try:
        manager = TemplateManager(db)

        # 检查模板是否存在
        existing = manager.template_repo.get(template_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Template not found")

        # 如果更新名称，检查是否冲突
        if template.name and template.name != existing.name:
            name_conflict = manager.template_repo.get_by_name(template.name)
            if name_conflict:
                raise HTTPException(status_code=400, detail="Template name already exists")

        # 构建更新数据
        update_data = template.dict(exclude_unset=True)
        updated_template = manager.update_template(template_id, **update_data)

        if not updated_template:
            raise HTTPException(status_code=404, detail="Template not found")

        return {"success": True, "data": {"id": updated_template.id, "name": updated_template.name}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    删除模板（软删除：设置为非激活）

    Args:
        template_id: 模板ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        manager = TemplateManager(db)
        template = manager.template_repo.get(template_id)

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        # 软删除：设置为非激活
        manager.update_template(template_id, is_active=False)

        return {"success": True, "message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/render")
async def render_template(
    request: TemplateRender,
    db: Session = Depends(get_db),
    user: str = Depends(AuthMiddleware.verify_token),  # 启用认证
):
    """
    渲染模板（预览）

    Args:
        request: 渲染请求
        db: 数据库会话

    Returns:
        渲染后的内容
    """
    try:
        manager = TemplateManager(db)

        rendered = manager.get_template_with_variables(
            name=request.template_name, category=request.category, variables=request.variables
        )

        if not rendered:
            raise HTTPException(status_code=404, detail="Template not found")

        return {"success": True, "data": {"rendered_content": rendered}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to render template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
