"""业务相关异常"""
from typing import Optional
from .base import AppException


class ValidationError(AppException):
    """验证错误"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        if field:
            self.details["field"] = field


class DatabaseError(AppException):
    """数据库错误"""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)
        if operation:
            self.details["operation"] = operation


class ProcessingError(AppException):
    """消息处理流程中的错误"""
    
    def __init__(self, message: str, step: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="PROCESSING_ERROR", **kwargs)
        if step:
            self.details["step"] = step

