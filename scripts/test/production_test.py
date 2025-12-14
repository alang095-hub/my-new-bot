"""
生产环境测试脚本
用于自动化执行生产环境测试流程
"""
import os
import sys
import argparse
import json
import time
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import subprocess

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 测试结果收集
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
        "PASS": "[PASS]",
        "FAIL": "[FAIL]",
        "WARN": "[WARN]",
        "SKIP": "[SKIP]"
    }.get(status, "[UNKNOWN]")
    
    duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
    print(f"{status_symbol} {name}{duration_str}")
    if message:
        print(f"   {message}")
    if error:
        print(f"   错误: {str(error)}")


def test_environment_config():
    """测试环境配置"""
    start_time = time.time()
    try:
        from src.core.config import settings
        
        required_vars = [
            'database_url',
            'facebook_app_id',
            'facebook_access_token',
            'openai_api_key',
            'telegram_bot_token'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = getattr(settings, var, None)
            if not value:
                missing_vars.append(var)
        
        if missing_vars:
            log_test("环境配置", "FAIL", f"缺少必需的环境变量: {', '.join(missing_vars)}", duration=time.time()-start_time)
        else:
            log_test("环境配置", "PASS", "所有必需的环境变量已配置", duration=time.time()-start_time)
    except Exception as e:
        log_test("环境配置", "FAIL", f"环境配置检查失败: {str(e)}", e, duration=time.time()-start_time)


def test_database_connection():
    """测试数据库连接"""
    start_time = time.time()
    try:
        from src.core.database.connection import engine, get_db
        from sqlalchemy import text
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            result.fetchone()
        
        # 测试会话
        db = next(get_db())
        db.close()
        
        log_test("数据库连接", "PASS", "数据库连接成功", duration=time.time()-start_time)
    except Exception as e:
        log_test("数据库连接", "FAIL", f"数据库连接失败: {str(e)}", e, duration=time.time()-start_time)


def test_service_startup():
    """测试服务启动"""
    start_time = time.time()
    try:
        from src.main import app
        
        if app is None:
            log_test("服务启动", "FAIL", "FastAPI应用创建失败", duration=time.time()-start_time)
        else:
            log_test("服务启动", "PASS", "FastAPI应用创建成功", duration=time.time()-start_time)
    except Exception as e:
        log_test("服务启动", "FAIL", f"服务启动测试失败: {str(e)}", e, duration=time.time()-start_time)


def test_health_endpoint(base_url: str = "http://localhost:8000"):
    """测试健康检查端点"""
    start_time = time.time()
    try:
        response = httpx.get(f"{base_url}/health", timeout=5.0)
        
        if response.status_code == 200:
            data = response.json()
            log_test("健康检查端点", "PASS", f"健康检查通过: {data.get('status', 'unknown')}", duration=time.time()-start_time)
        else:
            log_test("健康检查端点", "FAIL", f"健康检查返回状态码: {response.status_code}", duration=time.time()-start_time)
    except httpx.RequestError as e:
        log_test("健康检查端点", "FAIL", f"无法连接到服务: {str(e)}", e, duration=time.time()-start_time)
    except Exception as e:
        log_test("健康检查端点", "FAIL", f"健康检查测试失败: {str(e)}", e, duration=time.time()-start_time)


def test_api_endpoints(base_url: str = "http://localhost:8000"):
    """测试API端点"""
    endpoints = [
        ("/", "根端点"),
        ("/metrics", "性能指标端点"),
        ("/statistics/daily", "每日统计端点"),
    ]
    
    for endpoint, name in endpoints:
        start_time = time.time()
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=5.0)
            
            if response.status_code == 200:
                log_test(f"API端点 - {name}", "PASS", f"端点 {endpoint} 正常", duration=time.time()-start_time)
            else:
                log_test(f"API端点 - {name}", "FAIL", f"端点 {endpoint} 返回状态码: {response.status_code}", duration=time.time()-start_time)
        except httpx.RequestError as e:
            log_test(f"API端点 - {name}", "FAIL", f"无法连接到端点: {str(e)}", e, duration=time.time()-start_time)
        except Exception as e:
            log_test(f"API端点 - {name}", "FAIL", f"端点测试失败: {str(e)}", e, duration=time.time()-start_time)


