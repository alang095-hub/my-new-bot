"""统计数据API接口"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.core.database.connection import get_db
from src.statistics.tracker import StatisticsTracker
from datetime import date, datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/daily")
async def get_daily_statistics(
    target_date: Optional[str] = Query(None, description="日期，格式：YYYY-MM-DD，默认为今天"),
    db: Session = Depends(get_db)
):
    """
    获取每日统计数据
    
    返回：
    - 总接待客户数
    - 总消息数
    - 发送的群组邀请数
    - 成功引流数
    - 引流转化率
    - 总开单数
    - 成功开单数
    - 开单转化率
    - 高频问题
    """
    try:
        tracker = StatisticsTracker(db)
        
        if target_date:
            try:
                target = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                return {"error": "日期格式错误，请使用 YYYY-MM-DD 格式"}
        else:
            target = None
        
        stats = tracker.get_daily_statistics(target)
        return {"success": True, "data": stats}
    
    except Exception as e:
        logger.error(f"Error getting daily statistics: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/frequent-questions")
async def get_frequent_questions(
    limit: int = Query(20, description="返回的问题数量，默认20"),
    db: Session = Depends(get_db)
):
    """
    获取高频问题列表
    
    返回按出现次数排序的问题列表
    """
    try:
        tracker = StatisticsTracker(db)
        questions = tracker.get_frequent_questions(limit)
        return {"success": True, "data": questions, "count": len(questions)}
    
    except Exception as e:
        logger.error(f"Error getting frequent questions: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.post("/mark-joined-group")
async def mark_joined_group(
    customer_id: int = Query(..., description="客户ID"),
    db: Session = Depends(get_db)
):
    """
    标记客户已加入群组（手动标记）
    
    用于在Telegram群组中确认客户已加入时调用
    """
    try:
        tracker = StatisticsTracker(db)
        success = tracker.mark_joined_group(customer_id)
        
        if success:
            return {"success": True, "message": f"客户 {customer_id} 已标记为加入群组"}
        else:
            return {"success": False, "message": "未找到该客户今天的交互记录"}
    
    except Exception as e:
        logger.error(f"Error marking joined group: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.post("/mark-order-created")
async def mark_order_created(
    customer_id: int = Query(..., description="客户ID"),
    db: Session = Depends(get_db)
):
    """
    标记客户已开单（手动标记）
    
    用于确认客户已成功开单时调用
    """
    try:
        tracker = StatisticsTracker(db)
        success = tracker.mark_order_created(customer_id)
        
        if success:
            return {"success": True, "message": f"客户 {customer_id} 已标记为开单"}
        else:
            return {"success": False, "message": "未找到该客户今天的交互记录"}
    
    except Exception as e:
        logger.error(f"Error marking order created: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/summary")
async def get_statistics_summary(
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    获取统计摘要（多日汇总）
    
    如果不提供日期，返回最近7天的汇总
    """
    try:
        from datetime import timedelta
        from sqlalchemy import func as sql_func
        from src.core.database.statistics_models import DailyStatistics
        
        tracker = StatisticsTracker(db)
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                return {"error": "日期格式错误，请使用 YYYY-MM-DD 格式"}
        else:
            # 默认最近7天（使用UTC时区）
            end = datetime.now(timezone.utc).date()
            start = end - timedelta(days=6)
        
        # 查询日期范围内的统计数据
        stats_list = db.query(DailyStatistics)\
            .filter(
                DailyStatistics.date >= start,
                DailyStatistics.date <= end
            )\
            .order_by(DailyStatistics.date)\
            .all()
        
        # 汇总数据
        summary = {
            "period": {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "days": (end - start).days + 1
            },
            "total_customers": sum(s.total_customers for s in stats_list),
            "total_messages": sum(s.total_messages for s in stats_list),
            "total_invitations": sum(s.group_invitations_sent for s in stats_list),
            "total_leads": sum(s.successful_leads for s in stats_list),
            "total_orders": sum(s.total_orders for s in stats_list),
            "successful_orders": sum(s.successful_orders for s in stats_list),
            "daily_details": [
                {
                    "date": s.date.isoformat(),
                    "customers": s.total_customers,
                    "messages": s.total_messages,
                    "leads": s.successful_leads,
                    "orders": s.successful_orders,
                    "lead_conversion_rate": s.lead_conversion_rate,
                    "order_conversion_rate": s.order_conversion_rate
                }
                for s in stats_list
            ]
        }
        
        # 计算总体转化率
        if summary["total_invitations"] > 0:
            summary["overall_lead_rate"] = f"{(summary['total_leads'] / summary['total_invitations'] * 100):.1f}%"
        else:
            summary["overall_lead_rate"] = "0%"
        
        if summary["total_leads"] > 0:
            summary["overall_order_rate"] = f"{(summary['successful_orders'] / summary['total_leads'] * 100):.1f}%"
        else:
            summary["overall_order_rate"] = "0%"
        
        return {"success": True, "data": summary}
    
    except Exception as e:
        logger.error(f"Error getting statistics summary: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/ai-replies")
