"""数据库模型定义"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
import enum
from src.core.database.connection import Base


class MessageType(str, enum.Enum):
    """消息类型枚举"""
    AD = "ad"  # 广告
    MESSAGE = "message"  # 私信
    COMMENT = "comment"  # 评论


class ReviewStatus(str, enum.Enum):
    """审核状态枚举"""
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已通过
    REJECTED = "rejected"  # 已拒绝
    PROCESSING = "processing"  # 处理中


class Priority(str, enum.Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Platform(str, enum.Enum):
    """平台枚举"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"


class Customer(Base):
    """客户信息表"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # 平台相关字段
    platform = Column(Enum(Platform), default=Platform.FACEBOOK,
                      nullable=False, index=True)
    platform_user_id = Column(String(100), index=True)  # 通用平台用户ID
    platform_metadata = Column(JSON)  # 平台特定数据（JSON格式）

    # 兼容字段（保留用于向后兼容）
    facebook_id = Column(String(100), index=True)

    # 客户信息
    name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    company_name = Column(String(200))
    location = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    conversations = relationship("Conversation", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")


class Conversation(Base):
    """对话记录表"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # 平台相关字段
    platform = Column(Enum(Platform), default=Platform.FACEBOOK,
                      nullable=False, index=True)
    platform_message_id = Column(String(200), index=True)  # 通用平台消息ID

    # 兼容字段（保留用于向后兼容）
    facebook_message_id = Column(String(200), index=True)

    message_type = Column(Enum(MessageType), nullable=False)
    content = Column(Text, nullable=False)
    raw_data = Column(JSON)  # 原始平台数据

    # AI 回复相关
    ai_replied = Column(Boolean, default=False)
    ai_reply_content = Column(Text)
    ai_reply_at = Column(DateTime(timezone=True))

    # 状态
    is_processed = Column(Boolean, default=False)
    priority = Column(Enum(Priority), default=Priority.LOW)
    filtered = Column(Boolean, default=False)
    filter_reason = Column(String(500))

    # 时间戳
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    customer = relationship("Customer", back_populates="conversations")
    reviews = relationship("Review", back_populates="conversation")
    collected_data = relationship(
        "CollectedData", back_populates="conversation")


class CollectedData(Base):
    """收集的资料表"""
    __tablename__ = "collected_data"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey(
        "conversations.id"), nullable=False)

    # 收集的字段（JSON 格式存储）
    data = Column(JSON, nullable=False)

    # 验证状态
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    conversation = relationship(
        "Conversation", back_populates="collected_data")


class Review(Base):
    """审核记录表"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey(
        "conversations.id"), nullable=False)

    # 审核信息
    status = Column(Enum(ReviewStatus),
                    default=ReviewStatus.PENDING, nullable=False)
    reviewed_by = Column(String(100))  # 审核人（Telegram username 或 AI）
    review_notes = Column(Text)
    ai_assistance = Column(Boolean, default=False)  # 是否使用 AI 辅助
    ai_suggestion = Column(Text)  # AI 建议

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    customer = relationship("Customer", back_populates="reviews")
    conversation = relationship("Conversation", back_populates="reviews")


class IntegrationLog(Base):
    """集成日志表（ManyChat/Botcake）"""
    __tablename__ = "integration_logs"

    id = Column(Integer, primary_key=True, index=True)
    integration_type = Column(String(50), nullable=False)  # manychat, botcake
    action = Column(String(100), nullable=False)  # sync, send, receive
    status = Column(String(50), nullable=False)  # success, failed
    request_data = Column(JSON)
    response_data = Column(JSON)
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class APIUsageLog(Base):
    """API使用日志表"""
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_type = Column(String(50), nullable=False, index=True)  # openai, facebook, telegram
    endpoint = Column(String(200))  # API端点
    success = Column(Boolean, nullable=False, default=True)
    response_time_ms = Column(Integer, nullable=False)  # 响应时间（毫秒）
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    error_message = Column(Text)  # 错误信息
    tokens_used = Column(Integer)  # Token使用量（OpenAI）
    cost_usd = Column(String(50))  # 成本（美元，字符串格式避免精度问题）
    extra_metadata = Column(JSON)  # 其他元数据（避免与SQLAlchemy的metadata冲突）

    __table_args__ = (
        Index('idx_api_usage_api_type_timestamp', 'api_type', 'timestamp'),
    )


class ReplyTemplate(Base):
    """回复模板表"""
    __tablename__ = "reply_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # 模板名称
    category = Column(String(50), index=True)  # 模板分类（greeting, price, model等）
    content = Column(Text, nullable=False)  # 模板内容（支持变量）
    variables = Column(JSON)  # 可用变量列表
    is_active = Column(Boolean, default=True, index=True)  # 是否启用
    priority = Column(Integer, default=0)  # 优先级（数字越大优先级越高）
    
    # 元数据
    description = Column(String(500))  # 模板描述
    created_by = Column(String(100))  # 创建人
    updated_by = Column(String(100))  # 更新人
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_reply_templates_category_active', 'category', 'is_active'),
    )


class PromptVersion(Base):
    """提示词版本表（用于A/B测试）"""
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 版本名称
    version_code = Column(String(50), nullable=False, unique=True, index=True)  # 版本代码（如v1, v2）
    prompt_content = Column(Text, nullable=False)  # 提示词内容
    is_active = Column(Boolean, default=True, index=True)  # 是否启用
    traffic_percentage = Column(Integer, default=50)  # 流量分配百分比（0-100）
    
    # 测试配置
    test_start_date = Column(DateTime(timezone=True))  # 测试开始时间
    test_end_date = Column(DateTime(timezone=True))  # 测试结束时间
    
    # 统计信息
    total_uses = Column(Integer, default=0)  # 总使用次数
    avg_response_time_ms = Column(Integer)  # 平均响应时间（毫秒）
    
    # 元数据
    description = Column(String(500))  # 版本描述
    created_by = Column(String(100))  # 创建人
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PromptUsageLog(Base):
    """提示词使用日志表（用于A/B测试分析）"""
    __tablename__ = "prompt_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    prompt_version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    
    # 使用信息
    response_time_ms = Column(Integer)  # 响应时间
    tokens_used = Column(Integer)  # Token使用量
    success = Column(Boolean, default=True)  # 是否成功
    
    # 时间戳
    used_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_prompt_usage_version_date', 'prompt_version_id', 'used_at'),
    )