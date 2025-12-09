# Railway 部署指南

## 📋 目录

1. [Railway 简介](#railway-简介)
2. [准备工作](#准备工作)
3. [部署步骤](#部署步骤)
4. [环境变量配置](#环境变量配置)
5. [数据库配置](#数据库配置)
6. [域名配置](#域名配置)
7. [Webhook 配置](#webhook-配置)
8. [监控和维护](#监控和维护)

---

## Railway 简介

Railway 是一个现代化的云平台即服务（PaaS），支持：
- ✅ 自动部署（从 Git 仓库）
- ✅ 内置 PostgreSQL 数据库
- ✅ 自动 HTTPS
- ✅ 环境变量管理
- ✅ 日志查看
- ✅ 免费额度

---

## 准备工作

### 1. 创建 Railway 账号

访问 [railway.app](https://railway.app) 注册账号（可以使用 GitHub 账号登录）

### 2. 准备项目

确保项目包含以下文件：
- ✅ `requirements.txt` - Python 依赖
- ✅ `railway.json` 或 `railway.toml` - Railway 配置（已创建）
- ✅ `Procfile` - 启动命令（已创建）
- ✅ `config.yaml.example` - 配置文件示例

---

## 部署步骤

### 方式 1: 从 GitHub 部署（推荐）

#### 步骤 1: 推送代码到 GitHub

```bash
# 如果还没有 Git 仓库
git init
git add .
git commit -m "Initial commit"

# 创建 GitHub 仓库并推送
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

#### 步骤 2: 在 Railway 创建项目

1. 登录 Railway
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择你的仓库
5. Railway 会自动检测并开始部署

#### 步骤 3: 配置环境变量

在 Railway 项目页面：
1. 点击项目
2. 选择 "Variables" 标签
3. 添加所有必需的环境变量（见下方配置）

#### 步骤 4: 添加 PostgreSQL 数据库

1. 在项目页面点击 "New"
2. 选择 "Database" → "Add PostgreSQL"
3. Railway 会自动创建数据库并设置 `DATABASE_URL` 环境变量

### 方式 2: 使用 Railway CLI

#### 安装 Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (使用 PowerShell)
iwr https://railway.app/install.ps1 -useb | iex
```

#### 登录和部署

```bash
# 登录
railway login

# 初始化项目
railway init

# 链接到现有项目或创建新项目
railway link

# 部署
railway up
```

---

## 环境变量配置

在 Railway 项目页面 → Variables 中添加以下环境变量：

### 必需配置

```env
# 数据库（Railway 会自动提供，但可以手动设置）
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Facebook 配置
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_VERIFY_TOKEN=your_facebook_verify_token

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Telegram 配置
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# 安全配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256

# 服务器配置
HOST=0.0.0.0
PORT=$PORT
DEBUG=false
```

### 可选配置

```env
# Instagram 配置
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_VERIFY_TOKEN=your_instagram_verify_token
INSTAGRAM_USER_ID=your_instagram_user_id

# 第三方集成
MANYCHAT_API_KEY=your_manychat_api_key
BOTCAKE_API_KEY=your_botcake_api_key
```

### 使用 Railway 变量引用

Railway 支持变量引用，可以使用 `${{Service.VariableName}}` 格式：

```env
# 引用 PostgreSQL 数据库 URL
DATABASE_URL=${{Postgres.DATABASE_URL}}

# 引用其他服务的变量
CUSTOM_VAR=${{OtherService.VARIABLE_NAME}}
```

---

## 数据库配置

### 自动配置（推荐）

Railway 会自动：
1. 创建 PostgreSQL 数据库
2. 设置 `DATABASE_URL` 环境变量
3. 在服务重启时自动连接

### 手动配置

如果需要手动配置：

1. 在项目页面添加 PostgreSQL 服务
2. 复制数据库连接字符串
3. 在环境变量中设置 `DATABASE_URL`

### 运行数据库迁移

Railway 部署后，需要运行数据库迁移：

#### 方式 1: 使用 Railway CLI

```bash
railway run alembic upgrade head
```

#### 方式 2: 使用 Railway Shell

1. 在项目页面点击 "Shell"
2. 运行：
```bash
alembic upgrade head
```

#### 方式 3: 在启动时自动运行

修改 `Procfile` 或启动命令：

```bash
# Procfile
web: alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

---

## 域名配置

### 获取 Railway 域名

Railway 会自动为每个服务分配一个域名：
- 格式：`your-service-name.up.railway.app`
- 自动启用 HTTPS

### 自定义域名

1. 在项目页面选择服务
2. 点击 "Settings" → "Networking"
3. 点击 "Custom Domain"
4. 输入你的域名
5. 按照提示配置 DNS 记录

DNS 配置示例：
```
类型: CNAME
名称: @ 或 www
值: your-service-name.up.railway.app
```

---

## Webhook 配置

### Facebook Webhook

1. 获取 Railway 域名（如：`your-service.up.railway.app`）
2. 在 Facebook 开发者控制台配置：
   - **Webhook URL**: `https://your-service.up.railway.app/webhook`
   - **Verify Token**: 使用 `.env` 中的 `FACEBOOK_VERIFY_TOKEN`
   - **订阅事件**: `messages`, `messaging_postbacks`, `feed`

### Telegram Webhook

Telegram Bot 通常使用长轮询，不需要 Webhook。如果需要 Webhook：

```bash
# 使用 Railway CLI 或 API 设置
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -d "url=https://your-service.up.railway.app/telegram/webhook"
```

---

## 监控和维护

### 查看日志

#### 在 Railway 网站

1. 选择项目和服务
2. 点击 "Deployments" 标签
3. 选择部署版本
4. 查看实时日志

#### 使用 Railway CLI

```bash
# 查看日志
railway logs

# 实时日志
railway logs --follow
```

### 查看指标

在 Railway 项目页面可以查看：
- CPU 使用率
- 内存使用率
- 网络流量
- 请求数

### 重启服务

```bash
# 使用 CLI
railway restart

# 或在网站点击 "Redeploy"
```

### 环境变量管理

```bash
# 查看环境变量
railway variables

# 设置环境变量
railway variables set KEY=value

# 删除环境变量
railway variables unset KEY
```

---

## 配置文件管理

### config.yaml

Railway 不支持直接上传文件，有几种方式处理 `config.yaml`：

#### 方式 1: 使用环境变量（推荐）

将配置转换为环境变量，在代码中读取。

#### 方式 2: 使用 Railway Volume

1. 在项目页面添加 "Volume"
2. 上传 `config.yaml` 文件
3. 挂载到容器

#### 方式 3: 在代码中生成

在应用启动时检查 `config.yaml`，如果不存在则从环境变量生成。

---

## 故障排查

### 部署失败

```bash
# 查看部署日志
railway logs

# 检查环境变量
railway variables

# 测试本地运行
python run.py
```

### 数据库连接失败

1. 检查 `DATABASE_URL` 环境变量
2. 确认 PostgreSQL 服务正在运行
3. 检查数据库迁移是否完成

### 服务无法启动

1. 检查启动命令是否正确
2. 查看日志中的错误信息
3. 验证所有必需的环境变量已设置

### 端口问题

Railway 使用 `$PORT` 环境变量，确保启动命令使用：
```bash
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

---

## 最佳实践

### 1. 使用 Railway 变量引用

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### 2. 敏感信息使用 Secrets

Railway 会自动加密环境变量，但建议：
- 不要在代码中硬编码密钥
- 使用 Railway 的 Secrets 功能
- 定期轮换密钥

### 3. 数据库迁移

在每次部署时自动运行迁移：
```bash
# 在 Procfile 中
web: alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### 4. 健康检查

确保 `/health` 端点正常工作，Railway 会使用它进行健康检查。

### 5. 日志管理

- 使用结构化日志
- 避免记录敏感信息
- 定期清理旧日志

---

## 部署检查清单

### 部署前
- [ ] Railway 账号已创建
- [ ] 代码已推送到 GitHub
- [ ] 所有环境变量已准备
- [ ] 配置文件已准备

### 部署中
- [ ] 项目已创建
- [ ] 代码已部署
- [ ] PostgreSQL 数据库已添加
- [ ] 环境变量已配置
- [ ] 数据库迁移已运行

### 部署后
- [ ] 服务正常运行
- [ ] 健康检查通过
- [ ] API 文档可访问
- [ ] Webhook 已配置
- [ ] 域名已配置（如需要）
- [ ] 日志正常输出

---

## 常用命令

```bash
# 登录
railway login

# 初始化项目
railway init

# 链接项目
railway link

# 部署
railway up

# 查看日志
railway logs

# 运行命令
railway run <command>

# 查看变量
railway variables

# 设置变量
railway variables set KEY=value

# 重启服务
railway restart
```

---

## 相关文档

- [Railway 官方文档](https://docs.railway.app)
- [Railway CLI 文档](https://docs.railway.app/develop/cli)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [服务器部署](SERVER_DEPLOYMENT.md)

---

## 快速开始

1. **创建 Railway 账号**: https://railway.app
2. **连接 GitHub 仓库**: 在 Railway 中导入项目
3. **添加 PostgreSQL**: 在项目中添加数据库服务
4. **配置环境变量**: 在 Variables 中添加所有配置
5. **部署**: Railway 会自动部署
6. **运行迁移**: `railway run alembic upgrade head`
7. **配置 Webhook**: 使用 Railway 提供的域名

完成！🎉




