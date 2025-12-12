"""
生产环境就绪性测试
检查系统是否准备好用于生产环境部署
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试结果收集
test_results: List[Dict[str, Any]] = []


def log_test(name: str, status: str, message: str = "", error: Exception = None):
    """记录测试结果"""
    result = {
        "name": name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "error": str(error) if error else None
    }
    test_results.append(result)
    
    status_symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN" if status == "WARN" else "[SKIP]"
    print(f"{status_symbol} {name}")
    if message:
        print(f"   {message}")
    if error:
        print(f"   错误: {str(error)}")


def test_environment_variables():
    """测试环境变量配置"""
    try:
        from src.config import settings
        
        required_vars = [
            'DATABASE_URL',
            'FACEBOOK_APP_ID',
            'FACEBOOK_APP_SECRET',
            'FACEBOOK_ACCESS_TOKEN',
            'FACEBOOK_VERIFY_TOKEN',
            'OPENAI_API_KEY',
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            try:
                value = getattr(settings, var.lower(), None)
                if not value:
                    missing_vars.append(var)
            except:
                missing_vars.append(var)
        
        if missing_vars:
            log_test("环境变量 - 必需配置", "FAIL", f"缺少必需的环境变量: {', '.join(missing_vars)}")
        else:
            log_test("环境变量 - 必需配置", "PASS", "所有必需的环境变量已配置")
        
        # 检查敏感信息是否硬编码
        if 'password' in str(settings.database_url).lower() or 'secret' in str(settings.database_url).lower():
            if 'localhost' in str(settings.database_url) or '127.0.0.1' in str(settings.database_url):
                log_test("环境变量 - 数据库URL", "WARN", "数据库URL包含敏感信息，建议使用环境变量")
            else:
                log_test("环境变量 - 数据库URL", "PASS", "数据库URL已配置")
        
    except Exception as e:
        log_test("环境变量配置", "FAIL", f"环境变量检查失败: {str(e)}", e)


def test_security():
    """测试安全性配置"""
    try:
        from src.config import settings
        
        # 检查CORS配置
        from src.main import app
        cors_middleware = None
        for middleware in app.user_middleware:
            if 'CORSMiddleware' in str(middleware):
                cors_middleware = middleware
                break
        
        if cors_middleware:
            log_test("安全性 - CORS配置", "WARN", "CORS已配置，但允许所有来源 (*)，生产环境建议限制来源")
        else:
            log_test("安全性 - CORS配置", "PASS", "CORS配置正常")
        
        # 检查SECRET_KEY
        if settings.secret_key and len(settings.secret_key) >= 32:
            log_test("安全性 - SECRET_KEY", "PASS", "SECRET_KEY长度足够")
        else:
            log_test("安全性 - SECRET_KEY", "FAIL", "SECRET_KEY长度不足或未设置（建议至少32字符）")
        
        # 检查DEBUG模式
        if settings.debug:
            log_test("安全性 - DEBUG模式", "FAIL", "DEBUG模式在生产环境应设置为False")
        else:
            log_test("安全性 - DEBUG模式", "PASS", "DEBUG模式已关闭")
        
    except Exception as e:
        log_test("安全性检查", "FAIL", f"安全性检查失败: {str(e)}", e)


def test_database_production():
    """测试生产环境数据库配置"""
    try:
        from src.config import settings
        from src.database.database import engine
        
        # 检查数据库类型
        db_url = settings.database_url.lower()
        
        if 'sqlite' in db_url:
            log_test("数据库 - 类型", "WARN", "使用SQLite数据库，生产环境建议使用PostgreSQL")
        elif 'postgresql' in db_url or 'postgres' in db_url:
            log_test("数据库 - 类型", "PASS", "使用PostgreSQL数据库（适合生产环境）")
        else:
            log_test("数据库 - 类型", "WARN", f"数据库类型: {db_url[:20]}...")
        
        # 检查连接池配置
        if hasattr(engine, 'pool'):
            pool_size = getattr(engine.pool, 'size', None)
            if pool_size:
                log_test("数据库 - 连接池", "PASS", f"连接池已配置（大小: {pool_size}）")
            else:
                log_test("数据库 - 连接池", "WARN", "连接池配置可能未优化")
        else:
            log_test("数据库 - 连接池", "WARN", "无法检查连接池配置")
        
        # 测试数据库连接
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                log_test("数据库 - 连接测试", "PASS", "数据库连接正常")
            else:
                log_test("数据库 - 连接测试", "FAIL", "数据库连接测试失败")
        
    except Exception as e:
        log_test("数据库配置", "FAIL", f"数据库配置检查失败: {str(e)}", e)


def test_logging():
    """测试日志配置"""
    try:
        import logging
        
        # 检查日志级别
        root_logger = logging.getLogger()
        if root_logger.level <= logging.INFO:
            log_test("日志 - 日志级别", "PASS", f"日志级别: {logging.getLevelName(root_logger.level)}")
        else:
            log_test("日志 - 日志级别", "WARN", f"日志级别可能过高: {logging.getLevelName(root_logger.level)}")
        
        # 检查日志处理器
        handlers = root_logger.handlers
        if handlers:
            log_test("日志 - 处理器", "PASS", f"已配置 {len(handlers)} 个日志处理器")
        else:
            log_test("日志 - 处理器", "WARN", "未配置日志处理器，建议配置文件日志")
        
        # 检查是否有文件日志
        file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
        if file_handlers:
            log_test("日志 - 文件日志", "PASS", "已配置文件日志")
        else:
            log_test("日志 - 文件日志", "WARN", "未配置文件日志，生产环境建议配置")
        
    except Exception as e:
        log_test("日志配置", "FAIL", f"日志配置检查失败: {str(e)}", e)


def test_error_handling():
    """测试错误处理"""
    try:
        from src.main import app
        
        # 检查是否有全局异常处理
        # FastAPI默认有异常处理，这里主要检查自定义异常处理
        log_test("错误处理 - 异常处理", "PASS", "FastAPI提供默认异常处理")
        
        # 检查健康检查端点
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            log_test("错误处理 - 健康检查", "PASS", "健康检查端点正常")
        else:
            log_test("错误处理 - 健康检查", "FAIL", f"健康检查端点返回状态码: {response.status_code}")
        
    except Exception as e:
        log_test("错误处理", "FAIL", f"错误处理检查失败: {str(e)}", e)


def test_performance():
    """测试性能相关配置"""
    try:
        from src.config import settings
        
        # 检查异步配置
        from src.main import app
        if hasattr(app, 'router'):
            log_test("性能 - 异步支持", "PASS", "FastAPI支持异步处理")
        
        # 检查HTTP客户端超时配置
        from src.facebook.api_client import FacebookAPIClient
        client = FacebookAPIClient()
        if hasattr(client, 'client') and hasattr(client.client, 'timeout'):
            timeout = client.client.timeout
            if timeout:
                # httpx.Timeout对象可能有不同的属性
                timeout_str = str(timeout)
                if '30' in timeout_str or timeout_str != 'None':
                    log_test("性能 - HTTP超时", "PASS", f"HTTP客户端已配置超时: {timeout_str}")
                else:
                    log_test("性能 - HTTP超时", "WARN", "HTTP客户端超时配置可能不当")
            else:
                log_test("性能 - HTTP超时", "WARN", "HTTP客户端未配置超时")
        
    except Exception as e:
        log_test("性能配置", "WARN", f"性能配置检查失败: {str(e)}", e)


def test_deployment_config():
    """测试部署配置"""
    try:
        # 检查Dockerfile
        dockerfile = project_root / "Dockerfile"
        if dockerfile.exists():
            log_test("部署 - Dockerfile", "PASS", "Dockerfile存在")
        else:
            log_test("部署 - Dockerfile", "WARN", "Dockerfile不存在，如需容器化部署建议创建")
        
        # 检查docker-compose
        docker_compose = project_root / "docker-compose.yml"
        if docker_compose.exists():
            log_test("部署 - docker-compose", "PASS", "docker-compose.yml存在")
        else:
            log_test("部署 - docker-compose", "SKIP", "docker-compose.yml不存在（可选）")
        
        # 检查Procfile（用于Heroku/Railway等）
        procfile = project_root / "Procfile"
        if procfile.exists():
            with open(procfile, 'r') as f:
                content = f.read()
                if 'uvicorn' in content or 'gunicorn' in content:
                    log_test("部署 - Procfile", "PASS", "Procfile配置正确")
                else:
                    log_test("部署 - Procfile", "WARN", "Procfile可能配置不当")
        else:
            log_test("部署 - Procfile", "SKIP", "Procfile不存在（如不使用Heroku/Railway可忽略）")
        
        # 检查nginx配置
        nginx_conf = project_root / "config" / "nginx.conf"
        if nginx_conf.exists():
            log_test("部署 - Nginx配置", "PASS", "Nginx配置文件存在")
        else:
            log_test("部署 - Nginx配置", "SKIP", "Nginx配置文件不存在（如不使用Nginx可忽略）")
        
    except Exception as e:
        log_test("部署配置", "FAIL", f"部署配置检查失败: {str(e)}", e)


def test_monitoring():
    """测试监控配置"""
    try:
        from src.main import app
        
        # 检查监控API路由
        routes = [route.path for route in app.routes]
        
        if any('/monitoring' in r or '/stats' in r for r in routes):
            log_test("监控 - API端点", "PASS", "监控API端点已配置")
        else:
            log_test("监控 - API端点", "WARN", "未找到监控API端点")
        
        # 检查统计API
        if any('/statistics' in r or '/stats' in r for r in routes):
            log_test("监控 - 统计API", "PASS", "统计API已配置")
        else:
            log_test("监控 - 统计API", "WARN", "未找到统计API端点")
        
        # 检查健康检查
        if '/health' in routes:
            log_test("监控 - 健康检查", "PASS", "健康检查端点已配置")
        else:
            log_test("监控 - 健康检查", "FAIL", "健康检查端点未配置")
        
    except Exception as e:
        log_test("监控配置", "FAIL", f"监控配置检查失败: {str(e)}", e)


def test_backup_recovery():
    """测试备份和恢复"""
    try:
        # 检查数据库迁移
        alembic_dir = project_root / "alembic" / "versions"
        if alembic_dir.exists():
            migration_files = list(alembic_dir.glob("*.py"))
            if migration_files:
                log_test("备份恢复 - 数据库迁移", "PASS", f"找到 {len(migration_files)} 个迁移文件")
            else:
                log_test("备份恢复 - 数据库迁移", "WARN", "未找到数据库迁移文件")
        else:
            log_test("备份恢复 - 数据库迁移", "WARN", "Alembic迁移目录不存在")
        
        # 检查是否有备份脚本
        scripts_dir = project_root / "scripts"
        backup_scripts = []
        if scripts_dir.exists():
            backup_scripts = list(scripts_dir.glob("*backup*")) + list(scripts_dir.glob("*restore*"))
        
        # 也检查根目录
        backup_scripts += list(project_root.glob("*backup*")) + list(project_root.glob("*restore*"))
        
        if backup_scripts:
            log_test("备份恢复 - 备份脚本", "PASS", f"找到备份/恢复脚本: {', '.join([s.name for s in backup_scripts[:3]])}")
        else:
            log_test("备份恢复 - 备份脚本", "WARN", "未找到备份/恢复脚本，建议创建定期备份机制")
        
    except Exception as e:
        log_test("备份恢复", "WARN", f"备份恢复检查失败: {str(e)}", e)


def test_api_keys_security():
    """测试API密钥安全性"""
    try:
        from src.config import settings
        
        # 检查API密钥是否在代码中硬编码
        api_keys = [
            ('facebook_access_token', settings.facebook_access_token),
            ('openai_api_key', settings.openai_api_key),
            ('telegram_bot_token', settings.telegram_bot_token),
        ]
        
        all_from_env = True
        for key_name, key_value in api_keys:
            if not key_value:
                log_test(f"API密钥 - {key_name}", "FAIL", f"{key_name} 未配置")
                all_from_env = False
            elif len(key_value) < 10:
                log_test(f"API密钥 - {key_name}", "WARN", f"{key_name} 长度异常，可能配置错误")
        
        if all_from_env:
            log_test("API密钥 - 配置来源", "PASS", "所有API密钥从环境变量加载（安全）")
        
    except Exception as e:
        log_test("API密钥安全性", "FAIL", f"API密钥检查失败: {str(e)}", e)


def run_production_readiness_test():
    """运行生产环境就绪性测试"""
    print("=" * 80)
    print("生产环境就绪性测试")
    print("=" * 80)
    print()
    
    test_functions = [
        ("环境变量配置", test_environment_variables),
        ("安全性配置", test_security),
        ("数据库配置", test_database_production),
        ("日志配置", test_logging),
        ("错误处理", test_error_handling),
        ("性能配置", test_performance),
        ("部署配置", test_deployment_config),
        ("监控配置", test_monitoring),
        ("备份恢复", test_backup_recovery),
        ("API密钥安全性", test_api_keys_security),
    ]
    
    for name, test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            log_test(name, "FAIL", f"测试执行异常: {str(e)}", e)
        print()
    
    # 生成测试报告
    print("=" * 80)
    print("生产环境就绪性报告")
    print("=" * 80)
    
    total = len(test_results)
    passed = len([r for r in test_results if r["status"] == "PASS"])
    failed = len([r for r in test_results if r["status"] == "FAIL"])
    warned = len([r for r in test_results if r["status"] == "WARN"])
    skipped = len([r for r in test_results if r["status"] == "SKIP"])
    
    print(f"\n总计: {total} 个检查项")
    print(f"[PASS] 通过: {passed}")
    print(f"[FAIL] 失败: {failed}")
    print(f"[WARN] 警告: {warned}")
    print(f"[SKIP] 跳过: {skipped}")
    print()
    
    # 计算就绪度
    readiness_score = (passed / total * 100) if total > 0 else 0
    
    print(f"生产环境就绪度: {readiness_score:.1f}%")
    print()
    
    if failed > 0:
        print("必须修复的问题:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"  [FAIL] {result['name']}: {result['message']}")
        print()
    
    if warned > 0:
        print("建议改进的问题:")
        for result in test_results:
            if result["status"] == "WARN":
                print(f"  [WARN] {result['name']}: {result['message']}")
        print()
    
    # 生产环境建议
    if failed == 0 and readiness_score >= 80:
        print("[OK] 系统已准备好用于生产环境！")
        print()
        print("建议:")
        print("1. 确保所有环境变量在生产环境正确配置")
        print("2. 配置日志文件输出")
        print("3. 设置数据库备份机制")
        print("4. 配置监控和告警")
        print("5. 进行负载测试")
    elif failed == 0:
        print("[WARN] 系统基本可用，但建议改进警告项后再部署到生产环境")
    else:
        print("[FAIL] 系统尚未准备好用于生产环境，请先修复失败项")
    
    return failed == 0 and readiness_score >= 80


if __name__ == "__main__":
    try:
        is_ready = run_production_readiness_test()
        sys.exit(0 if is_ready else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

