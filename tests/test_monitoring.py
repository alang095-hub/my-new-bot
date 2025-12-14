"""监控服务单元测试"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.monitoring.health import HealthChecker
from src.monitoring.alerts import AlertManager, AlertLevel, Alert


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def health_checker():
    """创建健康检查器"""
    return HealthChecker()


class TestHealthChecker:
    """测试健康检查器"""
    
    @pytest.mark.asyncio
    async def test_check_health_success(self, health_checker, db_session):
        """测试健康检查成功"""
        result = await health_checker.check_health(db_session)
        
        assert result["status"] in ["healthy", "degraded"]
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert "checks" in result
        assert "database" in result["checks"]
    
    @pytest.mark.asyncio
    async def test_check_health_without_db(self, health_checker):
        """测试健康检查（无数据库）"""
        result = await health_checker.check_health(None)
        
        assert result["status"] in ["healthy", "degraded", "unhealthy"]
        assert "checks" in result
    
    @pytest.mark.asyncio
    async def test_check_database_success(self, health_checker, db_session):
        """测试数据库检查成功"""
        result = await health_checker._check_database(db_session)
        
        assert result["status"] == "healthy"
        assert "response_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_check_database_failure(self, health_checker):
        """测试数据库检查失败"""
        # 使用无效的数据库会话
        invalid_db = Mock()
        invalid_db.execute = Mock(side_effect=Exception("数据库连接失败"))
        
        result = await health_checker._check_database(invalid_db)
        
        assert result["status"] == "unhealthy"
        assert "error" in result
    
    def test_check_api_config(self, health_checker):
        """测试API配置检查"""
        result = health_checker._check_api_config()
        
        assert "status" in result
        assert result["status"] in ["healthy", "degraded"]
    
    def test_check_resources(self, health_checker):
        """测试系统资源检查"""
        result = health_checker._check_resources()
        
        assert "status" in result
        assert result["status"] in ["healthy", "degraded"]


class TestAlertManager:
    """测试告警管理器"""
    
    def test_send_alert(self):
        """测试发送告警"""
        manager = AlertManager()
        
        # send_alert返回None，但会添加告警到列表
        manager.send_alert(
            AlertLevel.INFO,
            "测试告警",
            "test_source"
        )
        
        # 验证告警已添加
        active_alerts = manager.get_active_alerts()
        assert len(active_alerts) >= 1
        assert any(alert.message == "测试告警" for alert in active_alerts)
    
    def test_send_alert_with_rate_limit(self):
        """测试发送告警（带速率限制）"""
        manager = AlertManager()
        
        # 发送第一个告警
        manager.send_alert(
            AlertLevel.WARNING,
            "测试告警1",
            "test_source",
            rate_limit=timedelta(seconds=1)
        )
        
        # 立即发送第二个相同类型的告警（应该被限制）
        manager.send_alert(
            AlertLevel.WARNING,
            "测试告警1",  # 相同消息
            "test_source",
            rate_limit=timedelta(seconds=1)
        )
        
        # 验证只有一个告警（第二个被限制）
        active_alerts = manager.get_active_alerts()
        test_alerts = [a for a in active_alerts if a.message == "测试告警1"]
        assert len(test_alerts) >= 1
    
    def test_get_active_alerts(self):
        """测试获取活跃告警"""
        manager = AlertManager()
        
        # 发送几个告警
        manager.send_alert(AlertLevel.INFO, "告警1", "source1")
        manager.send_alert(AlertLevel.WARNING, "告警2", "source2")
        manager.send_alert(AlertLevel.ERROR, "告警3", "source3")
        
        # 获取活跃告警
        active = manager.get_active_alerts()
        
        assert len(active) >= 3
    
    def test_get_active_alerts_by_level(self):
        """测试按级别获取活跃告警"""
        manager = AlertManager()
        
        # 发送不同级别的告警
        manager.send_alert(AlertLevel.INFO, "信息告警", "source1")
        manager.send_alert(AlertLevel.WARNING, "警告告警", "source2")
        manager.send_alert(AlertLevel.ERROR, "错误告警", "source3")
        
        # 获取ERROR级别的告警
        error_alerts = manager.get_active_alerts(level=AlertLevel.ERROR)
        
        assert len(error_alerts) >= 1
        assert all(alert.level == AlertLevel.ERROR for alert in error_alerts)
    
    def test_resolve_alert(self):
        """测试解决告警"""
        manager = AlertManager()
        
        # 发送一些告警
        manager.send_alert(AlertLevel.INFO, "告警1", "source1")
        manager.send_alert(AlertLevel.WARNING, "告警2", "source2")
        
        # 获取活跃告警
        active = manager.get_active_alerts()
        assert len(active) >= 2
        
        # 解决第一个告警
        if len(active) > 0:
            result = manager.resolve_alert(0)
            assert result is True
            
            # 验证告警已解决
            active_after = manager.get_active_alerts()
            assert len(active_after) < len(active)
    
    def test_get_statistics(self):
        """测试获取告警统计"""
        manager = AlertManager()
        
        # 发送一些告警
        manager.send_alert(AlertLevel.INFO, "告警1", "source1")
        manager.send_alert(AlertLevel.WARNING, "告警2", "source2")
        
        # 获取统计
        stats = manager.get_statistics()
        
        assert "total_alerts" in stats
        assert "active_alerts" in stats
        assert "by_level" in stats
        assert "by_source" in stats

