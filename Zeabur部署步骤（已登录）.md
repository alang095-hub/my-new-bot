# Zeabur部署步骤（已有账号版）

## 🎯 您已经登录了，直接开始部署！

## 📍 您的仓库地址
```
https://github.com/alang095-hub/my-new-bot
```

## 🚀 超简单5步完成部署

### 第1步：创建新项目

1. 在Zeabur控制台，点击 **"New Project"**（新建项目）
2. 输入项目名称（随便起，比如：`my-bot` 或 `facebook-service`）
3. 点击 **"Create"**（创建）

### 第2步：导入GitHub仓库

1. 点击 **"Import from GitHub"**（从GitHub导入）
2. 如果第一次使用，可能需要授权Zeabur访问GitHub
3. 在仓库列表中找到：**`alang095-hub/my-new-bot`**
4. 点击选择这个仓库
5. Zeabur会自动检测项目类型（Python/FastAPI）

### 第3步：添加PostgreSQL数据库

1. 在项目中，点击 **"Add Service"**（添加服务）
2. 选择 **"PostgreSQL"**
3. 等待数据库创建完成（约1-2分钟）
4. **重要**：点击PostgreSQL服务
5. 找到 **"Connection String"** 或 **"DATABASE_URL"**
6. **复制这个URL**（后面要用！）

### 第4步：配置环境变量

1. 点击**应用服务**（不是数据库服务）
2. 在服务页面，找到 **"Environment Variables"**（环境变量）
3. 点击 **"Add Variable"**（添加变量）
4. 逐个添加以下环境变量：

#### 必需的环境变量

**数据库配置**：
- 变量名：`DATABASE_URL`
- 变量值：粘贴刚才复制的数据库URL
- 点击保存

**Facebook配置**：
- 变量名：`FACEBOOK_APP_ID`
- 变量值：您的Facebook应用ID
- 点击保存

- 变量名：`FACEBOOK_APP_SECRET`
- 变量值：您的Facebook应用密钥
- 点击保存

- 变量名：`FACEBOOK_ACCESS_TOKEN`
- 变量值：您的Facebook访问令牌
- 点击保存

- 变量名：`FACEBOOK_VERIFY_TOKEN`
- 变量值：任意字符串（比如：`my_verify_token_123`）
- 点击保存

**OpenAI配置**：
- 变量名：`OPENAI_API_KEY`
- 变量值：您的OpenAI API密钥
- 点击保存

**Telegram配置**：
- 变量名：`TELEGRAM_BOT_TOKEN`
- 变量值：您的Telegram Bot令牌
- 点击保存

- 变量名：`TELEGRAM_CHAT_ID`
- 变量值：您的Telegram聊天ID
- 点击保存

**安全配置**：
- 变量名：`SECRET_KEY`
- 变量值：32位以上随机字符串（比如：`abc123def456ghi789jkl012mno345pq`）
- 点击保存

- 变量名：`DEBUG`
- 变量值：`false`
- 点击保存

### 第5步：部署应用

1. 确认所有环境变量已添加
2. 点击 **"Deploy"**（部署）按钮
3. 等待构建完成（约3-5分钟）
4. 看到绿色 **"Running"** 就成功了！

## ✅ 部署完成后的操作

### 1. 获取应用URL

部署完成后，在服务页面找到应用URL：
```
https://your-app-name.zeabur.app
```
**复制这个URL**，后面配置Webhook要用！

### 2. 运行数据库迁移

1. 在服务页面，点击 **"Terminal"**（终端）标签
2. 等待终端连接
3. 输入命令：
   ```bash
   alembic upgrade head
   ```
4. 按回车执行
5. 等待完成

### 3. 配置Facebook Webhook

1. 访问：https://developers.facebook.com
2. 进入您的应用设置
3. 找到 **"Webhooks"**
4. 配置Webhook URL：
   ```
   https://your-app-name.zeabur.app/webhook
   ```
   （替换为您的实际URL）
5. Verify Token：与`FACEBOOK_VERIFY_TOKEN`环境变量一致
6. 订阅事件：`messages`、`messaging_postbacks`、`feed`
7. 点击保存

## 🎉 完成！

现在您的应用已经部署成功了！

## 📝 快速检查清单

- [ ] 项目已创建
- [ ] GitHub仓库已导入
- [ ] PostgreSQL数据库已添加
- [ ] DATABASE_URL已复制
- [ ] 所有环境变量已配置
- [ ] 应用已部署（绿色Running）
- [ ] 数据库迁移已运行
- [ ] Facebook Webhook已配置

## 🆘 遇到问题？

1. **部署失败**：查看构建日志，检查环境变量
2. **502错误**：检查服务状态，查看日志
3. **数据库连接失败**：检查DATABASE_URL是否正确
4. **Webhook验证失败**：检查URL和Verify Token

详细问题解决：查看 `docs/deployment/BEGINNER_DEPLOYMENT_GUIDE.md`

---

**提示**：一步一步来，不着急！🎉

