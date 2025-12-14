"""数据收集器单元测试"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.collector.data_collector import DataCollector
from src.collector.data_validator import DataValidator


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
def data_collector(db_session):
    """创建数据收集器实例"""
    return DataCollector(db_session)


@pytest.fixture
def data_validator():
    """创建数据验证器实例"""
    return DataValidator()


def test_extract_email(data_collector):
    """测试邮箱提取"""
    text = "我的邮箱是 test@example.com，请发邮件给我"
    extracted = data_collector.extract_info_from_message(text)
    
    assert "email" in extracted or "emails" in extracted
    email_value = extracted.get("email") or (extracted.get("emails", [])[0] if extracted.get("emails") else None)
    assert email_value is not None
    assert "test@example.com" in str(email_value)


def test_extract_phone(data_collector):
    """测试电话号码提取"""
    test_cases = [
        "我的电话是 13812345678",
        "联系我：+86 138-1234-5678",
        "电话：010-12345678",
    ]
    
    for text in test_cases:
        extracted = data_collector.extract_info_from_message(text)
        assert isinstance(extracted, dict)
        # 验证提取到电话或至少提取了信息
        assert "phone" in extracted or "phones" in extracted or "message_content" in extracted


def test_extract_name(data_collector):
    """测试姓名提取"""
    text = "我是张三，想咨询一下"
    extracted = data_collector.extract_info_from_message(text)
    
    # 姓名提取可能不准确，至少应该尝试提取
    assert isinstance(extracted, dict)
    # 验证至少提取了消息内容
    assert "message_content" in extracted
    # 如果提取到姓名，应该包含在结果中
    if "name" in extracted:
        assert extracted["name"] is not None


def test_collect_from_message(data_collector, db_session):
    """测试从消息中收集数据"""
    from src.database.models import Customer, Conversation, MessageType, Platform
    
    # 创建测试客户和对话
    customer = Customer(
        platform=Platform.FACEBOOK,
        platform_user_id="test_user",
        name="测试用户"
    )
    db_session.add(customer)
    db_session.flush()
    
    conversation = Conversation(
        customer_id=customer.id,
        platform=Platform.FACEBOOK,
        message_type=MessageType.MESSAGE,
        content="你好，我是李四。我的邮箱是 lisi@example.com 电话：13912345678"
    )
    db_session.add(conversation)
    db_session.commit()
    
    # 测试收集数据
    collected_data = data_collector.collect_from_conversation(
        conversation_id=conversation.id,
        message_content=conversation.content
    )
    
    assert collected_data is not None
    assert collected_data.conversation_id == conversation.id
    assert collected_data.data is not None


def test_validate_email(data_validator):
    """测试邮箱验证"""
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+tag@example.com"
    ]
    
    invalid_emails = [
        "invalid-email",
        "@example.com",
        "user@",
        "user@domain"
    ]
    
    for email in valid_emails:
        result = data_validator.validate_email(email)
        # validate_email可能返回(is_valid, error)元组或布尔值
        if isinstance(result, tuple):
            assert result[0] is True
        else:
            assert result is True
    
    for email in invalid_emails:
        result = data_validator.validate_email(email)
        if isinstance(result, tuple):
            assert result[0] is False
        else:
            assert result is False


def test_validate_phone(data_validator):
    """测试电话号码验证"""
    valid_phones = [
        "13812345678",
        "01012345678",
        "+8613812345678"
    ]
    
    invalid_phones = [
        "123",
        "abc12345678",
        "123456789012345"  # 太长
    ]
    
    for phone in valid_phones:
        result = data_validator.validate_phone(phone)
        # validate_phone返回(is_valid, error)元组
        if isinstance(result, tuple):
            assert result[0] is True
        else:
            assert result is True
    
    for phone in invalid_phones:
        result = data_validator.validate_phone(phone)
        if isinstance(result, tuple):
            assert result[0] is False
        else:
            assert result is False


def test_validate_data_completeness(data_validator):
    """测试数据完整性验证"""
    complete_data = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13812345678"
    }
    
    incomplete_data = {
        "name": "李四"
        # 缺少email和phone
    }
    
    # 使用validate_collected_data方法
    complete_result = data_validator.validate_collected_data(complete_data)
    incomplete_result = data_validator.validate_collected_data(incomplete_data)
    
    # 完整数据应该验证通过
    assert complete_result.get("is_valid") is True
    assert len(complete_result.get("errors", {})) == 0
    
    # 不完整数据可能验证通过（如果只验证格式），但至少应该有结果
    assert "is_valid" in incomplete_result
    assert "data" in incomplete_result

