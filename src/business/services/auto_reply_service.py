"""
AI自动回复业务服务
从AIReplyHandler中提取的业务逻辑
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from .base_service import BaseBusinessService
from src.config.page_settings import page_settings
from src.ai.reply_generator import ReplyGenerator
from src.statistics.tracker import StatisticsTracker
from src.facebook.message_parser import MessageType
import logging

logger = logging.getLogger(__name__)


class AutoReplyService(BaseBusinessService):
    """AI自动回复业务服务"""
    
    def __init__(self):
        super().__init__("auto_reply", "AI自动回复服务")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行AI自动回复业务逻辑
        
        Args:
            context: 执行上下文，包含：
                - db: 数据库会话
                - customer_id: 客户ID
                - customer: 客户对象
                - message_data: 消息数据
                - platform_client: 平台客户端
                - message_summary: 消息摘要
                - platform_name: 平台名称
        
        Returns:
            执行结果字典
        """
        db: Session = context.get("db")
        customer_id: int = context.get("customer_id")
        customer = context.get("customer")
        message_data: Dict[str, Any] = context.get("message_data", {})
        platform_client = context.get("platform_client")
        message_summary: Optional[str] = context.get("message_summary")
        platform_name: str = context.get("platform_name", "facebook")
        
        # 检查是否启用自动回复
        page_id = message_data.get("page_id")
        auto_reply_enabled = page_settings.is_auto_reply_enabled(page_id)
        
        if not auto_reply_enabled:
            logger.info(f"页面 {page_id or '未知'} 的自动回复已禁用")
            return {
                "success": False,
                "skipped": True,
                "message": "自动回复已禁用"
            }
        
        # 生成AI回复
        reply_generator = ReplyGenerator(db)
        try:
            conversation_id = context.get("conversation_id")
            ai_reply = await reply_generator.generate_reply(
                customer_id=customer_id,
                message_content=message_data.get("content", ""),
                customer_name=customer.name if customer else None,
                conversation_id=conversation_id
            )
        except Exception as e:
            logger.error(f"AI回复生成失败: {str(e)}", exc_info=True)
            
            # 发送错误通知
            error_msg = str(e)
            error_type = "AI_REPLY_FAILED"
            if "token" in error_msg.lower() or "expired" in error_msg.lower() or "unauthorized" in error_msg.lower():
                error_type = "TOKEN_EXPIRED"
            
            # 记录失败率
            try:
                from src.monitoring.reply_failure_tracker import reply_failure_tracker
                reply_failure_tracker.record_failure(
                    failure_type=error_type,
                    error_message=error_msg,
                    customer_id=customer_id,
                    page_id=page_id,
                    metadata={"message_content": message_data.get("content", "")[:100]}
                )
            except Exception:
                pass  # 不影响主流程
            
            await self._send_error_notification(
                error_type=error_type,
                error_message=f"AI回复生成失败: {error_msg}",
                customer_id=customer_id,
                page_id=page_id,
                message_content=message_data.get("content", "")[:100]
            )
            
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "message": f"AI回复生成失败: {str(e)}"
            }
        
        if not ai_reply:
            logger.info(f"跳过回复：消息被识别为垃圾信息或无效沟通")
            return {
                "success": False,
                "skipped": True,
                "message": "消息为垃圾信息或无效沟通，已跳过回复"
            }
        
        # 检查是否包含群组邀请
        group_invitation_sent = "t.me" in ai_reply or "telegram" in ai_reply.lower()
        
        # 记录高频问题
        if message_summary:
            question_category = self._categorize_question(message_summary)
            stats_tracker = StatisticsTracker(db)
            stats_tracker.record_frequent_question(
                question_text=message_summary,
                category=question_category,
                sample_response=ai_reply[:200]
            )
        
        # 实时监控：记录AI回复事件
        try:
            from src.monitoring.realtime import realtime_monitor
            await realtime_monitor.record_ai_reply(
                customer_id=customer_id,
                customer_name=customer.name if customer else None,
                platform=platform_name,
                user_message=message_data.get("content", ""),
                ai_reply=ai_reply
            )
        except Exception as e:
            logger.warning(f"Failed to record AI reply to realtime monitor: {e}")
        
        # 发送回复到平台
        message_type = message_data.get("message_type", MessageType.MESSAGE)
        sender_id = message_data.get("sender_id")
        
        logger.info(
            f"Sending AI reply - sender_id={sender_id}, page_id={page_id}, message_type={message_type}")
        
        try:
            if message_type == MessageType.MESSAGE:
                await platform_client.send_message(
                    recipient_id=sender_id,
                    message=ai_reply,
                    page_id=page_id
                )
            elif message_type == MessageType.COMMENT and platform_name == "facebook":
                from src.facebook.api_client import FacebookAPIClient
                if isinstance(platform_client, FacebookAPIClient):
                    post_id = message_data.get("post_id")
                    if post_id:
                        await platform_client.comment_on_post(post_id, ai_reply)
            
            # 更新对话记录中的 AI 回复信息
            conversation_id = context.get("conversation_id")
            if conversation_id:
                from src.ai.conversation_manager import ConversationManager
                conversation_manager = ConversationManager(db)
                conversation_manager.update_ai_reply(conversation_id, ai_reply)
            
            # 记录成功
            try:
                from src.monitoring.reply_failure_tracker import reply_failure_tracker
                reply_failure_tracker.record_success()
            except Exception:
                pass
            
            return {
                "success": True,
                "ai_reply": ai_reply,
                "group_invitation_sent": group_invitation_sent,
                "message": "AI回复发送成功"
            }
        except Exception as e:
            logger.error(f"Error sending AI reply: {str(e)}", exc_info=True)
            
            # 发送错误通知
            error_msg = str(e)
            error_type = "SEND_MESSAGE_FAILED"
            
            # 检查是否是Token相关错误
            if "token" in error_msg.lower() or "expired" in error_msg.lower() or "unauthorized" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                error_type = "TOKEN_EXPIRED"
            
            # 记录失败率
            try:
                from src.monitoring.reply_failure_tracker import reply_failure_tracker
                reply_failure_tracker.record_failure(
                    failure_type=error_type,
                    error_message=error_msg,
                    customer_id=customer_id,
                    page_id=page_id,
                    metadata={"ai_reply": ai_reply[:100] if ai_reply else None}
                )
            except Exception:
                pass
            
            await self._send_error_notification(
                error_type=error_type,
                error_message=f"发送消息失败: {error_msg}",
                customer_id=customer_id,
                page_id=page_id,
                message_content=ai_reply[:100] if ai_reply else None
            )
            
            return {
                "success": False,
                "error": str(e),
                "ai_reply": ai_reply,  # 即使发送失败，也返回生成的回复
                "message": f"AI回复生成成功，但发送失败: {str(e)}"
            }
    
    def _categorize_question(self, question_text: str) -> str:
        """
        分类问题（从原AIReplyHandler提取）
        
        Args:
            question_text: 问题文本
            
        Returns:
            问题分类
        """
        question_lower = question_text.lower()
        
        if any(keyword in question_lower for keyword in ["价格", "价格", "price", "cost", "费用", "收费"]):
            return "价格咨询"
        elif any(keyword in question_lower for keyword in ["如何", "怎么", "how", "how to", "方法", "步骤"]):
            return "使用指导"
        elif any(keyword in question_lower for keyword in ["问题", "错误", "problem", "error", "bug", "故障"]):
            return "问题反馈"
        elif any(keyword in question_lower for keyword in ["功能", "feature", "功能", "特性"]):
            return "功能介绍"
        else:
            return "一般咨询"
    
    async def _send_error_notification(
        self,
        error_type: str,
        error_message: str,
        customer_id: Optional[int] = None,
        message_content: Optional[str] = None,
        page_id: Optional[str] = None
    ):
        """发送错误通知到Telegram"""
        try:
            from src.telegram.notification_sender import NotificationSender
            
            notification_sender = NotificationSender()
            additional_info = {}
            
            if message_content:
                # 截断长消息
                preview = message_content[:100] + "..." if len(message_content) > 100 else message_content
                additional_info["消息内容"] = preview
            
            await notification_sender.send_error_notification(
                error_type=error_type,
                error_message=error_message,
                page_id=page_id,
                customer_id=customer_id,
                additional_info=additional_info if additional_info else None
            )
            await notification_sender.close()
        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}", exc_info=True)

