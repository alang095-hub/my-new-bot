# 小白部署完全指南（Zeabur自动Docker）

## 📖 前言

本指南专为**零基础小白**设计，不需要任何技术背景，只需要按照步骤操作即可。

**您不需要**：
- ❌ 懂Docker
- ❌ 懂编程
- ❌ 安装任何软件
- ❌ 写任何代码

**您只需要**：
- ✅ 有一个GitHub账号
- ✅ 有一个Zeabur账号（免费注册）
- ✅ 准备好API密钥（Facebook、OpenAI、Telegram）
- ✅ 按照步骤操作

## ⏱️ 预计时间

- **总时间**：约25分钟
- **准备**：5分钟
- **部署**：10分钟
- **配置**：5分钟
- **测试**：5分钟

## 📋 第一步：准备工作（5分钟）

### 1.1 准备环境变量清单

创建一个文本文件（例如：`环境变量.txt`），记录以下信息：

#### 数据库配置（Zeabur会自动创建，稍后复制）

```
DATABASE_URL=待Zeabur创建后复制
```

#### Facebook配置（需要您填写）

```
FACEBOOK_APP_ID=您的Facebook应用ID
FACEBOOK_APP_SECRET=您的Facebook应用密钥
FACEBOOK_ACCESS_TOKEN=您的Facebook访问令牌
FACEBOOK_VERIFY_TOKEN=任意字符串（例如：my_token_123）
```

**如何获取Facebook配置**：
1. 访问 https://developers.facebook.com
2. 创建应用或使用现有应用
3. 在应用设置中获取这些信息

#### OpenAI配置（需要您填写）

```
OPENAI_API_KEY=您的OpenAI API密钥
OPENAI_MODEL=gpt-4o-mini（默认值，可以不填）
OPENAI_TEMPERATURE=0.7（默认值，可以不填）
```

**如何获取OpenAI密钥**：
1. 访问 https://platform.openai.com
2. 登录账号
3. 在API Keys页面创建新密钥

#### Telegram配置（需要您填写）

```
TELEGRAM_BOT_TOKEN=您的Telegram Bot令牌
TELEGRAM_CHAT_ID=您的Telegram聊天ID
```

**如何获取Telegram配置**：
1. 在Telegram中搜索 @BotFather
2. 发送 `/newbot` 创建新Bot
3. 获取Bot Token
4. 获取Chat ID（发送消息给Bot，访问 `https://api.telegram.org/bot<TOKEN>/getUpdates` 查看）

#### 安全配置（需要您填写）

```
SECRET_KEY=生成32位以上随机字符串
DEBUG=false
```

**如何生成SECRET_KEY**：
- 方法1：使用在线工具生成随机字符串
- 方法2：使用命令 `openssl rand -hex 32`（如果有命令行工具）
- 方法3：任意输入32位以上的字符和数字组合

### 1.2 确认代码在GitHub

- [ ] 代码已推送到GitHub
- [ ] 知道GitHub仓库地址
- [ ] GitHub仓库是公开的或已授权Zeabur访问

**如果还没有**：
```bash
# 在项目目录执行
git add .
git commit -m "准备部署"
git push
```

## 🚀 第二步：Zeabur部署（10分钟）

### 2.1 创建Zeabur账号

1. 访问 https://zeabur.com
2. 点击"Sign Up"（注册）
3. 选择"Sign in with GitHub"（使用GitHub登录）**推荐**
4. 授权Zeabur访问您的GitHub账号
5. 完成注册

**为什么用GitHub登录**：
- 可以直接连接GitHub仓库
- 不需要手动输入仓库地址
- 更安全更方便

### 2.2 创建新项目

1. 登录Zeabur后，点击"New Project"（新建项目）
2. 输入项目名称（例如：`facebook-customer-service`）
3. 点击"Create"（创建）

### 2.3 导入GitHub仓库

1. 在项目中，点击"Import from GitHub"（从GitHub导入）
2. 如果第一次使用，需要授权Zeabur访问GitHub
3. 选择您的仓库
4. Zeabur会自动检测项目类型（Python/FastAPI）

**等待Zeabur检测**：
- Zeabur会自动识别这是Python项目
- 会自动检测到`requirements.txt`
- 会自动检测到`Dockerfile`（如果有）

### 2.4 添加PostgreSQL数据库

