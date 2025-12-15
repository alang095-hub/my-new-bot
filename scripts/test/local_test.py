"""
本地快速测试脚本
用于快速验证本地开发环境的基本功能
"""
import os
import sys
import time
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

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


def test_database_connection():
    """测试数据库连接"""
    start_time = time.time()
    try:
        from src.core.database.connection import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        duration = time.time() - start_time
        log_test("数据库连接", "PASS", f"连接成功，响应时间: {duration:.3f}s", duration=duration)
        return True
    except Exception as e:
        duration = time.time() - start_time
        log_test("数据库连接", "FAIL", f"连接失败: {str(e)}", error=e, duration=duration)
        return False


def test_config_loading():
    """测试配置加载"""
    start_time = time.time()
    try:
        from src.core.config import settings
        # 检查关键配置
        checks = []
        if hasattr(settings, 'database_url'):
            checks.append("database_url")
        if hasattr(settings, 'facebook_access_token'):
            checks.append("facebook_access_token")
        if hasattr(settings, 'openai_api_key'):
            checks.append("openai_api_key")
        
        duration = time.time() - start_time
        log_test("配置加载", "PASS", f"配置加载成功，已加载: {len(checks)} 个关键配置", duration=duration)
        return True
    except Exception as e:
        duration = time.time() - start_time
        log_test("配置加载", "FAIL", f"配置加载失败: {str(e)}", error=e, duration=duration)
        return False


def test_api_health(base_url: str = "http://localhost:8000"):
    """测试API健康检查"""
    start_time = time.time()
    try:
        response = httpx.get(f"{base_url}/health/simple", timeout=5.0)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            log_test("API健康检查", "PASS", f"服务运行正常: {data.get('status')}", duration=duration)
            return True
        else:
            log_test("API健康检查", "FAIL", f"HTTP {response.status_code}", duration=duration)
            return False
    except httpx.ConnectError:
        duration = time.time() - start_time
        log_test("API健康检查", "SKIP", "服务未启动，请先运行: uvicorn src.main:app --reload", duration=duration)
        return None
    except Exception as e:
        duration = time.time() - start_time
        log_test("API健康检查", "FAIL", f"请求失败: {str(e)}", error=e, duration=duration)
        return False


def test_api_endpoints(base_url: str = "http://localhost:8000"):
    """测试基础API端点"""
    endpoints = [
        ("/", "根路径"),
        ("/health", "健康检查"),
        ("/health/simple", "简单健康检查"),
        ("/metrics", "性能指标"),
    ]
    
    results = []
    for endpoint, name in endpoints:
        start_time = time.time()
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=5.0)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                log_test(f"API端点: {name}", "PASS", f"响应时间: {duration:.3f}s", duration=duration)
                results.append(True)
            else:
                log_test(f"API端点: {name}", "FAIL", f"HTTP {response.status_code}", duration=duration)
                results.append(False)
        except httpx.ConnectError:
            duration = time.time() - start_time
            log_test(f"API端点: {name}", "SKIP", "服务未启动", duration=duration)
            results.append(None)
        except Exception as e:
            duration = time.time() - start_time
            log_test(f"API端点: {name}", "FAIL", f"请求失败: {str(e)}", error=e, duration=duration)
            results.append(False)
    
    return results


def test_core_modules():
    """测试核心模块导入"""
    modules = [
        ("src.core.database.connection", "数据库连接"),
        ("src.core.config", "配置管理"),
        ("src.core.logging.config", "日志配置"),
        ("src.ai.reply_generator", "AI回复生成器"),
        ("src.collector.data_collector", "数据收集器"),
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
    start_time = time.time()
    try:
        from src.core.database.connection import get_db
        from src.core.database.repositories.conversation_repo import ConversationRepository
        
        db = next(get_db())
        repo = ConversationRepository(db)
        
        # 测试基本方法
        assert hasattr(repo, 'get_by_id')
        assert hasattr(repo, 'create')
        assert hasattr(repo, 'get_by_platform_message_id')
        
        duration = time.time() - start_time
        log_test("Repository模式", "PASS", "Repository方法可用", duration=duration)
        return True
    except Exception as e:
        duration = time.time() - start_time
        log_test("Repository模式", "FAIL", f"测试失败: {str(e)}", error=e, duration=duration)
        return False


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
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"⏭️ 跳过: {skipped}")
    print(f"⚠️ 警告: {warned}")
    
    if failed > 0:
        print("\n失败的测试:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"  - {result['name']}: {result.get('error', result.get('message', ''))}")
    
    print("="*60)


def main():
    """主测试函数"""
    print("="*60)
    print("本地快速测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 阶段1: 基础功能测试
    print("阶段1: 基础功能测试")
    print("-" * 60)
    test_database_connection()
    test_config_loading()
    test_core_modules()
    test_repository_pattern()
    print()
    
    # 阶段2: API测试（如果服务运行）
    print("阶段2: API端点测试")
    print("-" * 60)
    print("提示: 如果服务未启动，这些测试将被跳过")
    print("启动服务: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
    print()
    
    api_health = test_api_health()
    if api_health is not None:
        test_api_endpoints()
    else:
        print("跳过API端点测试（服务未启动）")
    print()
    
    # 打印摘要
    print_summary()
    
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

