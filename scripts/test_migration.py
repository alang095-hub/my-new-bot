#!/usr/bin/env python
"""迁移验证脚本 - 验证所有导入路径和Repository是否正常工作"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """测试所有导入路径"""
    print("=" * 60)
    print("测试导入路径...")
    print("=" * 60)
    
    tests = [
        # 核心配置
        ("core.config", "settings", "配置模块"),
        ("core.config", "yaml_config", "YAML配置"),
        ("core.config", "ConfigValidator", "配置验证器"),
        
        # 数据库
        ("core.database.connection", "get_db", "数据库连接"),
        ("core.database.connection", "engine", "数据库引擎"),
        ("core.database.connection", "Base", "基础模型类"),
        ("core.database.models", "Customer", "客户模型"),
        ("core.database.models", "Conversation", "对话模型"),
        
        # Repository
        ("core.database.repositories", "CustomerRepository", "客户Repository"),
        ("core.database.repositories", "ConversationRepository", "对话Repository"),
        ("core.database.repositories", "ReviewRepository", "审核Repository"),
        ("core.database.repositories", "CollectedDataRepository", "收集数据Repository"),
        
        # 异常
        ("core.exceptions", "APIError", "API异常"),
        ("core.exceptions", "DatabaseError", "数据库异常"),
        ("core.exceptions", "ProcessingError", "处理异常"),
        
        # 日志
        ("core.logging", "setup_logging", "日志设置"),
        ("core.logging", "get_logger", "获取日志记录器"),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, attr_name, description in tests:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            attr = getattr(module, attr_name)
            print(f"✅ {description}: {module_name}.{attr_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {description}: {module_name}.{attr_name} - {str(e)}")
            failed += 1
    
    print(f"\n导入测试: {passed} 通过, {failed} 失败")
    return failed == 0


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 60)
    print("测试向后兼容性...")
    print("=" * 60)
    
    # 注意：这里需要从src目录导入，因为向后兼容层在src目录下
    tests = [
        ("config", "settings", "旧配置路径"),
        ("database.database", "get_db", "旧数据库路径"),
        ("database.models", "Customer", "旧模型路径"),
        ("utils.exceptions", "APIError", "旧异常路径"),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, attr_name, description in tests:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            attr = getattr(module, attr_name)
            print(f"✅ {description}: {module_name}.{attr_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {description}: {module_name}.{attr_name} - {str(e)}")
            failed += 1
    
    print(f"\n兼容性测试: {passed} 通过, {failed} 失败")
    return failed == 0


def test_repository_creation():
    """测试Repository创建"""
    print("\n" + "=" * 60)
    print("测试Repository创建...")
    print("=" * 60)
    
    try:
        from sqlalchemy.orm import Session
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from core.database.connection import Base
        from core.database.repositories import (
            CustomerRepository,
            ConversationRepository,
            ReviewRepository,
            CollectedDataRepository,
            DailyStatisticsRepository,
            CustomerInteractionRepository,
            FrequentQuestionRepository
        )
        
        # 创建内存数据库用于测试
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # 测试创建Repository实例
            repos = [
                ("CustomerRepository", CustomerRepository(db)),
                ("ConversationRepository", ConversationRepository(db)),
                ("ReviewRepository", ReviewRepository(db)),
                ("CollectedDataRepository", CollectedDataRepository(db)),
                ("DailyStatisticsRepository", DailyStatisticsRepository(db)),
                ("CustomerInteractionRepository", CustomerInteractionRepository(db)),
                ("FrequentQuestionRepository", FrequentQuestionRepository(db)),
            ]
            
            for name, repo in repos:
                print(f"✅ {name} 创建成功")
            
            print(f"\nRepository测试: {len(repos)} 通过")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Repository测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("迁移验证脚本")
    print("=" * 60)
    
    results = []
    
    # 测试导入
    results.append(("导入路径", test_imports()))
    
    # 测试向后兼容
    results.append(("向后兼容", test_backward_compatibility()))
    
    # 测试Repository
    results.append(("Repository创建", test_repository_creation()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！迁移成功！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述错误")
        return 1


if __name__ == "__main__":
    sys.exit(main())

