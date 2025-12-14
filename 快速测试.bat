@echo off
chcp 65001 >nul
cls
echo ================================================================
echo           AI自动回复系统 - 快速测试工具
echo ================================================================
echo.

echo [步骤 1/4] 检查Python环境...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python
    echo    请安装Python 3.9或更高版本
    echo    下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo [步骤 2/4] 检查 .env 配置文件...
if not exist ".env" (
    echo ⚠ 警告：未找到 .env 文件
    echo    正在创建基本配置文件...
    (
        echo # 数据库配置 - 使用SQLite便于测试
        echo DATABASE_URL=sqlite:///./facebook_customer_service.db
        echo DATABASE_ECHO=false
        echo.
        echo # Facebook 配置 - 请填写真实值
        echo FACEBOOK_APP_ID=test_app_id
        echo FACEBOOK_APP_SECRET=test_app_secret
        echo FACEBOOK_ACCESS_TOKEN=test_access_token
        echo FACEBOOK_VERIFY_TOKEN=test_verify_token_123
        echo.
        echo # OpenAI 配置 - 请填写真实API密钥
        echo OPENAI_API_KEY=sk-test-key-please-replace
        echo OPENAI_MODEL=gpt-4o-mini
        echo OPENAI_TEMPERATURE=0.7
        echo.
        echo # Telegram 配置 - 请填写真实值
        echo TELEGRAM_BOT_TOKEN=test_bot_token
        echo TELEGRAM_CHAT_ID=test_chat_id
        echo.
        echo # 服务器配置
        echo HOST=0.0.0.0
        echo PORT=8000
        echo DEBUG=true
        echo.
        echo # 安全配置
        echo SECRET_KEY=test-secret-key-please-change-in-production
        echo ALGORITHM=HS256
    ) > .env
    echo ✅ 已创建 .env 文件（请根据需要修改配置）
) else (
    echo ✅ .env 文件存在
)
echo.

echo [步骤 3/4] 安装Python依赖...
echo    这可能需要几分钟...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ⚠ 警告：部分依赖安装失败，但继续尝试启动...
) else (
    echo ✅ 依赖安装完成
)
echo.

echo [步骤 4/4] 启动服务...
echo ================================================================
echo.
echo 🚀 服务正在启动...
echo.
echo 📝 测试方法：
echo    1. 浏览器打开: http://localhost:8000
echo    2. API文档: http://localhost:8000/docs
echo    3. 健康检查: http://localhost:8000/health
echo.
echo 💡 提示：
echo    - 使用 Ctrl+C 停止服务
echo    - 如果端口被占用，请修改 .env 中的 PORT 配置
echo.
echo ================================================================
echo.

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

if %errorlevel% neq 0 (
    echo.
    echo ❌ 服务启动失败！
    echo.
    echo 常见问题排查：
    echo   1. 检查 .env 配置文件是否正确
    echo   2. 检查8000端口是否被占用
    echo   3. 查看上方的错误信息
    echo.
    pause
    exit /b 1
)

pause
