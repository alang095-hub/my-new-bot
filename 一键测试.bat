@echo off
chcp 65001 >nul
echo ========================================
echo    AI自动回复系统 - 一键测试
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo [2/3] 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 警告：依赖安装可能有问题，但继续尝试启动...
)
echo.

echo [3/3] 启动服务...
echo 服务将在 http://localhost:8000 启动
echo 按 Ctrl+C 可以停止服务
echo.
echo 测试方法：
echo   1. 浏览器打开: http://localhost:8000
echo   2. 查看API文档: http://localhost:8000/docs
echo   3. 健康检查: http://localhost:8000/health
echo.
echo ========================================
echo.

python -m src.main

pause
