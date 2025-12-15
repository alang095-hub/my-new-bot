"""数据库模型单元测试"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.core.database.models import Customer, Conversation, CollectedData, Review, MessageType, ReviewStatus, Platform
from datetime import datetime, timezone


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    # 使用内存SQLite数据库进行测试
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


def test_customer_model(db_session):
    """测试Customer模型"""
    from src.core.database.models import Platform
    
    customer = Customer(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户",
        email="test@example.com",
        phone="13812345678"
    )
    
    db_session.add(customer)
    db_session.commit()
    
    assert customer.id is not None
    assert customer.platform == Platform.FACEBOOK
    assert customer.platform_user_id == "123456789"
    assert customer.name == "测试用户"


def test_conversation_model(db_session):
    """测试Conversation模型"""
    # 先创建客户
    customer = Customer(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    db_session.add(customer)
    db_session.flush()
    
    conversation = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="test_msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    
    db_session.add(conversation)
    db_session.commit()
    
    assert conversation.id is not None
    assert conversation.customer_id == customer.id
    assert conversation.platform == Platform.FACEBOOK


def test_collected_data_model(db_session):
    """测试CollectedData模型"""
    # 先创建客户和对话
    from src.core.database.models import Platform
    customer = Customer(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    db_session.add(customer)
    db_session.flush()
    
    conversation = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="test_msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    db_session.add(conversation)
    db_session.flush()
    
    collected_data = CollectedData(
        conversation_id=conversation.id,
        data={"email": "test@example.com", "type": "email"}
    )
    
    db_session.add(collected_data)
    db_session.commit()
    
    assert collected_data.id is not None
    assert collected_data.conversation_id == conversation.id
    assert collected_data.data == {"email": "test@example.com", "type": "email"}


def test_review_model(db_session):
    """测试Review模型"""
    # 先创建客户和对话
    customer = Customer(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    db_session.add(customer)
    db_session.flush()
    
    conversation = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="test_msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    db_session.add(conversation)
    db_session.flush()
    
    review = Review(
        customer_id=customer.id,
        conversation_id=conversation.id,
        status=ReviewStatus.APPROVED,
        reviewed_by="admin",
        review_notes="测试审核"
    )
    
    db_session.add(review)
    db_session.commit()
    
    assert review.id is not None
    assert review.conversation_id == conversation.id
    assert review.status == ReviewStatus.APPROVED
    assert review.review_notes == "测试审核"


def test_model_relationships(db_session):
    """测试模型关系"""
    # 创建完整的关系链
    customer = Customer(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    db_session.add(customer)
    db_session.flush()
    
    conversation = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="test_msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    db_session.add(conversation)
    db_session.flush()
    
    collected_data = CollectedData(
        conversation_id=conversation.id,
        data={"email": "test@example.com", "type": "email"}
    )
    db_session.add(collected_data)
    
    review = Review(
        customer_id=customer.id,
        conversation_id=conversation.id,
        status=ReviewStatus.APPROVED
    )
    db_session.add(review)
    db_session.commit()
    
    # 测试关系
    assert conversation.customer == customer
    assert len(conversation.collected_data) == 1
    assert len(conversation.reviews) == 1
    assert customer.conversations[0] == conversation

