# 🚀 Zeabur 立即部署指南

## ✅ 已准备完成

- ✅ 代码已推送到GitHub
- ✅ SECRET_KEY需要生成：请生成32位以上随机字符串
- ✅ 所有部署文件已就绪

## 📋 部署步骤

### 步骤1：访问Zeabur并创建项目（2分钟）

1. 打开浏览器，访问：**https://zeabur.com**
2. 登录/注册账号（如果没有）
3. 点击 **"New Project"** 或 **"创建新项目"**
4. 选择 **"Deploy from GitHub"** 或 **"从GitHub部署"**
5. 授权Zeabur访问您的GitHub账号（如果首次使用）
6. 选择仓库：`vhsxy4pb7b-maker/my-telegram-bot33`
7. 选择分支：`main`
8. 点击 **"Deploy"** 或 **"部署"**

### 步骤2：添加PostgreSQL数据库（1分钟）

1. 在项目页面，点击 **"Add Service"** 或 **"添加服务"**
2. 选择 **"PostgreSQL"**
3. 等待数据库服务启动（约1-2分钟）
4. ✅ Zeabur会自动设置 `DATABASE_URL` 环境变量

### 步骤3：配置环境变量（5分钟）

在项目设置中找到 **"Environment Variables"** 或 **"环境变量"**，添加以下变量：

#### 🔐 必需的环境变量

```env
# Facebook配置
FACEBOOK_APP_ID=你的Facebook应用ID
FACEBOOK_APP_SECRET=你的Facebook应用密钥
FACEBOOK_ACCESS_TOKEN=你的用户级Token（有pages_show_list权限）
FACEBOOK_VERIFY_TOKEN=你的Webhook验证令牌

# OpenAI配置
OPENAI_API_KEY=sk-你的OpenAI密钥
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Telegram配置
TELEGRAM_BOT_TOKEN=你的Telegram Bot令牌
TELEGRAM_CHAT_ID=你的Telegram聊天ID

# 安全配置
SECRET_KEY=请生成32位以上随机字符串（不要使用示例值）
DEBUG=false

# CORS配置（部署后设置）
CORS_ORIGINS=https://your-app-name.zeabur.app
```

#### ⚠️ 重要提示

1. **FACEBOOK_ACCESS_TOKEN**：必须使用**用户级Token**（有`pages_show_list`权限），用于同步所有10+页面的Token
2. **DATABASE_URL**：Zeabur会自动设置，**无需手动配置**
3. **CORS_ORIGINS**：部署完成后，将获得应用URL（格式：`https://xxx.zeabur.app`），然后更新此变量

### 步骤4：等待部署完成（3-5分钟）

1. 查看构建日志，确认构建成功
2. 等待服务启动完成
3. 获取应用URL（格式：`https://xxx.zeabur.app`）
4. 记录此URL，后续需要用到

### 步骤5：更新CORS配置（1分钟）

1. 复制应用URL（例如：`https://my-app-123.zeabur.app`）
2. 在Zeabur环境变量中，更新 `CORS_ORIGINS`：
   ```
   CORS_ORIGINS=https://my-app-123.zeabur.app
   ```
3. 保存并等待服务重启

### 步骤6：运行数据库迁移（1分钟）

在Zeabur终端中运行：

alembic upgrade head
```

**如何访问终端：**
- 在Zeabur项目页面找到 **"Terminal"** 或 **"终端"** 选项
- 或点击服务名称，然后选择 **"Terminal"**

### 步骤7：同步所有页面Token（重要！2分钟）

```bash
python scripts/tools/manage_pages.py sync
```

**这会：**
- 使用 `FACEBOOK_ACCESS_TOKEN` 中的用户Token
- 自动获取所有10+页面的Token
- 保存到 `.page_tokens.json` 文件
- 自动为所有页面启用自动回复

### 步骤8：验证配置（1分钟）

```bash
# 查看所有已配置的页面
python scripts/tools/manage_pages.py status
```

应该看到所有10+页面都已配置。

### 步骤9：更新Facebook Webhook URL（2分钟）

1. 登录 **Facebook Developer Console**：https://developers.facebook.com
2. 进入您的应用设置
3. 找到 **Webhook** 配置
4. 更新 **Webhook URL** 为：`https://your-app-name.zeabur.app/webhook`
   - 将 `your-app-name` 替换为您的实际应用名称
