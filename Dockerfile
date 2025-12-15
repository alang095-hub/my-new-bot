FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口（使用环境变量，默认 8000）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, os; port = os.getenv('PORT', '8000'); urllib.request.urlopen(f'http://localhost:{port}/health')"

# 启动命令（支持 PORT 环境变量）
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"

