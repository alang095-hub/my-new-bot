"""Telegram notification sender"""
import httpx
from typing import Dict, Any, Optional
from src.core.config import settings, yaml_config
from src.core.database.models import Conversation, Customer, CollectedData
import logging

logger = logging.getLogger(__name__)


class NotificationSender:
    """Send review notifications to Telegram"""

    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.notification_config = yaml_config.get("telegram", {})

    async def send_review_notification(
        self,
        conversation: Conversation,
        customer: Customer,
        collected_data: Optional[CollectedData] = None
    ) -> bool:
        """
        Send review notification

        Args:
            conversation: Conversation record
            customer: Customer information
            collected_data: Collected data (optional)

        Returns:
            Whether the message was sent successfully
        """
        try:
            # Validate Bot Token
            if not self.bot_token or self.bot_token.startswith("your_"):
                logger.error("Telegram Bot Token not configured or invalid")
                return False
            
            # Validate Chat ID
            if not self.chat_id:
                logger.error("Telegram Chat ID not configured")
                return False
            
            message = self._format_notification_message(
                conversation,
                customer,
                collected_data
            )

            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": self.notification_config.get("notification_format", "Markdown")
            }

            response = await self.client.post(url, json=data)
            
            # Detailed error handling
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("description", f"HTTP {response.status_code}")
                    logger.error(f"Telegram API error: {error_msg}")
                    
                    if response.status_code == 401:
                        logger.error("Telegram Bot Token invalid or expired, please check and update TELEGRAM_BOT_TOKEN")
                    elif response.status_code == 400:
                        logger.error(f"Request parameter error: {error_msg}")
                    elif response.status_code == 403:
                        logger.error("Bot does not have permission to send messages to this Chat, please check TELEGRAM_CHAT_ID")
                except:
                    logger.error(f"Telegram API error (non-JSON): {response.text[:200]}")
            
            response.raise_for_status()

            logger.info(
                f"Sent review notification for conversation {conversation.id}")
            return True

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Error sending Telegram notification: HTTP {e.response.status_code}", exc_info=True)
            return False
        except Exception as e:
            logger.error(
                f"Error sending Telegram notification: {str(e)}", exc_info=True)
            return False

    def _format_notification_message(
        self,
        conversation: Conversation,
        customer: Customer,
        collected_data: Optional[CollectedData]
    ) -> str:
        """
        Format notification message

        Args:
            conversation: Conversation record
            customer: Customer information
            collected_data: Collected data

        Returns:
            Formatted message text
        """
        lines = []

        # Title
        lines.append("🔔 *New Message Requires Review*")
        lines.append("")

        # Customer information
        if self.notification_config.get("include_customer_info", True):
            lines.append("*Customer Information:*")
            if customer.name:
                lines.append(f"Name: {customer.name}")
            if customer.email:
                lines.append(f"Email: {customer.email}")
            if customer.phone:
                lines.append(f"Phone: {customer.phone}")
            lines.append(f"Facebook ID: `{customer.facebook_id}`")
            lines.append("")

        # Message content
        lines.append("*Message Content:*")
        content = conversation.content
        max_length = self.notification_config.get("max_preview_length", 200)
        if len(content) > max_length and self.notification_config.get("include_message_preview", True):
            content = content[:max_length] + "..."
        lines.append(content)
        lines.append("")

        # Message type and priority
        if conversation.message_type:
            try:
                message_type_value = conversation.message_type.value if hasattr(conversation.message_type, 'value') else str(conversation.message_type)
                lines.append(f"Type: {message_type_value}")
            except AttributeError:
                lines.append(f"Type: {str(conversation.message_type)}")
        else:
            lines.append(f"Type: Unknown")
        if conversation.priority:
            try:
                priority_value = conversation.priority.value.upper() if hasattr(conversation.priority, 'value') else str(conversation.priority).upper()
                lines.append(f"Priority: {priority_value}")
            except AttributeError:
                lines.append(f"Priority: {str(conversation.priority)}")
        else:
            lines.append(f"Priority: Not Set")
        lines.append("")

        # Collected data
        if collected_data and collected_data.data:
            lines.append("*Collected Data:*")
            for key, value in collected_data.data.items():
                if value:
                    lines.append(f"{key}: {value}")
            lines.append("")

        # Action commands
        lines.append("*Action Commands:*")
        lines.append(f"/approve_{conversation.id} - Approve")
        lines.append(f"/reject_{conversation.id} - Reject")
        lines.append(f"/review_{conversation.id} - View Details")

        return "\n".join(lines)

    async def send_ai_suggestion(
        self,
        conversation_id: int,
        suggestion: str
    ) -> bool:
        """
        Send AI suggestion

        Args:
            conversation_id: Conversation ID
            suggestion: AI suggestion

        Returns:
            Whether the message was sent successfully
        """
        try:
            message = f"🤖 *AI Suggestion*\n\nConversation ID: {conversation_id}\n\n{suggestion}"

            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }

            response = await self.client.post(url, json=data)
            response.raise_for_status()

            return True

        except Exception as e:
            logger.error(
                f"Error sending AI suggestion: {str(e)}", exc_info=True)
            return False

    async def send_error_notification(
        self,
        error_type: str,
        error_message: str,
        page_id: Optional[str] = None,
        customer_id: Optional[int] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send error notification

        Args:
            error_type: Error type (e.g., "AI_REPLY_FAILED", "TOKEN_EXPIRED", "API_ERROR")
            error_message: Error message
            page_id: Page ID (optional)
            customer_id: Customer ID (optional)
            additional_info: Additional information (optional)

        Returns:
            Whether the message was sent successfully
        """
        try:
            # Check if error notifications are enabled
            notifications_config = self.notification_config.get("notifications", {})
            if not notifications_config.get("enable_error_notifications", True):
                return False
            
            # Validate Bot Token
            if not self.bot_token or self.bot_token.startswith("your_"):
                logger.debug("Telegram Bot Token not configured, skipping error notification")
                return False
            
            # Validate Chat ID
            if not self.chat_id:
                logger.debug("Telegram Chat ID not configured, skipping error notification")
                return False
            
            message = self._format_error_message(
                error_type, error_message, page_id, customer_id, additional_info
            )
            
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": self.notification_config.get("notification_format", "Markdown")
            }
            
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            
            logger.info(f"Sent error notification: {error_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending error notification: {str(e)}", exc_info=True)
            return False
    
    def _format_error_message(
        self,
        error_type: str,
        error_message: str,
        page_id: Optional[str] = None,
        customer_id: Optional[int] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format error notification message"""
        lines = []
        
        # Error type mapping
        error_labels = {
            "AI_REPLY_FAILED": "❌ AI Reply Failed",
            "TOKEN_EXPIRED": "⚠️ Token Expired",
            "API_ERROR": "❌ API Error",
            "SEND_MESSAGE_FAILED": "❌ Send Message Failed",
            "WEBHOOK_ERROR": "❌ Webhook Error",
            "CONFIG_ERROR": "⚠️ Configuration Error"
        }
        
        error_label = error_labels.get(error_type, f"⚠️ {error_type}")
        lines.append(f"*{error_label}*")
        lines.append("")
        
        # Error details
        lines.append(f"*Error Message:* {error_message}")
        lines.append("")
        
        # Context information
        if page_id:
            lines.append(f"*Page ID:* `{page_id}`")
        if customer_id:
            lines.append(f"*Customer ID:* {customer_id}")
        
        # Additional information
        if additional_info:
            lines.append("")
            lines.append("*Additional Details:*")
            for key, value in additional_info.items():
                lines.append(f"{key}: {value}")
        
        lines.append("")
        lines.append(f"_Time: {self._get_current_time()}_")
        
        return "\n".join(lines)
    
    async def send_summary_notification(
        self,
        summary_data: Dict[str, Any]
    ) -> bool:
        """
        Send summary notification
        
        Args:
            summary_data: Summary data containing statistics
        
        Returns:
            Whether the message was sent successfully
        """
        try:
            # Check if summary notifications are enabled
            notifications_config = self.notification_config.get("notifications", {})
            if not notifications_config.get("enable_summary_notifications", True):
                return False
            
            # Validate Bot Token
            if not self.bot_token or self.bot_token.startswith("your_"):
                logger.debug("Telegram Bot Token not configured, skipping summary notification")
                return False
            
            # Validate Chat ID
            if not self.chat_id:
                logger.debug("Telegram Chat ID not configured, skipping summary notification")
                return False
            
            message = self._format_summary_message(summary_data)
            
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": self.notification_config.get("notification_format", "Markdown")
            }
            
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            
            logger.info("Sent summary notification")
            return True
            
        except Exception as e:
            logger.error(f"Error sending summary notification: {str(e)}", exc_info=True)
            return False
    
    def _format_summary_message(self, summary_data: Dict[str, Any]) -> str:
        """格式化汇总通知消息"""
        lines = []
        
        # Title
        period = summary_data.get("period", "Unknown")
        lines.append(f"📊 *Statistics Summary ({period})*")
        lines.append("")
        
        # Message statistics
        total_messages = summary_data.get("total_messages", 0)
        ai_replies = summary_data.get("ai_replies", 0)
        manual_reviews = summary_data.get("manual_reviews", 0)
        errors = summary_data.get("errors", 0)
        
        lines.append("*Message Statistics:*")
        lines.append(f"Total Messages: {total_messages}")
        lines.append(f"AI Auto Replies: {ai_replies}")
        lines.append(f"Requires Review: {manual_reviews}")
        lines.append(f"Errors: {errors}")
        lines.append("")
        
        # Statistics by page
        if "by_page" in summary_data:
            lines.append("*Statistics by Page:*")
            for page_id, page_stats in summary_data["by_page"].items():
                page_name = page_stats.get("name", page_id)
                page_messages = page_stats.get("messages", 0)
                lines.append(f"  • {page_name}: {page_messages} messages")
            lines.append("")
        
        # Time range
        time_range = summary_data.get("time_range", "")
        if time_range:
            lines.append(f"_Statistics Period: {time_range}_")
        
        return "\n".join(lines)
    
    def _get_current_time(self) -> str:
        """Get current time string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
