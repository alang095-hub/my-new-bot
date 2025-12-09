#!/bin/bash
# 快速部署脚本

set -e

echo "🚀 开始部署客户服务系统..."

# 检查 Python 版本
echo "📋 检查环境..."
python3 --version || { echo "❌ Python 3 未安装"; exit 1; }

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "请创建 .env 文件并配置所有必需的环境变量"
    exit 1
fi

# 检查 config.yaml
if [ ! -f "config.yaml" ]; then
    echo "📝 创建配置文件..."
    if [ -f "config.yaml.example" ]; then
        cp config.yaml.example config.yaml
        echo "✅ 已从 config.yaml.example 创建 config.yaml"
        echo "⚠️  请编辑 config.yaml 配置业务规则"
    else
        echo "❌ config.yaml.example 不存在"
        exit 1
    fi
fi

# 测试配置
echo "🔍 测试配置..."
python3 -c "from src.config import settings; print('✅ 配置加载成功')" || {
    echo "❌ 配置加载失败，请检查 .env 文件"
    exit 1
}

# 检查数据库连接
echo "🗄️  检查数据库连接..."
python3 -c "from src.database.database import engine; engine.connect(); print('✅ 数据库连接成功')" || {
    echo "❌ 数据库连接失败，请检查 DATABASE_URL"
    exit 1
}

# 运行数据库迁移
echo "📊 运行数据库迁移..."
alembic upgrade head || {
    echo "⚠️  数据库迁移失败，尝试直接创建表..."
    python3 -c "from src.database.database import engine, Base; Base.metadata.create_all(bind=engine)"
}

echo "✅ 部署完成！"
echo ""
echo "启动服务:"
echo "  python run.py"
echo ""
echo "或使用 uvicorn:"
echo "  uvicorn src.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "访问 API 文档: http://localhost:8000/docs"




