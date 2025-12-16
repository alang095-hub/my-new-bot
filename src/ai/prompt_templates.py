"""AI 回复模板和提示词管理"""
from typing import Dict, Any, Optional
from src.core.config import yaml_config


class PromptTemplates:
    """提示词模板管理"""
    
    def __init__(self):
        self.templates = yaml_config.get("ai_templates", {})
    
    def get_greeting(self) -> str:
        """Get greeting template"""
        return self.templates.get(
            "greeting",
            "Hello! Thank you for your inquiry. I'm an AI customer service assistant, happy to help you."
        )
    
    def get_collecting_info(self) -> str:
        """Get information collection prompt"""
        return self.templates.get(
            "collecting_info",
            "To better assist you, please provide the following information: name, contact details, and specific needs."
        )
    
    def get_processing(self) -> str:
        """Get processing prompt"""
        return self.templates.get(
            "processing",
            "Processing your request, please wait..."
        )
    
    def get_fallback(self) -> str:
        """Get fallback reply"""
        return self.templates.get(
            "fallback",
            "I didn't fully understand your question. Could you please describe your needs in more detail?"
        )
    
    def build_system_prompt(self, prompt_type: Optional[str] = None) -> str:
        """
        构建系统提示词
        
        Args:
            prompt_type: 提示词类型，如果为 'iphone_loan_telegram' 则使用专用提示词
            
        Returns:
            系统提示词字符串
        """
        # 检查是否使用专用提示词
        if prompt_type == "iphone_loan_telegram":
            try:
                from src.ai.prompts.iphone_loan_telegram import IPHONE_LOAN_TELEGRAM_PROMPT
                prompt = IPHONE_LOAN_TELEGRAM_PROMPT
                
                # 从配置中读取Telegram群组/频道名称并替换
                telegram_config = yaml_config.get("telegram_groups", {})
                main_group = telegram_config.get("main_group", "@your_group")
                main_channel = telegram_config.get("main_channel", "@your_channel")
                
                # 替换提示词中的占位符
                prompt = prompt.replace("@your_group", main_group)
                prompt = prompt.replace("@your_channel", main_channel)
                
                return prompt
            except ImportError:
                # 如果导入失败，使用默认提示词
                pass
        
        # 检查配置文件中是否有自定义提示词
        custom_prompt = self.templates.get("system_prompt")
        if custom_prompt:
            return custom_prompt
        
        # 默认提示词
        return """You are a professional AI customer service assistant. Your responsibilities are:
1. Reply to customer inquiries in a friendly and professional manner
2. Collect basic customer information (name, contact, needs, etc.)
3. Understand customer intent and provide initial assistance
4. If unable to resolve, guide customers to provide more information for manual processing

CRITICAL: You MUST reply in ENGLISH ONLY, regardless of the customer's language. Keep replies SHORT and CONCISE (maximum 20-25 words). Be direct and helpful."""
    
    def build_conversation_context(
        self,
        customer_name: str = None,
        previous_messages: list = None
    ) -> str:
        """Build conversation context"""
        context = ""
        
        if customer_name:
            context += f"Customer name: {customer_name}\n"
        
        if previous_messages:
            context += "\nConversation history:\n"
            for msg in previous_messages[-5:]:  # Keep only last 5 messages
                role = "Customer" if msg.get("role") == "user" else "Assistant"
                content = msg.get("content", "")
                context += f"{role}: {content}\n"
        
        return context


