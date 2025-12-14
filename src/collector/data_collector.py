"""资料收集模块"""
import re
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from src.core.database.models import CollectedData, Conversation
from src.collector.data_validator import DataValidator
from src.core.config import yaml_config
import logging

logger = logging.getLogger(__name__)


class DataCollector:
    """从对话中提取客户信息"""
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = DataValidator()
        self.required_fields = yaml_config.get("data_collection", {}).get("required_fields", [])
        self.optional_fields = yaml_config.get("data_collection", {}).get("optional_fields", [])
        # 使用Repository模式
        from src.core.database.repositories import CollectedDataRepository
        self.collected_data_repo = CollectedDataRepository(db)
    
    def extract_info_from_message(self, message_content: str) -> Dict[str, Any]:
        """
        从消息中提取信息
        
        Args:
            message_content: 消息内容
        
        Returns:
            提取的信息字典
        """
        extracted = {}
        
        # 提取邮箱
        email = self.validator.extract_email(message_content)
        if email:
            extracted["email"] = email
        
        # 提取电话
        phone = self.validator.extract_phone(message_content)
        if phone:
            extracted["phone"] = phone
        
        # 提取姓名（简单规则：寻找"我是"、"姓名"等关键词后的内容）
        name_patterns = [
            r'我是[：:]\s*([^\s，,。.]+)',
            r'姓名[：:]\s*([^\s，,。.]+)',
            r'我叫[：:]\s*([^\s，,。.]+)',
            r'name[：:]\s*([^\s，,。.]+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_content, re.IGNORECASE)
            if match:
                extracted["name"] = match.group(1).strip()
                break
        
        # 提取需求类型
        inquiry_keywords = {
            "咨询": ["咨询", "了解", "询问"],
            "购买": ["购买", "买", "价格", "多少钱"],
            "投诉": ["投诉", "不满", "问题"],
            "合作": ["合作", "代理", "加盟"],
        }
        
        message_lower = message_content.lower()
        for inquiry_type, keywords in inquiry_keywords.items():
            if any(keyword in message_content or keyword.lower() in message_lower for keyword in keywords):
                extracted["inquiry_type"] = inquiry_type
                break
        
        # 保存原始消息内容
        extracted["message_content"] = message_content
        
        return extracted
    
    def collect_from_conversation(
        self,
        conversation_id: int,
        message_content: str
    ) -> CollectedData:
        """
        从对话中收集资料并保存
        
        Args:
            conversation_id: 对话 ID
            message_content: 消息内容
        
        Returns:
            创建的收集数据记录
        """
        # 提取信息
        extracted_data = self.extract_info_from_message(message_content)
        
        # 验证数据
        validation_result = self.validator.validate_collected_data(extracted_data)
        
        # 使用Repository创建收集数据记录
        collected_data = self.collected_data_repo.create_collected_data(
            conversation_id=conversation_id,
            data=validation_result["data"],
            is_validated=validation_result["is_valid"],
            validation_errors=validation_result["errors"] if not validation_result["is_valid"] else None
        )
        
        logger.info(f"Collected data for conversation {conversation_id}: {validation_result['data']}")
        
        return collected_data
    
    def get_collected_data(self, conversation_id: int) -> Optional[CollectedData]:
        """
        获取对话的收集数据
        
        Args:
            conversation_id: 对话 ID
        
        Returns:
            收集数据记录，如果不存在则返回 None
        """
        # 使用Repository获取收集数据
        return self.collected_data_repo.get_by_conversation_id(conversation_id)
    
    def is_data_complete(self, collected_data: CollectedData) -> bool:
        """
        检查收集的数据是否完整
        
        Args:
            collected_data: 收集数据记录
        
        Returns:
            数据是否完整
        """
        if not collected_data or not collected_data.data:
            return False
        
        data = collected_data.data
        
        # 检查必需字段
        for field in self.required_fields:
            if field not in data or not data[field]:
                return False
        
        return True
    
    def merge_data(
        self,
        existing_data: Dict[str, Any],
        new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        合并数据（新数据覆盖旧数据）
        
        Args:
            existing_data: 现有数据
            new_data: 新数据
        
        Returns:
            合并后的数据
        """
        merged = existing_data.copy() if existing_data else {}
        merged.update(new_data)
        return merged


