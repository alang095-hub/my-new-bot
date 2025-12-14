"""消息处理器实现"""
from typing import Dict, Any
from .base import BaseProcessor, ProcessorResult, ProcessorStatus, ProcessorContext
from src.core.database.models import MessageType
import logging

logger = logging.getLogger(__name__)


class MessageReceiver(BaseProcessor):
    """消息接收处理器 - 准备消息摘要和提取信息"""

    def __init__(self):
        super().__init__("message_receiver", "消息接收和预处理")

    async def process(self, context: ProcessorContext) -> ProcessorResult:
        """接收消息并生成摘要"""
        try:
            message_content = context.message_data.get("content", "")

            # 生成消息摘要（最多500字符）
            if len(message_content) > 500:
                context.message_summary = message_content[:497] + "..."
            else:
                context.message_summary = message_content

            # 提取关键信息
            from src.collector.data_collector import DataCollector
            collector = DataCollector(context.db)
            context.extracted_info = collector.extract_info_from_message(
                message_content)

            return ProcessorResult(
                status=ProcessorStatus.SUCCESS,
                message="消息接收成功",
                data={"summary": context.message_summary}
            )
        except Exception as e:
            logger.error(f"Error in message receiver: {str(e)}", exc_info=True)
            return ProcessorResult(
                status=ProcessorStatus.ERROR,
                message=f"消息接收失败: {str(e)}",
                error=e
            )


class UserInfoHandler(BaseProcessor):
    """用户信息处理 - 获取或创建客户"""

    def __init__(self):
        super().__init__("user_info_handler", "用户信息处理")

    def get_dependencies(self) -> list:
        return ["message_receiver"]

    async def process(self, context: ProcessorContext) -> ProcessorResult:
        """获取或创建客户信息"""
        try:
            from src.ai.conversation_manager import ConversationManager
            conversation_manager = ConversationManager(context.db)

            sender_id = context.message_data.get("sender_id")

            # 尝试获取用户信息
            try:
                platform_user_info = await context.platform_client.get_user_info(sender_id)
                if context.platform_name == "facebook":
                    context.user_info = {
                        "name": platform_user_info.get("name"),
                        "first_name": platform_user_info.get("first_name"),
                        "last_name": platform_user_info.get("last_name")
                    }
                elif context.platform_name == "instagram":
                    context.user_info = {
                        "name": platform_user_info.get("username"),
                        "username": platform_user_info.get("username")
                    }
            except Exception as e:
                logger.warning(f"Failed to get user info: {str(e)}")

            # 获取或创建客户
            customer = conversation_manager.get_or_create_customer(
                platform=context.platform_name,
                platform_user_id=sender_id,
                name=context.user_info.get("name")
            )

            context.customer = customer
            context.customer_id = customer.id

            return ProcessorResult(
                status=ProcessorStatus.SUCCESS,
                message="客户信息处理成功",
                data={"customer_id": customer.id}
            )
        except Exception as e:
            logger.error(
                f"Error in user info handler: {str(e)}", exc_info=True)
            return ProcessorResult(
                status=ProcessorStatus.ERROR,
                message=f"用户信息处理失败: {str(e)}",
                error=e
            )


