#!/usr/bin/env python3
"""
Zeabur部署状态检查脚本
检查应用服务的所有端点和配置
包括：服务健康、数据库连接、API端点、性能指标、资源使用、错误统计等
"""

import sys
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

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
            "checks": {},
            "summary": {},
            "errors": {},
            "diagnostics": []
        }
        self.error_categories = defaultdict(list)
    
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
        self._categorize_error(result)
        
        # 2. 完整健康检查
        print("\n2️⃣  检查完整健康检查端点...")
        result = self.check_endpoint("/health", "完整健康检查")
        self.results["checks"]["health"] = result
        self._print_result(result)
        self._categorize_error(result)
        self._parse_health_check(result)
        
        # 3. 根路径
        print("\n3️⃣  检查根路径...")
        result = self.check_endpoint("/", "根路径")
        self.results["checks"]["root"] = result
        self._print_result(result)
        self._categorize_error(result)
        
        # 4. API文档
        print("\n4️⃣  检查API文档...")
        result = self.check_endpoint("/docs", "API文档")
        self.results["checks"]["docs"] = result
        self._print_result(result)
        self._categorize_error(result)
        
        # 5. 部署状态
        print("\n5️⃣  检查部署状态端点...")
        result = self.check_endpoint("/admin/deployment/status", "部署状态")
        self.results["checks"]["deployment_status"] = result
        self._print_result(result)
        self._categorize_error(result)
        self._parse_deployment_status(result)
        
        # 6. Token验证
        print("\n6️⃣  检查Token验证端点...")
        result = self.check_endpoint("/admin/deployment/verify-token", "Token验证")
        self.results["checks"]["verify_token"] = result
        self._print_result(result)
        self._categorize_error(result)
        
        # 7. 统计端点
        print("\n7️⃣  检查统计端点...")
        result = self.check_endpoint("/statistics/daily", "每日统计")
        self.results["checks"]["statistics"] = result
        self._print_result(result)
        self._categorize_error(result)
        
        # 8. 性能指标
        print("\n8️⃣  检查性能指标端点...")
        result = self.check_endpoint("/metrics", "性能指标")
        self.results["checks"]["metrics"] = result
        self._print_result(result)
        self._categorize_error(result)
        self._parse_metrics(result)
        
        # 分析错误并生成诊断
        self._analyze_errors()
        self._generate_diagnostics()
        
        # 生成总结
        self._generate_summary()
        
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
                        db_status = db_check.get('status', 'unknown')
                        db_icon = "✅" if db_status == "healthy" else "❌"
                        print(f"      数据库: {db_icon} {db_status}")
                        if "response_time_ms" in db_check:
                            print(f"      数据库响应时间: {db_check['response_time_ms']}ms")
    
    def _categorize_error(self, result: Dict[str, Any]):
        """分类错误"""
        if result["status"] != "success":
            error_type = result["status"]
            self.error_categories[error_type].append({
                "name": result["name"],
                "url": result["url"],
                "error": result.get("error", "未知错误"),
                "status_code": result.get("status_code")
            })
    
    def _parse_health_check(self, result: Dict[str, Any]):
        """解析健康检查结果"""
        if result["status"] == "success" and result.get("data"):
            data = result["data"]
            if isinstance(data, dict):
                health_info = {
                    "overall_status": data.get("status", "unknown"),
                    "uptime_seconds": data.get("uptime_seconds", 0),
                    "timestamp": data.get("timestamp")
                }
                
                # 解析各项检查
                checks = data.get("checks", {})
                health_info["checks"] = {}
                
                # 数据库检查
                if "database" in checks:
                    db_check = checks["database"]
                    health_info["checks"]["database"] = {
                        "status": db_check.get("status", "unknown"),
                        "message": db_check.get("message", ""),
                        "response_time_ms": db_check.get("response_time_ms", 0)
                    }
                
                # API配置检查
                if "api_config" in checks:
                    api_check = checks["api_config"]
                    health_info["checks"]["api_config"] = {
                        "status": api_check.get("status", "unknown"),
                        "message": api_check.get("message", "")
                    }
                
                # 资源检查
                if "resources" in checks:
                    resource_check = checks["resources"]
                    health_info["checks"]["resources"] = {
                        "status": resource_check.get("status", "unknown"),
                        "message": resource_check.get("message", ""),
                        "metrics": resource_check.get("metrics", {})
                    }
                
                self.results["health_info"] = health_info
    
    def _parse_deployment_status(self, result: Dict[str, Any]):
        """解析部署状态结果"""
        if result["status"] == "success" and result.get("data"):
            data = result["data"]
            if isinstance(data, dict) and data.get("success"):
                status = data.get("status", {})
                deployment_info = {
                    "database": status.get("database", {}),
                    "pages": status.get("pages", {}),
                    "token": status.get("token", {}),
                    "sync": status.get("sync", {})
                }
                self.results["deployment_info"] = deployment_info
    
    def _parse_metrics(self, result: Dict[str, Any]):
        """解析性能指标结果"""
        if result["status"] == "success" and result.get("data"):
            data = result["data"]
            if isinstance(data, dict):
                metrics_info = {
                    "request_count": data.get("request_count", 0),
                    "error_count": data.get("error_count", 0),
                    "error_rate_percent": data.get("error_rate_percent", 0),
                    "avg_response_time_ms": data.get("avg_response_time_ms", 0),
                    "p95_response_time_ms": data.get("p95_response_time_ms", 0),
                    "uptime_seconds": data.get("uptime_seconds", 0)
                }
                self.results["metrics_info"] = metrics_info
    
    def _analyze_errors(self):
        """分析错误"""
        self.results["errors"] = {
            "total_errors": sum(len(errors) for errors in self.error_categories.values()),
            "by_category": {
                category: len(errors) 
                for category, errors in self.error_categories.items()
            },
            "details": dict(self.error_categories)
        }
    
    def _generate_diagnostics(self):
        """生成诊断建议"""
        diagnostics = []
        
        # 检查连接错误
        if "connection_error" in self.error_categories:
            diagnostics.append({
                "level": "critical",
                "issue": "连接错误",
                "description": "无法连接到服务器，可能是502错误",
                "suggestions": [
                    "在Zeabur控制台检查服务状态（应该是 'Running'）",
                    "查看服务日志，查找启动错误",
                    "确认服务端口配置正确",
                    "检查环境变量是否正确配置",
                    "如果服务刚部署，等待1-2分钟让服务完全启动"
                ]
            })
        
        # 检查超时错误
        if "timeout" in self.error_categories:
            diagnostics.append({
                "level": "warning",
                "issue": "请求超时",
                "description": "某些端点响应超时（超过10秒）",
                "suggestions": [
                    "检查服务是否负载过高",
                    "查看服务日志，查找性能问题",
                    "检查数据库连接是否正常",
                    "考虑增加服务资源"
                ]
            })
        
        # 检查数据库连接
        health_info = self.results.get("health_info", {})
        if health_info:
            db_check = health_info.get("checks", {}).get("database", {})
            if db_check.get("status") != "healthy":
                diagnostics.append({
                    "level": "critical",
                    "issue": "数据库连接失败",
                    "description": db_check.get("message", "数据库连接异常"),
                    "suggestions": [
                        "在Zeabur控制台检查PostgreSQL服务状态",
                        "确认PostgreSQL服务已连接到应用服务",
                        "检查 DATABASE_URL 环境变量是否正确",
                        "在Zeabur终端运行数据库连接测试",
                        "查看应用日志中的数据库错误信息"
                    ]
                })
        
        # 检查API配置
        if health_info:
            api_check = health_info.get("checks", {}).get("api_config", {})
            if api_check.get("status") != "healthy":
                diagnostics.append({
                    "level": "warning",
                    "issue": "API配置问题",
                    "description": api_check.get("message", "API配置异常"),
                    "suggestions": [
                        "检查必需的环境变量是否已配置",
                        "确认 FACEBOOK_ACCESS_TOKEN 已设置",
                        "确认 OPENAI_API_KEY 已设置",
                        "确认 TELEGRAM_BOT_TOKEN 已设置"
                    ]
                })
        
        # 检查资源使用
        if health_info:
            resource_check = health_info.get("checks", {}).get("resources", {})
            if resource_check.get("status") == "degraded":
                metrics = resource_check.get("metrics", {})
                warnings = []
                if metrics.get("cpu_percent", 0) > 90:
                    warnings.append(f"CPU使用率过高: {metrics.get('cpu_percent')}%")
                if metrics.get("memory_percent", 0) > 90:
                    warnings.append(f"内存使用率过高: {metrics.get('memory_percent')}%")
                if metrics.get("disk_percent", 0) > 90:
                    warnings.append(f"磁盘使用率过高: {metrics.get('disk_percent')}%")
                
                if warnings:
                    diagnostics.append({
                        "level": "warning",
                        "issue": "资源使用率过高",
                        "description": "; ".join(warnings),
                        "suggestions": [
                            "考虑升级服务资源配置",
                            "检查是否有内存泄漏",
                            "优化应用性能",
                            "清理不必要的日志文件"
                        ]
                    })
        
        # 检查性能指标
        metrics_info = self.results.get("metrics_info", {})
        if metrics_info:
            error_rate = metrics_info.get("error_rate_percent", 0)
            if error_rate > 5:
                diagnostics.append({
                    "level": "warning",
                    "issue": "错误率过高",
                    "description": f"错误率达到 {error_rate}%",
                    "suggestions": [
                        "查看服务日志，查找错误原因",
                        "检查API配置是否正确",
                        "检查数据库连接是否稳定",
                        "监控错误趋势"
                    ]
                })
            
            avg_response_time = metrics_info.get("avg_response_time_ms", 0)
            if avg_response_time > 1000:
                diagnostics.append({
                    "level": "warning",
                    "issue": "响应时间过长",
                    "description": f"平均响应时间 {avg_response_time}ms",
                    "suggestions": [
                        "优化数据库查询",
                        "检查API调用性能",
                        "考虑使用缓存",
                        "检查网络延迟"
                    ]
                })
        
        # 检查部署状态
        deployment_info = self.results.get("deployment_info", {})
        if deployment_info:
            pages_info = deployment_info.get("pages", {})
            if pages_info.get("total", 0) == 0:
                diagnostics.append({
                    "level": "info",
                    "issue": "未配置页面",
                    "description": "没有配置任何Facebook页面",
                    "suggestions": [
                        "访问 /admin/deployment/sync-pages 同步页面",
                        "确认 FACEBOOK_ACCESS_TOKEN 有 pages_show_list 权限"
                    ]
                })
            
            token_info = deployment_info.get("token", {})
            if not token_info.get("default_token_configured", False):
                diagnostics.append({
                    "level": "warning",
                    "issue": "未配置Token",
                    "description": "未配置默认Token",
                    "suggestions": [
                        "确认 FACEBOOK_ACCESS_TOKEN 环境变量已设置",
                        "检查Token是否有效"
                    ]
                })
        
        self.results["diagnostics"] = diagnostics
    
    def _generate_summary(self):
        """生成总结"""
        total = len(self.results["checks"])
        success = sum(1 for r in self.results["checks"].values() if r["status"] == "success")
        failed = sum(1 for r in self.results["checks"].values() if r["status"] == "failed")
        errors = sum(1 for r in self.results["checks"].values() if r["status"] in ["error", "timeout", "connection_error"])
        
        self.results["summary"] = {
            "total_checks": total,
            "successful": success,
            "failed": failed,
            "errors": errors,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0
        }
    
    def _print_summary(self):
        """打印总结"""
        summary = self.results["summary"]
        
        print(f"\n{'='*60}")
        print("📊 检查总结")
        print(f"{'='*60}\n")
        
        print(f"总计: {summary['total_checks']} 个检查")
        print(f"✅ 成功: {summary['successful']}")
        print(f"❌ 失败: {summary['failed']}")
        print(f"⚠️  错误: {summary['errors']}")
        print(f"📈 成功率: {summary['success_rate']}%")
        
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
        health_info = self.results.get("health_info", {})
        if health_info:
            db_check = health_info.get("checks", {}).get("database", {})
            if db_check:
                db_status = db_check.get("status", "unknown")
                status_icon = "✅" if db_status == "healthy" else "❌"
                print(f"{status_icon} 数据库连接: {db_status}")
                if db_check.get("response_time_ms"):
                    print(f"   响应时间: {db_check['response_time_ms']}ms")
        
        # 性能指标
        metrics_info = self.results.get("metrics_info", {})
        if metrics_info:
            print(f"\n{'='*60}")
            print("📈 性能指标")
            print(f"{'='*60}\n")
            print(f"请求总数: {metrics_info.get('request_count', 0)}")
            print(f"错误总数: {metrics_info.get('error_count', 0)}")
            print(f"错误率: {metrics_info.get('error_rate_percent', 0)}%")
            print(f"平均响应时间: {metrics_info.get('avg_response_time_ms', 0)}ms")
            print(f"P95响应时间: {metrics_info.get('p95_response_time_ms', 0)}ms")
            uptime_hours = metrics_info.get('uptime_seconds', 0) / 3600
            print(f"运行时间: {uptime_hours:.2f} 小时")
        
        # 资源使用
        health_info = self.results.get("health_info", {})
        if health_info:
            resource_check = health_info.get("checks", {}).get("resources", {})
            if resource_check.get("metrics"):
                metrics = resource_check["metrics"]
                print(f"\n{'='*60}")
                print("💻 资源使用")
                print(f"{'='*60}\n")
                print(f"CPU使用率: {metrics.get('cpu_percent', 0)}%")
                print(f"内存使用率: {metrics.get('memory_percent', 0)}%")
                print(f"磁盘使用率: {metrics.get('disk_percent', 0)}%")
        
        # 部署状态
        deployment_info = self.results.get("deployment_info", {})
        if deployment_info:
            print(f"\n{'='*60}")
            print("🚀 部署状态")
            print(f"{'='*60}\n")
            pages_info = deployment_info.get("pages", {})
            print(f"页面总数: {pages_info.get('total', 0)}")
            print(f"已启用: {pages_info.get('enabled', 0)}")
            print(f"已禁用: {pages_info.get('disabled', 0)}")
            token_info = deployment_info.get("token", {})
            token_status = "✅ 已配置" if token_info.get("default_token_configured") else "❌ 未配置"
            print(f"Token状态: {token_status}")
        
        # 错误统计
        errors = self.results.get("errors", {})
        if errors.get("total_errors", 0) > 0:
            print(f"\n{'='*60}")
            print("❌ 错误统计")
            print(f"{'='*60}\n")
            for category, count in errors.get("by_category", {}).items():
                category_name = {
                    "connection_error": "连接错误",
                    "timeout": "超时",
                    "failed": "失败",
                    "error": "错误"
                }.get(category, category)
                print(f"{category_name}: {count} 个")
        
        # 诊断建议
        diagnostics = self.results.get("diagnostics", [])
        if diagnostics:
            print(f"\n{'='*60}")
            print("🔍 诊断建议")
            print(f"{'='*60}\n")
            
            for diag in diagnostics:
                level_icon = {
                    "critical": "🔴",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }.get(diag["level"], "ℹ️")
                
                print(f"{level_icon} {diag['issue']}")
                print(f"   问题: {diag['description']}")
                print(f"   建议:")
                for suggestion in diag["suggestions"]:
                    print(f"     • {suggestion}")
                print()
        
        # 最终状态
        print(f"{'='*60}")
        if summary["success_rate"] == 100:
            print("🎉 所有检查都通过！服务运行正常！")
        elif summary["success_rate"] >= 80:
            print("⚠️  大部分检查通过，但有一些问题需要注意")
        else:
            print("❌ 有多个检查失败，请查看上面的诊断建议")
        print(f"{'='*60}\n")
    
    def save_report(self, filename: str = "zeabur_check_report.json"):
        """保存检查报告"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 检查报告已保存到: {filename}")
    
    def generate_html_report(self, filename: str = "zeabur_check_report.html"):
        """生成HTML格式的报告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zeabur部署检查报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .check-item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #ddd;
        }}
        .check-item.success {{
            background-color: #d4edda;
            border-left-color: #28a745;
        }}
        .check-item.failed {{
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }}
        .check-item.error {{
            background-color: #fff3cd;
            border-left-color: #ffc107;
        }}
        .diagnostic {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        .diagnostic.critical {{
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }}
        .diagnostic.warning {{
            background-color: #fff3cd;
            border-left-color: #ffc107;
        }}
        .diagnostic.info {{
            background-color: #d1ecf1;
            border-left-color: #17a2b8;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .badge-success {{
            background-color: #28a745;
            color: white;
        }}
        .badge-danger {{
            background-color: #dc3545;
            color: white;
        }}
        .badge-warning {{
            background-color: #ffc107;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Zeabur部署检查报告</h1>
        <p>检查时间: {self.results['timestamp']}</p>
        <p>检查目标: {self.results['base_url']}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>总检查数</h3>
            <div class="value">{self.results['summary']['total_checks']}</div>
        </div>
        <div class="summary-card">
            <h3>成功</h3>
            <div class="value" style="color: #28a745;">{self.results['summary']['successful']}</div>
        </div>
        <div class="summary-card">
            <h3>失败</h3>
            <div class="value" style="color: #dc3545;">{self.results['summary']['failed']}</div>
        </div>
        <div class="summary-card">
            <h3>成功率</h3>
            <div class="value">{self.results['summary']['success_rate']}%</div>
        </div>
    </div>
    
    <div class="section">
        <h2>检查详情</h2>
"""
        
        for key, check in self.results["checks"].items():
            status_class = {
                "success": "success",
                "failed": "failed",
                "error": "error",
                "timeout": "error",
                "connection_error": "error"
            }.get(check["status"], "error")
            
            status_badge = {
                "success": '<span class="badge badge-success">✅ 成功</span>',
                "failed": '<span class="badge badge-danger">❌ 失败</span>',
                "error": '<span class="badge badge-warning">⚠️ 错误</span>',
                "timeout": '<span class="badge badge-warning">⏱️ 超时</span>',
                "connection_error": '<span class="badge badge-warning">🔌 连接错误</span>'
            }.get(check["status"], '<span class="badge badge-warning">❓ 未知</span>')
            
            html += f"""
        <div class="check-item {status_class}">
            <strong>{check['name']}</strong> {status_badge}<br>
            <small>URL: {check['url']}</small><br>
"""
            if check.get("status_code"):
                html += f"            <small>状态码: {check['status_code']}</small><br>"
            if check.get("response_time_ms"):
                html += f"            <small>响应时间: {check['response_time_ms']}ms</small><br>"
            if check.get("error"):
                html += f"            <small>错误: {check['error']}</small><br>"
            html += "        </div>"
        
        html += """
    </div>
"""
        
        # 诊断建议
        diagnostics = self.results.get("diagnostics", [])
        if diagnostics:
            html += """
    <div class="section">
        <h2>诊断建议</h2>
"""
            for diag in diagnostics:
                level_class = diag["level"]
                html += f"""
        <div class="diagnostic {level_class}">
            <strong>{diag['issue']}</strong><br>
            <p>{diag['description']}</p>
            <strong>建议:</strong>
            <ul>
"""
                for suggestion in diag["suggestions"]:
                    html += f"                <li>{suggestion}</li>"
                html += """
            </ul>
        </div>
"""
            html += """
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📄 HTML报告已保存到: {filename}")


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
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="生成HTML格式的报告"
    )
    parser.add_argument(
        "--report-name",
        default="zeabur_check_report",
        help="报告文件名（不含扩展名，默认: zeabur_check_report）"
    )
    
    args = parser.parse_args()
    
    checker = ZeaburChecker(args.url)
    checker.check_all()
    
    if args.save_report:
        checker.save_report(f"{args.report_name}.json")
    
    if args.html_report:
        checker.generate_html_report(f"{args.report_name}.html")


if __name__ == "__main__":
    main()




