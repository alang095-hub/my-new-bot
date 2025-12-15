# 🚀 超简单部署步骤（小白版）

## 第一步：推送代码到GitHub

### 方法1：使用GitHub Desktop（推荐，最简单）⭐

1. **下载GitHub Desktop**
   - 访问：https://desktop.github.com
   - 下载并安装

2. **打开GitHub Desktop**
   - 登录您的GitHub账号
   - 添加本地仓库：`C:\Users\rick\Desktop\无极1`
   - 连接远程仓库：`https://github.com/alang095-hub/my-new-bot.git`

3. **提交并推送**
   - 写提交信息："准备部署"
   - 点击"Commit to main"
   - 点击"Push origin"

**详细步骤**：查看 `使用GitHub Desktop推送代码.md`

### 方法2：使用批处理文件（如果GitHub Desktop不行）

1. **双击运行**：`一键部署准备.bat`
2. **双击运行**：`推送代码.bat`

## 第二步：在Zeabur部署

### 超简单5步

1. **访问Zeabur**
   - 打开：https://zeabur.com
   - 用GitHub账号登录

2. **创建项目**
   - 点击"New Project"（新建项目）
   - 输入项目名称（随便起，比如：my-bot）

3. **导入仓库**
   - 点击"Import from GitHub"
   - 选择：`alang095-hub/my-new-bot`
   - Zeabur会自动检测项目类型

4. **添加数据库**
   - 点击"Add Service"（添加服务）
   - 选择"PostgreSQL"
   - 等待创建完成
   - **重要**：复制`DATABASE_URL`（后面要用）

5. **配置环境变量**
   - 点击应用服务（不是数据库）
   - 进入"Environment Variables"（环境变量）
   - 添加以下变量：

#### 必需的环境变量

```
DATABASE_URL=粘贴刚才复制的数据库URL
FACEBOOK_ACCESS_TOKEN=您的Facebook令牌
OPENAI_API_KEY=您的OpenAI密钥
TELEGRAM_BOT_TOKEN=您的Telegram令牌
SECRET_KEY=任意32位以上随机字符串（比如：abc123def456ghi789jkl012mno345pq）
DEBUG=false
```

6. **部署**
   - 点击"Deploy"（部署）
   - 等待3-5分钟
   - 看到绿色"Running"就成功了！

## 第三步：配置Facebook Webhook

1. **获取应用URL**
   - 在Zeabur控制台，找到应用URL
   - 格式：`https://your-app-name.zeabur.app`

2. **配置Webhook**
   - 访问：https://developers.facebook.com
   - 进入您的应用设置
   - 找到"Webhooks"
   - 配置URL：`https://your-app-name.zeabur.app/webhook`
   - Verify Token：与`FACEBOOK_VERIFY_TOKEN`一致

## ✅ 完成！

现在您的应用已经部署成功了！

## 📚 详细文档

- **GitHub Desktop使用**：`使用GitHub Desktop推送代码.md`
- **完整部署指南**：`docs/deployment/BEGINNER_DEPLOYMENT_GUIDE.md`
- **Docker概念解释**：`docs/deployment/DOCKER_FOR_BEGINNERS.md`

## 🆘 需要帮助？

1. 查看详细文档
2. 检查部署检查清单：`docs/deployment/DEPLOYMENT_CHECKLIST.md`
3. 查看常见问题：`docs/deployment/BEGINNER_DEPLOYMENT_GUIDE.md` 中的"常见问题"部分

---

**记住**：一步一步来，不着急！🎉

