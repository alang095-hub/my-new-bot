#!/bin/bash
# 生产环境快速测试脚本 (Linux/Mac)
# 用于快速验证生产环境的关键功能

set -e

echo "=========================================="
echo "生产环境快速测试"
echo "=========================================="
echo

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# 1. 检查环境配置
echo "1. 环境配置检查"
echo "----------------------------------------"
if python -c "from src.core.config import settings; print('✅ 配置加载成功')" 2>/dev/null; then
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
if python -c "from src.core.database.connection import engine; engine.connect(); print('✅ 数据库连接成功')" 2>/dev/null; then
    echo "[PASS] 数据库连接正常"
    ((PASS_COUNT++))
else
    echo "[FAIL] 数据库连接失败"
    ((FAIL_COUNT++))
fi

# 3. 检查服务启动
echo
echo "3. 服务启动检查"
echo "----------------------------------------"
if python -c "from src.main import app; assert app is not None" 2>/dev/null; then
    echo "[PASS] FastAPI应用创建成功"
    ((PASS_COUNT++))
else
    echo "[FAIL] FastAPI应用创建失败"
    ((FAIL_COUNT++))
fi

# 4. 检查服务是否运行
echo
echo "4. 服务运行检查"
echo "----------------------------------------"
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "[PASS] 服务正在运行"
    ((PASS_COUNT++))
    
    # 5. 健康检查端点测试
    echo
    echo "5. 健康检查端点测试"
    echo "----------------------------------------"
    if curl -s http://localhost:8000/health | grep -q "status"; then
        echo "[PASS] 健康检查端点正常"
        ((PASS_COUNT++))
    else
        echo "[WARN] 健康检查端点响应异常"
        ((WARN_COUNT++))
    fi
    
    # 6. API端点测试
    echo
    echo "6. API端点测试"
    echo "----------------------------------------"
    if curl -s http://localhost:8000/ >/dev/null 2>&1; then
        echo "[PASS] 根端点正常"
        ((PASS_COUNT++))
    else
        echo "[WARN] 根端点响应异常"
        ((WARN_COUNT++))
    fi
    
    if curl -s http://localhost:8000/metrics >/dev/null 2>&1; then
        echo "[PASS] 性能指标端点正常"
        ((PASS_COUNT++))
    else
        echo "[WARN] 性能指标端点响应异常"
        ((WARN_COUNT++))
    fi
else
    echo "[WARN] 服务未运行，跳过端点测试"
    echo "提示: 请先启动服务 (python run.py)"
    ((WARN_COUNT++))
fi

# 7. 运行自动化测试脚本
echo
echo "7. 运行自动化测试"
echo "----------------------------------------"
if [ -f "scripts/test/production_test.py" ]; then
    if python scripts/test/production_test.py --test environment --url http://localhost:8000 >/dev/null 2>&1; then
        echo "[PASS] 自动化测试通过"
        ((PASS_COUNT++))
    else
        echo "[WARN] 自动化测试有警告或失败"
        ((WARN_COUNT++))
    fi
else
    echo "[SKIP] 自动化测试脚本不存在"
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
        echo "[SUCCESS] 所有测试通过！生产环境准备就绪。"
        exit 0
    else
        echo "[WARN] 测试基本通过，但有 $WARN_COUNT 个警告项。"
        echo "建议检查警告项后再部署到生产环境。"
        exit 0
    fi
else
    echo "[ERROR] 发现 $FAIL_COUNT 个失败项，请检查并修复。"
    echo
    echo "建议:"
    echo "1. 检查环境变量配置 (.env 文件)"
    echo "2. 检查数据库连接"
    echo "3. 检查服务是否正常运行"
    echo "4. 查看日志文件: logs/app.log"
    exit 1
fi

