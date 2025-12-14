"""
性能监控脚本
持续监控系统性能指标，特别是响应时间
"""
import asyncio
import httpx
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, base_url: str = "http://localhost:8000", interval: int = 60):
        self.base_url = base_url
        self.interval = interval  # 监控间隔（秒）
        self.metrics_history: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            "response_time_ms": 1000,  # 响应时间阈值（毫秒）
            "error_rate_percent": 5.0,  # 错误率阈值（%）
            "cpu_percent": 80.0,  # CPU使用率阈值（%）
            "memory_percent": 85.0,  # 内存使用率阈值（%）
        }
    
    async def check_health(self) -> Dict[str, Any]:
        """检查健康状态"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": response_time,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "response_time_ms": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def check_metrics(self) -> Dict[str, Any]:
        """检查性能指标"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/metrics")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            return {"error": str(e)}
        return {}
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[str]:
        """检查是否超过阈值"""
        alerts = []
        
        # 检查响应时间
        if metrics.get("avg_response_time_ms", 0) > self.alert_thresholds["response_time_ms"]:
            alerts.append(
                f"⚠️  响应时间过高: {metrics.get('avg_response_time_ms', 0):.1f}ms "
                f"(阈值: {self.alert_thresholds['response_time_ms']}ms)"
            )
        
        # 检查错误率
        if metrics.get("error_rate_percent", 0) > self.alert_thresholds["error_rate_percent"]:
            alerts.append(
                f"⚠️  错误率过高: {metrics.get('error_rate_percent', 0):.1f}% "
                f"(阈值: {self.alert_thresholds['error_rate_percent']}%)"
            )
        
        # 检查资源使用（从健康检查数据）
        health_data = metrics.get("health_data", {})
        resources = health_data.get("checks", {}).get("resources", {})
        resource_metrics = resources.get("metrics", {})
        
        if resource_metrics.get("cpu_percent", 0) > self.alert_thresholds["cpu_percent"]:
            alerts.append(
                f"⚠️  CPU使用率过高: {resource_metrics.get('cpu_percent', 0):.1f}% "
                f"(阈值: {self.alert_thresholds['cpu_percent']}%)"
            )
        
        if resource_metrics.get("memory_percent", 0) > self.alert_thresholds["memory_percent"]:
            alerts.append(
                f"⚠️  内存使用率过高: {resource_metrics.get('memory_percent', 0):.1f}% "
                f"(阈值: {self.alert_thresholds['memory_percent']}%)"
            )
        
        return alerts
    
    async def monitor_loop(self):
        """监控循环"""
        print(f"开始性能监控 (间隔: {self.interval}秒)")
        print(f"监控目标: {self.base_url}")
        print("=" * 80)
        
        while True:
            try:
                # 检查健康状态
                health = await self.check_health()
                
                # 检查性能指标
                metrics = await self.check_metrics()
                metrics["health_data"] = health
                
                # 记录指标
                self.metrics_history.append(metrics)
                
                # 只保留最近100条记录
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]
                
                # 显示当前状态
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] 性能监控")
                print(f"  状态: {health.get('status', 'unknown')}")
                print(f"  响应时间: {health.get('response_time_ms', 0):.1f}ms")
                
                if "avg_response_time_ms" in metrics:
                    print(f"  平均响应时间: {metrics.get('avg_response_time_ms', 0):.1f}ms")
                    print(f"  P95响应时间: {metrics.get('p95_response_time_ms', 0):.1f}ms")
                    print(f"  错误率: {metrics.get('error_rate_percent', 0):.1f}%")
                
                # 检查阈值
                alerts = self.check_thresholds(metrics)
                if alerts:
                    print("\n  ⚠️  告警:")
                    for alert in alerts:
                        print(f"    {alert}")
                
                # 等待下一次检查
                await asyncio.sleep(self.interval)
                
            except KeyboardInterrupt:
                print("\n\n监控已停止")
                break
            except Exception as e:
                print(f"\n监控错误: {str(e)}")
                await asyncio.sleep(self.interval)
    
    def save_report(self, output_file: str = None):
        """保存监控报告"""
        if output_file is None:
            report_dir = Path("data/monitoring")
            report_dir.mkdir(parents=True, exist_ok=True)
            output_file = report_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_duration_seconds": len(self.metrics_history) * self.interval,
            "metrics_count": len(self.metrics_history),
            "metrics": self.metrics_history,
            "summary": self._calculate_summary()
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n监控报告已保存: {output_file}")
        return output_file
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """计算统计摘要"""
        if not self.metrics_history:
            return {}
        
        response_times = [
            m.get("health_data", {}).get("response_time_ms", 0)
            for m in self.metrics_history
            if m.get("health_data", {}).get("response_time_ms")
        ]
        
        avg_response_times = [
            m.get("avg_response_time_ms", 0)
            for m in self.metrics_history
            if m.get("avg_response_time_ms", 0) > 0
        ]
        
        error_rates = [
            m.get("error_rate_percent", 0)
            for m in self.metrics_history
            if m.get("error_rate_percent", 0) > 0
        ]
        
        summary = {}
        if response_times:
            summary["avg_health_check_time_ms"] = sum(response_times) / len(response_times)
            summary["max_health_check_time_ms"] = max(response_times)
            summary["min_health_check_time_ms"] = min(response_times)
        
        if avg_response_times:
            summary["avg_response_time_ms"] = sum(avg_response_times) / len(avg_response_times)
            summary["max_response_time_ms"] = max(avg_response_times)
        
        if error_rates:
            summary["avg_error_rate_percent"] = sum(error_rates) / len(error_rates)
            summary["max_error_rate_percent"] = max(error_rates)
        
        return summary


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="性能监控脚本")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="服务URL (默认: http://localhost:8000)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="监控间隔（秒）(默认: 60)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="监控持续时间（秒），0表示持续监控 (默认: 0)"
    )
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(base_url=args.url, interval=args.interval)
    
    try:
        if args.duration > 0:
            # 运行指定时间后停止
            await asyncio.wait_for(monitor.monitor_loop(), timeout=args.duration)
        else:
            # 持续监控
            await monitor.monitor_loop()
    except KeyboardInterrupt:
        print("\n\n监控已停止")
    finally:
        # 保存报告
        monitor.save_report()


if __name__ == "__main__":
    asyncio.run(main())

