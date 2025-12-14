"""Repository层单元测试"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.core.database.models import Customer, Conversation, Review, CollectedData, Platform, MessageType, ReviewStatus
from src.core.database.repositories import (
    CustomerRepository,
    ConversationRepository,
    ReviewRepository,
    CollectedDataRepository
)
from datetime import datetime, timezone


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
def customer_repo(db_session):
    """创建CustomerRepository实例"""
    return CustomerRepository(db_session)


@pytest.fixture
def conversation_repo(db_session):
    """创建ConversationRepository实例"""
    return ConversationRepository(db_session)


@pytest.fixture
def review_repo(db_session):
    """创建ReviewRepository实例"""
    return ReviewRepository(db_session)


@pytest.fixture
def collected_data_repo(db_session):
    """创建CollectedDataRepository实例"""
    return CollectedDataRepository(db_session)


def test_customer_repository_create(customer_repo):
    """测试CustomerRepository创建"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    assert customer.id is not None
    assert customer.platform == Platform.FACEBOOK
    assert customer.platform_user_id == "123456789"
    assert customer.name == "测试用户"


def test_customer_repository_get(customer_repo):
    """测试CustomerRepository查询"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    found = customer_repo.get(customer.id)
    assert found is not None
    assert found.id == customer.id
    assert found.name == "测试用户"


def test_customer_repository_get_by_platform_user_id(customer_repo):
    """测试CustomerRepository按平台用户ID查询"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    found = customer_repo.get_by_platform_user_id(Platform.FACEBOOK, "123456789")
    assert found is not None
    assert found.id == customer.id


def test_customer_repository_get_or_create(customer_repo):
    """测试CustomerRepository获取或创建"""
    # 第一次调用应该创建
    customer1 = customer_repo.get_or_create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    assert customer1.id is not None
    
    # 第二次调用应该获取已存在的
    customer2 = customer_repo.get_or_create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户2"
    )
    assert customer2.id == customer1.id
    assert customer2.name == "测试用户"  # 名称不应该更新


def test_customer_repository_update(customer_repo):
    """测试CustomerRepository更新"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    updated = customer_repo.update(customer.id, name="更新后的名称")
    assert updated is not None
    assert updated.name == "更新后的名称"


def test_customer_repository_delete(customer_repo):
    """测试CustomerRepository删除"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    result = customer_repo.delete(customer.id)
    assert result is True
    
    found = customer_repo.get(customer.id)
    assert found is None


def test_conversation_repository_create(conversation_repo, customer_repo):
    """测试ConversationRepository创建"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    conversation = conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    
    assert conversation.id is not None
    assert conversation.customer_id == customer.id
    assert conversation.content == "测试消息"


def test_conversation_repository_get_conversation_history(conversation_repo, customer_repo):
    """测试ConversationRepository获取对话历史"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    # 创建多个对话
    for i in range(5):
        conversation_repo.create_conversation(
            customer_id=customer.id,
            platform=Platform.FACEBOOK,
            platform_message_id=f"msg_{i}",
            message_type=MessageType.MESSAGE,
            content=f"消息{i}"
        )
    
    history = conversation_repo.get_customer_conversations(customer.id, limit=3)
    assert len(history) == 3
    # 注意：get_customer_conversations可能不按时间排序，所以只检查数量


def test_conversation_repository_update_ai_reply(conversation_repo, customer_repo):
    """测试ConversationRepository更新AI回复"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    conversation = conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    
    # 使用update方法更新AI回复
    updated = conversation_repo.update(
        conversation.id,
        ai_replied=True,
        ai_reply_content="AI回复内容"
    )
    assert updated is not None
    assert updated.ai_replied is True
    assert updated.ai_reply_content == "AI回复内容"


def test_review_repository_create_or_update(review_repo, conversation_repo, customer_repo):
    """测试ReviewRepository创建或更新"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    conversation = conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    
    # 第一次创建
    review1 = review_repo.create_review(
        conversation_id=conversation.id,
        customer_id=customer.id,
        status=ReviewStatus.PENDING,
        reviewed_by="admin"
    )
    assert review1.id is not None
    assert review1.status == ReviewStatus.PENDING
    
    # 第二次更新
    review2 = review_repo.update_review_status(
        review_id=review1.id,
        status=ReviewStatus.APPROVED,
        reviewed_by="admin",
        review_notes="已审核"
    )
    assert review2 is not None
    assert review2.id == review1.id
    assert review2.status == ReviewStatus.APPROVED
    assert review2.review_notes == "已审核"


def test_review_repository_get_by_conversation_id(review_repo, conversation_repo, customer_repo):
    """测试ReviewRepository按对话ID查询"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    conversation = conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    
    review = review_repo.create_review(
        conversation_id=conversation.id,
        customer_id=customer.id,
        status=ReviewStatus.APPROVED,
        reviewed_by="admin"
    )
    
    found = review_repo.get_by_conversation_id(conversation.id)
    assert found is not None
    assert found.id == review.id


def test_collected_data_repo_create(collected_data_repo, conversation_repo, customer_repo):
    """测试CollectedDataRepository创建"""
    customer = customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )
    
    conversation = conversation_repo.create_conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        platform_message_id="msg_123",
        message_type=MessageType.MESSAGE,
        content="测试消息"
    )
    
    # CollectedData使用data字段（JSON格式）
    collected_data = collected_data_repo.create(
        conversation_id=conversation.id,
        data={"email": "test@example.com", "phone": "1234567890"}
    )
    
    assert collected_data.id is not None
    assert collected_data.conversation_id == conversation.id
    assert collected_data.data["email"] == "test@example.com"
    assert collected_data.data["phone"] == "1234567890"

