"""
部署验证测试脚本
用于验证部署到Zeabur后的服务是否正常工作
"""
import os
import sys
import time
import httpx
import json
import argparse
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


def test_service_availability(base_url: str):
    """测试服务可用性"""
    print("\n" + "="*60)
    print("服务可用性测试")
    print("="*60)
    
    # 测试服务是否可以访问
    start_time = time.time()
    try:
        response = httpx.get(f"{base_url}/health/simple", timeout=10.0)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            log_test("服务可访问", "PASS", f"响应时间: {duration:.3f}s, 状态: {data.get('status')}", duration=duration)
            return True
        else:
            log_test("服务可访问", "FAIL", f"HTTP {response.status_code}", duration=duration)
            return False
    except httpx.ConnectError:
        duration = time.time() - start_time
        log_test("服务可访问", "FAIL", "无法连接到服务，请检查URL是否正确", duration=duration)
        return False
    except Exception as e:
        duration = time.time() - start_time
        log_test("服务可访问", "FAIL", f"连接失败: {str(e)}", error=e, duration=duration)
        return False


def test_health_endpoints(base_url: str):
    """测试健康检查端点"""
    print("\n" + "="*60)
    print("健康检查端点测试")
    print("="*60)
    
    endpoints = [
        ("/health/simple", "简单健康检查"),
        ("/health", "完整健康检查"),
    ]
    
    results = []
    for endpoint, name in endpoints:
        start_time = time.time()
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=10.0)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                
                if duration < 0.5:
                    log_test(f"健康检查: {name}", "PASS", f"状态: {status}, 响应时间: {duration:.3f}s (优秀)", duration=duration)
                elif duration < 1.0:
                    log_test(f"健康检查: {name}", "PASS", f"状态: {status}, 响应时间: {duration:.3f}s (良好)", duration=duration)
                else:
                    log_test(f"健康检查: {name}", "WARN", f"状态: {status}, 响应时间: {duration:.3f}s (较慢)", duration=duration)
                results.append(True)
            else:
                log_test(f"健康检查: {name}", "FAIL", f"HTTP {response.status_code}", duration=duration)
                results.append(False)
        except Exception as e:
            duration = time.time() - start_time
            log_test(f"健康检查: {name}", "FAIL", f"请求失败: {str(e)}", error=e, duration=duration)
            results.append(False)
    
    return all(results)


def test_api_endpoints(base_url: str):
    """测试API端点"""
    print("\n" + "="*60)
    print("API端点测试")
    print("="*60)
    
    endpoints = [
        ("GET", "/", "根路径"),
        ("GET", "/metrics", "性能指标"),
        ("GET", "/api/v1/admin/conversations?page=1&page_size=10", "对话列表"),
        ("GET", "/api/v1/admin/statistics", "统计信息"),
    ]
    
    results = []
    for method, endpoint, name in endpoints:
        start_time = time.time()
        try:
            if method == "GET":
                response = httpx.get(f"{base_url}{endpoint}", timeout=10.0)
            else:
                response = httpx.post(f"{base_url}{endpoint}", timeout=10.0)
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                log_test(f"API端点: {name}", "PASS", f"响应时间: {duration:.3f}s", duration=duration)
                results.append(True)
            elif response.status_code in [401, 403]:
                log_test(f"API端点: {name}", "WARN", f"需要认证 (HTTP {response.status_code})", duration=duration)
                results.append(True)  # 需要认证也算正常
            else:
                log_test(f"API端点: {name}", "FAIL", f"HTTP {response.status_code}", duration=duration)
                results.append(False)
        except Exception as e:
            duration = time.time() - start_time
            log_test(f"API端点: {name}", "FAIL", f"请求失败: {str(e)}", error=e, duration=duration)
            results.append(False)
    
    return results


def test_webhook_endpoint(base_url: str):
    """测试Webhook端点"""
    print("\n" + "="*60)
    print("Webhook端点测试")
    print("="*60)
    
    # 测试Webhook验证（GET请求）
    start_time = time.time()
    try:
        # 模拟Facebook Webhook验证请求
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "test_token",
            "hub.challenge": "test_challenge_123"
        }
        response = httpx.get(f"{base_url}/webhook", params=params, timeout=10.0)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            # 如果验证token正确，应该返回challenge
            if response.text == "test_challenge_123":
                log_test("Webhook验证", "PASS", "验证端点正常（使用测试token）", duration=duration)
            else:
                log_test("Webhook验证", "PASS", f"端点可访问 (HTTP {response.status_code})", duration=duration)
            return True
        elif response.status_code == 403:
            log_test("Webhook验证", "WARN", "验证token不匹配（这是正常的，因为使用了测试token）", duration=duration)
            return True  # Token不匹配也算正常
        else:
            log_test("Webhook验证", "FAIL", f"HTTP {response.status_code}", duration=duration)
            return False
    except Exception as e:
        duration = time.time() - start_time
        log_test("Webhook验证", "FAIL", f"请求失败: {str(e)}", error=e, duration=duration)
        return False


