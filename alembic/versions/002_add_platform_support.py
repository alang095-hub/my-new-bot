"""Add platform support

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建Platform枚举类型
    platform_enum = sa.Enum('facebook', 'instagram', 'twitter', 'linkedin', 'whatsapp', name='platform')
    platform_enum.create(op.get_bind(), checkfirst=True)
    
    # 修改customers表：添加平台相关字段
    op.add_column('customers', sa.Column('platform', platform_enum, nullable=True))
    op.add_column('customers', sa.Column('platform_user_id', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('platform_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # 修改facebook_id为可空（向后兼容）
    op.alter_column('customers', 'facebook_id',
                    existing_type=sa.String(length=100),
                    nullable=True)
    
    # 为现有数据设置默认platform值
    op.execute("UPDATE customers SET platform = 'facebook' WHERE platform IS NULL")
    op.execute("UPDATE customers SET platform_user_id = facebook_id WHERE platform_user_id IS NULL")
    
    # 设置platform为NOT NULL
    op.alter_column('customers', 'platform',
                    existing_type=platform_enum,
                    nullable=False)
    
    # 创建索引
    op.create_index(op.f('ix_customers_platform'), 'customers', ['platform'], unique=False)
    op.create_index(op.f('ix_customers_platform_user_id'), 'customers', ['platform_user_id'], unique=False)
    
    # 修改conversations表：添加平台相关字段
    op.add_column('conversations', sa.Column('platform', platform_enum, nullable=True))
    op.add_column('conversations', sa.Column('platform_message_id', sa.String(length=200), nullable=True))
    
    # 修改facebook_message_id为可空（向后兼容）
    op.alter_column('conversations', 'facebook_message_id',
                    existing_type=sa.String(length=200),
                    nullable=True)
    
    # 删除原有的唯一索引（因为现在可能有多平台消息）
    op.drop_index(op.f('ix_conversations_facebook_message_id'), table_name='conversations')
    
    # 为现有数据设置默认platform值
    op.execute("UPDATE conversations SET platform = 'facebook' WHERE platform IS NULL")
    op.execute("UPDATE conversations SET platform_message_id = facebook_message_id WHERE platform_message_id IS NULL")
    
    # 设置platform为NOT NULL
    op.alter_column('conversations', 'platform',
                    existing_type=platform_enum,
                    nullable=False)
    
    # 创建新索引
    op.create_index(op.f('ix_conversations_platform'), 'conversations', ['platform'], unique=False)
    op.create_index(op.f('ix_conversations_platform_message_id'), 'conversations', ['platform_message_id'], unique=False)
    # 保留facebook_message_id索引（向后兼容）
    op.create_index(op.f('ix_conversations_facebook_message_id'), 'conversations', ['facebook_message_id'], unique=False)


def downgrade() -> None:
    # 删除索引
    op.drop_index(op.f('ix_conversations_facebook_message_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_platform_message_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_platform'), table_name='conversations')
    op.drop_index(op.f('ix_customers_platform_user_id'), table_name='customers')
    op.drop_index(op.f('ix_customers_platform'), table_name='customers')
    
    # 恢复conversations表
    op.alter_column('conversations', 'platform',
                    existing_type=sa.Enum('facebook', 'instagram', 'twitter', 'linkedin', 'whatsapp', name='platform'),
                    nullable=True)
    op.drop_column('conversations', 'platform_message_id')
    op.drop_column('conversations', 'platform')
    op.alter_column('conversations', 'facebook_message_id',
                    existing_type=sa.String(length=200),
                    nullable=True)
    op.create_index(op.f('ix_conversations_facebook_message_id'), 'conversations', ['facebook_message_id'], unique=True)
    
    # 恢复customers表
    op.alter_column('customers', 'platform',
                    existing_type=sa.Enum('facebook', 'instagram', 'twitter', 'linkedin', 'whatsapp', name='platform'),
                    nullable=True)
    op.drop_column('customers', 'platform_metadata')
    op.drop_column('customers', 'platform_user_id')
    op.drop_column('customers', 'platform')
    op.alter_column('customers', 'facebook_id',
                    existing_type=sa.String(length=100),
                    nullable=False)
    
    # 删除Platform枚举类型
    op.execute("DROP TYPE IF EXISTS platform")







