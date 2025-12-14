"""Auto-reply scheduler - Periodically scan and reply to unreplied product-related messages"""
import asyncio
import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from src.core.database.connection import SessionLocal
from src.core.database.models import Conversation, Customer, Platform, MessageType
from src.core.database.repositories import ConversationRepository
from src.ai.reply_generator import ReplyGenerator
from src.facebook.api_client import FacebookAPIClient
from src.core.config import settings
from src.config.page_token_manager import page_token_manager
from src.config.page_settings import page_settings
from src.ai.conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

# Product keywords list (consistent with reply_generator.py)
PRODUCT_KEYWORDS = [
    "iphone", "ip", "苹果", "apple", "loan", "borrow", "lend", "贷款", "借款",
    "借", "贷", "price", "cost", "费用", "价格", "多少钱", "interest", "利息",
    "model", "型号", "容量", "storage", "apple id", "id card", "身份证",
    "咨询", "了解", "询问", "办理", "申请", "apply", "怎么", "如何", "how",
    "服务", "service", "客服", "customer service", "legit", "legitimate",
    "真实", "真的", "可靠", "reliable", "可信", "?", "？"
]

# Start date: December 13, 2025
START_DATE = datetime(2025, 12, 13, 0, 0, 0, tzinfo=timezone.utc)

# Unreplied time threshold: 5 minutes
UNREPLIED_THRESHOLD_MINUTES = 5


def contains_product_keyword(message_content: str) -> bool:
    """Check if message contains product keywords"""
    if not message_content:
        return False

    message_lower = message_content.lower()
    return any(keyword in message_lower for keyword in PRODUCT_KEYWORDS)


