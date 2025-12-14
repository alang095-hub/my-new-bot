"""过滤规则引擎"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from src.core.database.models import Conversation, Priority
from src.core.config import yaml_config
import re
import logging

logger = logging.getLogger(__name__)


class FilterEngine:
    """可配置的过滤规则引擎"""
    
    def __init__(self, db: Session):
        self.db = db
        self.filter_config = yaml_config.get("filtering", {})
        self.keyword_config = self.filter_config.get("keyword_filter", {})
        self.sentiment_config = self.filter_config.get("sentiment_filter", {})
        self.priority_config = self.filter_config.get("priority_rules", [])
    
    def filter_message(
        self,
        conversation: Conversation,
        message_content: str
    ) -> Dict[str, Any]:
        """
        过滤消息
        
        Args:
            conversation: 对话记录
            message_content: 消息内容
        
        Returns:
            过滤结果，包含是否被过滤、原因、优先级等
        """
        result = {
            "filtered": False,
            "filter_reason": None,
            "priority": Priority.LOW,
            "should_review": True
        }
        
        # 关键词过滤
        if self.keyword_config.get("enabled", True):
            keyword_result = self._check_keywords(message_content)
            if keyword_result["blocked"]:
                result["filtered"] = True
                result["filter_reason"] = f"包含屏蔽关键词: {keyword_result['matched_keywords']}"
                result["should_review"] = False
                return result
            elif keyword_result["spam"]:
                result["filtered"] = True
                result["filter_reason"] = f"疑似垃圾信息: {keyword_result['matched_keywords']}"
                result["should_review"] = False
                return result
        
        # 优先级判断
        priority = self._determine_priority(message_content)
        result["priority"] = priority
        
        # 情感分析过滤（简化版，实际可以使用 AI）
        if self.sentiment_config.get("enabled", True):
            sentiment_result = self._analyze_sentiment(message_content)
            if sentiment_result["is_negative"] and self.sentiment_config.get("priority_negative", True):
                result["priority"] = Priority.HIGH
        
        return result
    
    def _check_keywords(self, message_content: str) -> Dict[str, Any]:
        """
        检查关键词
        
        Args:
            message_content: 消息内容
        
        Returns:
            关键词检查结果
        """
        message_lower = message_content.lower()
        
        # 检查屏蔽关键词
        block_keywords = self.keyword_config.get("block_keywords", [])
        matched_block = []
        for keyword in block_keywords:
            if keyword.lower() in message_lower:
                matched_block.append(keyword)
        
        if matched_block:
            return {
                "blocked": True,
                "spam": False,
                "matched_keywords": matched_block
            }
        
        # 检查垃圾信息关键词
        spam_keywords = self.keyword_config.get("spam_keywords", [])
        matched_spam = []
        for keyword in spam_keywords:
            if keyword.lower() in message_lower:
                matched_spam.append(keyword)
        
        if matched_spam:
            return {
                "blocked": False,
                "spam": True,
                "matched_keywords": matched_spam
            }
        
        return {
            "blocked": False,
            "spam": False,
            "matched_keywords": []
        }
    
    def _determine_priority(self, message_content: str) -> Priority:
        """
        确定消息优先级
        
        Args:
            message_content: 消息内容
        
        Returns:
            优先级
        """
        message_lower = message_content.lower()
        
        # 按配置的优先级规则检查
        for rule in self.priority_config:
            condition = rule.get("condition", "")
            keywords = rule.get("keywords", [])
            priority_str = rule.get("priority", "low")
            
            # 检查是否匹配条件
            if condition == "包含紧急关键词":
                if any(keyword.lower() in message_lower for keyword in keywords):
                    return Priority.URGENT if priority_str == "high" else Priority.HIGH
            
            elif condition == "包含购买意向":
                if any(keyword.lower() in message_lower for keyword in keywords):
                    return Priority.MEDIUM if priority_str == "medium" else Priority.LOW
            
            elif condition == "默认":
                priority_map = {
                    "low": Priority.LOW,
                    "medium": Priority.MEDIUM,
                    "high": Priority.HIGH,
                    "urgent": Priority.URGENT
                }
                return priority_map.get(priority_str, Priority.LOW)
        
        return Priority.LOW
    
    def _analyze_sentiment(self, message_content: str) -> Dict[str, Any]:
        """
        简单的情感分析（基于关键词）
        
        Args:
            message_content: 消息内容
        
        Returns:
            情感分析结果
        """
        message_lower = message_content.lower()
        
        # 负面情感关键词
        negative_keywords = [
            "不满", "投诉", "问题", "错误", "失败", "糟糕",
            "disappointed", "complaint", "problem", "error", "bad"
        ]
        
        # 正面情感关键词
        positive_keywords = [
            "满意", "感谢", "好", "棒", "优秀",
            "satisfied", "thanks", "good", "great", "excellent"
        ]
        
        negative_count = sum(1 for keyword in negative_keywords if keyword in message_lower)
        positive_count = sum(1 for keyword in positive_keywords if keyword in message_lower)
        
        return {
            "is_negative": negative_count > positive_count,
            "is_positive": positive_count > negative_count,
            "negative_score": negative_count,
            "positive_score": positive_count
        }
    
    def apply_filter_to_conversation(
        self,
        conversation: Conversation,
        message_content: str
    ) -> Conversation:
        """
        应用过滤规则到对话
        
        Args:
            conversation: 对话记录
            message_content: 消息内容
        
        Returns:
            更新后的对话记录
        """
        filter_result = self.filter_message(conversation, message_content)
        
        conversation.filtered = filter_result["filtered"]
        conversation.filter_reason = filter_result["filter_reason"]
        conversation.priority = filter_result["priority"]
        
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(
            f"Applied filter to conversation {conversation.id}: "
            f"filtered={filter_result['filtered']}, priority={filter_result['priority']}"
        )
        
        return conversation


