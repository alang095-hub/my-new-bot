@echo off
chcp 65001 >nul
echo ============================================================
echo 自动提交代码（小白版）
echo ============================================================
echo.

cd /d "%~dp0\..\.."

echo 正在检查Git状态...
git status --short
echo.

echo 正在添加所有更改...
git add .
echo.

echo 正在提交代码...
git commit -m "准备部署：添加部署文档和测试脚本"
echo.

echo 检查远程仓库...
git remote -v
echo.

echo ============================================================
echo 完成！
echo ============================================================
echo.
echo 如果看到"Your branch is ahead"，说明需要推送到GitHub
echo 运行以下命令推送代码：
echo   git push
echo.
pause

