@echo off
chcp 65001 >nul
echo ============================================================
echo 交互式页面控制工具（可选择页面）
echo ============================================================
echo.

cd /d "%~dp0"

:MENU
echo 请选择操作：
echo.
echo [1] 交互式控制（推荐 - 可选择页面）
echo [2] 查看所有页面状态
echo [3] 同步所有页面（从Facebook获取）
echo [0] 退出
echo.
set /p choice=请输入选项 (0-3): 

if "%choice%"=="1" goto INTERACTIVE
if "%choice%"=="2" goto STATUS
if "%choice%"=="3" goto SYNC
if "%choice%"=="0" goto END
goto MENU

:INTERACTIVE
echo.
echo 启动交互式页面控制...
python scripts/tools/control_pages.py
echo.
pause
goto MENU

:STATUS
echo.
echo 正在查看页面状态...
python scripts/tools/manage_pages.py status
echo.
pause
goto MENU

:SYNC
echo.
echo 正在同步所有页面...
python scripts/tools/manage_pages.py sync
echo.
pause
goto MENU

:END
echo.
echo 再见！
exit