class FilterHandler(BaseProcessor):
    """过滤处理器 - 应用过滤规则"""

    def __init__(self):
        super().__init__("filter_handler", "消息过滤")

    def get_dependencies(self) -> list:
        return ["user_info_handler"]

    async def process(self, context: ProcessorContext) -> ProcessorResult:
        """应用过滤规则并保存对话记录"""
        try:
            from src.collector.filter_engine import FilterEngine
            from src.ai.conversation_manager import ConversationManager
            from src.core.database.models import Platform

            # 保存对话记录到数据库
            conversation_manager = ConversationManager(context.db)
            message_content = context.message_data.get("content", "")
            message_type = context.message_data.get(
                "message_type", MessageType.MESSAGE)
            
            # 保存对话记录
            conversation = conversation_manager.save_conversation(
                customer_id=context.customer_id,
                platform_message_id=context.message_data.get("message_id"),
                platform=context.platform_name,
                message_type=message_type,
                content=message_content,
                raw_data=context.message_data.get("raw_data")
            )
            
            # 保存对话ID到上下文，供后续处理器使用
            context.conversation_id = conversation.id
            context.conversation = conversation

            # 应用过滤规则
            filter_engine = FilterEngine(context.db)
            filter_result = filter_engine.filter_message(
                conversation, message_content)
            context.filter_result = filter_result
            context.should_review = filter_result.get("should_review", False)

            # 检查是否包含产品关键词（如果包含，即使被过滤也要回复）
            message_lower = message_content.lower()
            product_keywords = [
                "iphone", "ip", "苹果", "apple", "loan", "borrow", "lend", "贷款", "借款", 
                "借", "贷", "price", "cost", "费用", "价格", "多少钱", "interest", "利息",
                "model", "型号", "容量", "storage", "apple id", "id card", "身份证",
                "咨询", "了解", "询问", "办理", "申请", "apply", "怎么", "如何", "how",
                "服务", "service", "客服", "customer service", "legit", "legitimate", 
                "真实", "真的", "可靠", "reliable", "可信", "?", "？"
            ]
            has_product_keyword = any(keyword in message_lower for keyword in product_keywords)
            
            # 应用过滤结果到对话记录
            conversation.filtered = filter_result.get("filtered", False)
            conversation.filter_reason = filter_result.get("filter_reason")
            conversation.priority = filter_result.get("priority")
            context.db.commit()

            # 如果被过滤且不需要审核，但包含产品关键词，仍然继续处理（确保产品相关消息被回复）
            if filter_result.get("filtered") and not filter_result.get("should_review"):
                if has_product_keyword:
                    logger.info(f"Message contains product keyword, will reply despite being filtered: {message_content[:50]}")
                    # 重置过滤状态，确保消息被处理
                    conversation.filtered = False
                    conversation.filter_reason = None
                    context.db.commit()
                else:
                    return ProcessorResult(
                        status=ProcessorStatus.SKIP,
                        message="消息已被过滤，跳过处理",
                        should_continue=False
                    )

            return ProcessorResult(
                status=ProcessorStatus.SUCCESS,
                message="过滤处理完成",
                data={"filtered": filter_result.get("filtered", False), "conversation_id": conversation.id}
            )
        except Exception as e:
            logger.error(f"Error in filter handler: {str(e)}", exc_info=True)
            return ProcessorResult(
                status=ProcessorStatus.ERROR,
                message=f"过滤处理失败: {str(e)}",
                error=e
            )


class AIReplyHandler(BaseProcessor):
    """AI回复处理器 - 使用业务服务层处理业务逻辑"""

    def __init__(self):
        super().__init__("ai_reply_handler", "AI自动回复")

    def get_dependencies(self) -> list:
        return ["filter_handler"]

    async def process(self, context: ProcessorContext) -> ProcessorResult:
        """生成并发送AI回复（通过业务服务层）"""
        try:
            # 从业务注册器获取AI自动回复服务
            from src.business.registry import business_registry
            auto_reply_service = business_registry.get("auto_reply")
            
            if not auto_reply_service:
                logger.error("AI自动回复服务未注册")
                return ProcessorResult(
                    status=ProcessorStatus.ERROR,
                    message="AI自动回复服务未注册",
                    should_continue=True
                )
            
            # 构建业务服务上下文
            service_context = {
                "db": context.db,
                "customer_id": context.customer_id,
                "customer": context.customer,
                "message_data": context.message_data,
                "platform_client": context.platform_client,
                "message_summary": context.message_summary,
                "platform_name": context.platform_name,
                "conversation_id": getattr(context, "conversation_id", None)
            }
            
            # 调用业务服务执行业务逻辑
            result = await auto_reply_service.execute(service_context)
            
            # 处理业务服务返回结果
            if result.get("skipped"):
                return ProcessorResult(
                    status=ProcessorStatus.SKIP,
                    message=result.get("message", "已跳过"),
                    should_continue=True
                )
            
            if not result.get("success"):
                return ProcessorResult(
                    status=ProcessorStatus.ERROR,
                    message=result.get("message", "AI回复处理失败"),
                    should_continue=True  # 即使失败也继续后续处理
                )
            
            # 更新上下文
            ai_reply = result.get("ai_reply", "")
            context.ai_reply = ai_reply
            context.ai_replied = True
            context.group_invitation_sent = result.get("group_invitation_sent", False)
            
            return ProcessorResult(
                status=ProcessorStatus.SUCCESS,
                message=result.get("message", "AI回复发送成功"),
                data={"ai_reply": ai_reply[:100] if ai_reply else ""}
            )
        except Exception as e:
            logger.error(f"Error in AI reply handler: {str(e)}", exc_info=True)
            return ProcessorResult(
                status=ProcessorStatus.ERROR,
                message=f"AI回复处理失败: {str(e)}",
                error=e,
                should_continue=True  # 即使出错也继续后续处理
            )


