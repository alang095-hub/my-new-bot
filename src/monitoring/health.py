"""健康检查和性能监控"""
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.core.database.connection import engine
from src.core.config import settings
from src.monitoring.alerts import alert_manager, AlertLevel
import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.request_count = 0
        self.error_count = 0
        self.response_times: list = []
    
    async def check_health(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        执行健康检查
        
        Args:
            db: 数据库会话
        
        Returns:
            健康检查结果
        """
        checks = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "checks": {}
        }
        
        # 数据库连接检查
        db_status = await self._check_database(db)
        checks["checks"]["database"] = db_status
        
        # API配置检查
        api_status = self._check_api_config()
        checks["checks"]["api_config"] = api_status
        
        # 系统资源检查
        resource_status = self._check_resources()
        checks["checks"]["resources"] = resource_status
        
        # 确定总体状态
        all_healthy = all(
            check.get("status") == "healthy"
            for check in checks["checks"].values()
        )
        
        if not all_healthy:
            checks["status"] = "degraded"
        
        # 如果有严重问题，发送告警
        critical_issues = [
            name for name, check in checks["checks"].items()
            if check.get("status") == "unhealthy"
        ]
        
        if critical_issues:
            checks["status"] = "unhealthy"
            alert_manager.send_alert(
                AlertLevel.ERROR,
                f"健康检查失败: {', '.join(critical_issues)}",
                "health_checker",
                details={"failed_checks": critical_issues},
                rate_limit=timedelta(minutes=5)
            )
        
        return checks
    
    async def _check_database(self, db: Optional[Session]) -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            if db:
                db.execute(text("SELECT 1"))
                return {
                    "status": "healthy",
                    "message": "Database connection OK",
                    "response_time_ms": 0
                }
            else:
                # 直接使用engine检查
                start = time.time()
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                response_time = (time.time() - start) * 1000
                
                return {
                    "status": "healthy",
                    "message": "Database connection OK",
                    "response_time_ms": round(response_time, 2)
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "error": str(e)
            }
    
    def _check_api_config(self) -> Dict[str, Any]:
        """检查API配置"""
        issues = []
        
        # 检查必需的配置
        required_configs = {
            "facebook_access_token": getattr(settings, 'facebook_access_token', None),
            "openai_api_key": getattr(settings, 'openai_api_key', None),
            "telegram_bot_token": getattr(settings, 'telegram_bot_token', None),
        }
        
        missing = [key for key, value in required_configs.items() if not value]
        
        if missing:
            issues.append(f"Missing configs: {', '.join(missing)}")
        
        # 检查配置是否为占位符
        placeholder_configs = []
        for key, value in required_configs.items():
            if value and isinstance(value, str) and value.startswith('your_'):
                placeholder_configs.append(key)
        
        if placeholder_configs:
            issues.append(f"Placeholder configs: {', '.join(placeholder_configs)}")
        
        if issues:
            return {
                "status": "unhealthy",
                "message": "; ".join(issues),
                "issues": issues
            }
        
        return {
            "status": "healthy",
            "message": "All API configurations OK"
        }
    
    def _check_resources(self) -> Dict[str, Any]:
        """检查系统资源"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            warnings = []
            
            if cpu_percent > 90:
                warnings.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 90:
                warnings.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > 90:
                warnings.append(f"High disk usage: {disk.percent}%")
            
            status = "healthy" if not warnings else "degraded"
            
            return {
                "status": status,
                "message": "Resource check OK" if not warnings else "; ".join(warnings),
                "metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent
                },
                "warnings": warnings if warnings else None
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available, skipping resource check"
            }
        except Exception as e:
            logger.error(f"Resource check failed: {e}")
            return {
                "status": "unknown",
                "message": f"Resource check error: {str(e)}"
            }
    
    def record_request(self, response_time_ms: float, is_error: bool = False) -> None:
        """记录请求指标"""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        
        self.response_times.append(response_time_ms)
        
        # 只保留最近1000个请求的响应时间
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        if not self.response_times:
            avg_response_time = 0
            p95_response_time = 0
        else:
            sorted_times = sorted(self.response_times)
            avg_response_time = sum(sorted_times) / len(sorted_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
        
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "p95_response_time_ms": round(p95_response_time, 2),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }


# 全局健康检查器实例
health_checker = HealthChecker()