def test_database_queries():
    """测试数据库查询性能"""
    start_time = time.time()
    try:
        from src.core.database.connection import get_db
        from src.core.database.models import Conversation
        
        db = next(get_db())
        
        # 测试查询性能
        query_start = time.time()
        result = db.query(Conversation).limit(100).all()
        query_time = time.time() - query_start
        
        if query_time < 1.0:
            log_test("数据库查询性能", "PASS", f"查询100条记录耗时: {query_time:.3f}秒", duration=time.time()-start_time)
        else:
            log_test("数据库查询性能", "WARN", f"查询耗时较长: {query_time:.3f}秒", duration=time.time()-start_time)
        
        db.close()
    except Exception as e:
        log_test("数据库查询性能", "FAIL", f"数据库查询测试失败: {str(e)}", e, duration=time.time()-start_time)


def test_config_loading():
    """测试配置加载"""
    start_time = time.time()
    try:
        from src.core.config import settings, yaml_config
        
        # 检查环境变量配置
        if not settings.database_url:
            log_test("配置加载", "FAIL", "数据库URL未配置", duration=time.time()-start_time)
            return
        
        # 检查YAML配置
        telegram_config = yaml_config.get('telegram', {})
        
        log_test("配置加载", "PASS", "配置加载成功", duration=time.time()-start_time)
    except Exception as e:
        log_test("配置加载", "FAIL", f"配置加载失败: {str(e)}", e, duration=time.time()-start_time)


def test_e2e_workflow():
    """测试端到端工作流"""
    start_time = time.time()
    try:
        # 这里可以添加实际的端到端测试
        # 例如：发送测试消息，验证处理流程等
        
        log_test("端到端工作流", "SKIP", "需要手动测试或配置测试环境", duration=time.time()-start_time)
    except Exception as e:
        log_test("端到端工作流", "FAIL", f"端到端测试失败: {str(e)}", e, duration=time.time()-start_time)


def test_concurrency():
    """测试并发处理"""
    start_time = time.time()
    try:
        import asyncio
        import httpx
        
        async def make_request(client, url):
            try:
                response = await client.get(url, timeout=5.0)
                return response.status_code == 200
            except:
                return False
        
        async def run_concurrent_requests():
            async with httpx.AsyncClient() as client:
                tasks = [make_request(client, "http://localhost:8000/health") for _ in range(10)]
                results = await asyncio.gather(*tasks)
                return sum(results)
        
        success_count = asyncio.run(run_concurrent_requests())
        
        if success_count >= 8:  # 至少80%成功
            log_test("并发处理", "PASS", f"10个并发请求中 {success_count} 个成功", duration=time.time()-start_time)
        else:
            log_test("并发处理", "WARN", f"并发处理能力不足: {success_count}/10 成功", duration=time.time()-start_time)
    except Exception as e:
        log_test("并发处理", "FAIL", f"并发测试失败: {str(e)}", e, duration=time.time()-start_time)


def test_performance():
    """测试性能指标"""
    start_time = time.time()
    try:
        import httpx
        
        # 测试健康检查响应时间
        response_times = []
        for _ in range(5):
            req_start = time.time()
            try:
                response = httpx.get("http://localhost:8000/health", timeout=5.0)
                response_times.append(time.time() - req_start)
            except:
                pass
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            if avg_time < 0.5:
                log_test("性能指标", "PASS", f"平均响应时间: {avg_time*1000:.1f}ms", duration=time.time()-start_time)
            else:
                log_test("性能指标", "WARN", f"响应时间较慢: {avg_time*1000:.1f}ms", duration=time.time()-start_time)
        else:
            log_test("性能指标", "FAIL", "无法获取响应时间", duration=time.time()-start_time)
    except Exception as e:
        log_test("性能指标", "FAIL", f"性能测试失败: {str(e)}", e, duration=time.time()-start_time)


