@echo off
REM 部署前本地测试脚本 (Windows)
REM 用于在部署到Zeabur前进行完整测试

echo ==========================================
echo 部署前本地测试
echo ==========================================
echo.

set PASS_COUNT=0
set FAIL_COUNT=0
set WARN_COUNT=0

REM 1. 检查环境配置
echo 1. 环境配置检查
echo ----------------------------------------
python -c "from src.core.config import settings; print('配置加载成功')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] 环境配置加载成功
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] 环境配置加载失败
    set /a FAIL_COUNT+=1
)

REM 2. 检查数据库连接
echo.
echo 2. 数据库连接检查
echo ----------------------------------------
python -c "from src.core.database.connection import engine; engine.connect(); print('OK')" 2>nul
if %errorlevel% equ 0 (
    echo [PASS] 数据库连接正常
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] 数据库连接失败
    set /a FAIL_COUNT+=1
)

REM 3. 检查多页面Token配置
echo.
echo 3. 多页面Token配置检查
echo ----------------------------------------
python scripts\tools\manage_pages.py status >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] 多页面Token配置检查通过
    set /a PASS_COUNT+=1
    echo.
    echo 已配置的页面:
    python scripts\tools\manage_pages.py status 2>nul | findstr /C:"页面" /C:"Token" /C:"启用" /C:"禁用"
) else (
    echo [WARN] 无法检查多页面Token配置
    set /a WARN_COUNT+=1
)

REM 4. 检查服务启动
echo.
echo 4. 服务启动检查
echo ----------------------------------------
python -c "from src.main import app; assert app is not None" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] FastAPI应用创建成功
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] FastAPI应用创建失败
    set /a FAIL_COUNT+=1
)

REM 5. 运行生产环境测试
echo.
echo 5. 运行生产环境测试
echo ----------------------------------------
echo 提示: 请先启动服务 (python run.py)
echo 然后在另一个终端运行此脚本
echo.
set /p STARTED="服务是否已启动? (Y/N): "
if /i "%STARTED%"=="Y" (
    python scripts\test\production_test.py --test all --url http://localhost:8000 >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] 生产环境测试通过
        set /a PASS_COUNT+=1
    ) else (
        echo [WARN] 部分测试失败，请查看详细日志
        set /a WARN_COUNT+=1
    )
) else (
    echo [SKIP] 跳过测试（服务未启动）
)

REM 总结
echo.
echo ==========================================
echo 测试总结
echo ==========================================
echo 通过: %PASS_COUNT%
echo 失败: %FAIL_COUNT%
echo 警告: %WARN_COUNT%
echo.

if %FAIL_COUNT% equ 0 (
    if %WARN_COUNT% equ 0 (
        echo [SUCCESS] 所有测试通过！可以部署到Zeabur。
        echo.
        echo 下一步:
        echo 1. 备份配置文件 (.env, .page_tokens.json, config/config.yaml)
        echo 2. 按照Zeabur部署指南进行部署
        echo 3. 部署后运行: python scripts/tools/manage_pages.py sync
        exit /b 0
    ) else (
        echo [WARN] 测试基本通过，但有 %WARN_COUNT% 个警告项。
        echo 建议检查警告项后再部署。
        exit /b 0
    )
) else (
    echo [ERROR] 发现 %FAIL_COUNT% 个失败项，请修复后再部署。
    echo.
    echo 建议:
    echo 1. 检查环境变量配置
    echo 2. 检查数据库连接
    echo 3. 检查多页面Token配置
    echo 4. 查看详细日志: logs\app.log
    exit /b 1
)

