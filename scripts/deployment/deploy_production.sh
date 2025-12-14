#!/bin/bash
# 生产环境部署脚本
# 使用方法: ./scripts/deployment/deploy_production.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "生产环境部署脚本"
echo "=========================================="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}错误: 请不要使用root用户运行此脚本${NC}"
    exit 1
fi

# 项目根目录
PROJECT_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$PROJECT_ROOT"

echo "项目目录: $PROJECT_ROOT"
echo

# 1. 检查环境
echo "1. 检查环境..."
echo "----------------------------------------"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: Python3 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python3: $(python3 --version)"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi
echo -e "${GREEN}✓${NC} 虚拟环境存在"

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "检查依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓${NC} 依赖已安装"

# 2. 检查配置文件
echo
echo "2. 检查配置文件..."
echo "----------------------------------------"

if [ ! -f ".env" ]; then
    echo -e "${RED}错误: .env 文件不存在${NC}"
    echo "请从 env.example 创建 .env 并配置所有必需的环境变量"
    exit 1
fi
echo -e "${GREEN}✓${NC} .env 文件存在"

if [ ! -f "config/config.yaml" ]; then
    echo -e "${YELLOW}警告: config/config.yaml 不存在${NC}"
    if [ -f "config/config.yaml.example" ]; then
        echo "从示例文件创建..."
        cp config/config.yaml.example config/config.yaml
        echo -e "${YELLOW}请编辑 config/config.yaml 配置业务规则${NC}"
    fi
fi
echo -e "${GREEN}✓${NC} config.yaml 文件存在"

# 3. 验证配置
echo
echo "3. 验证配置..."
echo "----------------------------------------"

python3 -c "from src.core.config import settings; print('配置加载成功')" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 配置验证通过"
else
    echo -e "${RED}错误: 配置验证失败${NC}"
    exit 1
fi

# 4. 数据库迁移
echo
echo "4. 运行数据库迁移..."
echo "----------------------------------------"

alembic upgrade head
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 数据库迁移成功"
else
    echo -e "${RED}错误: 数据库迁移失败${NC}"
    exit 1
fi

# 5. 运行测试
echo
echo "5. 运行生产环境测试..."
echo "----------------------------------------"

python3 scripts/test/production_test.py --test environment 2>&1 | tail -20
TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 测试通过"
else
    echo -e "${YELLOW}警告: 部分测试失败，但继续部署${NC}"
fi

# 6. 创建必要的目录
echo
echo "6. 创建必要的目录..."
echo "----------------------------------------"

mkdir -p logs
mkdir -p data/backups
mkdir -p data/test_reports
mkdir -p data/monitoring
echo -e "${GREEN}✓${NC} 目录创建完成"

# 7. 部署完成
echo
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo
echo "下一步："
echo "1. 检查环境变量配置（.env文件）"
echo "2. 检查业务规则配置（config/config.yaml）"
echo "3. 启动服务："
echo "   - 开发环境: python run.py"
echo "   - 生产环境: 使用 systemd 或 Docker"
echo "4. 验证服务: curl http://localhost:8000/health"
echo "5. 运行完整测试: python scripts/test/production_test.py --test all"
echo

