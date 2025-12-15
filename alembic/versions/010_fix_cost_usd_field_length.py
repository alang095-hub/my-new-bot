"""修复cost_usd字段长度

Revision ID: 010_fix_cost_usd_field_length
Revises: 009_add_templates_and_ab_testing
Create Date: 2025-12-15 21:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '010_fix_cost_usd_field_length'
down_revision = '009_add_templates_and_ab_testing'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 修改api_usage_logs表的cost_usd字段长度从20增加到50
    op.alter_column(
        'api_usage_logs',
        'cost_usd',
        existing_type=sa.String(length=20),
        type_=sa.String(length=50),
        existing_nullable=True
    )


def downgrade() -> None:
    # 回滚：将cost_usd字段长度从50改回20
    op.alter_column(
        'api_usage_logs',
        'cost_usd',
        existing_type=sa.String(length=50),
        type_=sa.String(length=20),
        existing_nullable=True
    )

