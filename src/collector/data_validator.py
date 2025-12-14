"""数据验证和清洗"""
import re
from typing import Dict, Any, List, Optional, Tuple
try:
    from email_validator import validate_email, EmailNotValidError
except ImportError:
    # 如果没有安装 email_validator，使用简单的正则验证
    EmailNotValidError = Exception
    def validate_email(email: str):
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        if not re.match(pattern, email):
            raise Exception("Invalid email format")
        return True


class DataValidator:
    """数据验证器"""
    
    # 电话号码正则表达式（支持多种格式）
    PHONE_PATTERNS = [
        r'1[3-9]\d{9}',  # 中国手机号
        r'\d{3}-\d{3}-\d{4}',  # 美国格式
        r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # 国际格式
    ]
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        验证邮箱地址
        
        Args:
            email: 邮箱地址
        
        Returns:
            (是否有效, 错误信息)
        """
        if not email:
            return False, "邮箱地址为空"
        
        try:
            validate_email(email)
            return True, None
        except EmailNotValidError as e:
            return False, str(e)
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """
        验证电话号码
        
        Args:
            phone: 电话号码
        
        Returns:
            (是否有效, 错误信息)
        """
        if not phone:
            return False, "电话号码为空"
        
        # 移除常见分隔符
        cleaned = re.sub(r'[-.\s()]', '', phone)
        
        # 检查是否只包含数字和+号（+号只能在开头）
        if not re.match(r'^\+?\d+$', cleaned):
            return False, "电话号码包含非法字符"
        
        # 移除+号进行长度检查
        digits_only = cleaned.lstrip('+')
        
        # 检查长度（电话号码应该在7-14位之间，15位太长）
        if len(digits_only) < 7 or len(digits_only) > 14:
            return False, "电话号码长度不正确"
        
        # 检查是否符合任一模式（使用清理后的电话号码）
        for pattern in DataValidator.PHONE_PATTERNS:
            if re.fullmatch(pattern, cleaned):
                return True, None
        
        return False, "电话号码格式不正确"
    
    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """
        从文本中提取电话号码
        
        Args:
            text: 文本内容
        
        Returns:
            提取的电话号码，如果未找到则返回 None
        """
        for pattern in DataValidator.PHONE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """
        从文本中提取邮箱地址
        
        Args:
            text: 文本内容
        
        Returns:
            提取的邮箱地址，如果未找到则返回 None
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0)
        return None
    
    @staticmethod
    def validate_collected_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证收集的数据
        
        Args:
            data: 收集的数据字典
        
        Returns:
            验证结果，包含验证状态和错误信息
        """
        errors = {}
        validated_data = {}
        
        # 验证邮箱
        if "email" in data and data["email"]:
            is_valid, error = DataValidator.validate_email(data["email"])
            if is_valid:
                validated_data["email"] = data["email"]
            else:
                errors["email"] = error
        
        # 验证电话
        if "phone" in data and data["phone"]:
            is_valid, error = DataValidator.validate_phone(data["phone"])
            if is_valid:
                validated_data["phone"] = data["phone"]
            else:
                errors["phone"] = error
        
        # 其他字段直接复制
        for key, value in data.items():
            if key not in ["email", "phone"] and value:
                validated_data[key] = value
        
        return {
            "is_valid": len(errors) == 0,
            "data": validated_data,
            "errors": errors
        }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
        
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符（保留中文、英文、数字、基本标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()（）]', '', text)
        
        return text.strip()

