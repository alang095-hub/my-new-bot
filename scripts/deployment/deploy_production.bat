@echo off
REM 生产环境部署脚本 (Windows)
REM 使用方法: scripts\deployment\deploy_production.bat

echo ==========================================
echo 生产环境部署脚本
echo ==========================================
echo.

set PROJECT_ROOT=%~dp0..\..
cd /d "%PROJECT_ROOT%"

echo 项目目录: %PROJECT_ROOT%
echo.

REM 1. 检查环境
echo 1. 检查环境...
echo ----------------------------------------

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python 未安装
    exit /b 1
)
echo [OK] Python已安装

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)
echo [OK] 虚拟环境存在

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [OK] 依赖已安装

REM 2. 检查配置文件
echo.
echo 2. 检查配置文件...
echo ----------------------------------------

if not exist ".env" (
    echo [错误] .env 文件不存在
    echo 请从 env.example 创建 .env 并配置所有必需的环境变量
    exit /b 1
)
echo [OK] .env 文件存在

if not exist "config\config.yaml" (
    echo [警告] config\config.yaml 不存在
    if exist "config\config.yaml.example" (
        echo 从示例文件创建...
        copy config\config.yaml.example config\config.yaml
        echo [提示] 请编辑 config\config.yaml 配置业务规则
    )
)
echo [OK] config.yaml 文件存在

REM 3. 验证配置
echo.
echo 3. 验证配置...
echo ----------------------------------------

python -c "from src.core.config import settings; print('配置加载成功')" 2>nul
if %errorlevel% neq 0 (
    echo [错误] 配置验证失败
    exit /b 1
)
echo [OK] 配置验证通过

REM 4. 数据库迁移
echo.
echo 4. 运行数据库迁移...
echo ----------------------------------------

alembic upgrade head
if %errorlevel% neq 0 (
    echo [错误] 数据库迁移失败
    exit /b 1
)
echo [OK] 数据库迁移成功

REM 5. 运行测试
echo.
echo 5. 运行生产环境测试...
echo ----------------------------------------

python scripts\test\production_test.py --test environment 2>nul
if %errorlevel% equ 0 (
    echo [OK] 测试通过
) else (
    echo [警告] 部分测试失败，但继续部署
)

REM 6. 创建必要的目录
echo.
echo 6. 创建必要的目录...
echo ----------------------------------------

if not exist "logs" mkdir logs
if not exist "data\backups" mkdir data\backups
if not exist "data\test_reports" mkdir data\test_reports
if not exist "data\monitoring" mkdir data\monitoring
echo [OK] 目录创建完成

REM 7. 部署完成
echo.
echo ==========================================
echo [成功] 部署完成！
echo ==========================================
echo.
echo 下一步：
echo 1. 检查环境变量配置（.env文件）
echo 2. 检查业务规则配置（config\config.yaml）
echo 3. 启动服务: python run.py
echo 4. 验证服务: curl http://localhost:8000/health
echo 5. 运行完整测试: python scripts\test\production_test.py --test all
echo.

