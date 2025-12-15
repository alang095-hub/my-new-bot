"""API调用量监控追踪器"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class APIType(str, Enum):
    """API类型枚举"""
    OPENAI = "openai"
    FACEBOOK = "facebook"
    TELEGRAM = "telegram"


@dataclass
class APIUsageRecord:
    """API使用记录"""
    api_type: str
    endpoint: str
    success: bool
    response_time_ms: float
    timestamp: datetime
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None  # OpenAI token使用量
    cost_usd: Optional[float] = None  # 估算成本（美元）
    metadata: Optional[Dict[str, Any]] = None


class APIUsageTracker:
    """API使用量追踪器"""
    
    # OpenAI定价（每1000 tokens，美元）
    # gpt-4o-mini: $0.15/$0.60 per 1M tokens (input/output)
    OPENAI_PRICING = {
        "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
        "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-4": {"input": 30.00 / 1_000_000, "output": 60.00 / 1_000_000},
    }
    
    def __init__(self, db: Session):
        self.db = db
        self._in_memory_logs: List[APIUsageRecord] = []  # 内存中的日志（用于快速统计）
        self._max_memory_logs = 1000  # 最多保留1000条内存日志
    
    def record_api_call(
        self,
        api_type: str,
        endpoint: str,
        success: bool,
        response_time_ms: float,
        error_message: Optional[str] = None,
        tokens_used: Optional[int] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        记录API调用
        
        Args:
            api_type: API类型 (openai, facebook, telegram)
            endpoint: API端点
            success: 是否成功
            response_time_ms: 响应时间（毫秒）
            error_message: 错误信息（如有）
            tokens_used: Token使用量（OpenAI）
            model: 模型名称（OpenAI）
            metadata: 其他元数据
        """
        timestamp = datetime.now(timezone.utc)
        
        # 计算成本（仅OpenAI）
        cost_usd = None
        if api_type == APIType.OPENAI and tokens_used and model:
            cost_usd = self._calculate_openai_cost(tokens_used, model)
        
        record = APIUsageRecord(
            api_type=api_type,
            endpoint=endpoint,
            success=success,
            response_time_ms=response_time_ms,
            timestamp=timestamp,
            error_message=error_message,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            metadata=metadata or {}
        )
        
        # 添加到内存日志
        self._in_memory_logs.append(record)
        if len(self._in_memory_logs) > self._max_memory_logs:
            self._in_memory_logs = self._in_memory_logs[-self._max_memory_logs:]
        
        # 保存到数据库（异步或批量）
        self._save_to_database(record)
        
        # 检查错误率并触发告警
        self._check_error_rate(api_type)
    
    def _calculate_openai_cost(self, tokens_used: int, model: str) -> float:
        """计算OpenAI成本"""
        # 简化计算：假设50%输入，50%输出
        if model not in self.OPENAI_PRICING:
            # 默认使用gpt-4o-mini定价
            model = "gpt-4o-mini"
        
        pricing = self.OPENAI_PRICING[model]
        input_cost = (tokens_used * 0.5) * pricing["input"]
        output_cost = (tokens_used * 0.5) * pricing["output"]
        return input_cost + output_cost
    
    def _save_to_database(self, record: APIUsageRecord) -> None:
        """保存记录到数据库"""
        try:
            # 检查是否有APIUsageLog模型，如果没有则只记录到内存
            from src.core.database.models import APIUsageLog
            
            log_entry = APIUsageLog(
                api_type=record.api_type,
                endpoint=record.endpoint,
                success=record.success,
                response_time_ms=int(record.response_time_ms),
                timestamp=record.timestamp,
                error_message=record.error_message,
                tokens_used=record.tokens_used,
                cost_usd=f"{record.cost_usd:.10f}" if record.cost_usd else None,  # 使用固定格式，避免科学计数法
                metadata=record.metadata
            )
            
            self.db.add(log_entry)
            self.db.commit()
        except ImportError:
            # 模型不存在，只记录到内存
            pass
        except Exception as e:
            logger.error(f"Failed to save API usage log to database: {e}", exc_info=True)
            self.db.rollback()
    
    def _check_error_rate(self, api_type: str) -> None:
        """检查错误率并触发告警"""
        try:
            from src.monitoring.alerts import alert_manager, AlertLevel
            
            # 检查最近100次调用的错误率
            recent_calls = [r for r in self._in_memory_logs if r.api_type == api_type][-100:]
            if len(recent_calls) < 10:
                return  # 样本太少，不检查
            
            error_count = sum(1 for r in recent_calls if not r.success)
            error_rate = (error_count / len(recent_calls)) * 100
            
            # 触发告警
            if error_rate > 20:
                alert_manager.send_alert(
                    AlertLevel.ERROR,
                    f"{api_type.upper()} API错误率过高: {error_rate:.1f}%",
                    "api_usage_tracker",
                    details={
                        "api_type": api_type,
                        "error_rate": error_rate,
                        "error_count": error_count,
                        "total_calls": len(recent_calls)
                    },
                    rate_limit=timedelta(minutes=5)
                )
            elif error_rate > 10:
                alert_manager.send_alert(
                    AlertLevel.WARNING,
                    f"{api_type.upper()} API错误率较高: {error_rate:.1f}%",
                    "api_usage_tracker",
                    details={
                        "api_type": api_type,
                        "error_rate": error_rate,
                        "error_count": error_count,
                        "total_calls": len(recent_calls)
                    },
                    rate_limit=timedelta(minutes=10)
                )
        except Exception as e:
            logger.error(f"Error checking error rate: {e}", exc_info=True)
    
    def get_statistics(
        self,
        api_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取API使用统计
        
        Args:
            api_type: API类型过滤（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
        
        Returns:
            统计数据字典
        """
        # 从内存日志计算（快速）
        logs = self._in_memory_logs
        
        if api_type:
            logs = [r for r in logs if r.api_type == api_type]
        
        if start_date:
            logs = [r for r in logs if r.timestamp >= start_date]
        
        if end_date:
            logs = [r for r in logs if r.timestamp <= end_date]
        
        if not logs:
            return {
                "total_calls": 0,
                "success_calls": 0,
                "error_calls": 0,
                "success_rate": 0.0,
                "avg_response_time_ms": 0.0,
                "total_cost_usd": 0.0,
                "total_tokens": 0
            }
        
        success_count = sum(1 for r in logs if r.success)
        error_count = len(logs) - success_count
        success_rate = (success_count / len(logs)) * 100 if logs else 0
        avg_response_time = sum(r.response_time_ms for r in logs) / len(logs)
        total_cost = sum(r.cost_usd or 0 for r in logs)
        total_tokens = sum(r.tokens_used or 0 for r in logs)
        
        return {
            "total_calls": len(logs),
            "success_calls": success_count,
            "error_calls": error_count,
            "success_rate": round(success_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "api_type": api_type or "all"
        }
    
    def get_daily_statistics(
        self,
        target_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取指定日期的统计
        
        Args:
            target_date: 目标日期（默认为今天）
        
        Returns:
            每日统计数据
        """
        if target_date is None:
            target_date = datetime.now(timezone.utc)
        
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        stats = {}
        for api_type in [APIType.OPENAI, APIType.FACEBOOK, APIType.TELEGRAM]:
            stats[api_type.value] = self.get_statistics(
                api_type=api_type.value,
                start_date=start_of_day,
                end_date=end_of_day
            )
        
        # 总计
        stats["total"] = {
            "total_calls": sum(s["total_calls"] for s in stats.values() if isinstance(s, dict)),
            "total_cost_usd": sum(s["total_cost_usd"] for s in stats.values() if isinstance(s, dict)),
            "total_tokens": sum(s["total_tokens"] for s in stats.values() if isinstance(s, dict))
        }
        
        return stats

