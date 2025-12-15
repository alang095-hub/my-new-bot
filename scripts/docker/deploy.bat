@echo off
REM Docker 容器部署脚本 (Windows)

setlocal enabledelayedexpansion

set IMAGE_NAME=my-telegram-bot
set CONTAINER_NAME=my-telegram-bot
set PORT=8000

echo ========================================
echo 🐳 Docker 容器部署脚本
echo ========================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    echo https://www.docker.com/products/docker-desktop
    exit /b 1
)

REM 检查 .env 文件
if not exist .env (
    echo ⚠️  .env 文件不存在
    echo 请创建 .env 文件并配置所有必需的环境变量
    exit /b 1
)

set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=deploy

if "%COMMAND%"=="build" goto :build
if "%COMMAND%"=="deploy" goto :deploy
if "%COMMAND%"=="start" goto :start
if "%COMMAND%"=="stop" goto :stop
if "%COMMAND%"=="restart" goto :restart
if "%COMMAND%"=="logs" goto :logs
if "%COMMAND%"=="shell" goto :shell
if "%COMMAND%"=="migrate" goto :migrate
if "%COMMAND%"=="status" goto :status
if "%COMMAND%"=="clean" goto :clean
goto :usage

:build
echo 📦 构建 Docker 镜像...
docker build -t %IMAGE_NAME%:latest .
if errorlevel 1 (
    echo ❌ 镜像构建失败
    exit /b 1
)
echo ✅ 镜像构建完成
echo.
goto :end

:deploy
call :build
call :cleanup
call :run
timeout /t 5 /nobreak >nul
call :migrate
call :status
goto :end

:start
call :cleanup
call :run
call :status
goto :end

:stop
echo 🛑 停止容器...
docker stop %CONTAINER_NAME% >nul 2>&1
echo ✅ 容器已停止
goto :end

:restart
echo 🔄 重启容器...
docker restart %CONTAINER_NAME% >nul 2>&1
if errorlevel 1 (
    call :cleanup
    call :run
)
call :status
goto :end

:logs
docker logs -f %CONTAINER_NAME%
goto :end

:shell
docker exec -it %CONTAINER_NAME% bash
goto :end

:migrate
echo 📊 运行数据库迁移...
docker exec %CONTAINER_NAME% alembic upgrade head
if errorlevel 1 (
    echo ⚠️  迁移失败，请检查数据库连接
)
echo.
goto :end

:status
echo ========================================
echo 📊 容器状态
echo ========================================
echo.
docker ps --filter "name=%CONTAINER_NAME%" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo 📋 查看日志：
echo docker logs -f %CONTAINER_NAME%
echo.
echo 🔍 进入容器：
echo docker exec -it %CONTAINER_NAME% bash
echo.
echo 🌐 健康检查：
echo curl http://localhost:%PORT%/health
echo.
goto :end

:clean
echo 🧹 清理容器和镜像...
docker stop %CONTAINER_NAME% >nul 2>&1
docker rm %CONTAINER_NAME% >nul 2>&1
docker rmi %IMAGE_NAME%:latest >nul 2>&1
echo ✅ 清理完成
goto :end

:cleanup
docker ps -a --filter "name=%CONTAINER_NAME%" --format "{{.Names}}" | findstr /C:"%CONTAINER_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo 🛑 停止并删除旧容器...
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker rm %CONTAINER_NAME% >nul 2>&1
    echo ✅ 旧容器已清理
    echo.
)
goto :eof

:run
echo 🚀 启动容器...
docker run -d ^
    --name %CONTAINER_NAME% ^
    -p %PORT%:%PORT% ^
    --env-file .env ^
    -e PORT=%PORT% ^
    -v "%CD%\logs:/app/logs" ^
    %IMAGE_NAME%:latest
if errorlevel 1 (
    echo ❌ 容器启动失败
    exit /b 1
)
echo ✅ 容器已启动
echo.
goto :eof

:usage
echo 用法: %0 [命令]
echo.
echo 命令：
echo   build     - 构建 Docker 镜像
echo   deploy    - 完整部署（构建+运行+迁移）
echo   start     - 启动容器
echo   stop      - 停止容器
echo   restart   - 重启容器
echo   logs      - 查看日志
echo   shell     - 进入容器
echo   migrate   - 运行数据库迁移
echo   status    - 显示容器状态
echo   clean     - 清理容器和镜像
exit /b 1

:end
endlocal



