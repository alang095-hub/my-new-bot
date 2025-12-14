#!/bin/bash
# 部署前本地测试脚本 (Linux/Mac)
# 用于在部署到Zeabur前进行完整测试

set -e

echo "=========================================="
echo "部署前本地测试"
echo "=========================================="
echo

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# 1. 检查环境配置
echo "1. 环境配置检查"
echo "----------------------------------------"
if python -c "from src.core.config import settings; print('配置加载成功')" 2>/dev/null; then
    echo "[PASS] 环境配置加载成功"
    ((PASS_COUNT++))
else
    echo "[FAIL] 环境配置加载失败"
    ((FAIL_COUNT++))
fi

# 2. 检查数据库连接
echo
echo "2. 数据库连接检查"
echo "----------------------------------------"
if python -c "from src.core.database.connection import engine; engine.connect(); print('数据库连接成功')" 2>/dev/null; then
    echo "[PASS] 数据库连接正常"
    ((PASS_COUNT++))
else
    echo "[FAIL] 数据库连接失败"
    ((FAIL_COUNT++))
fi

# 3. 检查多页面Token配置
echo
echo "3. 多页面Token配置检查"
echo "----------------------------------------"
if python scripts/tools/manage_pages.py status >/dev/null 2>&1; then
    echo "[PASS] 多页面Token配置检查通过"
    ((PASS_COUNT++))
    echo
    echo "已配置的页面:"
    python scripts/tools/manage_pages.py status 2>/dev/null | grep "页面" || true
else
    echo "[WARN] 无法检查多页面Token配置"
    ((WARN_COUNT++))
fi

# 4. 检查服务启动
echo
echo "4. 服务启动检查"
echo "----------------------------------------"
if python -c "from src.main import app; assert app is not None" 2>/dev/null; then
    echo "[PASS] FastAPI应用创建成功"
    ((PASS_COUNT++))
else
    echo "[FAIL] FastAPI应用创建失败"
    ((FAIL_COUNT++))
fi

# 5. 运行生产环境测试
echo
echo "5. 运行生产环境测试"
echo "----------------------------------------"
echo "提示: 请先启动服务 (python run.py)"
echo "然后在另一个终端运行此脚本"
echo
read -p "服务是否已启动? (Y/N): " STARTED
if [ "$STARTED" = "Y" ] || [ "$STARTED" = "y" ]; then
    if python scripts/test/production_test.py --test all --url http://localhost:8000 >/dev/null 2>&1; then
        echo "[PASS] 生产环境测试通过"
        ((PASS_COUNT++))
    else
        echo "[WARN] 部分测试失败，请查看详细日志"
        ((WARN_COUNT++))
    fi
else
    echo "[SKIP] 跳过测试（服务未启动）"
fi

# 总结
echo
echo "=========================================="
echo "测试总结"
echo "=========================================="
echo "通过: $PASS_COUNT"
echo "失败: $FAIL_COUNT"
echo "警告: $WARN_COUNT"
echo

if [ $FAIL_COUNT -eq 0 ]; then
    if [ $WARN_COUNT -eq 0 ]; then
        echo "[SUCCESS] 所有测试通过！可以部署到Zeabur。"
        echo
        echo "下一步:"
        echo "1. 备份配置文件 (.env, .page_tokens.json, config/config.yaml)"
        echo "2. 按照Zeabur部署指南进行部署"
        echo "3. 部署后运行: python scripts/tools/manage_pages.py sync"
        exit 0
    else
        echo "[WARN] 测试基本通过，但有 $WARN_COUNT 个警告项。"
        echo "建议检查警告项后再部署。"
        exit 0
    fi
else
    echo "[ERROR] 发现 $FAIL_COUNT 个失败项，请修复后再部署。"
    echo
    echo "建议:"
    echo "1. 检查环境变量配置"
    echo "2. 检查数据库连接"
    echo "3. 检查多页面Token配置"
    echo "4. 查看详细日志: logs/app.log"
    exit 1
fi

