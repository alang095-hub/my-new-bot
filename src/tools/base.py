"""工具基类和接口定义"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ToolStatus(Enum):
    """工具执行状态"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


@dataclass
class ToolResult:
    """工具执行结果"""
    status: ToolStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    
    def is_success(self) -> bool:
        """检查是否成功"""
        return self.status == ToolStatus.SUCCESS
    
    def has_warnings(self) -> bool:
        """检查是否有警告"""
        return self.status == ToolStatus.WARNING
    
    def has_errors(self) -> bool:
        """检查是否有错误"""
        return self.status == ToolStatus.ERROR


class BaseTool(ABC):
    """工具基类 - 所有工具都应继承此类"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化工具
        
        Args:
            name: 工具名称
            description: 工具描述
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            工具执行结果
        """
        pass
    
    def validate_input(self, **kwargs) -> Optional[str]:
        """
        验证输入参数
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            如果验证失败返回错误消息，否则返回None
        """
        return None
    
    def get_help(self) -> str:
        """
        获取工具帮助信息
        
        Returns:
            帮助信息字符串
        """
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"






