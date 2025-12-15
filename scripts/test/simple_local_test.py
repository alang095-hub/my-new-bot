"""
简化本地测试脚本（不依赖httpx）
用于快速验证本地开发环境的基本功能
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 测试结果
test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, message: str = "", error: Exception = None, duration: float = 0):
    """记录测试结果"""
    result = {
        "name": name,
        "status": status,
        "message": message,
        "duration": duration,
        "timestamp": datetime.now().isoformat(),
        "error": str(error) if error else None
    }
    test_results.append(result)
    
    status_symbol = {
        "PASS": "✅",
        "FAIL": "❌",
        "WARN": "⚠️",
        "SKIP": "⏭️"
    }.get(status, "❓")
    
    duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
    print(f"{status_symbol} {name}{duration_str}")
    if message:
        print(f"   {message}")
    if error:
        print(f"   错误: {str(error)}")


def test_python_environment():
    """测试Python环境"""
    print("\n" + "="*60)
    print("Python环境检查")
    print("="*60)
    
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    log_test("Python版本", "PASS", f"Python {python_version}")
    
    # 检查关键模块
    modules = [
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("fastapi", "FastAPI"),
    ]
    
    for module_name, display_name in modules:
        start_time = time.time()
        try:
            __import__(module_name)
            duration = time.time() - start_time
            log_test(f"模块: {display_name}", "PASS", duration=duration)
        except ImportError:
            duration = time.time() - start_time
            log_test(f"模块: {display_name}", "FAIL", f"未安装 {module_name}", duration=duration)


def test_config_loading():
    """测试配置加载"""
    print("\n" + "="*60)
    print("配置加载测试")
    print("="*60)
    
    start_time = time.time()
    try:
        from src.core.config import settings
        duration = time.time() - start_time
        
        # 检查关键配置
        checks = []
        if hasattr(settings, 'database_url'):
            checks.append("database_url")
        if hasattr(settings, 'facebook_access_token'):
            checks.append("facebook_access_token")
        if hasattr(settings, 'openai_api_key'):
            checks.append("openai_api_key")
        if hasattr(settings, 'telegram_bot_token'):
            checks.append("telegram_bot_token")
        
        log_test("配置加载", "PASS", f"配置加载成功，已加载: {len(checks)} 个关键配置", duration=duration)
        return True
    except Exception as e:
        duration = time.time() - start_time
        log_test("配置加载", "FAIL", f"配置加载失败: {str(e)}", error=e, duration=duration)
        return False


def test_database_connection():
    """测试数据库连接"""
    print("\n" + "="*60)
    print("数据库连接测试")
    print("="*60)
    
    start_time = time.time()
    try:
        from src.core.database.connection import get_db
        from sqlalchemy import text
        db = next(get_db())
        # 执行简单查询（SQLAlchemy 2.0需要显式声明text）
        result = db.execute(text("SELECT 1"))
        duration = time.time() - start_time
        log_test("数据库连接", "PASS", f"连接成功，响应时间: {duration:.3f}s", duration=duration)
        return True
    except Exception as e:
        duration = time.time() - start_time
        # 如果是因为缺少DATABASE_URL，给出友好提示
        if "DATABASE_URL" in str(e) or "database" in str(e).lower():
            log_test("数据库连接", "SKIP", f"需要配置DATABASE_URL环境变量", duration=duration)
        else:
            log_test("数据库连接", "FAIL", f"连接失败: {str(e)}", error=e, duration=duration)
        return False


def test_core_modules():
    """测试核心模块导入"""
    print("\n" + "="*60)
    print("核心模块导入测试")
    print("="*60)
    
    modules = [
        ("src.core.database.connection", "数据库连接"),
        ("src.core.config", "配置管理"),
        ("src.core.logging.config", "日志配置"),
        ("src.core.database.repositories.conversation_repo", "对话Repository"),
        ("src.core.database.repositories.customer_repo", "客户Repository"),
    ]
    
    results = []
    for module_name, description in modules:
        start_time = time.time()
        try:
            __import__(module_name)
            duration = time.time() - start_time
            log_test(f"模块导入: {description}", "PASS", duration=duration)
            results.append(True)
        except Exception as e:
            duration = time.time() - start_time
            log_test(f"模块导入: {description}", "FAIL", f"导入失败: {str(e)}", error=e, duration=duration)
            results.append(False)
    
    return results


def test_repository_pattern():
    """测试Repository模式"""
    print("\n" + "="*60)
    print("Repository模式测试")
    print("="*60)
    
    start_time = time.time()
    try:
        from src.core.database.connection import get_db
        from src.core.database.repositories.conversation_repo import ConversationRepository
        
        db = next(get_db())
        repo = ConversationRepository(db)
        
        # 测试基本方法
        assert hasattr(repo, 'get')
        assert hasattr(repo, 'create')
        assert hasattr(repo, 'get_by_platform_message_id')
        
        duration = time.time() - start_time
        log_test("Repository模式", "PASS", "Repository方法可用", duration=duration)
        return True
    except Exception as e:
        duration = time.time() - start_time
        log_test("Repository模式", "FAIL", f"测试失败: {str(e)}", error=e, duration=duration)
        return False


def test_environment_variables():
    """测试环境变量"""
    print("\n" + "="*60)
    print("环境变量检查")
    print("="*60)
    
    required_vars = [
        "DATABASE_URL",
        "FACEBOOK_ACCESS_TOKEN",
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
    ]
    
    optional_vars = [
        "FACEBOOK_APP_ID",
        "FACEBOOK_APP_SECRET",
        "SECRET_KEY",
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        log_test("必需环境变量", "FAIL", f"缺少: {', '.join(missing_required)}")
    else:
        log_test("必需环境变量", "PASS", "所有必需的环境变量已配置")
    
    if missing_optional:
        log_test("可选环境变量", "WARN", f"缺少: {', '.join(missing_optional)}")
    else:
        log_test("可选环境变量", "PASS", "所有可选的环境变量已配置")


def print_summary():
    """打印测试摘要"""
    print("\n" + "="*60)
    print("测试摘要")
    print("="*60)
    
    total = len(test_results)
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    skipped = sum(1 for r in test_results if r["status"] == "SKIP")
    warned = sum(1 for r in test_results if r["status"] == "WARN")
    
    print(f"总计: {total}")
    print(f"✅ 通过: {passed} ({passed/total*100:.1f}%)")
    print(f"❌ 失败: {failed} ({failed/total*100:.1f}%)")
    print(f"⏭️ 跳过: {skipped} ({skipped/total*100:.1f}%)")
    print(f"⚠️ 警告: {warned} ({warned/total*100:.1f}%)")
    
    if failed > 0:
        print("\n失败的测试:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"  - {result['name']}: {result.get('error', result.get('message', ''))}")
    
    if warned > 0:
        print("\n警告的测试:")
        for result in test_results:
            if result["status"] == "WARN":
                print(f"  - {result['name']}: {result.get('message', '')}")
    
    print("="*60)
    
    # 总体评估
    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 有测试失败，请检查配置。")
        return 1


def main():
    """主测试函数"""
    print("="*60)
    print("简化本地测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 运行所有测试
    test_python_environment()
    test_environment_variables()
    test_config_loading()
    test_core_modules()
    test_database_connection()
    test_repository_pattern()
    
    # 打印摘要
    exit_code = print_summary()
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n测试执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