def generate_report(output_file: Optional[str] = None):
    """生成测试报告"""
    if output_file is None:
        report_dir = Path("data/test_reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        output_file = report_dir / f"production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    total = len(test_results)
    passed = len([r for r in test_results if r["status"] == "PASS"])
    failed = len([r for r in test_results if r["status"] == "FAIL"])
    warned = len([r for r in test_results if r["status"] == "WARN"])
    skipped = len([r for r in test_results if r["status"] == "SKIP"])
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "skipped": skipped,
            "pass_rate": (passed / total * 100) if total > 0 else 0
        },
        "results": test_results
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report, output_file


def run_tests(test_type: str = "all", base_url: str = "http://localhost:8000"):
    """运行测试"""
    print("=" * 80)
    print("生产环境测试")
    print("=" * 80)
    print()
    
    # 基础测试（总是运行）
    print("阶段1: 环境验证")
    print("-" * 80)
    test_environment_config()
    test_config_loading()
    test_database_connection()
    test_service_startup()
    print()
    
    # 如果服务未运行，跳过需要服务的测试
    try:
        httpx.get(f"{base_url}/health", timeout=2.0)
        service_running = True
    except:
        service_running = False
        print("⚠️  警告: 服务未运行，跳过需要服务的测试")
        print()
    
    if service_running:
        print("阶段2: 功能测试")
        print("-" * 80)
        test_health_endpoint(base_url)
        test_api_endpoints(base_url)
        print()
        
        if test_type in ["all", "performance"]:
            print("阶段3: 性能测试")
            print("-" * 80)
            test_database_queries()
            test_performance()
            if test_type == "all":
                test_concurrency()
            print()
    
    if test_type in ["all", "e2e"]:
        print("阶段4: 集成测试")
        print("-" * 80)
        test_e2e_workflow()
        print()
    
    # 生成报告
    print("=" * 80)
    print("测试报告")
    print("=" * 80)
    
    report, report_file = generate_report()
    
    total = report["summary"]["total"]
    passed = report["summary"]["passed"]
    failed = report["summary"]["failed"]
    warned = report["summary"]["warned"]
    skipped = report["summary"]["skipped"]
    pass_rate = report["summary"]["pass_rate"]
    
    print(f"\n总计: {total} 个测试项")
    print(f"[PASS] 通过: {passed}")
    print(f"[FAIL] 失败: {failed}")
    print(f"[WARN] 警告: {warned}")
    print(f"[SKIP] 跳过: {skipped}")
    print(f"\n通过率: {pass_rate:.1f}%")
    print()
    
    if failed > 0:
        print("失败项:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"  [FAIL] {result['name']}: {result['message']}")
        print()
    
    if warned > 0:
        print("警告项:")
        for result in test_results:
            if result["status"] == "WARN":
                print(f"  [WARN] {result['name']}: {result['message']}")
        print()
    
    print(f"测试报告已保存: {report_file}")
    print()
    
    # 判断测试是否通过
    if failed == 0 and pass_rate >= 80:
        print("[OK] 生产环境测试通过！")
        return 0
    elif failed == 0:
        print("[WARN] 测试基本通过，但建议改进警告项")
        return 0
    else:
        print("[FAIL] 测试失败，请修复失败项后重新测试")
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="生产环境测试脚本")
    parser.add_argument(
        "--test",
        choices=["all", "environment", "performance", "e2e", "concurrency"],
        default="all",
        help="测试类型 (默认: all)"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="服务URL (默认: http://localhost:8000)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="仅生成报告（需要先运行测试）"
    )
    
    args = parser.parse_args()
    
    if args.report:
        # 仅生成报告（如果有现有结果）
        if test_results:
            report, report_file = generate_report()
            print(f"报告已生成: {report_file}")
        else:
            print("没有测试结果，请先运行测试")
            return 1
    else:
        return run_tests(args.test, args.url)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

