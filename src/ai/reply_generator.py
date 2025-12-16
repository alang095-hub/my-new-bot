"""AI 回复生成器"""
import openai
import re
from typing import List, Dict, Any, Optional
from src.core.config import settings
from src.ai.prompt_templates import PromptTemplates
from src.ai.conversation_manager import ConversationManager
from src.core.exceptions import APIError, ProcessingError
from src.core.database.models import Conversation
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class ReplyGenerator:
    """使用 OpenAI API 生成智能回复"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.templates = PromptTemplates()
        self.conversation_manager = ConversationManager(db)
    
    def _is_spam_or_invalid(self, message_content: str) -> bool:
        """
        Detect spam or invalid messages with intelligent intent detection
        
        Priority:
        1. Basic spam detection (emojis, repeated chars)
        2. Buying/selling intent keywords (spam)
        3. Business-related intent keywords (must reply)
        4. If none match, allow reply if message length >= 2 chars
        
        Args:
            message_content: Message content
        
        Returns:
            Whether the message is spam or invalid
        """
        if not message_content:
            return True
        
        content_stripped = message_content.strip()
        
        # Step 1: Basic spam detection - blank or too short
        if len(content_stripped) < 2:
            return True
        
        # Step 1: Basic spam detection - mostly emojis/symbols
        import unicodedata
        text_chars = [c for c in content_stripped if c.isalnum() or c in '，。！？、']
        if len(text_chars) < 2:
            logger.info(f"Detected spam/invalid message (mostly emojis/symbols): {message_content[:50]}")
            return True
        
        # Step 1: Basic spam detection - repeated characters
        if len(content_stripped) >= 5:
            # Check for 5+ consecutive identical characters
            for i in range(len(content_stripped) - 4):
                char = content_stripped[i]
                if content_stripped[i:i+5] == char * 5:
                    logger.info(f"Detected spam/invalid message (repeated chars): {message_content[:50]}")
                    return True
            
            # Check overall character repeat ratio
            char_counts = {}
            for char in content_stripped:
                char_counts[char] = char_counts.get(char, 0) + 1
            max_count = max(char_counts.values())
            repeat_ratio = max_count / len(content_stripped)
            if repeat_ratio > 0.8:  # 80%+ same character
                logger.info(f"Detected spam/invalid message (high repeat ratio): {message_content[:50]}")
                return True
        
        message_lower = content_stripped.lower()
        
        # Step 2: Buying/selling intent keywords (SPAM)
        # These indicate "buy/sell phone" intent, should be marked as spam
        # Even if they contain product keywords like "手机", they are spam
        buying_selling_keywords = [
            # Chinese
            "买手机", "卖手机", "购买手机", "出售手机", "我要买", "我想买", 
            "我要卖", "我想卖", "收购", "回收", "买iphone", "卖iphone",
            # English
            "buy phone", "sell phone", "purchase phone", "want to buy", 
            "want to sell", "looking to buy", "looking to sell", "buy iphone", "sell iphone"
        ]
        
        # Check for buying/selling intent
        has_buying_selling_intent = any(keyword in message_lower for keyword in buying_selling_keywords)
        if has_buying_selling_intent:
            logger.info(f"Detected spam message (buying/selling intent): {message_content[:50]}")
            return True  # Mark as spam
        
        # Step 3: Business-related intent keywords (MUST REPLY)
        # These indicate "consult loan" intent, must reply
        business_intent_keywords = [
            # Loan related
            "贷款", "借款", "借钱", "借", "贷", "loan", "borrow", "lend",
            # Inquiry related
            "咨询", "了解", "询问", "问", "help", "inquiry", "question", "想了解", "想咨询",
            # Application related
            "办理", "申请", "apply", "application", "怎么", "如何", "how",
            # Price related
            "价格", "费用", "价钱", "多少钱", "price", "cost", "interest", "利息", "利率",
            # Legitimacy related
            "legit", "legitimate", "真实", "真的", "可靠", "reliable", "可信",
            # Question mark (indicates inquiry)
            "?", "？"
        ]
        
        # Check for business intent
        has_business_intent = any(keyword in message_lower for keyword in business_intent_keywords)
        if has_business_intent:
            logger.info(f"Message contains business intent keyword, will reply: {message_content[:50]}")
            return False  # Not spam, must reply
        
        # Step 4: If none match, allow reply if message length >= 2 chars
        # Note: Business context means we won't have very long conversations,
        # so no need for length-based spam detection
        logger.info(f"Message does not match any intent keywords, allowing reply: {message_content[:50]}")
        return False  # Allow reply
    
    async def _check_preset_reply(self, customer_id: int, message_content: str) -> Optional[str]:
        """
        检查是否应该使用预设回复（用于前三个标准问题）
        
        Args:
            customer_id: 客户 ID
            message_content: 消息内容
        
        Returns:
            预设回复内容，如果不匹配则返回 None
        """
        preset_replies = self.templates.templates.get("preset_replies", {})
        if not preset_replies:
            return None
        
        # 获取对话历史，统计已发送的AI回复数量
        history = await self.conversation_manager.get_conversation_history(customer_id, limit=10)
        ai_reply_count = sum(1 for msg in history if msg.get("role") == "assistant")
        
        # 只在前三个问题中使用预设回复（即AI回复数量少于3条时）
        if ai_reply_count >= 3:
            return None
        
        message_lower = message_content.lower()
        
        # 检查每个预设回复模板（按优先级顺序）
        # 优先匹配更具体的问题类型
        preset_order = ["question_model", "question_amount", "question_storage", "greeting_first"]
        
        for key in preset_order:
            if key not in preset_replies:
                continue
            
            preset = preset_replies[key]
            keywords = preset.get("keywords", [])
            reply = preset.get("reply", "")
            
            # 检查是否匹配关键词
            if any(keyword.lower() in message_lower for keyword in keywords):
                logger.info(f"Using preset reply '{key}' for customer {customer_id} (AI reply count: {ai_reply_count}/3)")
                return reply
        
        return None
    
    def _has_received_telegram_link(self, customer_id: int) -> bool:
        """
        Check if customer has already received Telegram group link
        
        Args:
            customer_id: Customer ID
        
        Returns:
            True if customer has received Telegram link, False otherwise
        """
        # Check all conversations for this customer
        from src.core.database.repositories.conversation_repo import ConversationRepository
        conversation_repo = ConversationRepository(self.db)
        conversations = conversation_repo.get_customer_ai_replied_conversations(customer_id)
        
        # Check if any reply contains Telegram group link
        from src.core.config import yaml_config
        telegram_config = yaml_config.get("telegram_groups", {})
        main_group = telegram_config.get("main_group", "@your_group")
        
        # Keywords that indicate Telegram group link was sent
        telegram_keywords = [
            "t.me", "telegram", "telegram group", "telegram群组", "join our telegram"
        ]
        
        # Add main_group to keywords if it's configured
        if main_group and main_group != "@your_group":
            # Add full group link/name
            telegram_keywords.append(main_group.lower())
            
            # Extract different formats from the group link
            # Handle formats like: https://t.me/+bNivsOGSM6ZlMGJl, @group_name, t.me/group_name
            if "t.me" in main_group.lower():
                # Extract the group identifier from URL
                if "/" in main_group:
                    parts = main_group.split("/")
                    if len(parts) > 1:
                        # Get the last part (group name or invite code)
                        group_id = parts[-1].lower()
                        telegram_keywords.append(group_id)
                        # Also check without + prefix if present
                        if group_id.startswith("+"):
                            telegram_keywords.append(group_id[1:])
            elif "@" in main_group:
                # Handle @group_name format
                telegram_keywords.append(main_group.replace("@", "").lower())
                telegram_keywords.append(main_group.lower())
        
        for conv in conversations:
            if conv.ai_reply_content:
                reply_lower = conv.ai_reply_content.lower()
                # Check if reply contains Telegram group link
                if any(keyword in reply_lower for keyword in telegram_keywords):
                    return True
        
        return False
    
    def _ensure_telegram_link_in_reply(self, reply: str, customer_id: int) -> str:
        """
        Ensure Telegram group link is included in reply if customer hasn't received it
        
        Args:
            reply: Generated reply
            customer_id: Customer ID
        
        Returns:
            Reply with Telegram link if needed
        """
        # Check if customer has already received Telegram link
        if self._has_received_telegram_link(customer_id):
            return reply
        
        # Check if reply already contains Telegram link
        from src.core.config import yaml_config
        telegram_config = yaml_config.get("telegram_groups", {})
        main_group = telegram_config.get("main_group", "@your_group")
        
        reply_lower = reply.lower()
        telegram_keywords = ["t.me", "telegram", "telegram group", "telegram群组", "join our telegram"]
        
        # Also check for the actual group link/name
        if main_group and main_group != "@your_group":
            # Check if reply contains the group link/name
            if main_group.lower() in reply_lower:
                return reply  # Already contains Telegram link
            # Check for partial match (e.g., if group is "t.me/+abc123", check for "+abc123")
            if "/" in main_group:
                group_id = main_group.split("/")[-1].lower()
                if group_id in reply_lower or group_id.replace("+", "") in reply_lower:
                    return reply
        
        if any(keyword in reply_lower for keyword in telegram_keywords):
            return reply  # Already contains Telegram link
        
        # Add Telegram group link to reply
        if main_group and main_group != "@your_group":
            # Format: "Reply content. Join our Telegram group: [link]"
            if not reply.endswith(('.', '!', '?')):
                reply += "."
            reply += f" Join our Telegram group: {main_group}"
            logger.info(f"Added Telegram group link to reply for customer {customer_id} (first time)")
        
        return reply
    
    async def generate_reply(
        self,
        customer_id: int,
        message_content: str,
        customer_name: Optional[str] = None,
        conversation_id: Optional[int] = None
    ) -> Optional[str]:
        """
        生成 AI 回复
        
        Args:
            customer_id: 客户 ID
            message_content: 客户消息内容
            customer_name: 客户姓名
        
        Returns:
            AI 生成的回复内容，如果是垃圾信息则返回 None
        """
        # 检测垃圾信息或无效沟通
        if self._is_spam_or_invalid(message_content):
            logger.info(f"Skipping reply generation for spam/invalid message from customer {customer_id}")
            return None
        
        # 检查是否应该使用预设回复（前三个标准问题）
        preset_reply = await self._check_preset_reply(customer_id, message_content)
        if preset_reply:
            # Ensure Telegram link is included in preset reply if needed
            preset_reply = self._ensure_telegram_link_in_reply(preset_reply, customer_id)
            return preset_reply
        
        try:
            # 获取对话历史
            history = await self.conversation_manager.get_conversation_history(
                customer_id,
                limit=10
            )
            
            # A/B测试：选择提示词版本
            prompt_version = None
            system_prompt = None
            
            try:
                from src.ai.prompt_ab_testing import PromptABTesting
                ab_testing = PromptABTesting(self.db)
                prompt_version = ab_testing.select_version(customer_id)
                
                if prompt_version:
                    system_prompt = prompt_version.prompt_content
                    logger.info(f"Using prompt version: {prompt_version.version_code} for customer {customer_id}")
            except Exception as e:
                logger.warning(f"Failed to select prompt version: {e}")
            
            # 如果没有选择版本，使用默认提示词
            if not system_prompt:
                prompt_type = self.templates.templates.get("prompt_type")
                system_prompt = self.templates.build_system_prompt(prompt_type=prompt_type)
            
            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]
            
            # 添加历史对话
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # 添加当前消息
            messages.append({
                "role": "user",
                "content": message_content
            })
            
            # 调用 OpenAI API
            # 严格限制回复长度：max_tokens=30 约等于20-25个英文单词
            import time
            start_time = time.time()
            
            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    temperature=settings.openai_temperature,
                    max_tokens=30  # 严格控制为20-25个英文单词（留出buffer）
                )
                
                response_time_ms = (time.time() - start_time) * 1000
                
                # 记录API使用
                tokens_used = None
                try:
                    from src.monitoring.api_usage_tracker import APIUsageTracker, APIType
                    usage_tracker = APIUsageTracker(self.db)
                    
                    # 计算token使用量
                    tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
                    
                    usage_tracker.record_api_call(
                        api_type=APIType.OPENAI.value,
                        endpoint="chat.completions",
                        success=True,
                        response_time_ms=response_time_ms,
                        tokens_used=tokens_used,
                        model=settings.openai_model,
                        metadata={"customer_id": customer_id}
                    )
                except Exception as e:
                    logger.warning(f"Failed to record API usage: {e}")
                
                # 记录A/B测试使用情况
                if prompt_version and conversation_id:
                    try:
                        from src.ai.prompt_ab_testing import PromptABTesting
                        ab_testing = PromptABTesting(self.db)
                        ab_testing.record_usage(
                            prompt_version_id=prompt_version.id,
                            customer_id=customer_id,
                            conversation_id=conversation_id,
                            response_time_ms=int(response_time_ms),
                            tokens_used=tokens_used,
                            success=True
                        )
                    except Exception as e:
                        logger.warning(f"Failed to record A/B testing usage: {e}")
                
                reply = response.choices[0].message.content.strip()
            except Exception as e:
                response_time_ms = (time.time() - start_time) * 1000
                
                # 记录失败的API调用
                try:
                    from src.monitoring.api_usage_tracker import APIUsageTracker, APIType
                    usage_tracker = APIUsageTracker(self.db)
                    usage_tracker.record_api_call(
                        api_type=APIType.OPENAI.value,
                        endpoint="chat.completions",
                        success=False,
                        response_time_ms=response_time_ms,
                        error_message=str(e),
                        model=settings.openai_model,
                        metadata={"customer_id": customer_id}
                    )
                except Exception:
                    pass
                
                raise
            
            # Ensure Telegram group link is included if customer hasn't received it
            reply = self._ensure_telegram_link_in_reply(reply, customer_id)
            
            logger.info(f"Generated reply for customer {customer_id}: {reply[:100]}...")
            
            return reply
        
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            raise APIError(
                message=f"AI回复生成失败: {str(e)}",
                api_name="OpenAI",
                status_code=getattr(e, 'status_code', None)
            )
        except Exception as e:
            logger.error(f"Error generating reply: {str(e)}", exc_info=True)
            raise ProcessingError(
                f"生成回复时发生错误: {str(e)}"
            )
    
    def generate_greeting(self) -> str:
        """生成问候语"""
        return self.templates.get_greeting()
    
    def generate_collecting_info_prompt(self) -> str:
        """生成收集信息提示"""
        return self.templates.get_collecting_info()
    
    def should_collect_info(self, message_content: str) -> bool:
        """
        判断是否需要收集更多信息
        
        Args:
            message_content: 消息内容
        
        Returns:
            是否需要收集信息
        """
        # 简单的启发式规则
        # 可以后续用 AI 来判断
        info_keywords = ["姓名", "电话", "邮箱", "联系方式", "需求", "预算"]
        message_lower = message_content.lower()
        
        # 如果消息很短，可能需要更多信息
        if len(message_content) < 20:
            return True
        
        # 如果包含信息关键词，可能已经提供了信息
        if any(keyword in message_content for keyword in info_keywords):
            return False
        
        return True