class AutoReplyScheduler:
    """Auto-reply scheduler"""

    def __init__(self):
        self.running = False
        self.task = None
        self.api_client = None

    async def start(self):
        """Start auto-reply scheduler"""
        if self.running:
            logger.warning("Auto-reply scheduler is already running")
            return

        self.running = True
        logger.info(
            "Auto-reply scheduler started (scanning for unreplied product messages every 5 minutes)")

        # Initialize API client
        self.api_client = FacebookAPIClient(
            access_token=settings.facebook_access_token)

        # Start background task
        self.task = asyncio.create_task(self._run_periodic_check())

    async def stop(self):
        """Stop auto-reply scheduler"""
        if not self.running:
            return

        self.running = False
        logger.info("Stopping auto-reply scheduler")

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        if self.api_client:
            await self.api_client.close()

    async def _run_periodic_check(self):
        """Periodically check for unreplied messages"""
        while self.running:
            try:
                await self._check_and_reply_unanswered_messages()
                # Check every 5 minutes
                await asyncio.sleep(300)  # 300 seconds = 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"Auto-reply scheduler error: {str(e)}", exc_info=True)
                # Wait 1 minute before retry after error
                await asyncio.sleep(60)

    async def _check_and_reply_unanswered_messages(self):
        """Check and reply to unreplied product-related messages from all enabled pages"""
        db = SessionLocal()

        try:
            # Get all enabled pages
            enabled_pages = await self._get_enabled_pages()

            if not enabled_pages:
                logger.info("No enabled pages found for auto-reply")
                return

            logger.info(
                f"Scanning {len(enabled_pages)} enabled pages for unreplied messages...")

            # Statistics
            total_scanned = 0
            total_unreplied = 0
            total_replied = 0
            total_errors = 0

            # Scan each enabled page
            for page_id, page_token in enabled_pages.items():
                try:
                    page_stats = await self._scan_and_reply_page(db, page_id, page_token)
                    total_scanned += 1
                    total_unreplied += page_stats.get("unreplied_count", 0)
                    total_replied += page_stats.get("replied_count", 0)
                    total_errors += page_stats.get("error_count", 0)
                except Exception as e:
                    logger.error(
                        f"Error scanning page {page_id}: {str(e)}", exc_info=True)
                    total_errors += 1
                    continue

            # Log summary
            logger.info(
                f"Auto-reply scan completed: "
                f"scanned {total_scanned} pages, "
                f"found {total_unreplied} unreplied messages, "
                f"replied to {total_replied}, "
                f"errors: {total_errors}"
            )

        except Exception as e:
            logger.error(
                f"Failed to check unreplied messages: {str(e)}", exc_info=True)
        finally:
            db.close()

    async def _get_enabled_pages(self) -> Dict[str, str]:
        """
        Get all pages with auto-reply enabled

        Returns:
            Dictionary mapping page_id to page_token
        """
        enabled_pages = {}

        # Get all pages from token manager
        all_pages = page_token_manager.list_pages()

        # Also check tokens directly
        for page_id in page_token_manager._tokens.keys():
            if page_id == "default":
                continue

            # Check if auto-reply is enabled for this page
            if page_settings.is_auto_reply_enabled(page_id):
                token = page_token_manager.get_token(page_id)
                if token:
                    enabled_pages[page_id] = token

        return enabled_pages

    async def _scan_and_reply_page(
        self,
        db: Session,
        page_id: str,
        page_token: str
    ) -> Dict[str, int]:
        """
        Scan a single page for unreplied messages and reply

        Returns:
            Statistics dictionary with counts
        """
        stats = {
            "unreplied_count": 0,
            "replied_count": 0,
            "error_count": 0
        }

        try:
            # Create API client for this page
            page_client = FacebookAPIClient(access_token=page_token)

            # Check for unreplied messages from API
            unreplied_messages = await page_client.check_unreplied_messages(
                page_id,
                threshold_minutes=UNREPLIED_THRESHOLD_MINUTES
            )

            stats["unreplied_count"] = len(unreplied_messages)

            if not unreplied_messages:
                await page_client.close()
                return stats

            logger.info(
                f"Found {len(unreplied_messages)} potentially unreplied messages for page {page_id}")

            # Initialize services
            reply_generator = ReplyGenerator(db)
            conversation_manager = ConversationManager(db)

            # Batch process messages (process in batches of 5 to avoid overwhelming the system)
            batch_size = 5
            total_batches = (len(unreplied_messages) + batch_size - 1) // batch_size
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, len(unreplied_messages))
                batch_messages = unreplied_messages[start_idx:end_idx]
                
                logger.info(
                    f"Processing batch {batch_idx + 1}/{total_batches} "
                    f"({len(batch_messages)} messages) for page {page_id}"
                )
                
                # Process batch concurrently
                batch_tasks = [
                    self._process_single_message(
                        db, msg_data, page_id, page_client,
                        reply_generator, conversation_manager, stats
                    )
                    for msg_data in batch_messages
                ]
                
                # Wait for batch to complete
                await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Delay between batches to avoid rate limiting
                if batch_idx < total_batches - 1:
                    await asyncio.sleep(2.0)  # 2 second delay between batches
            

            await page_client.close()

        except Exception as e:
            logger.error(
                f"Error scanning page {page_id}: {str(e)}", exc_info=True)
            stats["error_count"] += 1

        return stats

    async def _process_single_message(
        self,
        db: Session,
        msg_data: Dict[str, Any],
        page_id: str,
        page_client: FacebookAPIClient,
        reply_generator: ReplyGenerator,
        conversation_manager: ConversationManager,
        stats: Dict[str, int]
    ) -> None:
        """
        处理单条未回复消息（批量处理中的单个任务）
        
        Args:
            db: 数据库会话
            msg_data: 消息数据
            page_id: 页面ID
            page_client: Facebook API客户端
            reply_generator: 回复生成器
            conversation_manager: 对话管理器
            stats: 统计字典（会被修改）
        """
        try:
            message = msg_data["message"]
            message_content = message.get("message", "")

            if not message_content:
                return

            # Check if message is spam (using intelligent detection)
            if reply_generator._is_spam_or_invalid(message_content):
                logger.debug(
                    f"Skipping spam message: {message_content[:50]}")
                return

            # Sync message to database if not exists
            conversation = await self._sync_message_to_database(
                db, message, msg_data["conversation_id"], page_id
            )

            if not conversation:
                stats["error_count"] += 1
                return

            # Check if already replied
            if conversation.ai_replied:
                return

            # Get or create customer
            from_info = message.get("from", {})
            sender_id = from_info.get("id")

            if not sender_id:
                stats["error_count"] += 1
                return

            customer = await conversation_manager.get_or_create_customer(
                platform=Platform.FACEBOOK,
                platform_user_id=sender_id,
                name=from_info.get("name")
            )

                    # Generate AI reply
                    ai_reply = await reply_generator.generate_reply(
                        customer_id=customer.id,
                        message_content=message_content,
                        customer_name=customer.name,
                        conversation_id=conversation.id
                    )

            if not ai_reply:
                logger.debug(
                    f"Message {conversation.id} did not generate reply (may be flagged as spam)")
                stats["error_count"] += 1
                return

            # Send reply
            try:
                await page_client.send_message(
                    recipient_id=sender_id,
                    message=ai_reply,
                    page_id=page_id
                )

                # Update conversation record
                conversation_manager.update_ai_reply(
                    conversation.id, ai_reply)

                stats["replied_count"] += 1
                logger.info(
                    f"✅ Auto-replied to message {conversation.id} "
                    f"(Customer: {customer.name or sender_id}): {message_content[:50]}..."
                )
            except Exception as e:
                # Check if it's a 24-hour window limit error
                from src.core.exceptions import APIError
                is_24h_window_error = False

                if isinstance(e, APIError):
                    # Check if it's 24-hour window limit
                    error_subcode = e.details.get("error_subcode")
                    if error_subcode in [2018001, 2018278] or "24小时" in e.message:
                        is_24h_window_error = True
                elif isinstance(e, httpx.HTTPStatusError):
                    # Check HTTP response for 24-hour window error
                    if e.response.status_code == 400:
                        try:
                            error_detail = e.response.json()
                            error_info = error_detail.get("error", {})
                            error_subcode = error_info.get("error_subcode")
                            if error_subcode in [2018001, 2018278]:
                                is_24h_window_error = True
                        except:
                            pass

                if is_24h_window_error:
                    logger.warning(
                        f"⏰ 跳过消息 {conversation.id}: 超过24小时消息发送窗口限制。"
                        f"用户需要先发送新消息才能回复。"
                    )
                    # Don't count as error, just skip
                    return

                # For other errors, log and count as error
                logger.error(
                    f"Failed to send message to {sender_id}: {str(e)}", exc_info=True)
                stats["error_count"] += 1
                return

        except Exception as e:
            logger.error(
                f"Failed to process unreplied message: {str(e)}", exc_info=True)
            stats["error_count"] += 1
            return

    async def _sync_message_to_database(
        self,
        db: Session,
        message: Dict[str, Any],
        conversation_id: str,
        page_id: str
    ) -> Optional[Conversation]:
        """
        Sync a message from API to database if it doesn't exist

        Returns:
            Conversation object if successful, None otherwise
        """
        try:
            message_id = message.get("id")
            if not message_id:
                return None

            # 使用Repository检查消息是否已存在
            conversation_repo = ConversationRepository(db)
            existing = conversation_repo.get_by_platform_message_id(
                platform=Platform.FACEBOOK,
                platform_message_id=message_id
            )

            if existing:
                return existing

            # Get sender info
            from_info = message.get("from", {})
            sender_id = from_info.get("id")

            if not sender_id:
                return None

            # Get or create customer
            conversation_manager = ConversationManager(db)
            customer = await conversation_manager.get_or_create_customer(
                platform=Platform.FACEBOOK,
                platform_user_id=sender_id,
                name=from_info.get("name")
            )

            # Parse created_time
            created_time_str = message.get("created_time")
            if created_time_str:
                try:
                    if created_time_str.endswith('Z'):
                        created_time = datetime.fromisoformat(
                            created_time_str.replace('Z', '+00:00'))
                    else:
                        created_time = datetime.fromisoformat(created_time_str)
                    if created_time.tzinfo is None:
                        created_time = created_time.replace(
                            tzinfo=timezone.utc)
                except:
                    created_time = datetime.now(timezone.utc)
            else:
                created_time = datetime.now(timezone.utc)

            # Create conversation record
            conversation = conversation_manager.save_conversation(
                customer_id=customer.id,
                platform_message_id=message_id,
                platform=Platform.FACEBOOK,
                message_type=MessageType.MESSAGE,
                content=message.get("message", ""),
                raw_data={
                    "page_id": page_id,
                    "conversation_id": conversation_id,
                    "from": from_info
                }
            )

            # 使用Repository更新received_at时间
            conversation_repo = ConversationRepository(db)
            conversation = conversation_repo.update(
                id=conversation.id,
                received_at=created_time
            )

            logger.debug(f"Synced message {message_id} to database")
            return conversation

        except Exception as e:
            logger.error(
                f"Error syncing message to database: {str(e)}", exc_info=True)
            db.rollback()
            return None


# Global scheduler instance
auto_reply_scheduler = AutoReplyScheduler()
