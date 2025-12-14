"""添加API使用追踪表

Revision ID: 007_add_api_usage_tracking
Revises: 006_add_performance_indexes
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_api_usage_tracking'
down_revision = '006_add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建API使用日志表
    op.create_table(
        'api_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_type', sa.String(length=50), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('response_time_ms', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.String(length=20), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('idx_api_usage_api_type', 'api_usage_logs', ['api_type'])
    op.create_index('idx_api_usage_timestamp', 'api_usage_logs', ['timestamp'])
    op.create_index('idx_api_usage_api_type_timestamp', 'api_usage_logs', ['api_type', 'timestamp'])
    
    # 优化conversations表索引（如果不存在）
    try:
        op.create_index(
            'idx_conversations_ai_replied_received_at',
            'conversations',
            ['ai_replied', 'received_at']
        )
    except Exception:
        # 索引可能已存在，忽略错误
        pass


def downgrade() -> None:
    # 删除索引
    try:
        op.drop_index('idx_conversations_ai_replied_received_at', table_name='conversations')
    except Exception:
        pass
    
    op.drop_index('idx_api_usage_api_type_timestamp', table_name='api_usage_logs')
    op.drop_index('idx_api_usage_timestamp', table_name='api_usage_logs')
    op.drop_index('idx_api_usage_api_type', table_name='api_usage_logs')
    
    # 删除表
    op.drop_table('api_usage_logs')

