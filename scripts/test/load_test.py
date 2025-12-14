"""
负载测试脚本
用于测试系统在高负载下的性能表现
"""
import asyncio
import httpx
import time
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class LoadTester:
    """负载测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
    
    async def make_request(self, client: httpx.AsyncClient, endpoint: str) -> Dict[str, Any]:
        """发送单个请求"""
        start_time = time.time()
        try:
            response = await client.get(f"{self.base_url}{endpoint}", timeout=30.0)
            elapsed = (time.time() - start_time) * 1000  # 转换为毫秒
            
            return {
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response_time_ms": elapsed,
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "response_time_ms": elapsed,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_load_test(
        self,
        endpoint: str = "/health",
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        ramp_up_seconds: int = 5
    ) -> Dict[str, Any]:
        """运行负载测试"""
        print(f"开始负载测试")
        print(f"  目标: {self.base_url}{endpoint}")
        print(f"  并发用户: {concurrent_users}")
        print(f"  每用户请求数: {requests_per_user}")
        print(f"  总请求数: {concurrent_users * requests_per_user}")
        print(f"  预热时间: {ramp_up_seconds}秒")
        print("=" * 80)
        
        all_results: List[Dict[str, Any]] = []
        start_time = time.time()
        
        async def user_simulation(user_id: int):
            """模拟单个用户"""
            async with httpx.AsyncClient(timeout=30.0) as client:
                user_results = []
                for i in range(requests_per_user):
                    # 预热阶段：逐渐增加并发
                    if i == 0 and user_id > 0:
                        await asyncio.sleep(ramp_up_seconds / concurrent_users * user_id)
                    
                    result = await self.make_request(client, endpoint)
                    result["user_id"] = user_id
                    result["request_id"] = i
                    user_results.append(result)
                    all_results.append(result)
                    
                    # 请求间隔（模拟真实用户行为）
                    await asyncio.sleep(0.1)
                
                return user_results
        
        # 创建并发任务
        tasks = [user_simulation(i) for i in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # 分析结果
        return self._analyze_results(all_results, total_time)
    
    def _analyze_results(self, results: List[Dict[str, Any]], total_time: float) -> Dict[str, Any]:
        """分析测试结果"""
        if not results:
            return {"error": "没有测试结果"}
        
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]
        
        response_times = [r["response_time_ms"] for r in successful]
        
        analysis = {
            "total_requests": len(results),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate_percent": (len(successful) / len(results) * 100) if results else 0,
            "total_time_seconds": total_time,
            "requests_per_second": len(results) / total_time if total_time > 0 else 0,
        }
        
        if response_times:
            analysis["response_times"] = {
                "min_ms": min(response_times),
                "max_ms": max(response_times),
                "avg_ms": statistics.mean(response_times),
                "median_ms": statistics.median(response_times),
                "p95_ms": self._percentile(response_times, 95),
                "p99_ms": self._percentile(response_times, 99),
            }
        
        if failed:
            error_codes = {}
            for r in failed:
                code = r.get("status_code", "error")
                error_codes[code] = error_codes.get(code, 0) + 1
            analysis["error_codes"] = error_codes
        
        return analysis
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        if index >= len(sorted_data):
            return sorted_data[-1]
        return sorted_data[index]
    
    def print_results(self, analysis: Dict[str, Any]):
        """打印测试结果"""
        print("\n" + "=" * 80)
        print("负载测试结果")
        print("=" * 80)
        print(f"总请求数: {analysis.get('total_requests', 0)}")
        print(f"成功请求: {analysis.get('successful_requests', 0)}")
        print(f"失败请求: {analysis.get('failed_requests', 0)}")
        print(f"成功率: {analysis.get('success_rate_percent', 0):.2f}%")
        print(f"总耗时: {analysis.get('total_time_seconds', 0):.2f}秒")
        print(f"请求速率: {analysis.get('requests_per_second', 0):.2f} 请求/秒")
        
        if "response_times" in analysis:
            rt = analysis["response_times"]
            print("\n响应时间统计:")
            print(f"  最小: {rt.get('min_ms', 0):.2f}ms")
            print(f"  最大: {rt.get('max_ms', 0):.2f}ms")
            print(f"  平均: {rt.get('avg_ms', 0):.2f}ms")
            print(f"  中位数: {rt.get('median_ms', 0):.2f}ms")
            print(f"  P95: {rt.get('p95_ms', 0):.2f}ms")
            print(f"  P99: {rt.get('p99_ms', 0):.2f}ms")
        
        if "error_codes" in analysis:
            print("\n错误统计:")
            for code, count in analysis["error_codes"].items():
                print(f"  {code}: {count}")
        
        # 性能评估
        print("\n性能评估:")
        if analysis.get("success_rate_percent", 0) >= 99:
            print("  ✅ 优秀 - 成功率 >= 99%")
        elif analysis.get("success_rate_percent", 0) >= 95:
            print("  ⚠️  良好 - 成功率 >= 95%")
        else:
            print("  ❌ 需要改进 - 成功率 < 95%")
        
        avg_rt = analysis.get("response_times", {}).get("avg_ms", 0)
        if avg_rt < 200:
            print("  ✅ 响应时间优秀 - 平均 < 200ms")
        elif avg_rt < 500:
            print("  ⚠️  响应时间良好 - 平均 < 500ms")
        else:
            print("  ❌ 响应时间需要优化 - 平均 >= 500ms")
    
    def save_report(self, analysis: Dict[str, Any], output_file: str = None):
        """保存测试报告"""
        if output_file is None:
            report_dir = Path("data/test_reports")
            report_dir.mkdir(parents=True, exist_ok=True)
            output_file = report_dir / f"load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "analysis": analysis
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试报告已保存: {output_file}")
        return output_file


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="负载测试脚本")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="服务URL (默认: http://localhost:8000)"
    )
    parser.add_argument(
        "--endpoint",
        default="/health",
        help="测试端点 (默认: /health)"
    )
    parser.add_argument(
        "--users",
        type=int,
        default=10,
        help="并发用户数 (默认: 10)"
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=10,
        help="每用户请求数 (默认: 10)"
    )
    parser.add_argument(
        "--ramp-up",
        type=int,
        default=5,
        help="预热时间（秒）(默认: 5)"
    )
    
    args = parser.parse_args()
    
    tester = LoadTester(base_url=args.url)
    
    analysis = await tester.run_load_test(
        endpoint=args.endpoint,
        concurrent_users=args.users,
        requests_per_user=args.requests,
        ramp_up_seconds=args.ramp_up
    )
    
    tester.print_results(analysis)
    tester.save_report(analysis)


if __name__ == "__main__":
    asyncio.run(main())

