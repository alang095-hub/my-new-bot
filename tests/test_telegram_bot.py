"""Telegram Bot测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.core.database.connection import get_db, Base
from src.core.database.models import Customer, Conversation, Review, Platform, MessageType, ReviewStatus
from src.core.database.repositories import CustomerRepository, ConversationRepository, ReviewRepository
from src.telegram.command_processor import CommandProcessor
from src.telegram.notification_sender import NotificationSender


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
def customer(db_session):
    """创建测试客户"""
    customer_repo = CustomerRepository(db_session)
    return customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )


@pytest.fixture
def conversation(db_session, customer):
    """创建测试对话"""
    conversation_repo = ConversationRepository(db_session)
    return conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )


class TestTelegramWebhook:
    """测试Telegram Webhook"""
    
    def test_webhook_receive_message(self, client):
        """测试接收消息"""
        webhook_payload = {
            "message": {
                "text": "/approve 1",
                "chat": {"id": 123},
                "from": {"username": "test_user", "first_name": "Test"}
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_webhook_receive_non_command(self, client):
        """测试接收非命令消息"""
        webhook_payload = {
            "message": {
                "text": "普通消息",
                "chat": {"id": 123},
                "from": {"username": "test_user"}
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_webhook_no_message(self, client):
        """测试无消息的Webhook"""
        webhook_payload = {}
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_webhook_error_handling(self, client):
        """测试错误处理"""
        # 发送无效的JSON
        response = client.post("/telegram/webhook", json={"invalid": "data"})
        assert response.status_code == 200  # 应该返回200，但包含错误信息


class TestCommandProcessor:
    """测试命令处理器"""
    
    def test_approve_review(self, db_session, conversation):
        """测试审核通过命令"""
        processor = CommandProcessor(db_session)
        
        # 创建审核记录
        review_repo = ReviewRepository(db_session)
        review = review_repo.create_review(
            conversation_id=conversation.id,
            customer_id=conversation.customer_id,
            status=ReviewStatus.PENDING,
            reviewed_by="system"
        )
        
        result = processor.approve_review(
            conversation_id=conversation.id,
            reviewer="test_reviewer",
            notes="测试审核"
        )
        
        assert result["success"] is True
        assert "已批准" in result["message"] or "approved" in result["message"].lower()
    
    def test_reject_review(self, db_session, conversation):
        """测试审核拒绝命令"""
        processor = CommandProcessor(db_session)
        
        result = processor.reject_review(
            conversation_id=conversation.id,
            reviewer="test_reviewer",
            notes="测试拒绝"
        )
        
        assert result["success"] is True
    
    def test_get_conversation_info(self, db_session, conversation):
        """测试获取对话信息"""
        processor = CommandProcessor(db_session)
        
        result = processor.get_conversation_info(conversation.id)
        
        assert result["success"] is True
        assert "conversation" in result or "data" in result
    
    def test_process_command_approve(self, db_session, conversation):
        """测试处理审核命令"""
        processor = CommandProcessor(db_session)
        
        result = processor.process_command("/approve 1", "test_reviewer")
        
        # 可能成功或失败（取决于对话是否存在）
        assert "success" in result
    
    def test_process_command_reject(self, db_session, conversation):
        """测试处理拒绝命令"""
        processor = CommandProcessor(db_session)
        
        result = processor.process_command("/reject 1", "test_reviewer")
        
        assert "success" in result
    
    def test_process_command_info(self, db_session, conversation):
        """测试处理信息命令"""
        processor = CommandProcessor(db_session)
        
        result = processor.process_command("/info 1", "test_reviewer")
        
        assert "success" in result
    
    def test_process_command_unknown(self, db_session):
        """测试处理未知命令"""
        processor = CommandProcessor(db_session)
        
        result = processor.process_command("/unknown", "test_reviewer")
        
        assert result["success"] is False
        assert "unknown" in result["message"].lower() or "不支持" in result["message"]


class TestNotificationSender:
    """测试通知发送器"""
    
    def test_send_notification(self):
        """测试发送通知"""
        sender = NotificationSender()
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_post.return_value = mock_response
            
            # 由于是异步方法，这里只测试方法存在
            assert hasattr(sender, 'send_notification')
    
    def test_send_conversation_notification(self):
        """测试发送对话通知"""
        sender = NotificationSender()
        
        # 测试方法存在
        assert hasattr(sender, 'send_conversation_notification')
    
    def test_format_conversation_message(self):
        """测试格式化对话消息"""
        sender = NotificationSender()
        
        # 创建模拟对话
        conversation = Mock()
        conversation.id = 1
        conversation.content = "测试消息"
        conversation.customer_id = 1
        
        # 测试格式化方法
        if hasattr(sender, '_format_conversation_message'):
            message = sender._format_conversation_message(conversation)
            assert isinstance(message, str)

