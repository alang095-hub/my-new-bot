"""检查数据库连接状态"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.core.database.connection import engine, get_db
from sqlalchemy import text
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_database():
    """检查数据库连接状态"""
    print("=" * 70)
    print("数据库连接检查")
    print("=" * 70)
    print()
    
    # 1. 检查数据库URL
    try:
        from src.core.config import settings
        db_url = settings.database_url
        
        # 隐藏密码
        if "@" in db_url:
            parts = db_url.split("@")
            if len(parts) == 2:
                db_url_display = "***@" + parts[1]
            else:
                db_url_display = "***"
        else:
            db_url_display = db_url
        
        print(f"数据库URL: {db_url_display}")
        
        # 检查数据库类型
        if "postgresql" in db_url.lower():
            print("数据库类型: PostgreSQL ✅")
        elif "sqlite" in db_url.lower():
            print("数据库类型: SQLite ⚠️  (生产环境建议使用PostgreSQL)")
        else:
            print(f"数据库类型: 未知")
    except Exception as e:
        print(f"❌ 无法读取数据库配置: {str(e)}")
        return
    
    print()
    
    # 2. 测试数据库连接
    print("2. 测试数据库连接...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("   ✅ 数据库连接成功")
            else:
                print("   ⚠️  连接成功但查询异常")
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {str(e)}")
        return
    
    print()
    
    # 3. 检查数据库表
    print("3. 检查数据库表...")
    try:
        from src.core.database.models import Base
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"   找到 {len(tables)} 个表:")
        
        # 检查关键表
        key_tables = [
            "customers",
            "conversations",
            "collected_data",
            "reviews",
            "api_usage_logs",
            "reply_templates",
            "prompt_versions"
        ]
        
        for table in key_tables:
            if table in tables:
                print(f"     ✅ {table}")
            else:
                print(f"     ❌ {table} (未找到)")
        
        # 显示其他表
        other_tables = [t for t in tables if t not in key_tables]
        if other_tables:
            print(f"   其他表 ({len(other_tables)} 个):")
            for table in other_tables[:10]:  # 只显示前10个
                print(f"     - {table}")
            if len(other_tables) > 10:
                print(f"     ... 还有 {len(other_tables) - 10} 个表")
    except Exception as e:
        print(f"   ⚠️  检查表失败: {str(e)}")
    
    print()
    
    # 4. 检查数据统计
    print("4. 数据统计...")
    try:
        db = next(get_db())
        
        # 检查客户数量
        from src.core.database.models import Customer
        customer_count = db.query(Customer).count()
        print(f"   客户数量: {customer_count}")
        
        # 检查对话数量
        from src.core.database.models import Conversation
        conversation_count = db.query(Conversation).count()
        print(f"   对话数量: {conversation_count}")
        
        # 检查已回复的对话
        replied_count = db.query(Conversation).filter(
            Conversation.ai_replied == True
        ).count()
        print(f"   已回复对话: {replied_count}")
        
        if conversation_count > 0:
            reply_rate = (replied_count / conversation_count) * 100
            print(f"   回复率: {reply_rate:.1f}%")
        
        db.close()
    except Exception as e:
        print(f"   ⚠️  统计失败: {str(e)}")
    
    print()
    
    # 5. 检查数据库连接池
    print("5. 数据库连接池状态...")
    try:
        pool = engine.pool
        print(f"   连接池大小: {pool.size()}")
        print(f"   已使用连接: {pool.checkedout()}")
        print(f"   可用连接: {pool.checkedin()}")
        print(f"   溢出连接: {pool.overflow()}")
    except Exception as e:
        print(f"   ⚠️  无法获取连接池信息: {str(e)}")
    
    print()
    print("=" * 70)
    print("✅ 数据库检查完成")
    print("=" * 70)


if __name__ == "__main__":
    check_database()




