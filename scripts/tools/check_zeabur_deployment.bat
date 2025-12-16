@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 🔍 Zeabur部署状态检查
echo ========================================
echo.

set BASE_URL=https://my-telegram-bot33.zeabur.app
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%check_zeabur_deployment.py

echo 正在检查: %BASE_URL%
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python
    echo.
    echo 将使用curl进行基础检查...
    echo.
    goto :basic_check
)

REM 检查httpx是否安装
python -c "import httpx" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告: httpx未安装，正在尝试安装...
    pip install httpx >nul 2>&1
    if errorlevel 1 (
        echo ❌ 无法安装httpx，将使用curl进行基础检查...
        echo.
        goto :basic_check
    )
)

REM 使用Python脚本进行详细检查
echo 使用Python脚本进行详细检查...
echo.
python "%PYTHON_SCRIPT%" --url "%BASE_URL%" --save-report --html-report
if errorlevel 1 (
    echo.
    echo ❌ Python脚本执行失败，将使用curl进行基础检查...
    echo.
    goto :basic_check
) else (
    echo.
    echo ✅ 检查完成！报告已保存。
    echo.
    goto :end
)

:basic_check
echo ========================================
echo 基础检查（使用curl）
echo ========================================
echo.

echo 1️⃣  检查简单健康检查端点...
curl -s -o nul -w "状态码: %%{http_code}\n" "%BASE_URL%/health/simple" 2>nul
if errorlevel 1 (
    echo    ❌ 无法连接（可能是502错误）
    set ERROR_COUNT=1
) else (
    echo    ✅ 可以访问
)
echo.

echo 2️⃣  检查完整健康检查端点...
curl -s -o nul -w "状态码: %%{http_code}\n" "%BASE_URL%/health" 2>nul
if errorlevel 1 (
    echo    ❌ 无法连接
    set /a ERROR_COUNT+=1
) else (
    echo    ✅ 可以访问
)
echo.

echo 3️⃣  检查根路径...
curl -s -o nul -w "状态码: %%{http_code}\n" "%BASE_URL%/" 2>nul
if errorlevel 1 (
    echo    ❌ 无法连接
    set /a ERROR_COUNT+=1
) else (
    echo    ✅ 可以访问
)
echo.

echo 4️⃣  检查API文档...
curl -s -o nul -w "状态码: %%{http_code}\n" "%BASE_URL%/docs" 2>nul
if errorlevel 1 (
    echo    ❌ 无法连接
    set /a ERROR_COUNT+=1
) else (
    echo    ✅ 可以访问
)
echo.

if defined ERROR_COUNT (
    echo ⚠️  检测到 %ERROR_COUNT% 个连接错误
    echo.
)

echo ========================================
echo 📋 手动检查清单
echo ========================================
echo.
echo 请在Zeabur控制台检查以下项目：
echo.
echo 1. 服务状态
echo    - 访问: https://zeabur.com
echo    - 找到项目: my-telegram-bot33
echo    - 查看应用服务状态（应该是 Running）
echo.
echo 2. 环境变量配置
echo    - 在应用服务设置中，检查以下环境变量：
echo      ✅ DATABASE_URL（如果使用Zeabur的PostgreSQL，会自动设置）
echo      ✅ FACEBOOK_APP_ID
echo      ✅ FACEBOOK_APP_SECRET
echo      ✅ FACEBOOK_ACCESS_TOKEN
echo      ✅ FACEBOOK_VERIFY_TOKEN
echo      ✅ OPENAI_API_KEY
echo      ✅ TELEGRAM_BOT_TOKEN
echo      ✅ TELEGRAM_CHAT_ID
echo      ✅ SECRET_KEY
echo      ✅ DEBUG=false
echo.
echo 3. PostgreSQL服务
echo    - 确认PostgreSQL服务已添加
echo    - 确认服务状态是 Running
echo    - 确认已连接到应用服务
echo.
echo 4. 服务日志
echo    - 在应用服务页面，找到 Logs 标签
echo    - 查看最新的日志信息
echo    - 查找错误信息（ERROR/Exception）
echo.
echo ========================================
echo.
echo 💡 提示: 如果Python和httpx已安装，可以使用以下命令进行详细检查：
echo    python "%PYTHON_SCRIPT%" --url "%BASE_URL%" --save-report --html-report
echo.

:end
echo 按任意键退出...
pause >nul




