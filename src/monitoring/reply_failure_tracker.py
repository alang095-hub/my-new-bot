"""回复失败率追踪器"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict
from src.monitoring.alerts import alert_manager, AlertLevel
import logging

logger = logging.getLogger(__name__)


class ReplyFailureTracker:
    """回复失败率追踪器"""
    
    def __init__(self):
        self._failure_records: list[Dict[str, Any]] = []  # 内存中的失败记录
        self._max_records = 500  # 最多保留500条记录
        self._check_interval = timedelta(minutes=5)  # 每5分钟检查一次
        self._last_check_time = datetime.now(timezone.utc)
    
    def record_failure(
        self,
        failure_type: str,
        error_message: str,
        customer_id: Optional[int] = None,
        page_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        记录回复失败
        
        Args:
            failure_type: 失败类型 (AI_REPLY_FAILED, SEND_MESSAGE_FAILED, TOKEN_EXPIRED等)
            error_message: 错误信息
            customer_id: 客户ID
            page_id: 页面ID
            metadata: 其他元数据
        """
        record = {
            "failure_type": failure_type,
            "error_message": error_message,
            "customer_id": customer_id,
            "page_id": page_id,
            "timestamp": datetime.now(timezone.utc),
            "metadata": metadata or {}
        }
        
        self._failure_records.append(record)
        
        # 限制记录数量
        if len(self._failure_records) > self._max_records:
            self._failure_records = self._failure_records[-self._max_records:]
        
        # 定期检查失败率
        self._check_failure_rate()
    
    def record_success(self) -> None:
        """记录回复成功"""
        record = {
            "success": True,
            "timestamp": datetime.now(timezone.utc)
        }
        
        self._failure_records.append(record)
        
        # 限制记录数量
        if len(self._failure_records) > self._max_records:
            self._failure_records = self._failure_records[-self._max_records:]
    
    def _check_failure_rate(self) -> None:
        """检查失败率并触发告警"""
        now = datetime.now(timezone.utc)
        
        # 每5分钟检查一次
        if now - self._last_check_time < self._check_interval:
            return
        
        self._last_check_time = now
        
        # 检查最近100次回复的失败率
        recent_records = self._failure_records[-100:]
        if len(recent_records) < 20:
            return  # 样本太少，不检查
        
        # 统计失败次数
        failure_count = sum(1 for r in recent_records if not r.get("success", False))
        total_count = len(recent_records)
        failure_rate = (failure_count / total_count) * 100
        
        # 按失败类型统计
        failure_types = defaultdict(int)
        for r in recent_records:
            if not r.get("success", False):
                failure_type = r.get("failure_type", "UNKNOWN")
                failure_types[failure_type] += 1
        
        # 触发告警
        if failure_rate > 10:
            alert_manager.send_alert(
                AlertLevel.ERROR,
                f"回复失败率过高: {failure_rate:.1f}%",
                "reply_failure_tracker",
                details={
                    "failure_rate": failure_rate,
                    "failure_count": failure_count,
                    "total_count": total_count,
                    "failure_types": dict(failure_types)
                },
                rate_limit=timedelta(minutes=10)
            )
        elif failure_rate > 5:
            alert_manager.send_alert(
                AlertLevel.WARNING,
                f"回复失败率较高: {failure_rate:.1f}%",
                "reply_failure_tracker",
                details={
                    "failure_rate": failure_rate,
                    "failure_count": failure_count,
                    "total_count": total_count,
                    "failure_types": dict(failure_types)
                },
                rate_limit=timedelta(minutes=15)
            )
        
        # 检查特定错误类型
        if failure_types.get("TOKEN_EXPIRED", 0) > 0:
            alert_manager.send_alert(
                AlertLevel.ERROR,
                f"检测到Token过期错误: {failure_types['TOKEN_EXPIRED']}次",
                "reply_failure_tracker",
                details={
                    "failure_type": "TOKEN_EXPIRED",
                    "count": failure_types["TOKEN_EXPIRED"]
                },
                rate_limit=timedelta(minutes=5)
            )
    
    def get_statistics(
        self,
        hours: int = 1
    ) -> Dict[str, Any]:
        """
        获取失败率统计
        
        Args:
            hours: 统计时间范围（小时）
        
        Returns:
            统计数据
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_records = [r for r in self._failure_records if r.get("timestamp", datetime.min.replace(tzinfo=timezone.utc)) >= cutoff_time]
        
        if not recent_records:
            return {
                "total": 0,
                "success": 0,
                "failures": 0,
                "failure_rate": 0.0,
                "by_type": {}
            }
        
        success_count = sum(1 for r in recent_records if r.get("success", False))
        failure_count = len(recent_records) - success_count
        failure_rate = (failure_count / len(recent_records)) * 100 if recent_records else 0
        
        # 按类型统计
        failure_types = defaultdict(int)
        for r in recent_records:
            if not r.get("success", False):
                failure_type = r.get("failure_type", "UNKNOWN")
                failure_types[failure_type] += 1
        
        return {
            "total": len(recent_records),
            "success": success_count,
            "failures": failure_count,
            "failure_rate": round(failure_rate, 2),
            "by_type": dict(failure_types)
        }


# 全局追踪器实例
reply_failure_tracker = ReplyFailureTracker()

