"""提示词A/B测试管理器"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from src.core.database.models import PromptVersion, PromptUsageLog
from src.core.database.repositories.base import BaseRepository
import random
import logging

logger = logging.getLogger(__name__)


class PromptVersionRepository(BaseRepository[PromptVersion]):
    """提示词版本Repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, PromptVersion)
    
    def get_active_versions(self) -> list[PromptVersion]:
        """获取所有启用的版本"""
        return self.db.query(self.model)\
            .filter(self.model.is_active == True)\
            .order_by(self.model.created_at.desc())\
            .all()
    
    def get_by_version_code(self, version_code: str) -> Optional[PromptVersion]:
        """根据版本代码获取"""
        return self.get_by(version_code=version_code)
    
    def increment_usage(self, version_id: int, response_time_ms: Optional[int] = None) -> None:
        """增加使用次数并更新平均响应时间"""
        version = self.get(version_id)
        if not version:
            return
        
        version.total_uses += 1
        
        if response_time_ms is not None:
            # 更新平均响应时间（简单移动平均）
            if version.avg_response_time_ms:
                version.avg_response_time_ms = int(
                    (version.avg_response_time_ms * 0.9) + (response_time_ms * 0.1)
                )
            else:
                version.avg_response_time_ms = response_time_ms
        
        self.db.commit()


class PromptABTesting:
    """提示词A/B测试管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.version_repo = PromptVersionRepository(db)
    
    def select_version(self, customer_id: int) -> Optional[PromptVersion]:
        """
        为指定客户选择提示词版本（基于流量分配）
        
        Args:
            customer_id: 客户ID
        
        Returns:
            选中的提示词版本
        """
        active_versions = self.version_repo.get_active_versions()
        
        if not active_versions:
            logger.warning("No active prompt versions found")
            return None
        
        # 如果只有一个版本，直接返回
        if len(active_versions) == 1:
            return active_versions[0]
        
        # 基于客户ID的哈希值进行一致性分配（确保同一客户总是使用同一版本）
        # 使用简单的取模方式
        version_index = customer_id % len(active_versions)
        selected_version = active_versions[version_index]
        
        # 或者使用流量百分比分配（更复杂但更灵活）
        # 这里简化处理，使用轮询方式
        
        return selected_version
    
    def record_usage(
        self,
        prompt_version_id: int,
        customer_id: int,
        conversation_id: int,
        response_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
        success: bool = True
    ) -> None:
        """
        记录提示词使用情况
        
        Args:
            prompt_version_id: 提示词版本ID
            customer_id: 客户ID
            conversation_id: 对话ID
            response_time_ms: 响应时间
            tokens_used: Token使用量
            success: 是否成功
        """
        try:
            # 创建使用日志
            usage_log = PromptUsageLog(
                prompt_version_id=prompt_version_id,
                customer_id=customer_id,
                conversation_id=conversation_id,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                success=success,
                used_at=datetime.now(timezone.utc)
            )
            
            self.db.add(usage_log)
            
            # 更新版本统计
            self.version_repo.increment_usage(prompt_version_id, response_time_ms)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to record prompt usage: {e}", exc_info=True)
            self.db.rollback()
    
    def get_version_statistics(
        self,
        version_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        获取版本统计信息
        
        Args:
            version_id: 版本ID（可选，如果为None则返回所有版本）
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            统计数据
        """
        query = self.db.query(PromptUsageLog)
        
        if version_id:
            query = query.filter(PromptUsageLog.prompt_version_id == version_id)
        
        if start_date:
            query = query.filter(PromptUsageLog.used_at >= start_date)
        
        if end_date:
            query = query.filter(PromptUsageLog.used_at <= end_date)
        
        # 统计总数
        total_uses = query.count()
        
        # 统计成功数
        success_count = query.filter(PromptUsageLog.success == True).count()
        
        # 统计平均响应时间
        avg_response_time = query.with_entities(
            func.avg(PromptUsageLog.response_time_ms)
        ).scalar() or 0
        
        # 统计总Token使用量
        total_tokens = query.with_entities(
            func.sum(PromptUsageLog.tokens_used)
        ).scalar() or 0
        
        return {
            "total_uses": total_uses,
            "success_count": success_count,
            "failure_count": total_uses - success_count,
            "success_rate": (success_count / total_uses * 100) if total_uses > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_tokens": total_tokens
        }
    
    def compare_versions(
        self,
        version_ids: list[int],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        对比多个版本的效果
        
        Args:
            version_ids: 版本ID列表
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            对比结果
        """
        comparison = {}
        
        for version_id in version_ids:
            version = self.version_repo.get(version_id)
            if not version:
                continue
            
            stats = self.get_version_statistics(version_id, start_date, end_date)
            
            comparison[version.version_code] = {
                "version_name": version.name,
                "version_code": version.version_code,
                "statistics": stats
            }
        
        return comparison

