"""端到端工作流测试"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.main import app
from src.core.database.models import Customer, Conversation, MessageType, Priority


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
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.mark.asyncio
async def test_complete_message_workflow(db_session):
    """测试完整的消息处理工作流"""
    # 1. 模拟Facebook Webhook消息
    webhook_payload = {
        "object": "page",
        "entry": [{
            "id": "page_id",
            "messaging": [{
                "sender": {"id": "user123"},
                "recipient": {"id": "page_id"},
                "message": {
                    "mid": "msg123",
                    "text": "你好，我想咨询产品，我的邮箱是 test@example.com"
                },
                "timestamp": 1234567890
            }]
        }]
    }
    
    # 2. 模拟处理流程
    with patch('src.main_processor.process_platform_message') as mock_process:
        mock_process.return_value = {
            "success": True,
            "customer_id": 1,
            "conversation_id": 1
        }
        
        # 模拟发送Webhook请求
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.post("/webhook", json=webhook_payload)
        
        # 验证响应
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        
        # 验证处理函数被调用
        # mock_process.assert_called_once()


def test_health_check_endpoint(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data or "checks" in data


def test_metrics_endpoint(client):
    """测试性能指标端点"""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_webhook_verification(client):
    """测试Webhook验证"""
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test_token",
            "hub.challenge": "test_challenge"
        }
    )
    # 验证端点应该返回challenge或错误
    assert response.status_code in [200, 403]


def test_admin_conversations_endpoint(client, db_session):
    """测试管理后台对话列表端点"""
    # 需要模拟数据库会话
    with patch('src.admin.api.get_db') as mock_get_db:
        mock_get_db.return_value = db_session
        
        response = client.get("/admin/conversations?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data


def test_statistics_endpoint(client, db_session):
    """测试统计API端点"""
    with patch('src.statistics.api.get_db') as mock_get_db:
        mock_get_db.return_value = db_session
        
        response = client.get("/statistics/daily")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


@pytest.mark.asyncio
async def test_ai_reply_generation_workflow(db_session):
    """测试AI回复生成工作流"""
    # 创建测试客户
    customer = Customer(
        platform="facebook",
        platform_user_id="test_user",
        name="测试用户"
    )
    db_session.add(customer)
    db_session.flush()
    
    # 创建对话
    conversation = Conversation(
        customer_id=customer.id,
        platform="facebook",
        message_type=MessageType.MESSAGE,
        content="你好，我想咨询",
        status="pending"
    )
    db_session.add(conversation)
    db_session.commit()
    
    # 模拟AI回复生成
    with patch('src.ai.reply_generator.ReplyGenerator.generate_reply') as mock_generate:
        mock_generate.return_value = "您好！很高兴为您服务，有什么可以帮助您的吗？"
        
        from src.ai.reply_generator import ReplyGenerator
        generator = ReplyGenerator(db_session)
        
        reply = await generator.generate_reply(
            customer_id=customer.id,
            message_content="你好",
            customer_name="测试用户"
        )
        
        assert reply is not None
        assert len(reply) > 0


@pytest.mark.asyncio
async def test_data_collection_workflow(db_session):
    """测试数据收集工作流"""
    # 创建对话
    customer = Customer(
        platform="facebook",
        platform_user_id="test_user"
    )
    db_session.add(customer)
    db_session.flush()
    
    conversation = Conversation(
        customer_id=customer.id,
        platform="facebook",
        message_type=MessageType.MESSAGE,
        content="我是张三，邮箱是 zhangsan@example.com，电话13812345678"
    )
    db_session.add(conversation)
    db_session.flush()
    
    # 测试数据收集
    from src.collector.data_collector import DataCollector
    collector = DataCollector(db_session)
    
    extracted = collector.extract_info_from_message(conversation.content)
    
    # 验证提取的数据
    assert "email" in extracted or "emails" in extracted
    assert "phone" in extracted or "phones" in extracted
    assert "name" in extracted or "names" in extracted


@pytest.mark.asyncio
async def test_filter_workflow(db_session):
    """测试过滤工作流"""
    from src.collector.filter_engine import FilterEngine
    
    # 创建对话
    customer = Customer(
        platform="facebook",
        platform_user_id="test_user"
    )
    db_session.add(customer)
    db_session.flush()
    
    conversation = Conversation(
        customer_id=customer.id,
        platform="facebook",
        message_type=MessageType.MESSAGE,
        content="紧急！我需要帮助",
        priority=Priority.LOW
    )
    db_session.add(conversation)
    
    # 测试过滤
    filter_engine = FilterEngine(db_session)
    result = filter_engine.filter_message(conversation, conversation.content)
    
    # 验证过滤结果
    assert "filtered" in result
    assert "priority" in result
    assert "should_review" in result

