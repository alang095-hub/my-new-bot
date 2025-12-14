"""A/B测试管理API"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from src.core.database.connection import get_db
from src.core.database.models import PromptVersion
from src.core.database.repositories.base import BaseRepository
from src.ai.prompt_ab_testing import PromptABTesting
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ab-testing", tags=["admin"])


class PromptVersionCreate(BaseModel):
    """创建提示词版本请求"""
    name: str
    version_code: str
    prompt_content: str
    traffic_percentage: int = 50
    description: Optional[str] = None
    test_start_date: Optional[datetime] = None
    test_end_date: Optional[datetime] = None
    created_by: Optional[str] = None


class PromptVersionUpdate(BaseModel):
    """更新提示词版本请求"""
    name: Optional[str] = None
    prompt_content: Optional[str] = None
    traffic_percentage: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    test_start_date: Optional[datetime] = None
    test_end_date: Optional[datetime] = None


@router.get("/versions")
async def list_versions(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    列出所有提示词版本
    
    Args:
        active_only: 是否只返回启用的
        db: 数据库会话
    
    Returns:
        版本列表
    """
    try:
        version_repo = BaseRepository(db, PromptVersion)
        
        if active_only:
            versions = db.query(PromptVersion).filter(PromptVersion.is_active == True).all()
        else:
            versions = db.query(PromptVersion).all()
        
        return {
            "success": True,
            "data": [
                {
                    "id": v.id,
                    "name": v.name,
                    "version_code": v.version_code,
                    "prompt_content": v.prompt_content[:200] + "..." if len(v.prompt_content) > 200 else v.prompt_content,
                    "is_active": v.is_active,
                    "traffic_percentage": v.traffic_percentage,
                    "total_uses": v.total_uses,
                    "avg_response_time_ms": v.avg_response_time_ms,
                    "description": v.description,
                    "created_at": v.created_at.isoformat() if v.created_at else None
                }
                for v in versions
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list versions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/versions/{version_id}")
async def get_version(
    version_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个版本
    
    Args:
        version_id: 版本ID
        db: 数据库会话
    
    Returns:
        版本信息
    """
    try:
        version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
        
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        
        return {
            "success": True,
            "data": {
                "id": version.id,
                "name": version.name,
                "version_code": version.version_code,
                "prompt_content": version.prompt_content,
                "is_active": version.is_active,
                "traffic_percentage": version.traffic_percentage,
                "total_uses": version.total_uses,
                "avg_response_time_ms": version.avg_response_time_ms,
                "description": version.description,
                "test_start_date": version.test_start_date.isoformat() if version.test_start_date else None,
                "test_end_date": version.test_end_date.isoformat() if version.test_end_date else None,
                "created_at": version.created_at.isoformat() if version.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get version: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/versions")
async def create_version(
    version: PromptVersionCreate,
    db: Session = Depends(get_db)
):
    """
    创建新版本
    
    Args:
        version: 版本信息
        db: 数据库会话
    
    Returns:
        创建的版本
    """
    try:
        # 检查版本代码是否已存在
        existing = db.query(PromptVersion).filter(
            PromptVersion.version_code == version.version_code
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Version code already exists")
        
        new_version = PromptVersion(
            name=version.name,
            version_code=version.version_code,
            prompt_content=version.prompt_content,
            traffic_percentage=version.traffic_percentage,
            description=version.description,
            test_start_date=version.test_start_date,
            test_end_date=version.test_end_date,
            created_by=version.created_by,
            is_active=True
        )
        
        db.add(new_version)
        db.commit()
        db.refresh(new_version)
        
        return {
            "success": True,
            "data": {
                "id": new_version.id,
                "name": new_version.name,
                "version_code": new_version.version_code
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create version: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/versions/{version_id}")
async def update_version(
    version_id: int,
    version: PromptVersionUpdate,
    db: Session = Depends(get_db)
):
    """
    更新版本
    
    Args:
        version_id: 版本ID
        version: 更新信息
        db: 数据库会话
    
    Returns:
        更新后的版本
    """
    try:
        existing = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Version not found")
        
        update_data = version.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing, key, value)
        
        db.commit()
        db.refresh(existing)
        
        return {
            "success": True,
            "data": {
                "id": existing.id,
                "name": existing.name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update version: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/versions/{version_id}/statistics")
async def get_version_statistics(
    version_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取版本统计信息
    
    Args:
        version_id: 版本ID
        start_date: 开始日期（ISO格式）
        end_date: 结束日期（ISO格式）
        db: 数据库会话
    
    Returns:
        统计数据
    """
    try:
        ab_testing = PromptABTesting(db)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        stats = ab_testing.get_version_statistics(version_id, start, end)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get version statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_versions(
    version_ids: List[int] = Body(...),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    对比多个版本的效果
    
    Args:
        version_ids: 版本ID列表
        start_date: 开始日期（ISO格式）
        end_date: 结束日期（ISO格式）
        db: 数据库会话
    
    Returns:
        对比结果
    """
    try:
        ab_testing = PromptABTesting(db)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        comparison = ab_testing.compare_versions(version_ids, start, end)
        
        return {
            "success": True,
            "data": comparison
        }
    except Exception as e:
        logger.error(f"Failed to compare versions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

