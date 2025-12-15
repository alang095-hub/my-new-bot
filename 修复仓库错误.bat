@echo off
chcp 65001 >nul
echo ============================================================
echo 修复仓库错误（自动处理）
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] 检查Git状态...
git status --short
echo.

echo [2/4] 添加所有更改...
git add .
echo    完成！
echo.

echo [3/4] 提交更改...
git commit -m "添加容器部署指南和环境变量配置文档" -q
if %errorlevel% equ 0 (
    echo    完成！已提交更改
) else (
    echo    提示：可能没有新更改需要提交
)
echo.

echo [4/4] 推送到GitHub...
git push origin main
if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo 成功！所有更改已推送到GitHub
    echo ============================================================
    echo.
    echo 仓库地址：https://github.com/alang095-hub/my-new-bot
    echo.
    echo 现在可以继续部署了！
) else (
    echo.
    echo ============================================================
    echo 推送失败
    echo ============================================================
    echo.
    echo 可能的原因：
    echo 1. 需要登录GitHub账号
    echo 2. 网络连接问题
    echo.
    echo 解决方法：
    echo 1. 使用GitHub Desktop推送
    echo 2. 或者检查网络连接后重试
)

echo.
pause

