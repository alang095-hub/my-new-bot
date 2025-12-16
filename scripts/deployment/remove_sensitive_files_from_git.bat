@echo off
chcp 65001 >nul
echo ========================================
echo 🔒 从Git中移除敏感文件
echo ========================================
echo.
echo ⚠️  警告：此操作将从Git中移除敏感文件
echo 但会保留本地文件
echo.
pause

echo.
echo 正在从Git中移除敏感文件...
echo.

REM 移除页面Token文件
if exist .page_tokens.json (
    echo 移除 .page_tokens.json...
    git rm --cached .page_tokens.json 2>nul
)

if exist .page_tokens.json.backup (
    echo 移除 .page_tokens.json.backup...
    git rm --cached .page_tokens.json.backup 2>nul
)

REM 移除配置文件（如果已提交）
git ls-files | findstr /i "config\.yaml$" | findstr /v "\.example" >nul
if not errorlevel 1 (
    echo 移除 config/config.yaml...
    git rm --cached config/config.yaml 2>nul
)

REM 移除日志文件
if exist logs\ (
    echo 移除 logs/ 目录...
    git rm -r --cached logs/ 2>nul
)

echo.
echo ========================================
echo ✅ 完成！
echo ========================================
echo.
echo 请运行以下命令提交更改：
echo   git commit -m "Remove sensitive files from Git"
echo   git push
echo.
echo ⚠️  重要：如果这些文件包含真实密钥，请立即撤销并重新生成！
echo.
pause

