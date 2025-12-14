"""告警系统"""
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """告警信息"""
    level: AlertLevel
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.handlers: Dict[AlertLevel, List[Callable[[Alert], None]]] = defaultdict(list)
        self.alert_counts: Dict[str, int] = defaultdict(int)
        self.rate_limits: Dict[str, timedelta] = {}
    
    def register_handler(
        self,
        level: AlertLevel,
        handler: Callable[[Alert], None]
    ) -> None:
        """
        注册告警处理器
        
        Args:
            level: 告警级别
            handler: 处理函数
        """
        self.handlers[level].append(handler)
    
    def send_alert(
        self,
        level: AlertLevel,
        message: str,
        source: str,
        details: Optional[Dict[str, Any]] = None,
        rate_limit: Optional[timedelta] = None
    ) -> None:
        """
        发送告警
        
        Args:
            level: 告警级别
            message: 告警消息
            source: 告警来源
            details: 详细信息
            rate_limit: 速率限制（相同消息在时间窗口内只发送一次）
        """
        # 检查速率限制
        if rate_limit:
            alert_key = f"{source}:{message}"
            last_alert_time = self.rate_limits.get(alert_key)
            if last_alert_time and datetime.utcnow() - last_alert_time < rate_limit:
                return
            self.rate_limits[alert_key] = datetime.utcnow()
        
        alert = Alert(
            level=level,
            message=message,
            source=source,
            details=details or {}
        )
        
        self.alerts.append(alert)
        self.alert_counts[source] += 1
        
        # 记录日志
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }.get(level, logging.INFO)
        
        logger.log(log_level, f"[{level.value.upper()}] {source}: {message}", extra=details)
        
        # 调用处理器
        for handler in self.handlers.get(level, []):
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}", exc_info=True)
    
    def get_active_alerts(
        self,
        level: Optional[AlertLevel] = None,
        source: Optional[str] = None
    ) -> List[Alert]:
        """
        获取活跃告警
        
        Args:
            level: 过滤告警级别
            source: 过滤告警来源
        
        Returns:
            告警列表
        """
        alerts = [a for a in self.alerts if not a.resolved]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        if source:
            alerts = [a for a in alerts if a.source == source]
        
        return alerts
    
    def resolve_alert(self, alert_id: int) -> bool:
        """
        解决告警
        
        Args:
            alert_id: 告警索引
        
        Returns:
            是否成功
        """
        if 0 <= alert_id < len(self.alerts):
            self.alerts[alert_id].resolved = True
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取告警统计"""
        active_alerts = self.get_active_alerts()
        
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "resolved_alerts": len([a for a in self.alerts if a.resolved]),
            "by_level": {
                level.value: len([a for a in active_alerts if a.level == level])
                for level in AlertLevel
            },
            "by_source": dict(self.alert_counts)
        }


# 全局告警管理器实例
alert_manager = AlertManager()


def send_telegram_alert(alert: Alert) -> None:
    """通过Telegram发送告警"""
    try:
        from src.telegram.notification_sender import NotificationSender
        from src.core.config import settings
        
        if not hasattr(settings, 'telegram_bot_token'):
            return
        
        sender = NotificationSender()
        message = f"🚨 [{alert.level.value.upper()}] {alert.source}\n{alert.message}"
        
        # 异步发送（这里简化处理，实际应该使用后台任务）
        # sender.send_notification(message)
        logger.info(f"Would send Telegram alert: {message}")
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


# 注册默认处理器
alert_manager.register_handler(AlertLevel.CRITICAL, send_telegram_alert)
alert_manager.register_handler(AlertLevel.ERROR, send_telegram_alert)