class DataCollectionHandler(BaseProcessor):
    """数据收集处理器"""

    def __init__(self):
        super().__init__("data_collection_handler", "数据收集")

    def get_dependencies(self) -> list:
        return ["message_receiver"]

    async def process(self, context: ProcessorContext) -> ProcessorResult:
        """收集数据（已在MessageReceiver中完成，这里只是确认）"""
        # 数据收集已在MessageReceiver中完成
        return ProcessorResult(
            status=ProcessorStatus.SUCCESS,
            message="数据收集完成",
            data={"extracted_info": context.extracted_info}
        )


class StatisticsHandler(BaseProcessor):
    """统计处理器 - 记录交互统计"""

    def __init__(self):
        super().__init__("statistics_handler", "统计记录")

    def get_dependencies(self) -> list:
        return ["user_info_handler", "ai_reply_handler"]

    async def process(self, context: ProcessorContext) -> ProcessorResult:
        """记录客户交互统计"""
        try:
            from src.statistics.tracker import StatisticsTracker

            stats_tracker = StatisticsTracker(context.db)

            message_type = context.message_data.get(
                "message_type", MessageType.MESSAGE)
            message_type_str = message_type.value if hasattr(
                message_type, 'value') else str(message_type)

            interaction = stats_tracker.record_customer_interaction(
                customer_id=context.customer_id,
                platform=context.platform_name,
                message_type=message_type_str,
                message_summary=context.message_summary,
                extracted_info=context.extracted_info,
                ai_replied=context.ai_replied,
                group_invitation_sent=context.group_invitation_sent
            )

            return ProcessorResult(
                status=ProcessorStatus.SUCCESS,
                message="统计记录成功",
                data={"interaction_id": interaction.id}
            )
        except Exception as e:
            logger.error(
                f"Error in statistics handler: {str(e)}", exc_info=True)
            return ProcessorResult(
                status=ProcessorStatus.ERROR,
                message=f"统计记录失败: {str(e)}",
                error=e
            )


class NotificationHandler(BaseProcessor):
    """通知处理器 - 发送Telegram通知"""

    def __init__(self):
        super().__init__("notification_handler", "Telegram通知")

    def get_dependencies(self) -> list:
        return ["filter_handler"]

    async def process(self, context: ProcessorContext) -> ProcessorResult:
        """发送Telegram通知（如果需要审核）"""
        try:
            if not context.should_review:
                return ProcessorResult(
                    status=ProcessorStatus.SKIP,
                    message="不需要审核，跳过通知"
                )

            from src.telegram.notification_sender import NotificationSender
            from src.core.database.models import Conversation

            notification_sender = NotificationSender()

            # 创建临时对话对象用于通知
            temp_conversation = Conversation(
                customer_id=context.customer_id,
                platform_message_id=context.message_data.get("message_id"),
                message_type=context.message_data.get(
                    "message_type", MessageType.MESSAGE),
                content=context.message_summary
            )

            await notification_sender.send_review_notification(
                conversation=temp_conversation,
                customer=context.customer,
                collected_data=None
            )

            await notification_sender.close()

            return ProcessorResult(
                status=ProcessorStatus.SUCCESS,
                message="通知发送成功"
            )
        except Exception as e:
            logger.error(
                f"Error in notification handler: {str(e)}", exc_info=True)
            return ProcessorResult(
                status=ProcessorStatus.ERROR,
                message=f"通知发送失败: {str(e)}",
                error=e
            )
