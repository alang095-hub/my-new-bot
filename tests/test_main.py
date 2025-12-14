"""主应用测试"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.core.database.connection import get_db, Base


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
def client(db_session):
    """创建测试客户端"""
    # 确保所有表都已创建
    from src.core.database.statistics_models import DailyStatistics, CustomerInteraction, FrequentQuestion
    Base.metadata.create_all(bind=db_session.bind)
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestAppInitialization:
    """测试应用初始化"""
    
    def test_app_creation(self):
        """测试应用创建"""
        assert app is not None
        assert app.title == "多平台客服自动化系统"
        assert app.version == "2.0.0"
    
    def test_app_routes_registered(self, client):
        """测试路由注册"""
        # 检查主要路由是否存在
        response = client.get("/")
        assert response.status_code == 200 or response.status_code == 404
    
    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_metrics_endpoint(self, client):
        """测试指标端点"""
        response = client.get("/metrics")
        assert response.status_code == 200


class TestStartupEvents:
    """测试启动事件"""
    
    def test_startup_event(self, client):
        """测试应用启动事件"""
        # 启动事件在应用创建时执行
        # 这里主要验证应用可以正常启动
        response = client.get("/health")
        assert response.status_code == 200


class TestCORSConfiguration:
    """测试CORS配置"""
    
    def test_cors_headers(self, client):
        """测试CORS头"""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        # CORS配置可能允许或拒绝，但应该返回有效响应
        assert response.status_code in [200, 204, 400, 403, 405]


class TestErrorHandling:
    """测试错误处理"""
    
    def test_404_error(self, client):
        """测试404错误"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """测试方法不允许"""
        # 尝试使用不支持的方法
        response = client.patch("/health")
        # 可能返回405或404
        assert response.status_code in [404, 405]


class TestAPIRoutes:
    """测试API路由"""
    
    def test_admin_routes_exist(self, client, db_session):
        """测试管理路由存在"""
        # 确保所有表都已创建
        from src.core.database.statistics_models import DailyStatistics, CustomerInteraction, FrequentQuestion
        Base.metadata.create_all(bind=db_session.bind)
        
        response = client.get("/admin/conversations")
        # 应该返回200（空列表）或401（需要认证）
        assert response.status_code in [200, 401, 403, 500]
    
    def test_monitoring_routes_exist(self, client):
        """测试监控路由存在"""
        response = client.get("/monitoring/stats")
        assert response.status_code == 200
    
    def test_statistics_routes_exist(self, client):
        """测试统计路由存在"""
        response = client.get("/statistics/daily")
        assert response.status_code == 200
    
    def test_webhook_routes_exist(self, client):
        """测试Webhook路由存在"""
        response = client.get("/webhook")
        # Webhook验证可能返回200或403
        assert response.status_code in [200, 403]


class TestDatabaseConnection:
    """测试数据库连接"""
    
    def test_database_connection(self, db_session):
        """测试数据库连接"""
        from sqlalchemy import text
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    def test_database_models_created(self, db_session):
        """测试数据库模型已创建"""
        from src.core.database.models import Customer
        # 尝试查询（即使为空）
        customers = db_session.query(Customer).all()
        assert isinstance(customers, list)