def test_api_documentation(base_url: str):
    """测试API文档"""
    print("\n" + "="*60)
    print("API文档测试")
    print("="*60)
    
    endpoints = [
        ("/docs", "Swagger UI"),
        ("/redoc", "ReDoc"),
    ]
    
    results = []
    for endpoint, name in endpoints:
        start_time = time.time()
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=10.0)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                log_test(f"API文档: {name}", "PASS", f"文档可访问，响应时间: {duration:.3f}s", duration=duration)
                results.append(True)
            else:
                log_test(f"API文档: {name}", "WARN", f"HTTP {response.status_code}", duration=duration)
                results.append(False)
        except Exception as e:
            duration = time.time() - start_time
            log_test(f"API文档: {name}", "FAIL", f"请求失败: {str(e)}", error=e, duration=duration)
            results.append(False)
    
    return results


def test_performance(base_url: str):
    """性能测试"""
    print("\n" + "="*60)
    print("性能测试")
    print("="*60)
    
    # 测试多次请求的平均响应时间
    endpoint = "/health/simple"
    times = []
    
    for i in range(5):
        start_time = time.time()
        try:
            response = httpx.get(f"{base_url}{endpoint}", timeout=10.0)
            duration = time.time() - start_time
            if response.status_code == 200:
                times.append(duration)
        except Exception:
            pass
    
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        if avg_time < 0.1:
            log_test("平均响应时间", "PASS", f"{avg_time:.3f}s (优秀)", duration=avg_time)
        elif avg_time < 0.5:
            log_test("平均响应时间", "PASS", f"{avg_time:.3f}s (良好)", duration=avg_time)
        else:
            log_test("平均响应时间", "WARN", f"{avg_time:.3f}s (较慢)", duration=avg_time)
        
        log_test("响应时间范围", "PASS", f"最小: {min_time:.3f}s, 最大: {max_time:.3f}s")
        return True
    else:
        log_test("性能测试", "FAIL", "无法完成性能测试")
        return False


def test_ssl_certificate(base_url: str):
    """测试SSL证书"""
    print("\n" + "="*60)
    print("SSL证书测试")
    print("="*60)
    
    start_time = time.time()
    try:
        # 检查URL是否使用HTTPS
        if not base_url.startswith("https://"):
            log_test("SSL证书", "SKIP", "URL不是HTTPS，跳过SSL测试")
            return True
        
        response = httpx.get(f"{base_url}/health/simple", timeout=10.0, verify=True)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            log_test("SSL证书", "PASS", "HTTPS连接正常，证书有效", duration=duration)
            return True
        else:
            log_test("SSL证书", "WARN", f"HTTPS连接异常 (HTTP {response.status_code})", duration=duration)
            return False
    except httpx.ConnectError as e:
        duration = time.time() - start_time
        log_test("SSL证书", "FAIL", f"连接失败: {str(e)}", error=e, duration=duration)
        return False
    except Exception as e:
        duration = time.time() - start_time
        log_test("SSL证书", "WARN", f"SSL测试异常: {str(e)}", error=e, duration=duration)
        return False


def save_test_report(base_url: str):
    """保存测试报告"""
    report_dir = project_root / "data" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"deployment_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    report = {
        "test_time": datetime.now().isoformat(),
        "base_url": base_url,
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
    return report_file


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
    if failed == 0 and warned == 0:
        print("\n🎉 所有测试通过！部署验证成功！")
        return 0
    elif failed == 0:
        print("\n⚠️ 所有关键测试通过，但有警告项，建议检查。")
        return 0
    else:
        print("\n❌ 有测试失败，请检查部署配置。")
        return 1


def main():
    """主测试函数"""
    parser = argparse.ArgumentParser(description="部署验证测试")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="部署的服务URL（默认: http://localhost:8000）"
    )
    args = parser.parse_args()
    
    base_url = args.url.rstrip('/')
    
    print("="*60)
    print("部署验证测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试URL: {base_url}")
    print()
    
    # 运行所有测试
    if not test_service_availability(base_url):
        print("\n⚠️ 服务不可用，跳过其他测试")
        print_summary()
        save_test_report(base_url)
        return 1
    
    test_health_endpoints(base_url)
    test_api_endpoints(base_url)
    test_webhook_endpoint(base_url)
    test_api_documentation(base_url)
    test_performance(base_url)
    test_ssl_certificate(base_url)
    
    # 打印摘要
    exit_code = print_summary()
    
    # 保存报告
    save_test_report(base_url)
    
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