async def get_ai_replies(
    limit: int = Query(50, description="返回的记录数量，默认50"),
    offset: int = Query(0, description="偏移量，用于分页"),
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    获取AI回复记录
    
    返回所有AI回复的内容、时间、客户信息等
    """
    try:
        from src.core.database.models import Conversation, Customer
        from sqlalchemy import and_
        
        from src.core.database.repositories.conversation_repo import ConversationRepository
        conversation_repo = ConversationRepository(db)
        
        # 日期过滤（使用UTC时区）
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                start_dt = datetime.combine(start, datetime.min.time(), timezone.utc)
            except ValueError:
                return {"error": "开始日期格式错误，请使用 YYYY-MM-DD 格式"}
        
        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                end_dt = datetime.combine(end, datetime.max.time(), timezone.utc)
            except ValueError:
                return {"error": "结束日期格式错误，请使用 YYYY-MM-DD 格式"}
        
        # 使用Repository获取数据
        conversations, total = conversation_repo.get_ai_replied_with_customer(
            start_date=start_dt,
            end_date=end_dt,
            skip=(page - 1) * page_size,
            limit=page_size
        )
        
        # 格式化结果
        results = []
        for conv in conversations:
            # 确保时间有时区信息（如果数据库返回的时间没有时区，假设是UTC）
            ai_reply_at = conv.ai_reply_at
            if ai_reply_at and ai_reply_at.tzinfo is None:
                ai_reply_at = ai_reply_at.replace(tzinfo=timezone.utc)
            
            received_at = conv.received_at
            if received_at and received_at.tzinfo is None:
                received_at = received_at.replace(tzinfo=timezone.utc)
            
            results.append({
                "id": conv.id,
                "conversation_id": conv.id,
                "customer_id": conv.customer_id,
                "customer_name": conv.customer.name if conv.customer else None,
                "platform": conv.platform.value if conv.platform else None,
                "message_type": conv.message_type.value if conv.message_type else None,
                "user_message": conv.content[:200] if conv.content else None,  # 用户消息（前200字符）
                "ai_reply": conv.ai_reply_content,
                "ai_reply_at": ai_reply_at.isoformat() if ai_reply_at else None,  # ISO格式包含时区
                "received_at": received_at.isoformat() if received_at else None,  # ISO格式包含时区
            })
        
        return {
            "success": True,
            "data": results,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting AI replies: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/ai-replies/count")
async def get_ai_replies_count(
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    获取AI回复数量统计
    
    返回指定日期范围内的AI回复总数和每日统计
    """
    try:
        from src.core.database.models import Conversation
        from datetime import timedelta
        from sqlalchemy import func, cast, Date
        
        # 构建查询
        query = db.query(Conversation)\
            .filter(Conversation.ai_replied == True)\
            .filter(Conversation.ai_reply_content.isnot(None))
        
        # 日期过滤（使用UTC时区）
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                start_dt = datetime.combine(start, datetime.min.time(), timezone.utc)
                query = query.filter(Conversation.ai_reply_at >= start_dt)
            except ValueError:
                return {"error": "开始日期格式错误，请使用 YYYY-MM-DD 格式"}
        
        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                end_dt = datetime.combine(end, datetime.max.time(), timezone.utc)
                query = query.filter(Conversation.ai_reply_at <= end_dt)
            except ValueError:
                return {"error": "结束日期格式错误，请使用 YYYY-MM-DD 格式"}
        
        # 如果没有指定日期，默认今天（UTC时区）
        if not start_date and not end_date:
            today_utc = datetime.now(timezone.utc).date()
            today_start = datetime.combine(today_utc, datetime.min.time(), timezone.utc)
            today_end = datetime.combine(today_utc + timedelta(days=1), datetime.min.time(), timezone.utc)
            query = query.filter(
                Conversation.ai_reply_at >= today_start,
                Conversation.ai_reply_at < today_end
            )
        
        total_count = query.count()
        
        # 按日期分组统计
        daily_query = db.query(
            cast(Conversation.ai_reply_at, Date).label('date'),
            func.count(Conversation.id).label('count')
        )\
        .filter(Conversation.ai_replied == True)\
        .filter(Conversation.ai_reply_content.isnot(None))
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            start_dt = datetime.combine(start, datetime.min.time(), timezone.utc)
            daily_query = daily_query.filter(Conversation.ai_reply_at >= start_dt)
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            end_dt = datetime.combine(end, datetime.max.time(), timezone.utc)
            daily_query = daily_query.filter(Conversation.ai_reply_at <= end_dt)
        
        daily_counts = daily_query\
            .group_by(cast(Conversation.ai_reply_at, Date))\
            .order_by(cast(Conversation.ai_reply_at, Date).desc())\
            .all()
        
        daily_stats = [
            {
                "date": str(row.date),
                "count": row.count
            }
            for row in daily_counts
        ]
        
        return {
            "success": True,
            "data": {
                "total_count": total_count,
                "daily_breakdown": daily_stats
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting AI replies count: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


