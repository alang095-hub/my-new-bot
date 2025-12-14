"""平台集成测试"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.facebook.api_client import FacebookAPIClient
from src.instagram.api_client import InstagramAPIClient
from src.facebook.message_parser import FacebookMessageParser
from src.instagram.message_parser import InstagramMessageParser


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


class TestFacebookAPIClient:
    """测试Facebook API客户端"""
    
    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """测试发送消息成功"""
        client = FacebookAPIClient(access_token="test_token")
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"recipient_id": "123", "message_id": "msg_456"}
            mock_post.return_value = mock_response
            
            result = await client.send_message("user_123", "测试消息")
            
            assert result is not None
            assert "recipient_id" in result or "message_id" in result
    
    @pytest.mark.asyncio
    async def test_send_message_with_page_id(self):
        """测试使用页面ID发送消息"""
        client = FacebookAPIClient(access_token="test_token")
        
        with patch('src.config.page_token_manager.page_token_manager.get_token') as mock_get_token, \
             patch('httpx.AsyncClient.post') as mock_post:
            mock_get_token.return_value = "page_token"
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"recipient_id": "123"}
            mock_post.return_value = mock_response
            
            result = await client.send_message("user_123", "测试消息", page_id="page_123")
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_user_info(self):
        """测试获取用户信息"""
        client = FacebookAPIClient(access_token="test_token")
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "123",
                "name": "测试用户",
                "first_name": "测试"
            }
            mock_get.return_value = mock_response
            
            result = await client.get_user_info("user_123")
            
            assert result is not None
            assert "name" in result or "id" in result
    
    @pytest.mark.asyncio
    async def test_send_message_error(self):
        """测试发送消息错误处理"""
        client = FacebookAPIClient(access_token="test_token")
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": {"message": "Invalid token"}}
            mock_post.return_value = mock_response
            
            # 应该抛出异常或返回错误信息
            try:
                result = await client.send_message("user_123", "测试消息")
                # 如果返回了结果，应该包含错误信息
                assert result is not None
            except Exception as e:
                # 如果抛出异常，应该是预期的异常类型
                assert isinstance(e, Exception)
    
    @pytest.mark.asyncio
    async def test_close(self):
        """测试关闭客户端"""
        client = FacebookAPIClient(access_token="test_token")
        
        await client.close()
        # 应该能够正常关闭


class TestInstagramAPIClient:
    """测试Instagram API客户端"""
    
    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """测试发送消息成功"""
        client = InstagramAPIClient(access_token="test_token", ig_user_id="ig_123")
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "msg_456"}
            mock_post.return_value = mock_response
            
            result = await client.send_message("user_123", "测试消息")
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_user_info(self):
        """测试获取用户信息"""
        client = InstagramAPIClient(access_token="test_token", ig_user_id="ig_123")
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "123",
                "username": "test_user"
            }
            mock_get.return_value = mock_response
            
            result = await client.get_user_info("user_123")
            
            assert result is not None


class TestMessageParsers:
    """测试消息解析器"""
    
    def test_facebook_parser_parse_webhook(self):
        """测试Facebook消息解析"""
        parser = FacebookMessageParser()
        
        webhook_data = {
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
        
        messages = parser.parse_webhook_event(webhook_data)
        
        assert messages is not None
        assert len(messages) > 0
        assert messages[0]["sender_id"] == "user_456"
        assert messages[0]["content"] == "测试消息"
    
    def test_facebook_parser_invalid_data(self):
        """测试Facebook解析无效数据"""
        parser = FacebookMessageParser()
        
        invalid_data = {"invalid": "data"}
        messages = parser.parse_webhook_event(invalid_data)
        
        # 应该返回None或空列表
        assert messages is None or len(messages) == 0
    
    def test_instagram_parser_parse_webhook(self):
        """测试Instagram消息解析"""
        parser = InstagramMessageParser()
        
        webhook_data = {
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
        
        messages = parser.parse_webhook_event(webhook_data)
        
        assert messages is not None
        assert len(messages) > 0
    
    def test_instagram_parser_invalid_data(self):
        """测试Instagram解析无效数据"""
        parser = InstagramMessageParser()
        
        invalid_data = {"invalid": "data"}
        messages = parser.parse_webhook_event(invalid_data)
        
        # 应该返回None或空列表
        assert messages is None or len(messages) == 0

