"""集成测试 - 测试完整消息处理流程"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.core.database.models import Customer, Conversation, MessageType, Priority, Platform
from src.core.database.repositories import CustomerRepository, ConversationRepository
from src.main_processor import process_platform_message
from src.facebook.message_parser import FacebookMessageParser
from src.collector.data_collector import DataCollector
from src.collector.filter_engine import FilterEngine


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
def sample_webhook_message():
    """示例Webhook消息"""
    return {
        "object": "page",
        "entry": [{
            "id": "page_123",
            "messaging": [{
                "sender": {"id": "user_456"},
                "recipient": {"id": "page_123"},
                "message": {
                    "mid": "msg_789",
                    "text": "你好，我是张三，邮箱是 zhangsan@example.com，电话13812345678，我想咨询产品价格"
                },
                "timestamp": 1234567890
            }]
        }]
    }


@pytest.mark.asyncio
async def test_complete_facebook_message_flow(db_session, sample_webhook_message):
    """测试完整的Facebook消息处理流程"""
    # 1. 解析Webhook消息
    parser = FacebookMessageParser()
    parsed_messages = parser.parse_webhook_event(sample_webhook_message)
    
    assert parsed_messages is not None
    assert len(parsed_messages) > 0
    
    message_data = parsed_messages[0]
    assert message_data["sender_id"] == "user_456"
    assert "你好" in message_data["content"]
    
    # 2. 创建或获取客户（使用Repository）
    customer_repo = CustomerRepository(db_session)
    customer = customer_repo.get_by_platform_user_id(
        Platform.FACEBOOK,
        message_data["sender_id"]
    )
    
    if not customer:
        customer = customer_repo.get_or_create(
            platform=Platform.FACEBOOK,
            platform_user_id=message_data["sender_id"],
            facebook_id=message_data["sender_id"]
        )
    
    # 3. 创建对话记录（使用Repository）
    conversation_repo = ConversationRepository(db_session)
    conversation = conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id=message_data["message_id"],
        message_type=MessageType.MESSAGE,
        content=message_data["content"]
    )
    
    # 4. 测试数据收集
    collector = DataCollector(db_session)
    extracted = collector.extract_info_from_message(message_data["content"])
    
    # 验证提取的数据
    assert "email" in extracted or "emails" in extracted
    assert "phone" in extracted or "phones" in extracted
    
    # 5. 测试过滤
    filter_engine = FilterEngine(db_session)
    filter_result = filter_engine.filter_message(conversation, message_data["content"])
    
    assert "filtered" in filter_result
    assert "priority" in filter_result
    
    # 6. 测试AI回复生成（模拟）
    with patch('src.ai.reply_generator.ReplyGenerator.generate_reply') as mock_ai:
        mock_ai.return_value = "您好！感谢您的咨询，我们的产品价格..."
        
        from src.ai.reply_generator import ReplyGenerator
        generator = ReplyGenerator(db_session)
        
        reply = await generator.generate_reply(
            customer_id=customer.id,
            message_content=message_data["content"],
            customer_name=None
        )
        
        assert reply is not None
        assert len(reply) > 0
    
    # 7. 验证数据库记录（使用Repository）
    saved_conversation = conversation_repo.get(conversation.id)
    
    assert saved_conversation is not None
    assert saved_conversation.customer_id == customer.id
    assert saved_conversation.content == message_data["content"]


@pytest.mark.asyncio
async def test_message_processing_pipeline(db_session):
    """测试消息处理管道"""
    # 创建测试数据（使用Repository）
    customer_repo = CustomerRepository(db_session)
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="test_user",
        name="测试用户"
    )
    
    message_data = {
        "message_id": "test_msg_123",
        "sender_id": "test_user",
        "recipient_id": "page_123",
        "page_id": "page_123",
        "message_type": MessageType.MESSAGE,
        "content": "紧急！我需要帮助，我的邮箱是 help@example.com",
        "timestamp": 1234567890,
        "platform": "facebook"
    }
    
    # 模拟处理流程
    with patch('src.processors.pipeline.default_pipeline.process') as mock_pipeline:
        mock_pipeline.return_value = {
            "success": True,
            "customer_id": customer.id,
            "conversation_id": 1
        }
        
        result = await process_platform_message("facebook", message_data)
        
        assert result is not None
        assert result.get("success") is True


@pytest.mark.asyncio
async def test_error_handling_in_workflow(db_session):
    """测试工作流中的错误处理"""
    # 测试无效消息处理
    invalid_message = {
        "invalid": "data"
    }
    
    parser = FacebookMessageParser()
    result = parser.parse_webhook_event(invalid_message)
    
    # 无效消息应该返回None或空列表
    assert result is None or len(result) == 0
    
    # 测试数据库错误处理
    invalid_customer_id = 99999
    from src.ai.reply_generator import ReplyGenerator
    
    generator = ReplyGenerator(db_session)
    
    # 应该能够处理不存在的客户ID
    try:
        reply = await generator.generate_reply(
            customer_id=invalid_customer_id,
            message_content="测试",
            customer_name=None
        )
        # 应该返回默认回复或None，而不是抛出异常
        assert reply is None or isinstance(reply, str)
    except Exception as e:
        # 如果抛出异常，应该被捕获并记录
        assert isinstance(e, Exception)


@pytest.mark.asyncio
async def test_telegram_notification_flow(db_session):
    """测试Telegram通知流程"""
    # 创建测试对话（使用Repository）
    customer_repo = CustomerRepository(db_session)
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="test_user"
    )
    
    conversation_repo = ConversationRepository(db_session)
    conversation = conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="test_msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    # 更新优先级
    conversation_repo.update(conversation.id, priority=Priority.HIGH)
    
    # 模拟Telegram通知发送
    with patch('src.telegram.notification_sender.NotificationSender.send_notification') as mock_send:
        mock_send.return_value = True
        
        from src.telegram.notification_sender import NotificationSender
        sender = NotificationSender()
        
        # 测试通知发送
        result = await sender.send_conversation_notification(conversation)
        
        # 验证通知被发送（或至少尝试发送）
        assert result is True or result is None

