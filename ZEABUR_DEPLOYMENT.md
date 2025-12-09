# Zeabur 部署指南

## 📋 目录

1. [Zeabur 简介](#zeabur-简介)
2. [部署步骤](#部署步骤)
3. [环境变量配置](#环境变量配置)
4. [数据库配置](#数据库配置)
5. [域名配置](#域名配置)
6. [Webhook 配置](#webhook-配置)
7. [故障排查](#故障排查)

---

## Zeabur 简介

Zeabur 是一个现代化的云平台即服务（PaaS），支持：
- ✅ 自动部署（从 Git 仓库）
- ✅ 内置 PostgreSQL 数据库
- ✅ 自动 HTTPS
- ✅ 环境变量管理
- ✅ 日志查看
- ✅ 免费额度

---

## 部署步骤

### 步骤 1: 创建 Zeabur 项目

1. **访问**: https://zeabur.com
2. **登录**: 使用 GitHub 账号登录
3. **创建项目**:
   - 点击 "New Project" 或 "+" 按钮
   - 选择 "Import from GitHub"
   - 选择仓库: `vhsxy4pb7b-maker/my-telegram-bot33`
   - Zeabur 会自动检测项目类型并开始部署

### 步骤 2: 配置项目设置

Zeabur 会自动检测到 Python 项目，但可能需要确认：

1. **构建命令**（如果需要）:
   ```
   pip install -r requirements.txt
   ```

2. **启动命令**:
   ```
   uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

3. **端口**: Zeabur 会自动设置 `$PORT` 环境变量

### 步骤 3: 添加 PostgreSQL 数据库

1. 在项目页面，点击 **"Add Service"** 或 **"+"** 按钮
2. 选择 **"Database"** → **"PostgreSQL"**
3. Zeabur 会自动：
   - 创建 PostgreSQL 数据库
   - 设置 `DATABASE_URL` 环境变量
   - 连接到你的应用

### 步骤 4: 配置环境变量

1. 在项目页面，点击你的**应用服务**
2. 进入 **"Environment Variables"** 或 **"Variables"** 标签
3. 点击 **"Add Variable"** 或 **"+"** 按钮
4. 逐个添加以下变量：

#### 必需变量：

```
FACEBOOK_APP_ID=你的Facebook应用ID
FACEBOOK_APP_SECRET=你的Facebook应用密钥
FACEBOOK_ACCESS_TOKEN=你的Facebook访问令牌
FACEBOOK_VERIFY_TOKEN=你的Facebook验证令牌（自定义字符串）
OPENAI_API_KEY=你的OpenAI API密钥
TELEGRAM_BOT_TOKEN=你的Telegram Bot令牌
TELEGRAM_CHAT_ID=你的Telegram聊天ID
SECRET_KEY=YB-Y7XHm6JuFqMl1fJOuFRLgUEJZPG2x5lQnVC_tJ2U
```

#### 可选变量：

```
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
HOST=0.0.0.0
PORT=$PORT
DEBUG=false
```

**注意**: `DATABASE_URL` 由 Zeabur 自动设置，无需手动添加

### 步骤 5: 运行数据库迁移

部署完成后，需要运行数据库迁移：

#### 方式 1: 使用 Zeabur CLI

```bash
# 1. 安装 Zeabur CLI
npm i -g @zeabur/cli

# 2. 登录
zeabur login

# 3. 链接项目
zeabur link

# 4. 运行迁移
zeabur exec alembic upgrade head
```

#### 方式 2: 使用 Zeabur Web Terminal

1. 在 Zeabur 项目页面，点击你的应用服务
2. 点击 **"Terminal"** 或 **"Console"** 标签
3. 运行：
```bash
alembic upgrade head
```

### 步骤 6: 获取部署 URL

1. 在项目页面，点击你的应用服务
2. 查看 **"Domains"** 或 **"URL"** 部分
3. 你会看到类似：
   ```
   your-service.zeabur.app
   ```
4. **复制这个 URL**，用于配置 Webhook

### 步骤 7: 配置 Facebook Webhook

1. 打开 [Facebook 开发者控制台](https://developers.facebook.com/)
2. 进入你的应用
3. 进入 **"Webhooks"** 设置
4. 配置：
   - **Callback URL**: `https://your-service.zeabur.app/webhook`
   - **Verify Token**: 使用环境变量中的 `FACEBOOK_VERIFY_TOKEN`
   - **订阅事件**: `messages`, `messaging_postbacks`, `feed`
5. 点击 **"Verify and Save"**

---

## 环境变量配置

### 必需变量列表

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `FACEBOOK_APP_ID` | Facebook 应用 ID | `1234567890` |
| `FACEBOOK_APP_SECRET` | Facebook 应用密钥 | `abc123...` |
| `FACEBOOK_ACCESS_TOKEN` | Facebook 访问令牌 | `EAABwz...` |
| `FACEBOOK_VERIFY_TOKEN` | Webhook 验证令牌 | `my_verify_token_123` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-...` |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot 令牌 | `123456:ABC...` |
| `TELEGRAM_CHAT_ID` | Telegram 聊天 ID | `123456789` |
| `SECRET_KEY` | 应用密钥 | `YB-Y7XHm6JuFqMl1fJOuFRLgUEJZPG2x5lQnVC_tJ2U` |

### 使用 Zeabur 变量引用

Zeabur 支持变量引用，可以使用 `${{Service.VariableName}}` 格式：

```env
# 引用 PostgreSQL 数据库 URL
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
```

---

## 数据库配置

### 自动配置（推荐）

Zeabur 会自动：
1. 创建 PostgreSQL 数据库
2. 设置 `DATABASE_URL` 环境变量
3. 在服务重启时自动连接

### 手动配置

如果需要手动配置：

1. 在项目页面添加 PostgreSQL 服务
2. 复制数据库连接字符串
3. 在环境变量中设置 `DATABASE_URL`

---

## 域名配置

### 获取 Zeabur 域名

Zeabur 会自动为每个服务分配域名：
- 格式：`your-service.zeabur.app`
- 自动启用 HTTPS

### 自定义域名

1. 在项目页面，点击你的应用服务
2. 进入 **"Domains"** 设置
3. 点击 **"Add Custom Domain"**
4. 输入你的域名
5. 按照提示配置 DNS 记录

---

## Webhook 配置

### Facebook Webhook

1. 获取 Zeabur 域名（如：`your-service.zeabur.app`）
2. 在 Facebook 开发者控制台配置：
   - **Webhook URL**: `https://your-service.zeabur.app/webhook`
   - **Verify Token**: 使用 `.env` 中的 `FACEBOOK_VERIFY_TOKEN`
   - **订阅事件**: `messages`, `messaging_postbacks`, `feed`

### Telegram Webhook

Telegram Bot 通常使用长轮询，不需要 Webhook。如果需要：

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -d "url=https://your-service.zeabur.app/telegram/webhook"
```

---

## 监控和维护

### 查看日志

#### 在 Zeabur 网站

1. 选择项目和服务
2. 点击 **"Logs"** 标签
3. 查看实时日志

#### 使用 Zeabur CLI

```bash
# 查看日志
zeabur logs

# 实时日志
zeabur logs --follow
```

### 查看指标

在 Zeabur 项目页面可以查看：
- CPU 使用率
- 内存使用率
- 网络流量
- 请求数

### 重启服务

```bash
# 使用 CLI
zeabur restart

# 或在网站点击 "Redeploy"
```

---

## 故障排查

### 部署失败

**检查**:
- 查看 Zeabur 部署日志
- 确认所有必需的环境变量已设置
- 检查 `requirements.txt` 是否正确

**解决**:
- 修复错误后，Zeabur 会自动重新部署
- 或手动点击 "Redeploy"

### 数据库连接失败

**检查**:
- 确认 PostgreSQL 服务已添加
- 检查 `DATABASE_URL` 环境变量
- 运行数据库迁移

**解决**:
```bash
zeabur exec alembic upgrade head
```

### 环境变量错误

如果看到类似错误：
```
facebook_verify_token Field required
```

**解决**:
1. 在 Zeabur 项目页面 → Environment Variables
2. 添加所有必需的环境变量
3. Zeabur 会自动重新部署

### 服务无法启动

**检查**:
- 查看 Zeabur 日志
- 确认所有必需的环境变量已设置
- 验证启动命令正确（使用 `$PORT`）

---

## 部署检查清单

### 部署前
- [ ] Zeabur 账号已创建
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
# Zeabur CLI
zeabur login              # 登录
zeabur link               # 链接项目
zeabur logs               # 查看日志
zeabur exec <command>      # 执行命令
zeabur restart            # 重启服务
zeabur variables          # 查看变量
```

---

## 相关文档

- [Zeabur 官方文档](https://zeabur.com/docs)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [服务器部署](SERVER_DEPLOYMENT.md)

---

## 快速开始

1. **访问 Zeabur**: https://zeabur.com
2. **连接 GitHub 仓库**: 导入 `my-telegram-bot33`
3. **添加 PostgreSQL**: 在项目中添加数据库服务
4. **配置环境变量**: 在 Variables 中添加所有配置
5. **部署**: Zeabur 会自动部署
6. **运行迁移**: `zeabur exec alembic upgrade head`
7. **配置 Webhook**: 使用 Zeabur 提供的域名

完成！🎉




