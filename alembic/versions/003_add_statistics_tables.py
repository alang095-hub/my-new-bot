"""添加统计表

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建每日统计表
    op.create_table(
        'daily_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_customers', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('new_customers', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('returning_customers', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_messages', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('group_invitations_sent', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('successful_leads', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('lead_conversion_rate', sa.String(length=10), nullable=True, server_default='0%'),
        sa.Column('total_orders', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('successful_orders', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('order_conversion_rate', sa.String(length=10), nullable=True, server_default='0%'),
        sa.Column('frequent_questions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date')
    )
    op.create_index('idx_daily_statistics_date', 'daily_statistics', ['date'], unique=False)
    
    # 创建客户交互记录表
    op.create_table(
        'customer_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('platform', sa.String(length=20), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=True),
        sa.Column('message_summary', sa.String(length=500), nullable=True),
        sa.Column('extracted_info', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_replied', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('group_invitation_sent', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('joined_group', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('order_created', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('interaction_time', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_customer_interactions_customer_date', 'customer_interactions', ['customer_id', 'date'], unique=False)
    op.create_index('idx_customer_interactions_date', 'customer_interactions', ['date'], unique=False)
    
    # 创建高频问题表
    op.create_table(
        'frequent_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.String(length=500), nullable=False),
        sa.Column('question_category', sa.String(length=50), nullable=True),
        sa.Column('occurrence_count', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('first_seen', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_seen', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('sample_responses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question_text')
    )
    op.create_index('idx_category', 'frequent_questions', ['question_category'], unique=False)
    op.create_index('idx_count', 'frequent_questions', ['occurrence_count'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_count', table_name='frequent_questions')
    op.drop_index('idx_category', table_name='frequent_questions')
    op.drop_table('frequent_questions')
    op.drop_index('idx_customer_interactions_date', table_name='customer_interactions')
    op.drop_index('idx_customer_interactions_customer_date', table_name='customer_interactions')
    op.drop_table('customer_interactions')
    op.drop_index('idx_daily_statistics_date', table_name='daily_statistics')
    op.drop_table('daily_statistics')


