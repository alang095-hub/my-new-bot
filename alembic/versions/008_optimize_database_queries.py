"""优化数据库查询性能

Revision ID: 008_optimize_database_queries
Revises: 007_add_api_usage_tracking
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008_optimize_database_queries'
down_revision = '007_add_api_usage_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 为conversations表添加AI回复相关索引（用于调度器查询）
    try:
        op.create_index(
            'idx_conversations_ai_replied_received_at',
            'conversations',
            ['ai_replied', 'received_at'],
            unique=False
        )
    except Exception:
        # 索引可能已存在
        pass
    
    # 为conversations表添加平台消息ID索引（用于去重）
    try:
        op.create_index(
            'idx_conversations_platform_message_id',
            'conversations',
            ['platform', 'platform_message_id'],
            unique=False
        )
    except Exception:
        # 索引可能已存在
        pass
    
    # 为customers表优化平台用户ID查询
    try:
        op.create_index(
            'idx_customers_platform_user_id',
            'customers',
            ['platform', 'platform_user_id'],
            unique=False
        )
    except Exception:
        # 索引可能已存在
        pass
    
    # 为conversations表添加客户ID和时间索引（用于历史查询）
    try:
        op.create_index(
            'idx_conversations_customer_received_at',
            'conversations',
            ['customer_id', 'received_at'],
            unique=False
        )
    except Exception:
        # 索引可能已存在
        pass


def downgrade() -> None:
    try:
        op.drop_index('idx_conversations_customer_received_at', table_name='conversations')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_customers_platform_user_id', table_name='customers')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_conversations_platform_message_id', table_name='conversations')
    except Exception:
        pass
    
    try:
        op.drop_index('idx_conversations_ai_replied_received_at', table_name='conversations')
    except Exception:
        pass

