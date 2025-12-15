"""结构化日志配置"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import timezone, timedelta


class SensitiveDataFilter(logging.Filter):
    """过滤敏感信息的日志过滤器"""
    
    # 敏感信息关键词（用于识别需要过滤的字段）
    SENSITIVE_KEYWORDS = [
        'token', 'password', 'secret', 'key', 'api_key',
        'access_token', 'refresh_token', 'auth', 'credential'
    ]
    
    # 需要完全隐藏的值（如果包含这些关键词）
    SENSITIVE_PATTERNS = [
        r'[A-Za-z0-9]{32,}',  # 长token（32字符以上）
        r'sk-[A-Za-z0-9]+',    # OpenAI API key
        r'EAAG[A-Za-z0-9]+',   # Facebook token格式
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤敏感信息"""
        import re
        
        # 过滤消息内容
        if hasattr(record, 'msg') and record.msg:
            record.msg = self._sanitize(str(record.msg))
        
        # 过滤参数
        if hasattr(record, 'args') and record.args:
            record.args = tuple(self._sanitize(str(arg)) if isinstance(arg, str) else arg 
                              for arg in record.args)
        
        return True
    
    def _sanitize(self, text: str) -> str:
        """清理敏感信息"""
        import re
        
        # 检查是否包含敏感关键词
        text_lower = text.lower()
        has_sensitive = any(keyword in text_lower for keyword in self.SENSITIVE_KEYWORDS)
        
        if not has_sensitive:
            return text
        
        # 替换长token
        for pattern in self.SENSITIVE_PATTERNS:
            text = re.sub(pattern, '[REDACTED]', text)
        
        # 替换常见的token格式
        # Facebook token: EAAG... -> EAAG[REDACTED]
        text = re.sub(r'(EAAG[A-Za-z0-9]{10})[A-Za-z0-9]+', r'\1[REDACTED]', text)
        
        # OpenAI key: sk-... -> sk-[REDACTED]
        text = re.sub(r'(sk-[A-Za-z0-9]{10})[A-Za-z0-9]+', r'\1[REDACTED]', text)
        
        return text


class LocalTimeFormatter(logging.Formatter):
    """使用本地时区（UTC+8）的日志格式化器"""

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        # 设置本地时区（UTC+8，中国时区）
        self.local_tz = timezone(timedelta(hours=8))

    def formatTime(self, record, datefmt=None):
        """格式化时间为本地时区"""
        ct = datetime.fromtimestamp(record.created, tz=self.local_tz)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            s = ct.strftime('%Y-%m-%d %H:%M:%S')
        return s


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON格式"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    use_json: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 10
) -> None:
    """
    设置日志配置
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        use_json: 是否使用JSON格式
        max_bytes: 日志文件最大字节数
        backup_count: 备份文件数量
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 创建格式化器
    if use_json:
        formatter = StructuredFormatter()
    else:
        formatter = LocalTimeFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 创建敏感信息过滤器
    sensitive_filter = SensitiveDataFilter()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(sensitive_filter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(sensitive_filter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)

