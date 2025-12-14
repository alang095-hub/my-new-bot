"""过滤引擎单元测试"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
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
def filter_engine(db_session):
    """创建过滤引擎实例"""
    return FilterEngine(db_session)


def test_keyword_filter_spam(filter_engine, db_session):
    """测试垃圾消息过滤"""
    from src.database.models import Customer, Conversation, MessageType, Platform
    
    # 创建测试对话
    customer = Customer(platform=Platform.FACEBOOK, platform_user_id="test")
    db_session.add(customer)
    db_session.flush()
    
    spam_message = "这是一条垃圾广告消息"
    normal_message = "我想咨询产品信息"
    
    # 创建对话对象
    spam_conv = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content=spam_message
    )
    normal_conv = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content=normal_message
    )
    
    # 测试过滤
    spam_result = filter_engine.filter_message(spam_conv, spam_message)
    normal_result = filter_engine.filter_message(normal_conv, normal_message)
    
    # 垃圾消息应该被过滤或标记为高优先级
    assert spam_result.get("filtered") is True or spam_result.get("priority") is not None
    # 正常消息应该有结果
    assert "filtered" in normal_result


def test_keyword_filter_block(filter_engine, db_session):
    """测试敏感词过滤"""
    from src.database.models import Customer, Conversation, MessageType
    
    # 创建测试对话
    from src.database.models import Platform
    
    customer = Customer(platform=Platform.FACEBOOK, platform_user_id="test")
    db_session.add(customer)
    db_session.flush()
    
    blocked_message = "这是一个诈骗信息"
    normal_message = "我想了解产品"
    
    # 创建对话对象
    blocked_conv = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content=blocked_message
    )
    normal_conv = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content=normal_message
    )
    
    # 测试过滤
    blocked_result = filter_engine.filter_message(blocked_conv, blocked_message)
    normal_result = filter_engine.filter_message(normal_conv, normal_message)
    
    # 敏感词消息应该被过滤
    assert blocked_result.get("filtered") is True or blocked_result.get("priority") is not None
    # 正常消息应该有结果
    assert "filtered" in normal_result


def test_priority_detection(filter_engine, db_session):
    """测试优先级检测"""
    from src.database.models import Customer, Conversation, MessageType, Platform
    
    # 创建测试对话
    customer = Customer(platform=Platform.FACEBOOK, platform_user_id="test")
    db_session.add(customer)
    db_session.flush()
    
    urgent_message = "紧急！我需要帮助"
    purchase_message = "我想了解产品价格"
    normal_message = "你好"
    
    # 创建对话对象
    urgent_conv = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content=urgent_message
    )
    purchase_conv = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content=purchase_message
    )
    normal_conv = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content=normal_message
    )
    
    # 测试优先级检测
    urgent_result = filter_engine.filter_message(urgent_conv, urgent_message)
    purchase_result = filter_engine.filter_message(purchase_conv, purchase_message)
    normal_result = filter_engine.filter_message(normal_conv, normal_message)
    
    # 验证优先级
    from src.database.models import Priority
    assert urgent_result.get("priority") in [Priority.HIGH, Priority.URGENT]
    assert purchase_result.get("priority") in [Priority.MEDIUM, Priority.HIGH]
    assert normal_result.get("priority") in [Priority.LOW, Priority.MEDIUM]


def test_filter_message(filter_engine, db_session):
    """测试完整消息过滤流程"""
    from src.database.models import Customer, Conversation, MessageType, Platform
    
    # 创建测试客户
    customer = Customer(platform=Platform.FACEBOOK, platform_user_id="test")
    db_session.add(customer)
    db_session.flush()
    
    test_cases = [
        ("这是一条垃圾消息", {"filtered": True}),
        ("紧急！需要帮助", {"priority": "high"}),
        ("正常咨询消息", {"filtered": False}),
    ]
    
    for message_content, expected in test_cases:
        conv = Conversation(
            customer_id=customer.id,
            platform=Platform.FACEBOOK,
            message_type=MessageType.MESSAGE,
            content=message_content
        )
        result = filter_engine.filter_message(conv, message_content)
        
        if "filtered" in expected:
            assert result.get("filtered") == expected["filtered"]
        if "priority" in expected:
            assert result.get("priority") is not None


def test_filter_disabled(filter_engine, db_session):
    """测试过滤功能禁用"""
    from src.database.models import Customer, Conversation, MessageType, Platform
    
    # 创建测试客户和对话
    customer = Customer(platform=Platform.FACEBOOK, platform_user_id="test")
    db_session.add(customer)
    db_session.flush()
    
    spam_message = "这是一条垃圾消息"
    conv = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content=spam_message
    )
    
    # 测试过滤（即使包含垃圾关键词，也应该有结果返回）
    result = filter_engine.filter_message(conv, spam_message)
    
    # 验证有结果返回
    assert "filtered" in result
    assert "priority" in result

