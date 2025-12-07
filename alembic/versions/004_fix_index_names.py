"""修复索引名称冲突

Revision ID: 004
Revises: 003
Create Date: 2024-12-07 12:00:00.000000

修复 daily_statistics 和 customer_interactions 表的索引名称冲突
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """重命名索引以避免名称冲突"""
    # 检查并重命名 daily_statistics 表的索引
    try:
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'idx_date' 
                    AND tablename = 'daily_statistics'
                ) THEN
                    ALTER INDEX idx_date RENAME TO idx_daily_statistics_date;
                END IF;
            END $$;
        """)
    except Exception as e:
        # 如果索引不存在或已重命名，忽略错误
        pass
    
    # 检查并重命名 customer_interactions 表的索引
    try:
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'idx_customer_date' 
                    AND tablename = 'customer_interactions'
                ) THEN
                    ALTER INDEX idx_customer_date RENAME TO idx_customer_interactions_customer_date;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'idx_date' 
                    AND tablename = 'customer_interactions'
                ) THEN
                    ALTER INDEX idx_date RENAME TO idx_customer_interactions_date;
                END IF;
            END $$;
        """)
    except Exception as e:
        # 如果索引不存在或已重命名，忽略错误
        pass


def downgrade() -> None:
    """恢复原始索引名称"""
    try:
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'idx_daily_statistics_date' 
                    AND tablename = 'daily_statistics'
                ) THEN
                    ALTER INDEX idx_daily_statistics_date RENAME TO idx_date;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'idx_customer_interactions_customer_date' 
                    AND tablename = 'customer_interactions'
                ) THEN
                    ALTER INDEX idx_customer_interactions_customer_date RENAME TO idx_customer_date;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'idx_customer_interactions_date' 
                    AND tablename = 'customer_interactions'
                ) THEN
                    ALTER INDEX idx_customer_interactions_date RENAME TO idx_date;
                END IF;
            END $$;
        """)
    except Exception as e:
        # 如果索引不存在，忽略错误
        pass

