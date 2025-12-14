@echo off
REM 生产环境快速测试脚本 (Windows)
REM 用于快速验证生产环境的关键功能

echo ==========================================
echo 生产环境快速测试
echo ==========================================
echo.

set PASS_COUNT=0
set FAIL_COUNT=0
set WARN_COUNT=0

REM 1. 检查环境配置
echo 1. 环境配置检查
echo ----------------------------------------
python -c "from src.core.config import settings; print('✅ 配置加载成功')" >nul 2>&1
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
python -c "from src.core.database.connection import engine; engine.connect(); print('✅ 数据库连接成功')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] 数据库连接正常
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] 数据库连接失败
    set /a FAIL_COUNT+=1
)

REM 3. 检查服务启动
echo.
echo 3. 服务启动检查
echo ----------------------------------------
python -c "from src.main import app; assert app is not None" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] FastAPI应用创建成功
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] FastAPI应用创建失败
    set /a FAIL_COUNT+=1
)

REM 4. 检查服务是否运行
echo.
echo 4. 服务运行检查
echo ----------------------------------------
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] 服务正在运行
    set /a PASS_COUNT+=1
    
    REM 5. 健康检查端点测试
    echo.
    echo 5. 健康检查端点测试
    echo ----------------------------------------
    curl -s http://localhost:8000/health | findstr /C:"status" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] 健康检查端点正常
        set /a PASS_COUNT+=1
    ) else (
        echo [WARN] 健康检查端点响应异常
        set /a WARN_COUNT+=1
    )
    
    REM 6. API端点测试
    echo.
    echo 6. API端点测试
    echo ----------------------------------------
    curl -s http://localhost:8000/ >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] 根端点正常
        set /a PASS_COUNT+=1
    ) else (
        echo [WARN] 根端点响应异常
        set /a WARN_COUNT+=1
    )
    
    curl -s http://localhost:8000/metrics >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] 性能指标端点正常
        set /a PASS_COUNT+=1
    ) else (
        echo [WARN] 性能指标端点响应异常
        set /a WARN_COUNT+=1
    )
) else (
    echo [WARN] 服务未运行，跳过端点测试
    echo 提示: 请先启动服务 (python run.py)
    set /a WARN_COUNT+=1
)

REM 7. 运行自动化测试脚本
echo.
echo 7. 运行自动化测试
echo ----------------------------------------
if exist scripts\test\production_test.py (
    python scripts\test\production_test.py --test environment --url http://localhost:8000 >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] 自动化测试通过
        set /a PASS_COUNT+=1
    ) else (
        echo [WARN] 自动化测试有警告或失败
        set /a WARN_COUNT+=1
    )
) else (
    echo [SKIP] 自动化测试脚本不存在
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
        echo [SUCCESS] 所有测试通过！生产环境准备就绪。
        exit /b 0
    ) else (
        echo [WARN] 测试基本通过，但有 %WARN_COUNT% 个警告项。
        echo 建议检查警告项后再部署到生产环境。
        exit /b 0
    )
) else (
    echo [ERROR] 发现 %FAIL_COUNT% 个失败项，请检查并修复。
    echo.
    echo 建议:
    echo 1. 检查环境变量配置 (.env 文件)
    echo 2. 检查数据库连接
    echo 3. 检查服务是否正常运行
    echo 4. 查看日志文件: logs\app.log
    exit /b 1
)

