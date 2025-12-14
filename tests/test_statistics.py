"""统计服务单元测试"""
import pytest
from datetime import date, datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.connection import Base
from src.core.database.models import Customer, Platform
from src.core.database.repositories import CustomerRepository
from src.statistics.tracker import StatisticsTracker


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


@pytest.fixture
def statistics_tracker(db_session):
    """创建统计追踪器"""
    return StatisticsTracker(db_session)


class TestStatisticsTracker:
    """测试统计追踪器"""
    
    def test_get_or_create_daily_statistics(self, statistics_tracker):
        """测试获取或创建每日统计数据"""
        stats = statistics_tracker.get_or_create_daily_statistics()
        
        assert stats is not None
        assert stats.date == datetime.now(timezone.utc).date()
    
    def test_get_or_create_daily_statistics_with_date(self, statistics_tracker):
        """测试使用指定日期获取或创建每日统计数据"""
        target_date = date(2024, 1, 1)
        stats = statistics_tracker.get_or_create_daily_statistics(target_date)
        
        assert stats is not None
        assert stats.date == target_date
    
    def test_record_customer_interaction(self, statistics_tracker, customer):
        """测试记录客户交互"""
        interaction = statistics_tracker.record_customer_interaction(
            customer_id=customer.id,
            platform="facebook",
            message_type="message",
            message_summary="测试消息摘要",
            extracted_info={"email": "test@example.com"},
            ai_replied=True
        )
        
        assert interaction is not None
        assert interaction.customer_id == customer.id
        assert interaction.platform == "facebook"
        assert interaction.ai_replied is True
    
    def test_record_customer_interaction_long_summary(self, statistics_tracker, customer):
        """测试记录客户交互（长摘要）"""
        long_summary = "a" * 600
        interaction = statistics_tracker.record_customer_interaction(
            customer_id=customer.id,
            platform="facebook",
            message_type="message",
            message_summary=long_summary,
            extracted_info={}
        )
        
        assert interaction is not None
        assert len(interaction.message_summary) <= 500
        assert interaction.message_summary.endswith("...")
    
    def test_mark_joined_group(self, statistics_tracker, customer):
        """测试标记客户已加入群组"""
        # 先创建一个交互记录
        interaction = statistics_tracker.record_customer_interaction(
            customer_id=customer.id,
            platform="facebook",
            message_type="message",
            message_summary="测试消息",
            extracted_info={}
        )
        
        # 标记已加入群组
        result = statistics_tracker.mark_joined_group(customer.id)
        
        assert result is True
        
        # 验证记录已更新
        updated = statistics_tracker.interaction_repo.get(interaction.id)
        assert updated.joined_group is True
    
    def test_mark_order_created(self, statistics_tracker, customer):
        """测试标记订单已创建"""
        # 先创建一个交互记录
        interaction = statistics_tracker.record_customer_interaction(
            customer_id=customer.id,
            platform="facebook",
            message_type="message",
            message_summary="测试消息",
            extracted_info={}
        )
        
        # 标记订单已创建
        result = statistics_tracker.mark_order_created(customer.id)
        
        assert result is True
        
        # 验证记录已更新
        updated = statistics_tracker.interaction_repo.get(interaction.id)
        assert updated.order_created is True
    
    def test_record_frequent_question(self, statistics_tracker):
        """测试记录常见问题"""
        statistics_tracker.record_frequent_question(
            question_text="如何购买？",
            category="购买咨询",
            sample_response="您可以访问我们的网站购买"
        )
        
        # 获取常见问题（返回字典列表）
        questions = statistics_tracker.get_frequent_questions(limit=10)
        
        assert len(questions) > 0
        assert any(q.get("question") == "如何购买？" for q in questions)
    
    def test_get_daily_statistics(self, statistics_tracker):
        """测试获取每日统计数据"""
        target_date = date(2024, 1, 1)
        
        # 创建统计数据
        stats = statistics_tracker.get_or_create_daily_statistics(target_date)
        
        # 获取统计数据（返回字典）
        retrieved = statistics_tracker.get_daily_statistics(target_date)
        
        assert retrieved is not None
        assert isinstance(retrieved, dict)
        assert retrieved["date"] == target_date.isoformat()
    
    def test_get_frequent_questions(self, statistics_tracker):
        """测试获取常见问题"""
        # 记录几个问题
        statistics_tracker.record_frequent_question("问题1", "类别1")
        statistics_tracker.record_frequent_question("问题2", "类别2")
        
        # 获取常见问题
        questions = statistics_tracker.get_frequent_questions(limit=5)
        
        assert len(questions) >= 2