1. 在项目中，点击"Add Service"（添加服务）
2. 选择"PostgreSQL"
3. Zeabur会自动创建数据库服务
4. **重要步骤**：
   - 等待数据库创建完成（约1-2分钟）
   - 点击PostgreSQL服务
   - 找到"Connection String"或"DATABASE_URL"
   - **复制这个URL**（后面要用！）

**DATABASE_URL格式**：
```
postgresql://postgres:password@host:5432/database
```

### 2.5 配置环境变量

1. 点击应用服务（不是数据库服务）
2. 在服务页面，找到"Environment Variables"（环境变量）
3. 点击"Add Variable"（添加变量）
4. 逐个添加以下环境变量：

#### 添加数据库URL

- **变量名**：`DATABASE_URL`
- **变量值**：粘贴刚才复制的数据库URL
- 点击"Save"（保存）

#### 添加Facebook配置

- **变量名**：`FACEBOOK_APP_ID`
- **变量值**：您的Facebook应用ID
- 点击"Save"

- **变量名**：`FACEBOOK_APP_SECRET`
- **变量值**：您的Facebook应用密钥
- 点击"Save"

- **变量名**：`FACEBOOK_ACCESS_TOKEN`
- **变量值**：您的Facebook访问令牌
- 点击"Save"

- **变量名**：`FACEBOOK_VERIFY_TOKEN`
- **变量值**：任意字符串（例如：`my_verify_token_123`）
- 点击"Save"

#### 添加OpenAI配置

- **变量名**：`OPENAI_API_KEY`
- **变量值**：您的OpenAI API密钥
- 点击"Save"

- **变量名**：`OPENAI_MODEL`（可选）
- **变量值**：`gpt-4o-mini`
- 点击"Save"

- **变量名**：`OPENAI_TEMPERATURE`（可选）
- **变量值**：`0.7`
- 点击"Save"

#### 添加Telegram配置

- **变量名**：`TELEGRAM_BOT_TOKEN`
- **变量值**：您的Telegram Bot令牌
- 点击"Save"

- **变量名**：`TELEGRAM_CHAT_ID`
- **变量值**：您的Telegram聊天ID
- 点击"Save"

#### 添加安全配置

- **变量名**：`SECRET_KEY`
- **变量值**：32位以上随机字符串
- 点击"Save"

- **变量名**：`DEBUG`
- **变量值**：`false`
- 点击"Save"

#### 服务器配置（可选）

- **变量名**：`HOST`（可选）
- **变量值**：`0.0.0.0`
- 点击"Save"

**注意**：`PORT`变量不需要手动设置，Zeabur会自动设置。

### 2.6 开始部署

1. 确认所有环境变量已添加
2. 点击"Deploy"（部署）按钮
3. 等待构建完成（约3-5分钟）

**构建过程**：
- Zeabur自动检测代码
- 自动创建Docker容器
- 自动安装依赖
- 自动启动服务

**如何查看进度**：
- 在服务页面可以看到构建日志
- 绿色表示成功，红色表示失败

## ⚙️ 第三步：部署后配置（5分钟）

### 3.1 获取应用URL

部署完成后：

1. 在服务页面，找到"Domains"（域名）或"URL"
2. 您会看到一个URL，格式类似：
   ```
   https://your-app-name.zeabur.app
   ```
3. **复制这个URL**（后面配置Webhook要用！）

### 3.2 运行数据库迁移

**方法1：通过Zeabur终端**（推荐）

1. 在服务页面，点击"Terminal"（终端）标签
2. 等待终端连接（看到 `root@service-xxx:/app#` 表示连接成功）
3. 在终端中输入：
   ```bash
   alembic upgrade head
   ```
4. 按回车执行
5. 等待迁移完成（看到"INFO: Migration complete"表示成功）

**方法2：通过部署后命令**（如果配置了）

如果您的项目配置了postDeploy命令，Zeabur会自动运行迁移。

### 3.3 配置Facebook Webhook

