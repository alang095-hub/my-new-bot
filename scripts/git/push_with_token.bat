@echo off
REM 使用 Personal Access Token 推送代码的脚本

echo ========================================
echo 🔑 使用 Personal Access Token 推送代码
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

REM 获取仓库信息
set /p REPO_URL="请输入仓库地址（例如：https://github.com/用户名/仓库名.git）: "
if "%REPO_URL%"=="" (
    echo ❌ 未输入仓库地址
    pause
    exit /b 1
)

REM 获取 token
echo.
echo ⚠️  安全提示：Token 具有完整仓库访问权限，请妥善保管
echo.
set /p GITHUB_TOKEN="请输入 Personal Access Token: "
if "%GITHUB_TOKEN%"=="" (
    echo ❌ Token 不能为空
    pause
    exit /b 1
)

echo.
echo 🚀 开始推送代码...
echo.

REM 构建带 token 的 URL
set REPO_PATH=%REPO_URL:https://github.com/=%
set REPO_PATH=%REPO_PATH:.git=%
set PUSH_URL=https://%GITHUB_TOKEN%@github.com/%REPO_PATH%.git

REM 推送代码
git push %PUSH_URL% main

if errorlevel 1 (
    echo.
    echo ❌ 推送失败
    echo.
    echo 可能的原因：
    echo 1. Token 错误或已过期
    echo 2. Token 没有 repo 权限
    echo 3. 仓库地址错误
    echo 4. 网络连接问题
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 推送成功！
echo.
echo ⚠️  安全提示：建议不要在 URL 中永久保存 token
echo 推送完成后，远程地址已恢复为普通地址
echo.

REM 恢复远程地址（移除 token）
git remote set-url origin %REPO_URL%
echo ✅ 远程地址已恢复（token 已移除）
echo.
pause

