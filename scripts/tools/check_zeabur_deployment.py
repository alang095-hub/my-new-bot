#!/usr/bin/env python3
"""
Zeabur部署状态检查脚本
检查应用服务的所有端点和配置
"""

import sys
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import httpx
except ImportError:
    print("❌ 需要安装 httpx: pip install httpx")
    sys.exit(1)


class ZeaburChecker:
    """Zeabur部署检查器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "checks": {}
        }
    
    def check_endpoint(self, path: str, name: str, method: str = "GET", 
                      expected_status: int = 200) -> Dict[str, Any]:
        """检查端点"""
        url = f"{self.base_url}{path}"
        result = {
            "name": name,
            "url": url,
            "status": "unknown",
            "status_code": None,
            "response_time_ms": None,
            "error": None,
            "data": None
        }
        
        try:
            start_time = time.time()
            if method == "GET":
                response = httpx.get(url, timeout=10.0, follow_redirects=True)
            elif method == "POST":
                response = httpx.post(url, timeout=10.0, follow_redirects=True)
            else:
                result["error"] = f"不支持的HTTP方法: {method}"
                result["status"] = "error"
                return result
            
            response_time = (time.time() - start_time) * 1000
            result["status_code"] = response.status_code
            result["response_time_ms"] = round(response_time, 2)
            
            if response.status_code == expected_status:
                result["status"] = "success"
                try:
                    result["data"] = response.json()
                except:
                    result["data"] = response.text[:500]  # 限制长度
            else:
                result["status"] = "failed"
                result["error"] = f"期望状态码 {expected_status}，实际 {response.status_code}"
                try:
                    result["data"] = response.text[:500]
                except:
                    pass
                    
        except httpx.TimeoutException:
            result["status"] = "timeout"
            result["error"] = "请求超时（10秒）"
        except httpx.ConnectError:
            result["status"] = "connection_error"
            result["error"] = "无法连接到服务器（可能是502错误）"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def check_all(self):
        """检查所有端点"""
        print(f"\n{'='*60}")
        print(f"🔍 检查Zeabur部署状态: {self.base_url}")
        print(f"{'='*60}\n")
        
        # 1. 简单健康检查
        print("1️⃣  检查简单健康检查端点...")
        result = self.check_endpoint("/health/simple", "简单健康检查")
        self.results["checks"]["health_simple"] = result
        self._print_result(result)
        
        # 2. 完整健康检查
        print("\n2️⃣  检查完整健康检查端点...")
        result = self.check_endpoint("/health", "完整健康检查")
        self.results["checks"]["health"] = result
        self._print_result(result)
        
        # 3. 根路径
        print("\n3️⃣  检查根路径...")
        result = self.check_endpoint("/", "根路径")
        self.results["checks"]["root"] = result
        self._print_result(result)
        
        # 4. API文档
        print("\n4️⃣  检查API文档...")
        result = self.check_endpoint("/docs", "API文档")
        self.results["checks"]["docs"] = result
        self._print_result(result)
        
        # 5. 部署状态
        print("\n5️⃣  检查部署状态端点...")
        result = self.check_endpoint("/admin/deployment/status", "部署状态")
        self.results["checks"]["deployment_status"] = result
        self._print_result(result)
        
        # 6. Token验证
        print("\n6️⃣  检查Token验证端点...")
        result = self.check_endpoint("/admin/deployment/verify-token", "Token验证")
        self.results["checks"]["verify_token"] = result
        self._print_result(result)
        
        # 7. 统计端点
        print("\n7️⃣  检查统计端点...")
        result = self.check_endpoint("/statistics/daily", "每日统计")
        self.results["checks"]["statistics"] = result
        self._print_result(result)
        
        # 8. 性能指标
        print("\n8️⃣  检查性能指标端点...")
        result = self.check_endpoint("/metrics", "性能指标")
        self.results["checks"]["metrics"] = result
        self._print_result(result)
        
        # 打印总结
        self._print_summary()
    
    def _print_result(self, result: Dict[str, Any]):
        """打印检查结果"""
        status_icon = {
            "success": "✅",
            "failed": "❌",
            "error": "⚠️",
            "timeout": "⏱️",
            "connection_error": "🔌",
            "unknown": "❓"
        }.get(result["status"], "❓")
        
        print(f"   {status_icon} {result['name']}")
        print(f"      URL: {result['url']}")
        
        if result["status_code"]:
            print(f"      状态码: {result['status_code']}")
        
        if result["response_time_ms"]:
            print(f"      响应时间: {result['response_time_ms']}ms")
        
        if result["error"]:
            print(f"      错误: {result['error']}")
        
        if result["data"] and result["status"] == "success":
            if isinstance(result["data"], dict):
                # 显示关键信息
                if "status" in result["data"]:
                    print(f"      状态: {result['data']['status']}")
                if "checks" in result["data"]:
                    db_check = result["data"]["checks"].get("database", {})
                    if db_check:
                        print(f"      数据库: {db_check.get('status', 'unknown')}")
    
    def _print_summary(self):
        """打印总结"""
        print(f"\n{'='*60}")
        print("📊 检查总结")
        print(f"{'='*60}\n")
        
        total = len(self.results["checks"])
        success = sum(1 for r in self.results["checks"].values() if r["status"] == "success")
        failed = sum(1 for r in self.results["checks"].values() if r["status"] == "failed")
        errors = sum(1 for r in self.results["checks"].values() if r["status"] in ["error", "timeout", "connection_error"])
        
        print(f"总计: {total} 个检查")
        print(f"✅ 成功: {success}")
        print(f"❌ 失败: {failed}")
        print(f"⚠️  错误: {errors}")
        
        # 关键检查
        print(f"\n{'='*60}")
        print("🔑 关键检查结果")
        print(f"{'='*60}\n")
        
        critical_checks = ["health_simple", "health", "root"]
        for key in critical_checks:
            if key in self.results["checks"]:
                result = self.results["checks"][key]
                status_icon = "✅" if result["status"] == "success" else "❌"
                print(f"{status_icon} {result['name']}: {result['status']}")
        
        # 数据库连接状态
        if "health" in self.results["checks"]:
            health_result = self.results["checks"]["health"]
            if health_result["status"] == "success" and health_result.get("data"):
                data = health_result["data"]
                if isinstance(data, dict) and "checks" in data:
                    db_check = data["checks"].get("database", {})
                    if db_check:
                        db_status = db_check.get("status", "unknown")
                        status_icon = "✅" if db_status == "healthy" else "❌"
                        print(f"{status_icon} 数据库连接: {db_status}")
        
        print(f"\n{'='*60}")
        print("💡 建议")
        print(f"{'='*60}\n")
        
        if errors > 0:
            print("⚠️  有连接错误，可能的原因：")
            print("   1. 服务未启动或已崩溃")
            print("   2. 502错误（负载均衡器无法连接到服务）")
            print("   3. 网络问题")
            print("\n   建议：")
            print("   - 在Zeabur控制台查看服务状态")
            print("   - 查看服务日志，查找错误信息")
            print("   - 确认服务状态是 'Running'")
        
        if failed > 0:
            print("❌ 有检查失败，请查看上面的详细信息")
        
        if success == total:
            print("🎉 所有检查都通过！服务运行正常！")
    
    def save_report(self, filename: str = "zeabur_check_report.json"):
        """保存检查报告"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 检查报告已保存到: {filename}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="检查Zeabur部署状态")
    parser.add_argument(
        "--url",
        default="https://my-telegram-bot33.zeabur.app",
        help="应用URL（默认: https://my-telegram-bot33.zeabur.app）"
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="保存检查报告到JSON文件"
    )
    
    args = parser.parse_args()
    
    checker = ZeaburChecker(args.url)
    checker.check_all()
    
    if args.save_report:
        checker.save_report()


if __name__ == "__main__":
    main()