5. 确认 **Verify Token** 与 `FACEBOOK_VERIFY_TOKEN` 环境变量一致
6. 点击 **"Verify and Save"**

### 步骤10：验证部署（1分钟）

访问健康检查端点：

```bash
# 在浏览器中访问
https://your-app-name.zeabur.app/health

# 或使用curl
curl https://your-app-name.zeabur.app/health
```

**预期响应：**
```json
{
  "status": "healthy",
  "timestamp": "...",
  "checks": {
    "database": {"status": "healthy"},
    "api_config": {"status": "healthy"},
    "resources": {"status": "healthy"}
  }
}
```

## 📝 环境变量检查清单

在Zeabur中配置时，请确认以下变量都已设置：

- [ ] `FACEBOOK_APP_ID`
- [ ] `FACEBOOK_APP_SECRET`
- [ ] `FACEBOOK_ACCESS_TOKEN`（用户级Token）
- [ ] `FACEBOOK_VERIFY_TOKEN`
- [ ] `OPENAI_API_KEY`
- [ ] `OPENAI_MODEL`（默认：gpt-4o-mini）
- [ ] `OPENAI_TEMPERATURE`（默认：0.7）
- [ ] `TELEGRAM_BOT_TOKEN`
- [ ] `TELEGRAM_CHAT_ID`
- [ ] `SECRET_KEY`（请生成32位以上随机字符串）
- [ ] `DEBUG=false`
- [ ] `CORS_ORIGINS`（部署后设置）
- [ ] `DATABASE_URL`（Zeabur自动设置，无需手动配置）

## ✅ 部署后验证清单

- [ ] 健康检查通过：`/health` 返回 `healthy`
- [ ] 数据库迁移成功：`alembic upgrade head` 无错误
- [ ] 所有页面Token已同步：`manage_pages.py status` 显示所有页面
- [ ] Facebook Webhook URL已更新
- [ ] 向测试页面发送消息，验证自动回复功能
- [ ] 检查日志，确认无错误

## 🆘 遇到问题？

### 问题1：部署失败

**检查：**
1. 查看构建日志，确认错误信息
2. 检查 `requirements.txt` 是否完整
3. 确认Python版本兼容

### 问题2：数据库连接失败

**解决：**
1. 确认PostgreSQL服务已启动
2. 检查 `DATABASE_URL` 环境变量（Zeabur自动设置）
3. 运行迁移：`alembic upgrade head`

### 问题3：页面Token同步失败

**解决：**
1. 确认 `FACEBOOK_ACCESS_TOKEN` 是用户级Token
2. 确认Token有 `pages_show_list` 权限
3. 检查Token是否过期
4. 查看日志确认错误信息

### 问题4：Webhook验证失败

**解决：**
1. 确认 `FACEBOOK_VERIFY_TOKEN` 与Facebook配置一致
2. 确认Webhook URL正确
3. 检查应用日志

## 📚 相关文档

- [快速部署指南](QUICK_DEPLOY.md)
- [详细部署步骤](ZEABUR_DEPLOY_STEPS.md)
- [部署检查清单](ZEABUR_DEPLOY_CHECKLIST.md)
- [多页面配置指南](ZEABUR_MULTI_PAGE_SETUP.md)
- [环境变量详细说明](ZEABUR_ENV_VARS.md)

## 🎉 部署完成！

部署成功后，您的系统将：
- ✅ 自动接收Facebook/Instagram消息
- ✅ 使用AI自动回复
- ✅ 支持10+个页面同时运行
- ✅ 发送Telegram通知
- ✅ 记录统计信息

祝部署顺利！🚀

