# 🐳 容器部署完整指南

## 📖 概述

本指南介绍如何使用 Docker 容器部署应用，包括：
- 本地 Docker 部署（开发和测试）
- Zeabur 容器部署（生产环境）
- Docker Compose 部署（本地完整环境）

## 🎯 部署方式对比

| 方式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **本地 Docker** | 本地开发、测试 | 环境一致、易于调试 | 需要本地 Docker |
| **Zeabur 容器** | 生产环境 | 自动管理、易于扩展 | 需要 Zeabur 账号 |
| **Docker Compose** | 本地完整环境 | 包含数据库、一键启动 | 资源占用较大 |

## 🚀 方式1：本地 Docker 部署

### 前置要求

1. **安装 Docker**
   - Windows: 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Mac: 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux: 
     ```bash
     curl -fsSL https://get.docker.com -o get-docker.sh
     sh get-docker.sh
     ```

2. **验证 Docker 安装**
   ```bash
   docker --version
   docker-compose --version
   ```

### 步骤1：准备环境变量

创建 `.env` 文件（如果还没有）：

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 文件，填入所有必需的环境变量
```

**必需的环境变量：**
```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_VERIFY_TOKEN=your_verify_token

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 安全
SECRET_KEY=your_secret_key
DEBUG=false

# 服务器
PORT=8000
HOST=0.0.0.0
```

### 步骤2：构建 Docker 镜像

```bash
# 在项目根目录执行
docker build -t my-telegram-bot:latest .
```

**构建过程：**
- 下载 Python 3.9 基础镜像
- 安装系统依赖（PostgreSQL 客户端、gcc）
- 安装 Python 依赖包
- 复制应用代码
- 创建非 root 用户

**构建时间：** 约 3-5 分钟（首次构建）

### 步骤3：运行容器

#### 基本运行

```bash
docker run -d \
  --name my-telegram-bot \
  -p 8000:8000 \
  --env-file .env \
  my-telegram-bot:latest
```

#### 带数据卷的运行（持久化日志）

```bash
docker run -d \
  --name my-telegram-bot \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  my-telegram-bot:latest
```

#### 使用环境变量（不依赖 .env 文件）

```bash
docker run -d \
  --name my-telegram-bot \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e FACEBOOK_APP_ID="..." \
  -e FACEBOOK_APP_SECRET="..." \
  -e FACEBOOK_ACCESS_TOKEN="..." \
  -e FACEBOOK_VERIFY_TOKEN="..." \
  -e OPENAI_API_KEY="..." \
  -e TELEGRAM_BOT_TOKEN="..." \
  -e TELEGRAM_CHAT_ID="..." \
  -e SECRET_KEY="..." \
  -e PORT=8000 \
  my-telegram-bot:latest
```

### 步骤4：验证部署

#### 检查容器状态

```bash
# 查看运行中的容器
docker ps

# 查看容器日志
docker logs my-telegram-bot

# 实时查看日志
docker logs -f my-telegram-bot
```

#### 测试健康检查

```bash
# 测试健康端点
curl http://localhost:8000/health

# 或使用浏览器访问
# http://localhost:8000/health
```

**预期响应：**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-15T12:00:00Z"
}
```

### 步骤5：运行数据库迁移

```bash
# 进入容器
docker exec -it my-telegram-bot bash

# 运行迁移
alembic upgrade head

# 退出容器
exit
```

**或直接执行命令：**
```bash
docker exec my-telegram-bot alembic upgrade head
```

## 🐙 方式2：Zeabur 容器部署

Zeabur 自动使用容器部署，您只需要：

### 步骤1：连接 GitHub 仓库

