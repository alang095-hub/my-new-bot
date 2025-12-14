# Zeabur 部署步骤（详细版）

## 部署前最后检查

### 1. 确认环境变量已准备

确保您已准备好以下环境变量的值：

- [ ] `FACEBOOK_ACCESS_TOKEN` - 用户级Token（用于同步10+页面）
- [ ] `FACEBOOK_APP_ID` - Facebook应用ID
- [ ] `FACEBOOK_APP_SECRET` - Facebook应用密钥
- [ ] `FACEBOOK_VERIFY_TOKEN` - Webhook验证令牌
- [ ] `OPENAI_API_KEY` - OpenAI API密钥
- [ ] `TELEGRAM_BOT_TOKEN` - Telegram Bot令牌
- [ ] `TELEGRAM_CHAT_ID` - Telegram聊天ID
- [ ] `SECRET_KEY` - 应用密钥（至少32字符）
- [ ] `DEBUG=false` - 生产环境必须
- [ ] `CORS_ORIGINS` - CORS允许的来源

### 2. 确认代码已准备

- [ ] 代码已推送到GitHub（如果使用GitHub部署）
- [ ] 所有文件已保存
- [ ] 本地测试已通过

## 部署步骤

### 步骤1：访问Zeabur并创建项目

1. 访问 https://zeabur.com
2. 登录/注册账号
3. 点击 **"New Project"** 或 **"创建新项目"**
4. 选择 **"Deploy from GitHub"** 或 **"从GitHub部署"**

### 步骤2：连接GitHub仓库

1. 授权Zeabur访问您的GitHub账号
2. 选择包含项目代码的仓库
3. 选择分支（通常是 `main` 或 `master`）
4. 点击 **"Deploy"** 或 **"部署"**

### 步骤3：添加PostgreSQL数据库

1. 在项目页面，点击 **"Add Service"** 或 **"添加服务"**
2. 选择 **"PostgreSQL"**
3. Zeabur会自动创建数据库并设置 `DATABASE_URL` 环境变量
4. 等待数据库服务启动完成

### 步骤4：配置环境变量

在项目设置中找到 **"Environment Variables"** 或 **"环境变量"**，添加以下变量：

#### 必需的环境变量

```
DATABASE_URL=postgresql://...  # Zeabur自动设置，无需手动配置

FACEBOOK_APP_ID=你的Facebook应用ID
FACEBOOK_APP_SECRET=你的Facebook应用密钥
FACEBOOK_ACCESS_TOKEN=你的用户级Token（有pages_show_list权限）
FACEBOOK_VERIFY_TOKEN=你的Webhook验证令牌

OPENAI_API_KEY=sk-你的OpenAI密钥
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

TELEGRAM_BOT_TOKEN=你的Telegram Bot令牌
TELEGRAM_CHAT_ID=你的Telegram聊天ID

SECRET_KEY=你的32字符密钥（至少32字符）
DEBUG=false

CORS_ORIGINS=https://your-app-name.zeabur.app
```

#### 重要提示

- **FACEBOOK_ACCESS_TOKEN**：必须使用**用户级Token**（有`pages_show_list`权限），用于同步所有10+页面的Token
- **SECRET_KEY**：可以使用以下Python命令生成：
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```
- **CORS_ORIGINS**：部署后会获得一个URL，格式类似 `https://xxx.zeabur.app`，将其添加到CORS_ORIGINS

### 步骤5：等待部署完成

1. 查看部署日志，确认构建成功
2. 等待服务启动完成
3. 获取应用URL（格式：`https://xxx.zeabur.app`）

### 步骤6：运行数据库迁移

部署完成后，通过Zeabur的终端/SSH连接运行：

```bash
alembic upgrade head
```

**如何访问终端：**
- 在Zeabur项目页面找到 **"Terminal"** 或 **"终端"** 选项
- 或使用SSH连接到容器

### 步骤7：同步所有页面Token（重要！）

```bash
python scripts/tools/manage_pages.py sync
```

**这会：**
- 使用 `FACEBOOK_ACCESS_TOKEN` 中的用户Token
- 自动获取所有10+页面的Token
- 保存到 `.page_tokens.json` 文件
- 自动为所有页面启用自动回复

### 步骤8：验证配置

```bash
# 查看所有已配置的页面
python scripts/tools/manage_pages.py status
```

应该看到所有10+页面都已配置。

### 步骤9：更新Facebook Webhook URL

1. 登录 Facebook Developer Console
2. 进入您的应用设置
3. 找到 Webhook 配置
4. 更新 Webhook URL 为：`https://your-app-name.zeabur.app/webhook`
5. 确认 Verify Token 与 `FACEBOOK_VERIFY_TOKEN` 环境变量一致

### 步骤10：验证部署

```bash
# 健康检查
curl https://your-app-name.zeabur.app/health

# 或使用浏览器访问
# https://your-app-name.zeabur.app/health
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

## 部署后验证清单

- [ ] 健康检查通过
- [ ] 数据库迁移成功
- [ ] 所有页面Token已同步（10+页面）
- [ ] Facebook Webhook URL已更新
- [ ] 向测试页面发送消息，验证自动回复
- [ ] 检查日志，确认无错误

## 常见问题

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

## 部署完成后的维护

### 定期任务

1. **每月同步Token**（Token会过期）：
   ```bash
   python scripts/tools/manage_pages.py sync
   ```

2. **监控日志**：定期查看应用日志

3. **备份数据**：定期备份数据库

### 更新代码

1. 推送代码到GitHub
2. Zeabur会自动检测并重新部署
3. 或手动触发部署

## 相关文档

- [Zeabur快速部署](ZEABUR_QUICK_START.md)
- [多页面用户Token配置](MULTI_PAGE_USER_TOKEN_CONFIG.md)
- [环境变量详细说明](ZEABUR_ENV_VARS.md)

