"""Summary notification scheduler - Periodically send statistical summaries"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from src.core.config import yaml_config
from src.telegram.notification_sender import NotificationSender
from src.core.database.models import Conversation
from src.core.database.repositories import ConversationRepository

logger = logging.getLogger(__name__)


class SummaryScheduler:
    """Summary notification scheduler"""

    def __init__(self, db: Session):
        self.db = db
        self.notification_sender = NotificationSender()
        self.notifications_config = yaml_config.get(
            "telegram", {}).get("notifications", {})
        self.running = False
        self._task: Optional[asyncio.Task] = None
        # 使用Repository模式
        self.conversation_repo = ConversationRepository(db)

    def start(self):
        """Start scheduler"""
        if self.running:
            logger.warning("Summary scheduler is already running")
            return

        # Check if summary notifications are enabled
        if not self.notifications_config.get("enable_summary_notifications", True):
            logger.info("Summary notifications are disabled")
            return

        self.running = True
        self._task = asyncio.create_task(self._run_scheduler())
        logger.info("Summary scheduler started")

    def stop(self):
        """Stop scheduler"""
        self.running = False
        if self._task:
            self._task.cancel()
        logger.info("Summary scheduler stopped")

    async def _run_scheduler(self):
        """Run scheduler main loop"""
        try:
            while self.running:
                await self._wait_for_next_schedule()
                if self.running:
                    await self.send_summary()
        except asyncio.CancelledError:
            logger.info("Summary scheduler cancelled")
        except Exception as e:
            logger.error(
                f"Error in summary scheduler: {str(e)}", exc_info=True)

    async def _wait_for_next_schedule(self):
        """等待到下一次调度时间"""
        frequency = self.notifications_config.get("summary_frequency", "daily")

        if frequency == "disabled":
            # 如果禁用，等待很长时间但不发送
            await asyncio.sleep(86400)  # 24小时
            return

        if frequency == "hourly":
            # 每小时发送，等待到下一个整点
            now = datetime.now()
            next_hour = (now + timedelta(hours=1)
                         ).replace(minute=0, second=0, microsecond=0)
            wait_seconds = (next_hour - now).total_seconds()
            await asyncio.sleep(wait_seconds)
        elif frequency == "daily":
            # 每天发送，等待到指定时间
            summary_time_str = self.notifications_config.get(
                "summary_time", "09:00")
            hour, minute = map(int, summary_time_str.split(":"))

            now = datetime.now()
            target_time = now.replace(
                hour=hour, minute=minute, second=0, microsecond=0)

            # 如果今天的目标时间已过，等待到明天
            if target_time <= now:
                target_time += timedelta(days=1)

            wait_seconds = (target_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)
        else:
            # 未知频率，等待24小时
            await asyncio.sleep(86400)

    async def send_summary(self):
        """发送汇总通知"""
        try:
            frequency = self.notifications_config.get(
                "summary_frequency", "daily")
            summary_data = self._collect_statistics(frequency)

            await self.notification_sender.send_summary_notification(summary_data)

        except Exception as e:
            logger.error(f"Error sending summary: {str(e)}", exc_info=True)

    def _collect_statistics(self, period: str) -> Dict[str, Any]:
        """
        收集统计数据

        Args:
            period: 统计周期 ("hourly", "daily")

        Returns:
            统计数据字典
        """
        now = datetime.now()

        # 根据周期计算时间范围
        if period == "hourly":
            start_time = now - timedelta(hours=1)
            period_label = "过去1小时"
            time_range = f"{start_time.strftime('%H:%M')} - {now.strftime('%H:%M')}"
        else:  # daily
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_label = "今天"
            time_range = start_time.strftime("%Y-%m-%d")

        # 使用Repository统计查询
        # 总消息数
        total_messages = self.conversation_repo.count_by_time_range(start_time)

        # AI回复数
        ai_replies = self.conversation_repo.count_ai_replied_by_time_range(start_time)

        # 需要审核的数量（通过优先级判断）
        manual_reviews = self.conversation_repo.count_by_priority_by_time_range(start_time)

        # 错误数量（这里简化处理，实际可能需要从错误日志或专门的错误表中统计）
        errors = 0  # Error count from logs (can be enhanced later)

        # 按页面统计
        by_page = {}
        page_conversations = self.db.query(
            Conversation.platform_message_id,
            func.count(Conversation.id).label("count")
        ).filter(
            Conversation.created_at >= start_time
        ).group_by(Conversation.platform_message_id).all()

        # 获取页面名称（从Token管理器）
        from src.config.page_token_manager import page_token_manager
        pages = page_token_manager.list_pages()

        for platform_msg_id, count in page_conversations:
            # 尝试从pages中找到页面信息
            page_name = "未知页面"
            for page_id, info in pages.items():
                if page_id in str(platform_msg_id) or str(page_id) == str(platform_msg_id):
                    page_name = info.get("name", page_id)
                    break

            by_page[platform_msg_id or "unknown"] = {
                "name": page_name,
                "messages": count
            }

        return {
            "period": period_label,
            "time_range": time_range,
            "total_messages": total_messages,
            "ai_replies": ai_replies,
            "manual_reviews": manual_reviews,
            "errors": errors,
            "by_page": by_page
        }

    async def close(self):
        """关闭资源"""
        self.stop()
        await self.notification_sender.close()
