@echo off
chcp 65001 >nul
echo ============================================================
echo 仓库清理脚本
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/6] 删除临时/错误文件...
if exist "tall requests" del /f /q "tall requests"
if exist "tatus" del /f /q "tatus"
if exist "coverage.xml" del /f /q "coverage.xml"
if exist "facebook_customer_service.db" del /f /q "facebook_customer_service.db"
if exist "zeabur_check_report.json" del /f /q "zeabur_check_report.json"
if exist "htmlcov" rmdir /s /q "htmlcov"
if exist "data\test_reports" rmdir /s /q "data\test_reports"
echo    完成！
echo.

echo [2/6] 移动部署文档到docs/troubleshooting/...
if not exist "docs\troubleshooting" mkdir "docs\troubleshooting"
if exist "Facebook消息发送限制说明.md" move "Facebook消息发送限制说明.md" "docs\troubleshooting\"
if exist "修复SECRET_KEY错误.md" move "修复SECRET_KEY错误.md" "docs\troubleshooting\"
if exist "部署成功后续步骤.md" move "部署成功后续步骤.md" "docs\deployment\"
echo    完成！
echo.

echo [3/6] 删除重复的临时文档...
if exist "Facebook错误551说明.txt" del /f /q "Facebook错误551说明.txt"
if exist "紧急修复清单.txt" del /f /q "紧急修复清单.txt"
if exist "容器部署说明.md" del /f /q "容器部署说明.md"
if exist "容器部署快速清单.txt" del /f /q "容器部署快速清单.txt"
if exist "环境变量配置清单.txt" del /f /q "环境变量配置清单.txt"
if exist "Zeabur快速部署清单.txt" del /f /q "Zeabur快速部署清单.txt"
if exist "仓库错误检查报告.md" del /f /q "仓库错误检查报告.md"
echo    完成！
echo.

echo [4/6] 移动批处理脚本到scripts/...
if not exist "scripts\deployment" mkdir "scripts\deployment"
if exist "一键推送.bat" move "一键推送.bat" "scripts\deployment\"
if exist "推送代码.bat" move "推送代码.bat" "scripts\deployment\"
if exist "一键部署准备.bat" move "一键部署准备.bat" "scripts\deployment\"
if exist "修复仓库错误.bat" move "修复仓库错误.bat" "scripts\git\"
echo    完成！
echo.

echo [5/6] 清理docs目录中的旧文档...
if exist "docs\CLEANUP_SUMMARY.md" del /f /q "docs\CLEANUP_SUMMARY.md"
if exist "docs\FINAL_IMPLEMENTATION_SUMMARY.md" del /f /q "docs\FINAL_IMPLEMENTATION_SUMMARY.md"
if exist "docs\FINAL_MIGRATION_REPORT.md" del /f /q "docs\FINAL_MIGRATION_REPORT.md"
if exist "docs\FINAL_TEST_REPORT.md" del /f /q "docs\FINAL_TEST_REPORT.md"
if exist "docs\FIX_TEST_AND_COVERAGE_PLAN.md" del /f /q "docs\FIX_TEST_AND_COVERAGE_PLAN.md"
if exist "docs\FIXES_SUMMARY.md" del /f /q "docs\FIXES_SUMMARY.md"
if exist "docs\IMPLEMENTATION_SUMMARY.md" del /f /q "docs\IMPLEMENTATION_SUMMARY.md"
if exist "docs\IMPROVEMENT_IMPLEMENTATION_STATUS.md" del /f /q "docs\IMPROVEMENT_IMPLEMENTATION_STATUS.md"
if exist "docs\IMPROVEMENT_PLAN.md" del /f /q "docs\IMPROVEMENT_PLAN.md"
if exist "docs\PRE_TEST_SUMMARY.md" del /f /q "docs\PRE_TEST_SUMMARY.md"
if exist "docs\QUICK_TEST_CHECKLIST.md" del /f /q "docs\QUICK_TEST_CHECKLIST.md"
if exist "docs\READY_FOR_TESTING.md" del /f /q "docs\READY_FOR_TESTING.md"
if exist "docs\REFACTORING_GUIDE.md" del /f /q "docs\REFACTORING_GUIDE.md"
if exist "docs\TEST_EXECUTION_SUMMARY.md" del /f /q "docs\TEST_EXECUTION_SUMMARY.md"
if exist "docs\TEST_RESULTS.md" del /f /q "docs\TEST_RESULTS.md"
if exist "docs\TEST_UPDATE_SUMMARY.md" del /f /q "docs\TEST_UPDATE_SUMMARY.md"
if exist "docs\TESTING_FEASIBILITY_ANALYSIS.md" del /f /q "docs\TESTING_FEASIBILITY_ANALYSIS.md"
if exist "docs\TESTING_FEASIBILITY_REPORT.md" del /f /q "docs\TESTING_FEASIBILITY_REPORT.md"
if exist "docs\TESTING_PLAN.md" del /f /q "docs\TESTING_PLAN.md"
if exist "docs\TESTING_STEPS.md" del /f /q "docs\TESTING_STEPS.md"
echo    完成！
echo.

echo [6/6] 更新.gitignore...
echo # 临时文件 >> .gitignore
echo tall requests >> .gitignore
echo tatus >> .gitignore
echo zeabur_check_report.json >> .gitignore
echo. >> .gitignore
echo # 测试报告 >> .gitignore
echo data/test_reports/ >> .gitignore
echo    完成！
echo.

echo ============================================================
echo 清理完成！
echo ============================================================
echo.
echo 已执行的操作：
echo 1. 删除临时/错误文件
echo 2. 移动部署文档到docs目录
echo 3. 删除重复的临时文档
echo 4. 移动批处理脚本到scripts目录
echo 5. 清理docs目录中的旧文档
echo 6. 更新.gitignore
echo.
echo 下一步：运行 git add . 然后提交更改
echo.
pause

