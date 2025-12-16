@echo off
chcp 65001 >nul
echo ========================================
echo 🔒 部署前安全检查
echo ========================================
echo.

echo 1️⃣  检查敏感信息...
python scripts\tools\check_sensitive_data.py
if errorlevel 1 (
    echo.
    echo ❌ 发现敏感信息泄露！请先修复后再部署。
    echo.
    pause
    exit /b 1
)

echo.
echo 2️⃣  检查Git状态...
git status --short | findstr /i "\.env config\.yaml \.page_tokens logs\"
if not errorlevel 1 (
    echo.
    echo ⚠️  警告：发现敏感文件在Git跟踪中！
    echo 请检查以下文件：
    git status --short | findstr /i "\.env config\.yaml \.page_tokens logs\"
    echo.
    echo 建议：
    echo 1. 确保这些文件在 .gitignore 中
    echo 2. 如果已提交，使用 git rm --cached 移除
    echo.
    pause
    exit /b 1
)

echo.
echo 3️⃣  检查 .gitignore 配置...
findstr /i "\.env config\.yaml \.page_tokens logs" .gitignore >nul
if errorlevel 1 (
    echo ⚠️  警告：.gitignore 可能缺少敏感文件配置
    echo 请检查 .gitignore 文件
) else (
    echo ✅ .gitignore 配置正确
)

echo.
echo ========================================
echo ✅ 安全检查通过！
echo ========================================
echo.
echo 可以安全地推送到GitHub并部署到Zeabur
echo.
pause

