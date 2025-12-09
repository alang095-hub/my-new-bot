"""处理器基类和接口定义"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ProcessorStatus(Enum):
    """处理器状态"""
    SUCCESS = "success"
    SKIP = "skip"
    ERROR = "error"
    CONTINUE = "continue"


@dataclass
class ProcessorResult:
    """处理器执行结果"""
    status: ProcessorStatus
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    should_continue: bool = True
    error: Optional[Exception] = None
    
    def is_success(self) -> bool:
        """检查是否成功"""
        return self.status == ProcessorStatus.SUCCESS
    
    def should_skip(self) -> bool:
        """检查是否应该跳过后续处理"""
        return self.status == ProcessorStatus.SKIP or not self.should_continue


@dataclass
class ProcessorContext:
    """处理器上下文（在处理器之间传递数据）"""
    platform_name: str
    message_data: Dict[str, Any]
    
    # 处理过程中的数据
    customer_id: Optional[int] = None
    customer: Any = None
    user_info: Dict[str, Any] = field(default_factory=dict)
    message_summary: str = ""
    extracted_info: Dict[str, Any] = field(default_factory=dict)
    ai_reply: Optional[str] = None
    filter_result: Optional[Dict[str, Any]] = None
    collected_data: Any = None
    
    # 状态标志
    ai_replied: bool = False
    group_invitation_sent: bool = False
    should_review: bool = False
    
    # 数据库和客户端
    db: Any = None
    platform_client: Any = None


class BaseProcessor(ABC):
    """处理器基类 - 所有处理器都应继承此类"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化处理器
        
        Args:
            name: 处理器名称
            description: 处理器描述
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def process(self, context: ProcessorContext) -> ProcessorResult:
        """
        处理消息
        
        Args:
            context: 处理器上下文
            
        Returns:
            处理结果
        """
        pass
    
    def validate(self, context: ProcessorContext) -> Optional[str]:
        """
        验证上下文是否有效
        
        Args:
            context: 处理器上下文
            
        Returns:
            如果验证失败返回错误消息，否则返回None
        """
        return None
    
    def get_dependencies(self) -> list:
        """
        获取依赖的处理器名称列表
        
        Returns:
            依赖列表
        """
        return []
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"




