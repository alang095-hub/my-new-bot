@echo off
REM 推送到新 GitHub 账号仓库的脚本

echo ========================================
echo 📤 推送到新 GitHub 账号仓库
echo ========================================
echo.

REM 检查是否已提交
git status | findstr /C:"nothing to commit" >nul
if errorlevel 1 (
    echo ⚠️  检测到未提交的更改
    echo 请先提交所有更改
    pause
    exit /b 1
)

echo ✅ 代码已提交到本地
echo.

REM 获取新仓库信息
set /p NEW_REPO_URL="请输入新仓库的完整地址（例如：https://github.com/用户名/仓库名.git）: "
if "%NEW_REPO_URL%"=="" (
    echo ❌ 未输入仓库地址
    pause
    exit /b 1
)

echo.
echo 📝 更新远程仓库地址...
git remote set-url origin %NEW_REPO_URL%
if errorlevel 1 (
    echo ❌ 更新远程地址失败
    pause
    exit /b 1
)

echo ✅ 远程地址已更新
echo.

REM 获取认证方式
echo 请选择认证方式：
echo 1. 使用 Personal Access Token（推荐）
echo 2. 使用 SSH 密钥
echo 3. 使用 GitHub CLI
set /p AUTH_METHOD="请输入选项 (1-3): "

if "%AUTH_METHOD%"=="1" goto :token
if "%AUTH_METHOD%"=="2" goto :ssh
if "%AUTH_METHOD%"=="3" goto :cli
goto :push

:token
echo.
echo 📋 使用 Personal Access Token 方式
echo.
echo 如果没有 Personal Access Token，请先创建：
echo 1. 访问：https://github.com/settings/tokens
echo 2. 点击 "Generate new token (classic)"
echo 3. 勾选 "repo" 权限
echo 4. 复制生成的 token
echo.
set /p GITHUB_USER="请输入 GitHub 用户名: "
set /p GITHUB_TOKEN="请输入 Personal Access Token: "

if "%GITHUB_TOKEN%"=="" (
    echo ❌ Token 不能为空
    pause
    exit /b 1
)

REM 使用 token 更新 URL
for /f "tokens=*" %%i in ("%NEW_REPO_URL%") do set REPO_PATH=%%i
set REPO_PATH=%REPO_PATH:https://github.com/=%
set REPO_PATH=%REPO_PATH:.git=%
git remote set-url origin https://%GITHUB_TOKEN%@github.com/%REPO_PATH%.git
goto :push

:ssh
echo.
echo 🔐 使用 SSH 方式
echo.
REM 检查 SSH 密钥
if not exist "%USERPROFILE%\.ssh\id_rsa.pub" (
    if not exist "%USERPROFILE%\.ssh\id_ed25519.pub" (
        echo ⚠️  未找到 SSH 密钥
        echo 请先生成 SSH 密钥：ssh-keygen -t ed25519 -C "your_email@example.com"
        pause
        exit /b 1
    )
)
REM 转换为 SSH URL
set SSH_URL=%NEW_REPO_URL:https://github.com/=git@github.com:%
set SSH_URL=%SSH_URL:.git=.git%
git remote set-url origin %SSH_URL%
goto :push

:cli
echo.
echo 🔧 使用 GitHub CLI
echo.
gh auth status >nul 2>&1
if errorlevel 1 (
    echo ⚠️  GitHub CLI 未登录
    echo 请先运行：gh auth login
    pause
    exit /b 1
)
goto :push

:push
echo.
echo 🚀 开始推送代码...
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ 推送失败
    echo.
    echo 可能的原因：
    echo 1. 认证信息错误
    echo 2. 仓库不存在或无权限
    echo 3. 网络连接问题
    echo.
    echo 请检查：
    echo - Personal Access Token 是否正确
    echo - 仓库地址是否正确
    echo - 是否有推送权限
    pause
    exit /b 1
)

echo.
echo ✅ 推送成功！
echo.
echo 仓库地址：%NEW_REPO_URL%
echo 分支：main
echo.
pause