1. 访问 [Zeabur](https://zeabur.com)
2. 创建新项目
3. 选择 "Import from GitHub"
4. 选择您的仓库

### 步骤2：添加 PostgreSQL 数据库

1. 在项目中点击 "Add Service"
2. 选择 "PostgreSQL"
3. Zeabur 会自动创建数据库并设置 `DATABASE_URL`

### 步骤3：配置环境变量

在服务设置中，添加所有必需的环境变量：

```
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_VERIFY_TOKEN=...
OPENAI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
SECRET_KEY=...
PORT=8080
DEBUG=false
```

### 步骤4：部署

Zeabur 会自动：
1. 检测 Dockerfile（如果有）
2. 或使用 NIXPACKS 构建容器
3. 运行构建命令
4. 启动容器
5. 运行 postDeploy 命令（数据库迁移）

### 步骤5：验证

```bash
# 使用检查脚本
python scripts/tools/check_zeabur_deployment.py
```

**详细指南：** [Zeabur 部署指南](ZEABUR_DEPLOY_NOW.md)

## 🎼 方式3：Docker Compose 部署（本地完整环境）

Docker Compose 可以同时启动应用和数据库。

### 步骤1：创建 docker-compose.yml

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    container_name: my-telegram-bot-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: facebook_customer_service
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 应用服务
  app:
    build: .
    container_name: my-telegram-bot-app
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/facebook_customer_service
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  postgres_data:
```

### 步骤2：启动所有服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务的日志
docker-compose logs -f app
docker-compose logs -f postgres
```

### 步骤3：运行数据库迁移

```bash
# 在应用容器中运行迁移
docker-compose exec app alembic upgrade head
```

### 步骤4：停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（⚠️ 会删除数据库数据）
docker-compose down -v
```

## 🔧 容器管理命令

### 查看容器

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 查看容器详细信息
docker inspect my-telegram-bot
```

### 容器日志

```bash
# 查看日志
docker logs my-telegram-bot

# 实时查看日志
docker logs -f my-telegram-bot

# 查看最后 100 行日志
docker logs --tail 100 my-telegram-bot

# 查看特定时间段的日志
docker logs --since 30m my-telegram-bot
```

### 进入容器

```bash
# 进入容器（bash）
docker exec -it my-telegram-bot bash

# 进入容器（sh，如果 bash 不可用）
docker exec -it my-telegram-bot sh

# 执行单个命令
docker exec my-telegram-bot python --version
docker exec my-telegram-bot alembic current
```

### 停止和启动

```bash
# 停止容器
docker stop my-telegram-bot

# 启动容器
docker start my-telegram-bot

# 重启容器
docker restart my-telegram-bot

# 删除容器（必须先停止）
docker rm my-telegram-bot
```

### 更新容器

```bash
# 1. 停止并删除旧容器
docker stop my-telegram-bot
docker rm my-telegram-bot

# 2. 重新构建镜像（如果有代码更新）
docker build -t my-telegram-bot:latest .

# 3. 运行新容器
docker run -d \
  --name my-telegram-bot \
  -p 8000:8000 \
  --env-file .env \
  my-telegram-bot:latest
```

## 🐛 调试和故障排除

### 问题1：容器无法启动

**检查日志：**
```bash
docker logs my-telegram-bot
```

**常见原因：**
- 环境变量缺失
- 数据库连接失败
- 端口被占用

**解决方法：**
1. 检查 `.env` 文件是否完整
2. 确认数据库服务已启动
3. 检查端口是否被占用：`netstat -an | grep 8000`

### 问题2：数据库连接失败

**测试数据库连接：**
```bash
# 进入容器
docker exec -it my-telegram-bot bash

# 测试连接
python -c "from src.core.database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print('OK'); conn.close()"
```

**如果使用 Docker Compose：**
- 确认 `depends_on` 配置正确
- 确认 `DATABASE_URL` 使用服务名（`postgres`）而不是 `localhost`

### 问题3：端口冲突

**检查端口占用：**
```bash
# Windows
netstat -an | findstr 8000

# Linux/Mac
lsof -i :8000
```

**解决方法：**
- 修改容器端口映射：`-p 8001:8000`（主机 8001，容器 8000）
- 或停止占用端口的其他服务

### 问题4：容器健康检查失败

**查看健康检查状态：**
```bash
docker inspect my-telegram-bot | grep -A 10 Health
```

**手动测试健康端点：**
```bash
docker exec my-telegram-bot curl http://localhost:8000/health
```

**如果失败：**
- 检查应用是否正常启动
- 检查 `/health` 端点是否可访问
- 查看应用日志找出错误

### 问题5：代码更新未生效

**原因：** Docker 镜像包含的是构建时的代码，不会自动更新。

**解决方法：**
```bash
# 1. 重新构建镜像
docker build -t my-telegram-bot:latest .

# 2. 停止并删除旧容器
docker stop my-telegram-bot
docker rm my-telegram-bot

# 3. 运行新容器
docker run -d --name my-telegram-bot -p 8000:8000 --env-file .env my-telegram-bot:latest
```

**或使用开发模式（代码挂载）：**
```bash
docker run -d \
  --name my-telegram-bot-dev \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/src:/app/src \
  my-telegram-bot:latest \
  python run.py
```

## 📊 性能优化

### 多阶段构建（减小镜像大小）

更新 `Dockerfile`：

```dockerfile
# 构建阶段
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
# ... 其余配置
```

### 使用 .dockerignore

确保 `.dockerignore` 包含不需要的文件：

```
__pycache__
*.pyc
.git
.env
*.md
logs/
```

### 资源限制

```bash
docker run -d \
  --name my-telegram-bot \
  --memory="512m" \
  --cpus="1.0" \
  -p 8000:8000 \
  --env-file .env \
  my-telegram-bot:latest
```

## 🔒 安全最佳实践

### 1. 使用非 root 用户

Dockerfile 中已包含：
```dockerfile
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

### 2. 不要将敏感信息写入镜像

- 使用环境变量
- 使用 `.env` 文件（不要提交到 Git）
- 使用 Docker secrets（生产环境）

### 3. 定期更新基础镜像

```dockerfile
FROM python:3.9-slim  # 定期更新到最新版本
```

### 4. 扫描镜像漏洞

```bash
# 使用 Docker Scout（如果可用）
docker scout cves my-telegram-bot:latest
```

## 📚 相关文档

- [Zeabur 部署指南](ZEABUR_DEPLOY_NOW.md)
- [Zeabur Docker 容器使用](ZEABUR_DOCKER_GUIDE.md)
- [环境变量配置](ZEABUR_ENV_VARS_TEMPLATE.txt)
- [数据库连接修复](FIX_DATABASE_CONNECTION.md)

## 🎯 快速参考

### 本地 Docker 部署（一键）

```bash
# 构建
docker build -t my-telegram-bot:latest .

# 运行
docker run -d --name my-telegram-bot -p 8000:8000 --env-file .env my-telegram-bot:latest

# 查看日志
docker logs -f my-telegram-bot

# 运行迁移
docker exec my-telegram-bot alembic upgrade head
```

### Docker Compose 部署（一键）

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 运行迁移
docker-compose exec app alembic upgrade head

# 停止
docker-compose down
```

## 🆘 需要帮助？

如果遇到问题：
1. 查看容器日志：`docker logs my-telegram-bot`
2. 进入容器调试：`docker exec -it my-telegram-bot bash`
3. 检查环境变量：`docker exec my-telegram-bot env`
4. 提供错误信息，我会帮您解决！



