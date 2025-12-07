"""统计数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Date, Boolean, Index
from sqlalchemy.sql import func
from src.database.database import Base


class DailyStatistics(Base):
    """每日统计数据表"""
    __tablename__ = "daily_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)  # 日期（唯一）
    
    # 接待统计
    total_customers = Column(Integer, default=0)  # 总接待客户数
    new_customers = Column(Integer, default=0)  # 新客户数
    returning_customers = Column(Integer, default=0)  # 回头客数
    
    # 引流统计
    total_messages = Column(Integer, default=0)  # 总消息数
    group_invitations_sent = Column(Integer, default=0)  # 发送的群组邀请数
    successful_leads = Column(Integer, default=0)  # 成功引流数（加入群组）
    lead_conversion_rate = Column(String(10), default="0%")  # 引流转化率
    
    # 开单统计
    total_orders = Column(Integer, default=0)  # 总开单数
    successful_orders = Column(Integer, default=0)  # 成功开单数
    order_conversion_rate = Column(String(10), default="0%")  # 开单转化率
    
    # 问题统计（JSON格式）
    # {"问题内容": 出现次数}
    frequent_questions = Column(JSON, default={})
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_daily_statistics_date', 'date'),
    )


class CustomerInteraction(Base):
    """客户交互记录表（简化版，不保存详细聊天记录）"""
    __tablename__ = "customer_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # 基本信息（不保存详细聊天内容）
    platform = Column(String(20), nullable=False)  # facebook, instagram
    message_type = Column(String(20))  # message, comment, ad
    message_summary = Column(String(500))  # 消息摘要（最多500字符）
    
    # 关键信息提取
    extracted_info = Column(JSON)  # 提取的关键信息（姓名、电话、需求等）
    
    # 处理状态
    ai_replied = Column(Boolean, default=False)  # 是否AI回复
    group_invitation_sent = Column(Boolean, default=False)  # 是否发送群组邀请
    joined_group = Column(Boolean, default=False)  # 是否加入群组
    order_created = Column(Boolean, default=False)  # 是否开单
    
    # 时间戳
    interaction_time = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_customer_interactions_customer_date', 'customer_id', 'date'),
        Index('idx_customer_interactions_date', 'date'),
    )


class FrequentQuestion(Base):
    """高频问题表"""
    __tablename__ = "frequent_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String(500), nullable=False, unique=True, index=True)  # 问题文本
    question_category = Column(String(50))  # 问题分类
    occurrence_count = Column(Integer, default=1)  # 出现次数
    first_seen = Column(DateTime(timezone=True), server_default=func.now())  # 首次出现时间
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 最后出现时间
    
    # 关联信息
    sample_responses = Column(JSON)  # 示例回复（存储几个典型的AI回复）
    
    __table_args__ = (
        Index('idx_category', 'question_category'),
        Index('idx_count', 'occurrence_count'),
    )


