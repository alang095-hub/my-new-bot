"""添加模板和A/B测试表

Revision ID: 009_add_templates_and_ab_testing
Revises: 008_optimize_database_queries
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_templates_and_ab_testing'
down_revision = '008_optimize_database_queries'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建回复模板表
    op.create_table(
        'reply_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_reply_templates_category_active', 'reply_templates', ['category', 'is_active'])
    op.create_index(op.f('ix_reply_templates_name'), 'reply_templates', ['name'], unique=True)
    op.create_index(op.f('ix_reply_templates_category'), 'reply_templates', ['category'])
    op.create_index(op.f('ix_reply_templates_is_active'), 'reply_templates', ['is_active'])
    
    # 创建提示词版本表
    op.create_table(
        'prompt_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version_code', sa.String(length=50), nullable=False),
        sa.Column('prompt_content', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('traffic_percentage', sa.Integer(), nullable=True),
        sa.Column('test_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('test_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_uses', sa.Integer(), nullable=True),
        sa.Column('avg_response_time_ms', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(op.f('ix_prompt_versions_version_code'), 'prompt_versions', ['version_code'], unique=True)
    op.create_index(op.f('ix_prompt_versions_is_active'), 'prompt_versions', ['is_active'])
    
    # 创建提示词使用日志表
    op.create_table(
        'prompt_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prompt_version_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['prompt_version_id'], ['prompt_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_prompt_usage_version_date', 'prompt_usage_logs', ['prompt_version_id', 'used_at'])
    op.create_index(op.f('ix_prompt_usage_logs_prompt_version_id'), 'prompt_usage_logs', ['prompt_version_id'])
    op.create_index(op.f('ix_prompt_usage_logs_customer_id'), 'prompt_usage_logs', ['customer_id'])
    op.create_index(op.f('ix_prompt_usage_logs_conversation_id'), 'prompt_usage_logs', ['conversation_id'])
    op.create_index(op.f('ix_prompt_usage_logs_used_at'), 'prompt_usage_logs', ['used_at'])


def downgrade() -> None:
    op.drop_index(op.f('ix_prompt_usage_logs_used_at'), table_name='prompt_usage_logs')
    op.drop_index(op.f('ix_prompt_usage_logs_conversation_id'), table_name='prompt_usage_logs')
    op.drop_index(op.f('ix_prompt_usage_logs_customer_id'), table_name='prompt_usage_logs')
    op.drop_index(op.f('ix_prompt_usage_logs_prompt_version_id'), table_name='prompt_usage_logs')
    op.drop_index('idx_prompt_usage_version_date', table_name='prompt_usage_logs')
    op.drop_table('prompt_usage_logs')
    
    op.drop_index(op.f('ix_prompt_versions_is_active'), table_name='prompt_versions')
    op.drop_index(op.f('ix_prompt_versions_version_code'), table_name='prompt_versions')
    op.drop_table('prompt_versions')
    
    op.drop_index(op.f('ix_reply_templates_is_active'), table_name='reply_templates')
    op.drop_index(op.f('ix_reply_templates_category'), table_name='reply_templates')
    op.drop_index(op.f('ix_reply_templates_name'), table_name='reply_templates')
    op.drop_index('idx_reply_templates_category_active', table_name='reply_templates')
    op.drop_table('reply_templates')