1. 登录 [Facebook开发者控制台](https://developers.facebook.com)
2. 选择您的应用
3. 在左侧菜单找到"Webhooks"（Webhook）
4. 点击"Add Callback URL"（添加回调URL）或编辑现有Webhook
5. 填写以下信息：

   **Callback URL**（回调URL）：
   ```
   https://your-app-name.zeabur.app/webhook
   ```
   （替换为您的实际URL）

   **Verify Token**（验证令牌）：
   ```
   my_verify_token_123
   ```
   （与`FACEBOOK_VERIFY_TOKEN`环境变量一致）

6. 点击"Verify and Save"（验证并保存）

7. 订阅事件：
   - ✅ 勾选 `messages` - 消息
   - ✅ 勾选 `messaging_postbacks` - 回传
   - ✅ 勾选 `feed` - 评论（如果需要）

8. 点击"Save"（保存）

**验证成功标志**：
- Webhook状态显示为"已订阅"（Subscribed）
- 绿色勾号表示验证成功

## ✅ 第四步：验证部署（5分钟）

### 4.1 健康检查

在浏览器中访问：
```
https://your-app-name.zeabur.app/health/simple
```

**预期结果**：
```json
{
  "status": "ok",
  "timestamp": "2025-01-XX...",
  "message": "Service is running"
}
```

**如果看到这个**：✅ 服务运行正常！

**如果看到错误**：
- 检查服务是否运行（Zeabur控制台）
- 查看服务日志
- 检查环境变量是否正确

### 4.2 查看API文档

在浏览器中访问：
```
https://your-app-name.zeabur.app/docs
```

**预期结果**：
- 看到Swagger API文档页面
- 可以看到所有API端点

**如果看到这个**：✅ API服务正常！

### 4.3 测试Webhook

1. 在Facebook Messenger中，向您的页面发送测试消息
2. 在Zeabur控制台，查看服务日志
3. 应该能看到消息接收的日志

**如何查看日志**：
- 在服务页面，点击"Logs"（日志）标签
- 应该能看到类似这样的日志：
  ```
  INFO: Received Facebook webhook event
  INFO: Processing message from user: ...
  ```

**如果看到日志**：✅ Webhook工作正常！

## 🎉 部署完成！

如果以上所有步骤都成功，恭喜您！部署已完成！

## 📝 后续操作

### 更新代码

1. 修改代码
2. 推送到GitHub：
   ```bash
   git add .
   git commit -m "更新代码"
   git push
   ```
3. Zeabur会自动检测并重新部署

### 修改配置

1. 在Zeabur控制台，进入服务设置
2. 修改环境变量
3. Zeabur会自动重启服务

### 查看日志

1. 在服务页面，点击"Logs"（日志）
2. 可以查看实时日志
3. 可以搜索和过滤日志

### 监控状态

1. 在服务页面，可以看到服务状态
2. 绿色表示运行正常
3. 红色表示有问题

## ❓ 常见问题

### Q1: 部署失败怎么办？

**检查清单**：
1. 查看构建日志，找到错误信息
2. 检查所有环境变量是否已配置
3. 检查代码是否有语法错误
4. 确认`requirements.txt`完整

### Q2: 502错误怎么办？

**解决步骤**：
1. 检查服务是否运行（应该是绿色）
2. 查看服务日志
3. 检查数据库连接
4. 确认`PORT`环境变量（Zeabur会自动设置）

### Q3: Webhook验证失败？

**检查清单**：
1. 确认Webhook URL正确（包含`/webhook`）
2. 确认Verify Token与`FACEBOOK_VERIFY_TOKEN`一致
3. 确认服务正常运行
4. 查看服务日志

### Q4: 数据库连接失败？

**解决步骤**：
1. 确认PostgreSQL服务已创建
2. 检查`DATABASE_URL`是否正确
3. 确认数据库服务运行中
4. 检查网络连接

### Q5: 如何查看详细错误？

**方法**：
1. 在服务页面，点击"Logs"（日志）
2. 查看错误日志
3. 复制错误信息，搜索解决方案

## 📚 相关文档

- [Docker小白指南](DOCKER_FOR_BEGINNERS.md) - 了解Docker是什么
- [部署检查清单](DEPLOYMENT_CHECKLIST.md) - 完整的检查清单
- [故障排查指南](../production/502_TROUBLESHOOTING_STEPS.md) - 常见问题解决

## 🎓 总结

**您已经学会了**：
- ✅ 如何在Zeabur部署应用
- ✅ 如何配置环境变量
- ✅ 如何配置Facebook Webhook
- ✅ 如何验证部署

**记住**：
- Zeabur会自动处理所有Docker相关的事情
- 您只需要填写配置和点击按钮
- 遇到问题查看日志和文档

**下一步**：
- 运行部署验证测试
- 测试核心功能
- 监控服务状态

---

**祝您部署顺利！** 🚀

