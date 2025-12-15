"""
部署准备检查脚本
检查所有部署前的准备工作是否完成
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 检查结果
check_results = []


def log_check(name: str, status: str, message: str = ""):
    """记录检查结果"""
    result = {
        "name": name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    check_results.append(result)
    
    status_symbol = {
        "PASS": "✅",
        "FAIL": "❌",
        "WARN": "⚠️",
        "SKIP": "⏭️"
    }.get(status, "❓")
    
    print(f"{status_symbol} {name}")
    if message:
        print(f"   {message}")


def check_git_status():
    """检查Git状态"""
    print("\n" + "="*60)
    print("Git状态检查")
    print("="*60)
    
    try:
        # 检查是否在Git仓库中
        result = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode != 0:
            log_check("Git仓库", "FAIL", "不在Git仓库中或Git未安装")
            return False
        
        # 检查是否有未提交的更改
        if "Changes not staged for commit" in result.stdout or "Untracked files" in result.stdout:
            log_check("未提交的更改", "WARN", "有未提交的更改，建议先提交")
        else:
            log_check("未提交的更改", "PASS", "所有更改已提交")
        
        # 检查远程仓库
        remote_result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if remote_result.returncode == 0 and remote_result.stdout.strip():
            log_check("远程仓库", "PASS", "已配置远程仓库")
            print(f"   远程仓库: {remote_result.stdout.strip()}")
        else:
            log_check("远程仓库", "WARN", "未配置远程仓库（Zeabur需要GitHub仓库）")
        
        return True
    except FileNotFoundError:
        log_check("Git", "FAIL", "Git未安装")
        return False
    except Exception as e:
        log_check("Git状态", "FAIL", f"检查失败: {str(e)}")
        return False


def check_required_files():
    """检查必需文件"""
    print("\n" + "="*60)
    print("必需文件检查")
    print("="*60)
    
    required_files = [
        ("requirements.txt", "Python依赖文件"),
        ("src/main.py", "主应用文件"),
        ("alembic.ini", "数据库迁移配置"),
        ("Dockerfile", "Docker配置文件（可选）"),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            log_check(f"文件: {description}", "PASS", f"{file_path}")
        else:
            if file_path == "Dockerfile":
                log_check(f"文件: {description}", "WARN", f"{file_path} 不存在（Zeabur会自动检测）")
            else:
                log_check(f"文件: {description}", "FAIL", f"{file_path} 不存在")
                all_exist = False
    
    return all_exist


def check_dependencies():
    """检查依赖包"""
    print("\n" + "="*60)
    print("依赖包检查")
    print("="*60)
    
    required_modules = {
        "sqlalchemy": "SQLAlchemy",
        "pydantic": "Pydantic",
        "fastapi": "FastAPI",
        "httpx": "HTTPX",
        "uvicorn": "Uvicorn",
    }
    
    missing = []
    for module_name, display_name in required_modules.items():
        try:
            __import__(module_name)
            log_check(f"依赖: {display_name}", "PASS")
        except ImportError:
            log_check(f"依赖: {display_name}", "FAIL", f"{module_name} 未安装")
            missing.append(module_name)
    
    if missing:
        print(f"\n缺少的依赖: {', '.join(missing)}")
        print("安装命令: pip install " + " ".join(missing))
        return False
    
    return True


def check_environment_variables():
    """检查环境变量配置"""
    print("\n" + "="*60)
    print("环境变量检查")
    print("="*60)
    
    # 检查是否有.env文件
    env_file = project_root / ".env"
    env_example = project_root / "env.example"
    
    if env_file.exists():
        log_check(".env文件", "PASS", ".env文件存在")
    else:
        log_check(".env文件", "WARN", ".env文件不存在（部署时需要在Zeabur配置）")
    
    if env_example.exists():
        log_check("env.example", "PASS", "环境变量模板存在")
    else:
        log_check("env.example", "WARN", "环境变量模板不存在")
    
    # 检查必需的环境变量（仅提示，不要求本地必须有）
    required_vars = [
        "DATABASE_URL",
        "FACEBOOK_ACCESS_TOKEN",
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "SECRET_KEY",
    ]
    
    print("\n部署时需要配置的环境变量:")
    for var in required_vars:
        if os.getenv(var):
            log_check(f"环境变量: {var}", "PASS", "已配置（本地）")
        else:
            log_check(f"环境变量: {var}", "WARN", "需要在Zeabur配置")
    
    return True


def check_database_migrations():
    """检查数据库迁移"""
    print("\n" + "="*60)
    print("数据库迁移检查")
    print("="*60)
    
    alembic_dir = project_root / "alembic" / "versions"
    if alembic_dir.exists():
        migration_files = list(alembic_dir.glob("*.py"))
        if migration_files:
            log_check("迁移文件", "PASS", f"找到 {len(migration_files)} 个迁移文件")
        else:
            log_check("迁移文件", "WARN", "迁移目录存在但没有迁移文件")
    else:
        log_check("迁移目录", "WARN", "alembic/versions 目录不存在")
    
    return True


def check_code_quality():
    """检查代码质量"""
    print("\n" + "="*60)
    print("代码质量检查")
    print("="*60)
    
    # 检查是否有明显的语法错误
    try:
        import src.main
        log_check("主模块导入", "PASS", "src/main.py 可以正常导入")
    except Exception as e:
        log_check("主模块导入", "FAIL", f"导入失败: {str(e)}")
        return False
    
    # 检查关键模块
    key_modules = [
        "src.core.config",
        "src.core.database.connection",
    ]
    
    for module_name in key_modules:
        try:
            __import__(module_name)
            log_check(f"模块: {module_name}", "PASS")
        except Exception as e:
            log_check(f"模块: {module_name}", "FAIL", f"导入失败: {str(e)}")
            return False
    
    return True


def check_test_status():
    """检查测试状态"""
    print("\n" + "="*60)
    print("测试状态检查")
    print("="*60)
    
    test_script = project_root / "scripts" / "test" / "simple_local_test.py"
    if test_script.exists():
        log_check("测试脚本", "PASS", "测试脚本存在")
        print("\n建议运行测试:")
        print("  python scripts/test/simple_local_test.py")
    else:
        log_check("测试脚本", "WARN", "测试脚本不存在")
    
    return True


def generate_deployment_checklist():
    """生成部署检查清单"""
    print("\n" + "="*60)
    print("部署检查清单")
    print("="*60)
    
    checklist = [
        ("代码已推送到GitHub", "确保代码在GitHub仓库中"),
        ("Zeabur账号已创建", "访问 https://zeabur.com 注册账号"),
        ("环境变量已准备", "准备所有必需的环境变量"),
        ("PostgreSQL数据库已添加", "在Zeabur项目中添加PostgreSQL服务"),
        ("Webhook URL已配置", "在Facebook开发者控制台配置Webhook"),
        ("数据库迁移已运行", "在Zeabur终端运行: alembic upgrade head"),
    ]
    
    print("\n部署前检查项:")
    for i, (item, description) in enumerate(checklist, 1):
        print(f"{i}. {item}")
        print(f"   {description}")
    
    return True


def print_summary():
    """打印检查摘要"""
    print("\n" + "="*60)
    print("检查摘要")
    print("="*60)
    
    total = len(check_results)
    passed = sum(1 for r in check_results if r["status"] == "PASS")
    failed = sum(1 for r in check_results if r["status"] == "FAIL")
    warned = sum(1 for r in check_results if r["status"] == "WARN")
    skipped = sum(1 for r in check_results if r["status"] == "SKIP")
    
    print(f"总计: {total}")
    print(f"✅ 通过: {passed} ({passed/total*100:.1f}%)")
    print(f"❌ 失败: {failed} ({failed/total*100:.1f}%)")
    print(f"⚠️ 警告: {warned} ({warned/total*100:.1f}%)")
    print(f"⏭️ 跳过: {skipped} ({skipped/total*100:.1f}%)")
    
    if failed > 0:
        print("\n失败的检查:")
        for result in check_results:
            if result["status"] == "FAIL":
                print(f"  - {result['name']}: {result.get('message', '')}")
    
    print("\n" + "="*60)
    
    # 总体评估
    if failed == 0:
        print("\n🎉 所有检查通过！可以开始部署！")
        print("\n下一步:")
        print("1. 确保代码已推送到GitHub")
        print("2. 访问 https://zeabur.com 创建项目")
        print("3. 按照部署指南操作")
        print("4. 参考: docs/deployment/BEGINNER_DEPLOYMENT_GUIDE.md")
        return 0
    else:
        print("\n⚠️ 有检查失败，请先解决这些问题再部署。")
        return 1


def main():
    """主检查函数"""
    print("="*60)
    print("部署准备检查")
    print("="*60)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目路径: {project_root}")
    print()
    
    # 运行所有检查
    check_git_status()
    check_required_files()
    check_dependencies()
    check_environment_variables()
    check_database_migrations()
    check_code_quality()
    check_test_status()
    generate_deployment_checklist()
    
    # 打印摘要
    exit_code = print_summary()
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

