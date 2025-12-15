@echo off
chcp 65001 >nul
echo ============================================================
echo 推送代码到GitHub（小白版）
echo ============================================================
echo.

cd /d "%~dp0"

echo 正在检查远程仓库...
git remote -v >nul 2>&1
if %errorlevel% neq 0 (
    echo 未配置远程仓库，正在配置...
    git remote add origin https://github.com/alang095-hub/my-new-bot.git
    echo 完成！
    echo.
)

echo 正在推送到GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 成功！代码已推送到GitHub
    echo ============================================================
    echo.
    echo 现在可以去Zeabur部署了！
    echo 仓库地址：https://github.com/alang095-hub/my-new-bot
) else (
    echo.
    echo ============================================================
    echo 推送失败
    echo ============================================================
    echo.
    echo 可能的原因：
    echo 1. 需要登录GitHub账号
    echo 2. 需要配置Git凭证
    echo.
    echo 解决方法：
    echo 1. 在浏览器登录GitHub
    echo 2. 或者使用GitHub Desktop软件
)

echo.
pause

