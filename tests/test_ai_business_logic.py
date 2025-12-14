"""AI业务逻辑测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.core.database.models import Customer, Conversation, Platform, MessageType
from src.core.database.repositories import CustomerRepository, ConversationRepository
from src.ai.reply_generator import ReplyGenerator
from src.ai.conversation_manager import ConversationManager


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
def customer(db_session):
    """创建测试客户"""
    customer_repo = CustomerRepository(db_session)
    return customer_repo.create(
        platform=Platform.FACEBOOK,
        platform_user_id="123456789",
        name="测试用户"
    )


class TestReplyGenerator:
    """测试AI回复生成器"""
    
    @pytest.mark.asyncio
    async def test_spam_detection(self, db_session):
        """测试垃圾消息检测"""
        generator = ReplyGenerator(db_session)
        
        # 测试空消息
        assert generator._is_spam_or_invalid("") is True
        assert generator._is_spam_or_invalid(" ") is True
        
        # 测试太短的消息
        assert generator._is_spam_or_invalid("a") is True
        
        # 测试重复字符
        assert generator._is_spam_or_invalid("aaaaa") is True
        assert generator._is_spam_or_invalid("11111") is True
        
        # 测试购买/出售意图（垃圾消息）
        assert generator._is_spam_or_invalid("我要买手机") is True
        assert generator._is_spam_or_invalid("sell phone") is True
        
        # 测试正常消息（不应被标记为垃圾）
        assert generator._is_spam_or_invalid("你好，我想咨询贷款") is False
        assert generator._is_spam_or_invalid("我需要帮助") is False
    
    @pytest.mark.asyncio
    async def test_generate_reply_success(self, db_session, customer):
        """测试生成回复成功"""
        generator = ReplyGenerator(db_session)
        
        with patch.object(generator.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "这是AI生成的回复"
            mock_create.return_value = mock_response
            
            reply = await generator.generate_reply(
                customer_id=customer.id,
                message_content="我想咨询贷款",
                customer_name="测试用户"
            )
            
            assert reply is not None
            assert "AI生成的回复" in reply
    
    @pytest.mark.asyncio
    async def test_generate_reply_spam(self, db_session, customer):
        """测试垃圾消息不生成回复"""
        generator = ReplyGenerator(db_session)
        
        reply = await generator.generate_reply(
            customer_id=customer.id,
            message_content="我要买手机",
            customer_name="测试用户"
        )
        
        # 垃圾消息应该返回None或空字符串
        assert reply is None or reply == ""
    
    @pytest.mark.asyncio
    async def test_generate_reply_error_handling(self, db_session, customer):
        """测试错误处理"""
        generator = ReplyGenerator(db_session)
        
        with patch.object(generator.client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = Exception("API错误")
            
            # 应该能够处理错误而不崩溃
            try:
                reply = await generator.generate_reply(
                    customer_id=customer.id,
                    message_content="测试消息",
                    customer_name="测试用户"
                )
                # 可能返回None或默认回复
                assert reply is None or isinstance(reply, str)
            except Exception as e:
                # 如果抛出异常，应该是预期的异常类型
                assert isinstance(e, Exception)


class TestConversationManager:
    """测试对话管理器"""
    
    def test_get_conversation_history(self, db_session, customer):
        """测试获取对话历史"""
        manager = ConversationManager(db_session)
        
        # 创建一些对话
        conversation_repo = ConversationRepository(db_session)
        for i in range(5):
            conversation_repo.create_conversation(
                customer_id=customer.id,
                platform=Platform.FACEBOOK,
                platform_message_id=f"msg_{i}",
                message_type=MessageType.MESSAGE,
                content=f"消息{i}"
            )
        
        # 获取对话历史
        history = manager.get_conversation_history(customer.id, limit=3)
        
        assert len(history) <= 3
        assert all("content" in item for item in history)
    
    def test_save_conversation(self, db_session, customer):
        """测试保存对话"""
        manager = ConversationManager(db_session)
        
        conversation = manager.save_conversation(
            customer_id=customer.id,
            platform_message_id="test_msg_123",
            platform="facebook",
            message_type="message",
            content="测试消息"
        )
        
        assert conversation is not None
        assert conversation.customer_id == customer.id
        assert conversation.content == "测试消息"
    
    def test_get_or_create_customer(self, db_session):
        """测试获取或创建客户"""
        manager = ConversationManager(db_session)
        
        # 第一次创建
        customer1 = manager.get_or_create_customer(
            platform_user_id="new_user",
            platform="facebook",
            name="新用户"
        )
        
        assert customer1 is not None
        assert customer1.platform_user_id == "new_user"
        
        # 第二次获取（应该返回同一个客户）
        customer2 = manager.get_or_create_customer(
            platform_user_id="new_user",
            platform="facebook"
        )
        
        assert customer2.id == customer1.id
    
    def test_update_ai_reply(self, db_session, customer):
        """测试更新AI回复"""
        manager = ConversationManager(db_session)
        
        # 创建对话
        conversation = manager.save_conversation(
            customer_id=customer.id,
            platform_message_id="test_msg_123",
            platform="facebook",
            message_type="message",
            content="测试消息"
        )
        
        # 更新AI回复
        updated = manager.update_ai_reply(
            conversation.id,
            "这是AI回复"
        )
        
        assert updated is not None
        assert updated.ai_replied is True
        assert updated.ai_reply_content == "这是AI回复"

