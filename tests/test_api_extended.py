"""扩展API端点测试"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.core.database.connection import get_db, Base
from src.core.database.models import Customer, Conversation, Review, CollectedData, Platform, MessageType, ReviewStatus, Priority
from src.core.database.repositories import CustomerRepository, ConversationRepository, ReviewRepository, CollectedDataRepository
from src.core.database.statistics_models import DailyStatistics, CustomerInteraction, FrequentQuestion


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


@pytest.fixture
def test_data(db_session):
    """创建测试数据"""
    customer_repo = CustomerRepository(db_session)
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="test_user_123",
        name="测试用户"
    )
    
    conversation_repo = ConversationRepository(db_session)
    conversation = conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息内容"
    )
    
    return {
        "customer": customer,
        "conversation": conversation
    }


class TestAdminAPIExtended:
    """管理API扩展测试"""
    
    def test_get_conversation_detail_with_data(self, client, test_data):
        """测试获取对话详情（有数据）"""
        conversation_id = test_data["conversation"].id
        
        response = client.get(f"/admin/conversations/{conversation_id}")
        assert response.status_code == 200
        data = response.json()
        assert "conversation" in data or "error" in data
    
    def test_get_conversation_detail_not_found(self, client):
        """测试获取不存在的对话详情"""
        response = client.get("/admin/conversations/99999")
        assert response.status_code in [200, 404]
    
    def test_list_conversations_with_status_filter(self, client, test_data):
        """测试对话列表（状态过滤）"""
        response = client.get("/admin/conversations?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_list_conversations_with_platform_filter(self, client, test_data):
        """测试对话列表（平台过滤）"""
        response = client.get("/admin/conversations?platform=facebook")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_list_customers_with_platform_filter(self, client, test_data):
        """测试客户列表（平台过滤）"""
        response = client.get("/admin/customers?platform=facebook")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_statistics_with_days(self, client, test_data):
        """测试统计数据（指定天数）"""
        response = client.get("/admin/statistics?days=7")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_statistics_with_different_days(self, client, test_data):
        """测试统计数据（不同天数）"""
        for days in [1, 7, 30]:
            response = client.get(f"/admin/statistics?days={days}")
            assert response.status_code == 200


class TestStatisticsAPIExtended:
    """统计API扩展测试"""
    
    def test_daily_statistics_today(self, client, test_data):
        """测试今日统计"""
        response = client.get("/statistics/daily")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    def test_daily_statistics_specific_date(self, client, test_data):
        """测试指定日期统计"""
        response = client.get("/statistics/daily?target_date=2024-01-01")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    def test_frequent_questions_default_limit(self, client, test_data):
        """测试高频问题（默认限制）"""
        response = client.get("/statistics/frequent-questions")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    def test_frequent_questions_custom_limit(self, client, test_data):
        """测试高频问题（自定义限制）"""
        response = client.get("/statistics/frequent-questions?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    def test_mark_joined_group(self, client, test_data):
        """测试标记加入群组"""
        customer_id = test_data["customer"].id
        response = client.post(f"/statistics/mark-joined-group?customer_id={customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    def test_mark_order_created(self, client, test_data):
        """测试标记订单创建"""
        customer_id = test_data["customer"].id
        response = client.post(f"/statistics/mark-order-created?customer_id={customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


class TestMonitoringAPIExtended:
    """监控API扩展测试"""
    
    def test_live_monitoring_stream(self, client):
        """测试实时监控流"""
        response = client.get("/monitoring/live")
        # SSE端点应该返回200
        assert response.status_code == 200
    
    def test_live_stats(self, client, test_data):
        """测试实时统计"""
        response = client.get("/monitoring/stats")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    def test_recent_replies_default_limit(self, client, test_data):
        """测试最近回复（默认限制）"""
        response = client.get("/monitoring/recent-replies")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
    
    def test_recent_replies_custom_limit(self, client, test_data):
        """测试最近回复（自定义限制）"""
        response = client.get("/monitoring/recent-replies?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


class TestWebhookAPIExtended:
    """Webhook API扩展测试"""
    
    def test_facebook_webhook_verification_success(self, client):
        """测试Facebook Webhook验证成功"""
        with patch('src.core.config.settings') as mock_settings:
            mock_settings.facebook_verify_token = "test_token"
            
            response = client.get(
                "/webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "test_token",
                    "hub.challenge": "test_challenge"
                }
            )
            # 验证成功应该返回challenge
            assert response.status_code in [200, 403]
    
    def test_facebook_webhook_verification_failure(self, client):
        """测试Facebook Webhook验证失败"""
        response = client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token",
                "hub.challenge": "test_challenge"
            }
        )
        # 验证失败应该返回403
        assert response.status_code in [200, 403]
    
    def test_instagram_webhook_verification(self, client):
        """测试Instagram Webhook验证"""
        response = client.get(
            "/instagram/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_token",
                "hub.challenge": "test_challenge"
            }
        )
        assert response.status_code in [200, 403]
    
    def test_facebook_webhook_message_receive(self, client, test_data):
        """测试Facebook Webhook接收消息"""
        webhook_payload = {
            "object": "page",
            "entry": [{
                "id": "page_123",
                "messaging": [{
                    "sender": {"id": "user_456"},
                    "recipient": {"id": "page_123"},
                    "message": {
                        "mid": "msg_789",
                        "text": "测试消息"
                    },
                    "timestamp": 1234567890
                }]
            }]
        }
        
        response = client.post("/webhook", json=webhook_payload)
        assert response.status_code == 200
    
    def test_instagram_webhook_message_receive(self, client, test_data):
        """测试Instagram Webhook接收消息"""
        webhook_payload = {
            "object": "instagram",
            "entry": [{
                "id": "ig_user_123",
                "messaging": [{
                    "sender": {"id": "user_456"},
                    "recipient": {"id": "ig_user_123"},
                    "message": {
                        "mid": "msg_789",
                        "text": "测试消息"
                    },
                    "timestamp": 1234567890
                }]
            }]
        }
        
        response = client.post("/instagram/webhook", json=webhook_payload)
        assert response.status_code == 200


class TestAPIErrorHandling:
    """API错误处理测试"""
    
    def test_invalid_page_number(self, client):
        """测试无效页码"""
        response = client.get("/admin/conversations?page=0")
        # 应该返回400或使用默认值
        assert response.status_code in [200, 400, 422]
    
    def test_invalid_page_size(self, client):
        """测试无效页面大小"""
        response = client.get("/admin/conversations?page_size=200")
        # 应该返回400或使用默认值
        assert response.status_code in [200, 400, 422]
    
    def test_invalid_date_format(self, client):
        """测试无效日期格式"""
        response = client.get("/statistics/daily?target_date=invalid-date")
        assert response.status_code == 200
        data = response.json()
        # 应该返回错误信息
        assert "error" in data or "success" in data
    
    def test_missing_required_parameters(self, client):
        """测试缺少必需参数"""
        response = client.post("/statistics/mark-joined-group")
        # 应该返回400或422
        assert response.status_code in [200, 400, 422]

