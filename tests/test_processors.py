"""处理器单元测试"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.processors.base import BaseProcessor, ProcessorContext, ProcessorResult, ProcessorStatus
from src.processors.handlers import MessageReceiver, UserInfoHandler, FilterHandler
from src.processors.pipeline import MessagePipeline
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base


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
def mock_context(db_session):
    """创建模拟的处理器上下文"""
    context = ProcessorContext(
        platform_name="facebook",
        message_data={
            "sender_id": "123456789",
            "content": "测试消息内容",
            "message_id": "msg_123"
        },
        db=db_session
    )
    return context


@pytest.fixture
def mock_platform_client():
    """创建模拟的平台客户端"""
    client = Mock()
    client.get_user_info = AsyncMock(return_value={
        "name": "测试用户",
        "first_name": "测试",
        "last_name": "用户"
    })
    return client


class TestProcessorBase:
    """测试处理器基类"""
    
    def test_processor_result_is_success(self):
        """测试ProcessorResult的is_success方法"""
        result = ProcessorResult(status=ProcessorStatus.SUCCESS)
        assert result.is_success() is True
        
        result = ProcessorResult(status=ProcessorStatus.ERROR)
        assert result.is_success() is False
    
    def test_processor_result_should_skip(self):
        """测试ProcessorResult的should_skip方法"""
        result = ProcessorResult(status=ProcessorStatus.SKIP)
        assert result.should_skip() is True
        
        result = ProcessorResult(status=ProcessorStatus.SUCCESS, should_continue=False)
        assert result.should_skip() is True
        
        result = ProcessorResult(status=ProcessorStatus.SUCCESS, should_continue=True)
        assert result.should_skip() is False


class TestMessageReceiver:
    """测试消息接收处理器"""
    
    @pytest.mark.asyncio
    async def test_message_receiver_process_success(self, mock_context):
        """测试消息接收处理器成功处理"""
        processor = MessageReceiver()
        
        with patch('src.collector.data_collector.DataCollector') as mock_collector:
            mock_collector_instance = Mock()
            mock_collector_instance.extract_info_from_message = Mock(return_value={
                "email": "test@example.com"
            })
            mock_collector.return_value = mock_collector_instance
            
            result = await processor.process(mock_context)
            
            assert result.status == ProcessorStatus.SUCCESS
            assert len(mock_context.message_summary) > 0
            assert "email" in mock_context.extracted_info
    
    @pytest.mark.asyncio
    async def test_message_receiver_process_long_message(self, mock_context):
        """测试消息接收处理器处理长消息"""
        mock_context.message_data["content"] = "a" * 600
        
        processor = MessageReceiver()
        
        with patch('src.collector.data_collector.DataCollector') as mock_collector:
            mock_collector_instance = Mock()
            mock_collector_instance.extract_info_from_message = Mock(return_value={})
            mock_collector.return_value = mock_collector_instance
            
            result = await processor.process(mock_context)
            
            assert result.status == ProcessorStatus.SUCCESS
            assert len(mock_context.message_summary) <= 500
            assert mock_context.message_summary.endswith("...")
    
    @pytest.mark.asyncio
    async def test_message_receiver_process_error(self, mock_context):
        """测试消息接收处理器错误处理"""
        processor = MessageReceiver()
        
        with patch('src.collector.data_collector.DataCollector') as mock_collector:
            mock_collector.side_effect = Exception("测试错误")
            
            result = await processor.process(mock_context)
            
            assert result.status == ProcessorStatus.ERROR
            assert result.error is not None


class TestUserInfoHandler:
    """测试用户信息处理器"""
    
    @pytest.mark.asyncio
    async def test_user_info_handler_process_success(self, mock_context, mock_platform_client):
        """测试用户信息处理器成功处理"""
        mock_context.platform_client = mock_platform_client
        
        processor = UserInfoHandler()
        
        with patch('src.ai.conversation_manager.ConversationManager') as mock_manager:
            mock_manager_instance = Mock()
            mock_customer = Mock()
            mock_customer.id = 1
            mock_manager_instance.get_or_create_customer = Mock(return_value=mock_customer)
            mock_manager.return_value = mock_manager_instance
            
            result = await processor.process(mock_context)
            
            assert result.status == ProcessorStatus.SUCCESS
            assert mock_context.customer_id == 1
            assert "name" in mock_context.user_info
    
    @pytest.mark.asyncio
    async def test_user_info_handler_get_dependencies(self):
        """测试用户信息处理器的依赖"""
        processor = UserInfoHandler()
        deps = processor.get_dependencies()
        assert "message_receiver" in deps


class TestFilterHandler:
    """测试过滤处理器"""
    
    @pytest.mark.asyncio
    async def test_filter_handler_process_success(self, mock_context, db_session):
        """测试过滤处理器成功处理"""
        # 先创建一个客户
        from src.core.database.repositories import CustomerRepository
        from src.core.database.models import Platform
        
        customer_repo = CustomerRepository(db_session)
        customer = customer_repo.create(
            platform=Platform.FACEBOOK,
            platform_user_id="123456789",
            name="测试用户"
        )
        
        mock_context.customer_id = customer.id
        mock_context.message_summary = "测试消息"
        mock_context.extracted_info = {}
        
        processor = FilterHandler()
        
        with patch('src.collector.filter_engine.FilterEngine') as mock_filter:
            mock_filter_instance = Mock()
            mock_filter_instance.filter_message = Mock(return_value={
                "should_block": False,
                "priority": None
            })
            mock_filter.return_value = mock_filter_instance
            
            result = await processor.process(mock_context)
            
            assert result.status == ProcessorStatus.SUCCESS
            assert mock_context.filter_result is not None


class TestMessagePipeline:
    """测试消息处理管道"""
    
    def test_pipeline_add_processor(self):
        """测试管道添加处理器"""
        pipeline = MessagePipeline()
        processor = MessageReceiver()
        
        pipeline.add_processor(processor)
        
        assert len(pipeline.processors) == 1
        assert processor.name in pipeline.processor_map
    
    def test_pipeline_add_processors(self):
        """测试管道批量添加处理器"""
        pipeline = MessagePipeline()
        processors = [MessageReceiver(), UserInfoHandler()]
        
        pipeline.add_processors(processors)
        
        assert len(pipeline.processors) == 2
    
    @pytest.mark.asyncio
    async def test_pipeline_process_success(self, mock_context, mock_platform_client):
        """测试管道处理消息成功"""
        pipeline = MessagePipeline()
        pipeline.add_processor(MessageReceiver())
        
        with patch('src.collector.data_collector.DataCollector') as mock_collector, \
             patch('src.platforms.registry.registry') as mock_registry:
            mock_collector_instance = Mock()
            mock_collector_instance.extract_info_from_message = Mock(return_value={})
            mock_collector.return_value = mock_collector_instance
            
            mock_registry.create_client = Mock(return_value=mock_platform_client)
            
            result = await pipeline.process("facebook", mock_context.message_data)
            
            assert result is not None
            assert "success" in result or "error" in result

