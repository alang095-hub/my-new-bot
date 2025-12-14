# Zeabur 快速部署指南

## 5分钟快速部署

### 步骤1：准备代码（1分钟）

```bash
# 确保代码已提交到GitHub
git add .
git commit -m "准备部署到Zeabur"
git push origin main
```

### 步骤2：创建Zeabur项目（1分钟）

1. 访问 https://zeabur.com
2. 登录/注册
3. 点击 "New Project"
4. 选择 "Deploy from GitHub"
5. 选择您的仓库

### 步骤3：配置环境变量（2分钟）

在Zeabur项目设置中添加以下**必需**环境变量：

```
DATABASE_URL=postgresql://...  # 或使用Zeabur的PostgreSQL服务
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_token  # 多页面：使用用户Token；单页面：使用页面Token
FACEBOOK_VERIFY_TOKEN=your_verify_token
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
SECRET_KEY=your_32_char_secret_key
DEBUG=false
CORS_ORIGINS=https://your-app-name.zeabur.app
```

### 步骤4：添加数据库（30秒）

1. 在项目中点击 "Add Service"
2. 选择 "PostgreSQL"
3. Zeabur会自动设置 `DATABASE_URL`

### 步骤5：部署（30秒）

1. 点击 "Deploy"
2. 等待构建完成
3. 获取应用URL

### 步骤6：运行迁移（30秒）

在Zeabur终端中运行：
```bash
alembic upgrade head
```

### 步骤7：验证（30秒）

```bash
# 健康检查
curl https://your-app-name.zeabur.app/health

# API文档
# 访问: https://your-app-name.zeabur.app/docs
```

## 必需文件检查

部署前确保以下文件存在：

- [x] `Procfile` - 启动命令
- [x] `requirements.txt` - Python依赖
- [x] `zeabur.json` - Zeabur配置（可选）

## 环境变量快速清单

复制以下变量名到Zeabur配置：

```
DATABASE_URL
FACEBOOK_APP_ID
FACEBOOK_APP_SECRET
FACEBOOK_ACCESS_TOKEN
FACEBOOK_VERIFY_TOKEN
OPENAI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
SECRET_KEY
DEBUG
CORS_ORIGINS
```

## 常见问题快速解决

### 部署失败？

1. 检查构建日志
2. 确认 `requirements.txt` 完整
3. 检查Python版本兼容性

### 数据库连接失败？

1. 确认PostgreSQL服务已启动
2. 检查 `DATABASE_URL` 格式
3. 运行迁移：`alembic upgrade head`

### Webhook不工作？

1. 更新Facebook Webhook URL为Zeabur地址
2. 确认 `FACEBOOK_VERIFY_TOKEN` 一致
3. 检查应用日志

## 多页面配置

如果系统需要管理多个Facebook页面：

1. **设置用户Token**：`FACEBOOK_ACCESS_TOKEN` 设置为用户级别Token（有`pages_show_list`权限）
2. **部署后同步**：运行 `python scripts/tools/manage_page_tokens.py sync` 自动获取所有页面Token
3. **详细说明**：参考 [多页面配置指南](ZEABUR_MULTI_PAGE_SETUP.md)

## 详细文档

- [完整Zeabur部署指南](ZEABUR_DEPLOYMENT.md)
- [环境变量详细说明](ZEABUR_ENV_VARS.md)
- [多页面配置指南](ZEABUR_MULTI_PAGE_SETUP.md)
- [部署检查清单](../DEPLOYMENT_CHECKLIST.md)

