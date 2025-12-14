# 生产环境部署指南

## 概述

本指南提供完整的生产环境部署步骤，确保系统安全、稳定地运行在生产环境中。

## 部署前准备

### 1. 系统要求检查

**硬件要求：**
- CPU: 2核心或以上
- 内存: 4GB RAM 或以上
- 存储: 20GB 可用空间
- 网络: 稳定的互联网连接，公网IP

**软件要求：**
- Python 3.9+
- PostgreSQL 12+ (推荐) 或 SQLite (开发/测试)
- Nginx (可选，用于反向代理)
- Git

### 2. 环境变量配置

创建 `.env` 文件，配置所有必需的环境变量：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/customer_service
DATABASE_ECHO=false

# Facebook配置
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_VERIFY_TOKEN=your_verify_token

# OpenAI配置
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Telegram配置
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 安全配置
SECRET_KEY=your_secret_key_min_32_chars
DEBUG=false

# CORS配置（生产环境必需）
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com

# 服务器配置
HOST=0.0.0.0
PORT=8000
```

### 3. 配置文件

确保 `config/config.yaml` 已正确配置：

```bash
# 检查配置文件
cat config/config.yaml
```

## 部署方式

### 方式1：直接部署（推荐用于VPS/云服务器）

#### 步骤1：准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和PostgreSQL
sudo apt install python3.9 python3-pip python3-venv postgresql postgresql-contrib nginx -y
```

#### 步骤2：克隆代码

```bash
# 创建应用目录
sudo mkdir -p /opt/customer-service
sudo chown $USER:$USER /opt/customer-service
cd /opt/customer-service

# 克隆代码（或上传代码）
git clone <your-repo-url> .
# 或使用 scp/rsync 上传代码
```

#### 步骤3：设置Python环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

#### 步骤4：配置数据库

```bash
# 创建PostgreSQL数据库
sudo -u postgres psql
CREATE DATABASE customer_service;
CREATE USER service_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE customer_service TO service_user;
\q

# 更新 .env 中的 DATABASE_URL
# DATABASE_URL=postgresql://service_user:your_secure_password@localhost:5432/customer_service
```

#### 步骤5：运行数据库迁移

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行迁移
alembic upgrade head
```

#### 步骤6：创建系统服务

创建 systemd 服务文件 `/etc/systemd/system/customer-service.service`：

```ini
[Unit]
Description=Customer Service API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/customer-service
Environment="PATH=/opt/customer-service/venv/bin"
ExecStart=/opt/customer-service/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start customer-service

# 设置开机自启
sudo systemctl enable customer-service

# 检查状态
sudo systemctl status customer-service
```

#### 步骤7：配置Nginx（可选）

创建 `/etc/nginx/sites-available/customer-service`：

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/customer-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 方式2：Docker部署

#### 步骤1：构建Docker镜像

```bash
docker build -t customer-service:latest .
```

#### 步骤2：运行容器

```bash
docker run -d \
  --name customer-service \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  customer-service:latest
```

#### 步骤3：使用Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: customer_service
      POSTGRES_USER: service_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

启动：

```bash
docker-compose up -d
```

### 方式3：云平台部署（Railway/Heroku/Render）

#### Railway部署

1. 连接GitHub仓库
2. 配置环境变量
3. 设置启动命令：`uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. 部署

#### Heroku部署

```bash
# 安装Heroku CLI
# 登录
heroku login

# 创建应用
heroku create your-app-name

# 设置环境变量
heroku config:set DATABASE_URL=...
heroku config:set FACEBOOK_APP_ID=...
# ... 其他环境变量

# 部署
git push heroku main
```

## 部署后验证

### 1. 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/health

# 或使用浏览器访问
# http://yourdomain.com/health
```

### 2. 功能测试

```bash
# 运行生产环境测试
python scripts/test/production_test.py --test all --url http://localhost:8000

# 运行负载测试
python scripts/test/load_test.py --users 20 --requests 10
```

### 3. 日志检查

```bash
# 查看服务日志
sudo journalctl -u customer-service -f

# 或查看应用日志
tail -f logs/app.log
```

### 4. 监控设置

```bash
# 启动性能监控
python scripts/monitoring/performance_monitor.py --interval 60
```

## 安全配置

### 1. 防火墙配置

```bash
# 只允许必要端口
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. SSL/TLS配置

使用Let's Encrypt获取免费SSL证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 3. 定期备份

设置数据库自动备份：

```bash
# 创建备份脚本
cat > /opt/customer-service/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/customer-service/backups"
mkdir -p $BACKUP_DIR
pg_dump customer_service > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/customer-service/scripts/backup.sh

# 添加到crontab（每天凌晨2点备份）
crontab -e
# 添加：0 2 * * * /opt/customer-service/scripts/backup.sh
```

## 维护和更新

### 更新代码

```bash
# 停止服务
sudo systemctl stop customer-service

# 备份
./scripts/backup_db.sh

# 更新代码
git pull origin main

# 安装新依赖
source venv/bin/activate
pip install -r requirements.txt

# 运行迁移
alembic upgrade head

# 启动服务
sudo systemctl start customer-service
```

### 查看日志

```bash
# 应用日志
tail -f logs/app.log

# 系统服务日志
sudo journalctl -u customer-service -f

# 错误日志
grep ERROR logs/app.log
```

## 故障排查

### 服务无法启动

1. 检查日志：`sudo journalctl -u customer-service -n 50`
2. 检查环境变量：`cat .env`
3. 检查数据库连接：`python -c "from src.core.database.connection import engine; engine.connect()"`
4. 检查端口占用：`sudo netstat -tlnp | grep 8000`

### 数据库连接失败

1. 检查PostgreSQL服务：`sudo systemctl status postgresql`
2. 检查数据库用户权限
3. 验证连接字符串格式

### 性能问题

1. 运行性能监控：`python scripts/monitoring/performance_monitor.py`
2. 检查资源使用：`htop` 或 `top`
3. 查看慢查询日志
4. 优化数据库索引

## 相关文档

- [CORS配置指南](CORS_CONFIGURATION.md)
- [PostgreSQL迁移指南](POSTGRESQL_MIGRATION.md)
- [告警配置指南](ALERT_CONFIGURATION.md)
- [生产环境测试流程](../testing/PRODUCTION_TESTING_FLOW.md)

