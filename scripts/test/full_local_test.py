"""
本地完整测试脚本
用于全面测试本地开发环境的所有功能
"""
import os
import sys
import time
import httpx
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 测试结果
test_results: List[Dict[str, Any]] = []
base_url = "http://localhost:8000"


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


def test_environment():
    """测试环境配置"""
    print("\n" + "="*60)
    print("环境检查")
    print("="*60)
    
    # Python版本
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    log_test("Python版本", "PASS", f"Python {python_version}")
    
    # 环境变量
    required_env_vars = [
        "DATABASE_URL",
        "FACEBOOK_ACCESS_TOKEN",
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        log_test("环境变量", "WARN", f"缺少环境变量: {', '.join(missing_vars)}")
    else:
        log_test("环境变量", "PASS", "所有必需的环境变量已配置")


def test_database():
    """测试数据库功能"""
    print("\n" + "="*60)
    print("数据库测试")
    print("="*60)
    
    # 数据库连接
    start_time = time.time()
    try:
        from src.core.database.connection import get_db, engine
        db = next(get_db())
        db.execute("SELECT 1")
        duration = time.time() - start_time
        log_test("数据库连接", "PASS", f"连接成功 ({duration:.3f}s)", duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        log_test("数据库连接", "FAIL", f"连接失败: {str(e)}", error=e, duration=duration)
        return
    
    # 数据库表检查
    start_time = time.time()
    try:
        from src.core.database.models import Customer, Conversation
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        required_tables = ["customers", "conversations", "collected_data", "reviews"]
        
        missing_tables = [t for t in required_tables if t not in tables]
        if missing_tables:
            log_test("数据库表", "WARN", f"缺少表: {', '.join(missing_tables)}")
        else:
            duration = time.time() - start_time
            log_test("数据库表", "PASS", f"所有必需表存在 ({len(required_tables)}个)", duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        log_test("数据库表", "FAIL", f"检查失败: {str(e)}", error=e, duration=duration)


def test_api_endpoints():
    """测试所有API端点"""
    print("\n" + "="*60)
    print("API端点测试")
    print("="*60)
    
    # 检查服务是否运行
    try:
        response = httpx.get(f"{base_url}/health/simple", timeout=2.0)
        if response.status_code != 200:
            log_test("API服务", "SKIP", "服务未正常运行")
            return
    except httpx.ConnectError:
        log_test("API服务", "SKIP", "服务未启动，请先运行: uvicorn src.main:app --reload")
        return
    except Exception as e:
        log_test("API服务", "FAIL", f"无法连接服务: {str(e)}", error=e)
        return
    
    log_test("API服务", "PASS", "服务运行正常")
    
    # 基础端点
    endpoints = [
        ("GET", "/", "根路径"),
        ("GET", "/health", "健康检查"),
        ("GET", "/health/simple", "简单健康检查"),
        ("GET", "/metrics", "性能指标"),
    ]
    
    for method, endpoint, name in endpoints:
        start_time = time.time()
        try:
            if method == "GET":
                response = httpx.get(f"{base_url}{endpoint}", timeout=5.0)
            else:
                response = httpx.post(f"{base_url}{endpoint}", timeout=5.0)
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                log_test(f"API: {name}", "PASS", f"响应时间: {duration:.3f}s", duration=duration)
            else:
                log_test(f"API: {name}", "FAIL", f"HTTP {response.status_code}", duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            log_test(f"API: {name}", "FAIL", f"请求失败: {str(e)}", error=e, duration=duration)
    
    # 管理API端点
    admin_endpoints = [
        ("GET", "/api/v1/admin/conversations", "对话列表"),
        ("GET", "/api/v1/admin/statistics", "统计信息"),
    ]
    
    for method, endpoint, name in admin_endpoints:
        start_time = time.time()
        try:
            response = httpx.get(f"{base_url}{endpoint}?page=1&page_size=10", timeout=5.0)
            duration = time.time() - start_time
            
            if response.status_code in [200, 401, 403]:  # 401/403也算正常（需要认证）
                log_test(f"管理API: {name}", "PASS", f"端点可访问 ({response.status_code})", duration=duration)
            else:
                log_test(f"管理API: {name}", "WARN", f"HTTP {response.status_code}", duration=duration)
        except Exception as e:
            duration = time.time() - start_time
            log_test(f"管理API: {name}", "FAIL", f"请求失败: {str(e)}", error=e, duration=duration)


def test_core_functionality():
    """测试核心功能"""
    print("\n" + "="*60)
    print("核心功能测试")
    print("="*60)
    
    # AI回复生成器
    start_time = time.time()
    try:
        from src.core.database.connection import get_db
        from src.ai.reply_generator import ReplyGenerator
        
        db = next(get_db())
        generator = ReplyGenerator(db)
        duration = time.time() - start_time
        log_test("AI回复生成器", "PASS", "初始化成功", duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        log_test("AI回复生成器", "FAIL", f"初始化失败: {str(e)}", error=e, duration=duration)
    
    # 数据收集器
    start_time = time.time()
    try:
        from src.collector.data_collector import DataCollector
        collector = DataCollector()
        duration = time.time() - start_time
        log_test("数据收集器", "PASS", "初始化成功", duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        log_test("数据收集器", "FAIL", f"初始化失败: {str(e)}", error=e, duration=duration)
    
    # 数据验证器
    start_time = time.time()
    try:
        from src.collector.data_validator import DataValidator
        validator = DataValidator()
        
        # 测试邮箱验证
        is_valid, _ = validator.validate_email("test@example.com")
        if is_valid:
            log_test("数据验证器", "PASS", "邮箱验证功能正常", duration=time.time() - start_time)
        else:
            log_test("数据验证器", "FAIL", "邮箱验证功能异常", duration=time.time() - start_time)
    except Exception as e:
        duration = time.time() - start_time
        log_test("数据验证器", "FAIL", f"测试失败: {str(e)}", error=e, duration=duration)
    
    # 过滤引擎
    start_time = time.time()
    try:
        from src.collector.filter_engine import FilterEngine
        from src.core.config import yaml_config
        
        filter_engine = FilterEngine(yaml_config)
        duration = time.time() - start_time
        log_test("过滤引擎", "PASS", "初始化成功", duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        log_test("过滤引擎", "FAIL", f"初始化失败: {str(e)}", error=e, duration=duration)


def test_repository_pattern():
    """测试Repository模式"""
    print("\n" + "="*60)
    print("Repository模式测试")
    print("="*60)
    
    start_time = time.time()
    try:
        from src.core.database.connection import get_db
        from src.core.database.repositories.conversation_repo import ConversationRepository
        from src.core.database.repositories.customer_repo import CustomerRepository
        
        db = next(get_db())
        
        # 测试ConversationRepository
        conv_repo = ConversationRepository(db)
        assert hasattr(conv_repo, 'get_by_id')
        assert hasattr(conv_repo, 'create')
        assert hasattr(conv_repo, 'get_by_platform_message_id')
        log_test("ConversationRepository", "PASS", "所有方法可用")
        
        # 测试CustomerRepository
        customer_repo = CustomerRepository(db)
        assert hasattr(customer_repo, 'get_by_id')
        assert hasattr(customer_repo, 'get_or_create')
        log_test("CustomerRepository", "PASS", "所有方法可用")
        
        duration = time.time() - start_time
        log_test("Repository模式", "PASS", "所有Repository正常工作", duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        log_test("Repository模式", "FAIL", f"测试失败: {str(e)}", error=e, duration=duration)


def test_performance():
    """性能测试"""
    print("\n" + "="*60)
    print("性能测试")
    print("="*60)
    
    # API响应时间测试
    try:
        response = httpx.get(f"{base_url}/health/simple", timeout=5.0)
        if response.status_code == 200:
            response_time = response.elapsed.total_seconds()
            if response_time < 0.1:
                log_test("API响应时间", "PASS", f"响应时间: {response_time:.3f}s (优秀)")
            elif response_time < 0.5:
                log_test("API响应时间", "PASS", f"响应时间: {response_time:.3f}s (良好)")
            else:
                log_test("API响应时间", "WARN", f"响应时间: {response_time:.3f}s (较慢)")
    except Exception:
        log_test("API响应时间", "SKIP", "服务未启动")
    
    # 数据库查询性能
    start_time = time.time()
    try:
        from src.core.database.connection import get_db
        from src.core.database.repositories.conversation_repo import ConversationRepository
        
        db = next(get_db())
        repo = ConversationRepository(db)
        
        # 测试查询性能
        query_start = time.time()
        conversations, total = repo.get_by_filters(limit=10)
        query_duration = time.time() - query_start
        
        if query_duration < 0.1:
            log_test("数据库查询性能", "PASS", f"查询时间: {query_duration:.3f}s (优秀)")
        elif query_duration < 0.5:
            log_test("数据库查询性能", "PASS", f"查询时间: {query_duration:.3f}s (良好)")
        else:
            log_test("数据库查询性能", "WARN", f"查询时间: {query_duration:.3f}s (较慢)")
    except Exception as e:
        log_test("数据库查询性能", "FAIL", f"测试失败: {str(e)}", error=e)


def save_test_report():
    """保存测试报告"""
    report_dir = project_root / "data" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"local_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    report = {
        "test_time": datetime.now().isoformat(),
        "total_tests": len(test_results),
        "passed": sum(1 for r in test_results if r["status"] == "PASS"),
        "failed": sum(1 for r in test_results if r["status"] == "FAIL"),
        "skipped": sum(1 for r in test_results if r["status"] == "SKIP"),
        "warned": sum(1 for r in test_results if r["status"] == "WARN"),
        "results": test_results
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n测试报告已保存: {report_file}")


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


def main():
    """主测试函数"""
    print("="*60)
    print("本地完整测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试URL: {base_url}")
    print()
    
    # 运行所有测试
    test_environment()
    test_database()
    test_repository_pattern()
    test_core_functionality()
    test_api_endpoints()
    test_performance()
    
    # 打印摘要
    print_summary()
    
    # 保存报告
    save_test_report()
    
    # 返回退出码
    failed_count = sum(1 for r in test_results if r["status"] == "FAIL")
    return 0 if failed_count == 0 else 1


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

