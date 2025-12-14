"""API相关异常"""
from typing import Optional
from .base import AppException


class APIError(AppException):
    """API调用错误"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="API_ERROR", **kwargs)
        if status_code:
            self.details["status_code"] = status_code
        if api_name:
            self.details["api_name"] = api_name

