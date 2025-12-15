"""管理后台API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from src.core.database.connection import get_db
from src.core.database.models import Conversation, Customer, Review, CollectedData
from src.api.middleware.auth import AuthMiddleware

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/conversations")
async def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
    # user: str = Depends(AuthMiddleware.verify_token)  # 启用认证
) -> Dict[str, Any]:
    """
    获取对话列表
    
    Args:
        page: 页码
        page_size: 每页数量
        status: 状态过滤
        platform: 平台过滤
        db: 数据库会话
    
    Returns:
        对话列表和分页信息
    """
    from src.core.database.repositories.conversation_repo import ConversationRepository
    conversation_repo = ConversationRepository(db)
    
    conversations, total = conversation_repo.get_by_filters(
        status=status,
        platform=platform,
        skip=(page - 1) * page_size,
        limit=page_size,
        order_by_desc=True
    )
    
    return {
        "data": [
            {
                "id": conv.id,
                "customer_id": conv.customer_id,
                "platform": conv.platform.value if hasattr(conv.platform, 'value') else str(conv.platform),
                "content": conv.content[:200],  # 截断长内容
                "status": conv.status,
                "priority": conv.priority.value if hasattr(conv.priority, 'value') else str(conv.priority),
                "received_at": conv.received_at.isoformat() if conv.received_at else None,
                "ai_replied": conv.ai_replied
            }
            for conv in conversations
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取对话详情"""
    from src.core.database.repositories.conversation_repo import ConversationRepository
    conversation_repo = ConversationRepository(db)
    conversation = conversation_repo.get_by_id(conversation_id)
    
    if not conversation:
        return {"error": "Conversation not found"}
    
    # 获取收集的数据
    collected_data = db.query(CollectedData).filter(
        CollectedData.conversation_id == conversation_id
    ).all()
    
    # 获取审核记录
    reviews = db.query(Review).filter(
        Review.conversation_id == conversation_id
    ).order_by(desc(Review.created_at)).all()
    
    return {
        "conversation": {
            "id": conversation.id,
            "customer_id": conversation.customer_id,
            "platform": conversation.platform.value if hasattr(conversation.platform, 'value') else str(conversation.platform),
            "content": conversation.content,
            "status": conversation.status,
            "priority": conversation.priority.value if hasattr(conversation.priority, 'value') else str(conversation.priority),
            "received_at": conversation.received_at.isoformat() if conversation.received_at else None,
            "ai_replied": conversation.ai_replied,
            "ai_reply_content": conversation.ai_reply_content
        },
        "collected_data": [
            {
                "data": data.data,
                "is_validated": data.is_validated,
                "validation_errors": data.validation_errors
            }
            for data in collected_data
        ],
        "reviews": [
            {
                "id": review.id,
                "status": review.status.value if hasattr(review.status, 'value') else str(review.status),
                "reviewed_by": review.reviewed_by,
                "review_notes": review.review_notes,
                "created_at": review.created_at.isoformat() if review.created_at else None
            }
            for review in reviews
        ]
    }


@router.get("/statistics")
async def get_statistics(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取统计数据"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    from src.core.database.repositories.conversation_repo import ConversationRepository
    conversation_repo = ConversationRepository(db)
    
    # 对话统计
    total_conversations = conversation_repo.count_by_time_range(start_date)
    
    # 按状态统计
    status_stats = conversation_repo.get_status_stats_by_time_range(start_date)
    
    # 按平台统计
    platform_stats = conversation_repo.get_platform_stats_by_time_range(start_date)
    
    # AI回复率
    ai_replied_count = conversation_repo.count_ai_replied_by_time_range(start_date)
    
    ai_reply_rate = (ai_replied_count / total_conversations * 100) if total_conversations > 0 else 0
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "conversations": {
            "total": total_conversations,
            "ai_replied": ai_replied_count,
            "ai_reply_rate": round(ai_reply_rate, 2)
        },
        "by_status": {
            status: count for status, count in status_stats
        },
        "by_platform": {
            str(platform): count for platform, count in platform_stats
        }
    }


@router.get("/customers")
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取客户列表"""
    query = db.query(Customer)
    
    if platform:
        query = query.filter(Customer.platform == platform)
    
    total = query.count()
    
    customers = query.order_by(desc(Customer.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "data": [
            {
                "id": customer.id,
                "platform": customer.platform.value if hasattr(customer.platform, 'value') else str(customer.platform),
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "created_at": customer.created_at.isoformat() if customer.created_at else None
            }
            for customer in customers
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }

