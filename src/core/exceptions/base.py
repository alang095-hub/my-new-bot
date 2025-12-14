"""异常基类"""
from typing import Optional, Dict, Any


class AppException(Exception):
    """应用基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details
        }

