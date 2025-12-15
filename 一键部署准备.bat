@echo off
chcp 65001 >nul
echo ============================================================
echo 一键部署准备（小白版 - 全自动）
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] 安装缺失的依赖包...
python -m pip install requests -q
echo    完成！
echo.

echo [2/4] 添加所有文件到Git...
git add .
echo    完成！
echo.

echo [3/4] 提交代码...
git commit -m "准备部署：添加部署文档和测试脚本" -q
if %errorlevel% equ 0 (
    echo    完成！
) else (
    echo    提示：可能没有新更改需要提交
)
echo.

echo [4/4] 检查远程仓库...
git remote -v >nul 2>&1
if %errorlevel% neq 0 (
    echo    未配置远程仓库
    echo    正在配置远程仓库...
    git remote add origin https://github.com/alang095-hub/my-new-bot.git
    echo    完成！
) else (
    echo    远程仓库已配置
)
echo.

echo ============================================================
echo 完成！所有操作已自动完成
echo ============================================================
echo.
echo 下一步：推送到GitHub
echo 运行命令：git push -u origin main
echo.
echo 或者直接双击运行：推送代码.bat
echo.
pause

