"""API使用量监控API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone, timedelta
from src.core.database.connection import get_db
from src.monitoring.api_usage_tracker import APIUsageTracker
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api-usage", tags=["monitoring"])


@router.get("/statistics")
async def get_api_usage_statistics(
    api_type: Optional[str] = Query(None, description="API类型过滤 (openai, facebook, telegram)"),
    days: int = Query(1, description="统计天数，默认1天"),
    db: Session = Depends(get_db)
):
    """
    获取API使用统计
    
    Args:
        api_type: API类型过滤
        days: 统计天数
        db: 数据库会话
    
    Returns:
        API使用统计数据
    """
    try:
        tracker = APIUsageTracker(db)
        
        if days == 1:
            # 今日统计
            stats = tracker.get_daily_statistics()
        else:
            # 多日统计
            end_date = datetime.now(timezone.utc)
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days-1)
            stats = tracker.get_statistics(
                api_type=api_type,
                start_date=start_date,
                end_date=end_date
            )
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get API usage statistics: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/daily")
async def get_daily_api_usage(
    date: Optional[str] = Query(None, description="日期，格式：YYYY-MM-DD，默认为今天"),
    db: Session = Depends(get_db)
):
    """
    获取指定日期的API使用统计
    
    Args:
        date: 日期字符串
        db: 数据库会话
    
    Returns:
        每日统计数据
    """
    try:
        tracker = APIUsageTracker(db)
        
        if date:
            target_date = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
        else:
            target_date = None
        
        stats = tracker.get_daily_statistics(target_date)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get daily API usage: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

