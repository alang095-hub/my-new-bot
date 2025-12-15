"""
依赖检查脚本
检查项目依赖是否已安装，并提供安装建议
"""
import sys
import subprocess
from pathlib import Path

def check_module(module_name):
    """检查模块是否已安装"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def get_pip_command():
    """获取pip命令"""
    return [sys.executable, "-m", "pip"]

def main():
    print("="*60)
    print("依赖检查工具")
    print("="*60)
    print()
    
    # 检查关键依赖
    required_modules = {
        "sqlalchemy": "SQLAlchemy",
        "pydantic": "Pydantic",
        "pydantic_settings": "Pydantic Settings",
        "fastapi": "FastAPI",
        "httpx": "HTTPX",
        "uvicorn": "Uvicorn",
    }
    
    missing_modules = []
    installed_modules = []
    
    print("检查依赖包...")
    print("-" * 60)
    
    for module_name, display_name in required_modules.items():
        if check_module(module_name):
            print(f"✅ {display_name} ({module_name}) - 已安装")
            installed_modules.append(module_name)
        else:
            print(f"❌ {display_name} ({module_name}) - 未安装")
            missing_modules.append(module_name)
    
    print()
    print("="*60)
    print("检查结果")
    print("="*60)
    print(f"已安装: {len(installed_modules)}/{len(required_modules)}")
    print(f"未安装: {len(missing_modules)}/{len(required_modules)}")
    print()
    
    if missing_modules:
        print("缺少的依赖包:")
        for module in missing_modules:
            print(f"  - {module}")
        print()
        
        print("="*60)
        print("安装建议")
        print("="*60)
        print()
        print("方法1: 使用requirements.txt安装所有依赖")
        print("  python -m pip install -r requirements.txt")
        print()
        print("方法2: 逐个安装缺少的包")
        print(f"  python -m pip install {' '.join(missing_modules)}")
        print()
        print("方法3: 如果使用虚拟环境，先激活虚拟环境")
        print("  Windows PowerShell:")
        print("    .\\venv\\Scripts\\Activate.ps1")
        print("  Windows CMD:")
        print("    venv\\Scripts\\activate.bat")
        print("  Linux/Mac:")
        print("    source venv/bin/activate")
        print()
        
        # 尝试自动安装
        response = input("是否现在尝试安装缺少的依赖？(y/n): ").strip().lower()
        if response == 'y':
            print()
            print("正在安装依赖...")
            print("-" * 60)
            
            pip_cmd = get_pip_command()
            install_cmd = pip_cmd + ["install"] + missing_modules
            
            try:
                result = subprocess.run(
                    install_cmd,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    print("✅ 安装成功！")
                    print(result.stdout)
                else:
                    print("❌ 安装失败")
                    print(result.stderr)
                    print()
                    print("请手动运行以下命令:")
                    print(f"  {' '.join(install_cmd)}")
            except Exception as e:
                print(f"❌ 安装过程出错: {str(e)}")
                print()
                print("请手动运行以下命令:")
                print(f"  {' '.join(install_cmd)}")
    else:
        print("🎉 所有依赖已安装！")
        print()
        print("可以运行测试:")
        print("  python scripts/test/simple_local_test.py")
        print("  python scripts/test/local_test.py")
    
    print()
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

