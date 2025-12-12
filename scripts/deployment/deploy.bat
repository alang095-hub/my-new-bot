@echo off
REM Windows 快速部署脚本

echo 🚀 开始部署客户服务系统...

REM 检查 Python
python --version >nul 2>&1 || (
    echo ❌ Python 未安装
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 检查 .env 文件
if not exist ".env" (
    echo ⚠️  警告: .env 文件不存在
    echo 请创建 .env 文件并配置所有必需的环境变量
    exit /b 1
)

REM 检查 config/config.yaml
if not exist "config\config.yaml" (
    echo 📝 创建配置文件...
    if exist "config\config.yaml.example" (
        copy config\config.yaml.example config\config.yaml
        echo ✅ 已从 config\config.yaml.example 创建 config\config.yaml
        echo ⚠️  请编辑 config\config.yaml 配置业务规则
    ) else (
        echo ❌ config\config.yaml.example 不存在
        exit /b 1
    )
)

REM 测试配置
echo 🔍 测试配置...
python -c "from src.config import settings; print('✅ 配置加载成功')" || (
    echo ❌ 配置加载失败，请检查 .env 文件
    exit /b 1
)

REM 检查数据库连接
echo 🗄️  检查数据库连接...
python -c "from src.database.database import engine; engine.connect(); print('✅ 数据库连接成功')" || (
    echo ❌ 数据库连接失败，请检查 DATABASE_URL
    exit /b 1
)

REM 运行数据库迁移
echo 📊 运行数据库迁移...
alembic upgrade head || (
    echo ⚠️  数据库迁移失败，尝试直接创建表...
    python -c "from src.database.database import engine, Base; Base.metadata.create_all(bind=engine)"
)

echo ✅ 部署完成！
echo.
echo 启动服务:
echo   python run.py
echo.
echo 或使用 uvicorn:
echo   uvicorn src.main:app --host 0.0.0.0 --port 8000
echo.
echo 访问 API 文档: http://localhost:8000/docs

pause







