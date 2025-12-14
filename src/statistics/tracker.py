"""统计数据追踪器"""
from datetime import date, datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from src.core.database.statistics_models import DailyStatistics, CustomerInteraction, FrequentQuestion
from src.core.database.repositories import (
    DailyStatisticsRepository,
    CustomerInteractionRepository,
    FrequentQuestionRepository
)
import logging

logger = logging.getLogger(__name__)


class StatisticsTracker:
    """统计数据追踪器"""
    
    def __init__(self, db: Session):
        self.db = db
        # 使用Repository模式
        self.daily_stats_repo = DailyStatisticsRepository(db)
        self.interaction_repo = CustomerInteractionRepository(db)
        self.frequent_question_repo = FrequentQuestionRepository(db)
    
    def get_or_create_daily_statistics(self, target_date: Optional[date] = None) -> DailyStatistics:
        """获取或创建每日统计数据"""
        if target_date is None:
            # 使用UTC时区的今天日期
            target_date = datetime.now(timezone.utc).date()
        
        # 使用Repository获取或创建
        return self.daily_stats_repo.get_or_create_by_date(target_date)
    
    def record_customer_interaction(
        self,
        customer_id: int,
        platform: str,
        message_type: str,
        message_summary: str,
        extracted_info: Dict[str, Any],
        ai_replied: bool = False,
        group_invitation_sent: bool = False
    ) -> CustomerInteraction:
        """
        记录客户交互（不保存详细聊天记录）
        
        Args:
            customer_id: 客户ID
            platform: 平台名称
            message_type: 消息类型
            message_summary: 消息摘要（最多500字符）
            extracted_info: 提取的关键信息
            ai_replied: 是否AI回复
            group_invitation_sent: 是否发送群组邀请
            
        Returns:
            创建的交互记录
        """
        # 截断摘要到500字符
        if len(message_summary) > 500:
            message_summary = message_summary[:497] + "..."
        
        # 使用Repository创建交互记录
        interaction = self.interaction_repo.create_interaction(
            customer_id=customer_id,
            date=datetime.now(timezone.utc).date(),
            platform=platform,
            message_type=message_type,
            message_summary=message_summary,
            extracted_info=extracted_info,
            ai_replied=ai_replied,
            group_invitation_sent=group_invitation_sent
        )
        
        # 更新每日统计
        self._update_daily_statistics()
        
        return interaction
    
    def mark_joined_group(self, customer_id: int) -> bool:
        """标记客户已加入群组"""
        today = datetime.now(timezone.utc).date()
        
        # 使用Repository获取今天的交互记录
        interactions = self.interaction_repo.get_by_customer_and_date(customer_id, today)
        
        # 过滤未加入群组的记录
        interactions_to_update = [
            i for i in interactions 
            if not i.joined_group
        ]
        
        # 更新记录
        updated = False
        for interaction in interactions_to_update:
            self.interaction_repo.update(
                id=interaction.id,
                joined_group=True
            )
            updated = True
        
        if updated:
            self._update_daily_statistics()
            return True
        
        return False
    
    def mark_order_created(self, customer_id: int) -> bool:
        """标记客户已开单"""
        today = datetime.now(timezone.utc).date()
        
        # 使用Repository获取今天的交互记录
        interactions = self.interaction_repo.get_by_customer_and_date(customer_id, today)
        
        # 过滤未开单的记录
        interactions_to_update = [
            i for i in interactions 
            if not i.order_created
        ]
        
        # 更新记录
        updated = False
        for interaction in interactions_to_update:
            self.interaction_repo.update(
                id=interaction.id,
                order_created=True
            )
            updated = True
        
        if updated:
            self._update_daily_statistics()
            return True
        
        return False
    
    def record_frequent_question(self, question_text: str, category: str = None, sample_response: str = None):
        """记录高频问题"""
        # 清理问题文本
        question_text = question_text.strip()[:500]
        
        if not question_text:
            return
        
        # 使用Repository增加问题出现次数
        question = self.frequent_question_repo.increment_occurrence(question_text)
        
        # 更新其他字段
        update_data = {
            "last_seen": datetime.now(timezone.utc)
        }
        
        if category:
            update_data["question_category"] = category
        
        # 更新示例回复（保留最新的几个）
        if sample_response:
            sample_responses = question.sample_responses or []
            sample_responses.append({
                "response": sample_response[:200],
                "time": datetime.now(timezone.utc).isoformat()
            })
            # 只保留最近5个
            update_data["sample_responses"] = sample_responses[-5:]
        
        # 更新记录
        if update_data:
            self.frequent_question_repo.update(question.id, **update_data)
    
    def _update_daily_statistics(self):
        """更新每日统计数据"""
        # 使用UTC时区的今天日期
        today = datetime.now(timezone.utc).date()
        stats = self.get_or_create_daily_statistics(today)
        
        # 统计今天的客户数
        total_customers = self.db.query(sql_func.count(sql_func.distinct(CustomerInteraction.customer_id)))\
            .filter(CustomerInteraction.date == today)\
            .scalar() or 0
        
        # 统计今天的消息数
        total_messages = self.db.query(sql_func.count(CustomerInteraction.id))\
            .filter(CustomerInteraction.date == today)\
            .scalar() or 0
        
        # 统计发送的群组邀请数
        group_invitations_sent = self.db.query(sql_func.count(CustomerInteraction.id))\
            .filter(
                CustomerInteraction.date == today,
                CustomerInteraction.group_invitation_sent == True
            )\
            .scalar() or 0
        
        # 统计成功引流数（加入群组）
        successful_leads = self.db.query(sql_func.count(sql_func.distinct(CustomerInteraction.customer_id)))\
            .filter(
                CustomerInteraction.date == today,
                CustomerInteraction.joined_group == True
            )\
            .scalar() or 0
        
        # 统计开单数
        total_orders = self.db.query(sql_func.count(CustomerInteraction.id))\
            .filter(
                CustomerInteraction.date == today,
                CustomerInteraction.order_created == True
            )\
            .scalar() or 0
        
        successful_orders = self.db.query(sql_func.count(sql_func.distinct(CustomerInteraction.customer_id)))\
            .filter(
                CustomerInteraction.date == today,
                CustomerInteraction.order_created == True
            )\
            .scalar() or 0
        
        # 计算转化率
        lead_conversion_rate = "0%"
        if group_invitations_sent > 0:
            rate = (successful_leads / group_invitations_sent) * 100
            lead_conversion_rate = f"{rate:.1f}%"
        
        order_conversion_rate = "0%"
        if successful_leads > 0:
            rate = (successful_orders / successful_leads) * 100
            order_conversion_rate = f"{rate:.1f}%"
        
        # 更新统计数据
        stats.total_customers = total_customers
        stats.total_messages = total_messages
        stats.group_invitations_sent = group_invitations_sent
        stats.successful_leads = successful_leads
        stats.lead_conversion_rate = lead_conversion_rate
        stats.total_orders = total_orders
        stats.successful_orders = successful_orders
        stats.order_conversion_rate = order_conversion_rate
        
        self.db.commit()
        self.db.refresh(stats)
    
    def get_daily_statistics(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """获取每日统计数据"""
        if target_date is None:
            # 使用UTC时区的今天日期
            target_date = datetime.now(timezone.utc).date()
        
        stats = self.get_or_create_daily_statistics(target_date)
        
        return {
            "date": stats.date.isoformat(),
            "total_customers": stats.total_customers,
            "new_customers": stats.new_customers,
            "returning_customers": stats.returning_customers,
            "total_messages": stats.total_messages,
            "group_invitations_sent": stats.group_invitations_sent,
            "successful_leads": stats.successful_leads,
            "lead_conversion_rate": stats.lead_conversion_rate,
            "total_orders": stats.total_orders,
            "successful_orders": stats.successful_orders,
            "order_conversion_rate": stats.order_conversion_rate,
            "frequent_questions": stats.frequent_questions or {}
        }
    
    def get_frequent_questions(self, limit: int = 20) -> list:
        """获取高频问题列表"""
        # 使用Repository获取所有问题，然后排序
        all_questions = self.frequent_question_repo.get_all(limit=limit * 2)  # 获取更多以便排序
        # 按出现次数排序
        questions = sorted(all_questions, key=lambda x: x.occurrence_count, reverse=True)[:limit]
        
        return [
            {
                "id": q.id,
                "question": q.question_text,
                "category": q.question_category,
                "count": q.occurrence_count,
                "first_seen": q.first_seen.isoformat() if q.first_seen else None,
                "last_seen": q.last_seen.isoformat() if q.last_seen else None,
                "sample_responses": q.sample_responses or []
            }
            for q in questions
        ]


