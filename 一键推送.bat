@echo off
chcp 65001 >nul
echo ============================================================
echo 一键推送代码到GitHub（全自动）
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/5] 检查Git状态...
git status --short >nul 2>&1
if %errorlevel% neq 0 (
    echo    错误：当前目录不是Git仓库
    echo    请先运行：git init
    pause
    exit /b 1
)
echo    完成！
echo.

echo [2/5] 添加所有文件...
git add .
echo    完成！
echo.

echo [3/5] 提交代码...
git commit -m "准备部署：添加部署文档和测试脚本" -q
if %errorlevel% equ 0 (
    echo    完成！代码已提交
) else (
    echo    提示：可能没有新更改需要提交，继续推送已有提交...
)
echo.

echo [4/5] 检查并配置远程仓库...
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo    未配置远程仓库，正在配置...
    git remote add origin https://github.com/alang095-hub/my-new-bot.git
    echo    完成！已连接到：https://github.com/alang095-hub/my-new-bot.git
) else (
    echo    远程仓库已配置
    git remote set-url origin https://github.com/alang095-hub/my-new-bot.git
    echo    已更新远程仓库地址
)
echo.

echo [5/5] 推送到GitHub...
echo    正在推送，请稍候...
git push -u origin main 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 成功！代码已推送到GitHub
    echo ============================================================
    echo.
    echo 仓库地址：https://github.com/alang095-hub/my-new-bot
    echo.
    echo 下一步：去Zeabur部署
    echo 1. 访问：https://zeabur.com
    echo 2. 登录GitHub账号
    echo 3. 导入仓库：alang095-hub/my-new-bot
) else (
    echo.
    echo ============================================================
    echo 推送失败
    echo ============================================================
    echo.
    echo 可能的原因：
    echo 1. 需要登录GitHub账号
    echo 2. 需要配置Git凭证
    echo 3. 网络连接问题
    echo.
    echo 解决方法：
    echo 1. 使用GitHub Desktop软件（推荐）
    echo    查看：GitHub Desktop连接仓库步骤.md
    echo 2. 或者手动配置Git凭证
    echo.
    echo 如果使用GitHub Desktop：
    echo - 下载：https://desktop.github.com
    echo - 按照指南操作即可
)

echo.
pause

