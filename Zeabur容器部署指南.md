# Zeabur容器部署指南（Docker版）

## 📦 什么是容器部署？

**简单理解**：容器就像打包好的"盒子"，里面包含了您的应用和所有需要的东西。

**好处**：
- ✅ 环境一致，不会出错
- ✅ 自动管理，不需要手动配置
- ✅ 快速部署，几分钟完成

## 🎯 您的项目已准备好！

您的项目已经有 `Dockerfile`，Zeabur会自动检测并使用它！

## 🚀 超简单部署步骤

### 第1步：创建项目并导入仓库

1. 在Zeabur控制台，点击 **"New Project"**（新建项目）
2. 点击 **"Import from GitHub"**
3. 选择：**`alang095-hub/my-new-bot`**
4. **Zeabur会自动检测到Dockerfile**，自动使用容器部署！

### 第2步：添加PostgreSQL数据库

1. 在项目中，点击 **"Add Service"**（添加服务）
2. 选择 **"PostgreSQL"**
3. 等待创建完成（约1-2分钟）
4. **复制 `DATABASE_URL`**（后面要用）

### 第3步：配置环境变量

点击应用服务 → **"Environment Variables"** → 添加以下变量：

#### 必需的环境变量

**数据库配置**：
```
DATABASE_URL = 粘贴刚才复制的数据库URL
```

**Facebook配置**：
```
FACEBOOK_APP_ID = 您的Facebook应用ID
FACEBOOK_APP_SECRET = 您的Facebook应用密钥
FACEBOOK_ACCESS_TOKEN = 您的Facebook访问令牌
FACEBOOK_VERIFY_TOKEN = 任意字符串（比如：my_token_123）
```

**OpenAI配置**：
```
OPENAI_API_KEY = 您的OpenAI API密钥
```

**Telegram配置**：
```
TELEGRAM_BOT_TOKEN = 您的Telegram Bot令牌
TELEGRAM_CHAT_ID = 您的Telegram聊天ID
```

**安全配置**：
```
SECRET_KEY = 32位以上随机字符串
DEBUG = false
```

**服务器配置**（Zeabur会自动设置，无需手动配置）：
```
PORT = Zeabur自动设置
HOST = 0.0.0.0（默认值）
```

### 第4步：部署应用

1. 确认所有环境变量已添加
2. 点击 **"Deploy"**（部署）按钮
3. Zeabur会自动：
   - 读取Dockerfile
   - 构建Docker镜像
   - 创建容器
   - 启动服务
4. 等待3-5分钟
5. 看到绿色 **"Running"** 就成功了！

## ✅ 部署完成后的操作

### 1. 获取应用URL

部署完成后，在服务页面找到应用URL：
```
https://your-app-name.zeabur.app
```
**复制这个URL**，后面配置Webhook要用！

### 2. 运行数据库迁移

1. 在服务页面，点击 **"Terminal"**（终端）标签
2. 等待终端连接（会进入容器内部）
3. 输入命令：
   ```bash
   alembic upgrade head
   ```
4. 按回车执行
5. 等待迁移完成

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

## 🔍 容器部署的优势

### Zeabur自动处理

- ✅ **自动检测Dockerfile** - 不需要手动配置
- ✅ **自动构建镜像** - 根据Dockerfile自动构建
- ✅ **自动创建容器** - 自动创建和启动容器
- ✅ **自动管理** - 自动重启、扩展等

### 您不需要做的

- ❌ 不需要手动构建镜像
- ❌ 不需要手动运行容器
- ❌ 不需要配置Docker网络
- ❌ 不需要管理容器生命周期

## 📋 您的Dockerfile说明

您的项目已经有完整的Dockerfile：

```dockerfile
FROM python:3.9-slim          # 使用Python 3.9基础镜像
WORKDIR /app                   # 设置工作目录
COPY requirements.txt .        # 复制依赖文件
RUN pip install ...            # 安装依赖
COPY . .                       # 复制应用代码
EXPOSE 8000                    # 暴露端口
CMD uvicorn ...                # 启动命令
```

**Zeabur会自动使用这个Dockerfile！**

## 🆘 常见问题

### Q1: Zeabur会自动检测Dockerfile吗？

**A**: 是的！Zeabur会自动检测到您的Dockerfile，自动使用容器部署。

### Q2: 需要修改Dockerfile吗？

**A**: 不需要！您的Dockerfile已经配置好了，可以直接使用。

### Q3: 容器部署和普通部署有什么区别？

**A**: 
- **容器部署**：使用Dockerfile，环境更一致，更可靠
- **普通部署**：Zeabur自动检测项目类型，可能不够精确

**推荐使用容器部署**（您已经准备好了）！

### Q4: 如何查看容器日志？

**A**: 在Zeabur控制台，点击服务 → "Logs"（日志）标签

### Q5: 如何进入容器？

**A**: 在Zeabur控制台，点击服务 → "Terminal"（终端）标签

## 📝 快速检查清单

- [ ] 项目已创建
- [ ] GitHub仓库已导入（alang095-hub/my-new-bot）
- [ ] Zeabur自动检测到Dockerfile
- [ ] PostgreSQL数据库已添加
- [ ] DATABASE_URL已复制
- [ ] 所有环境变量已配置
- [ ] 应用已部署（绿色Running）
- [ ] 数据库迁移已运行
- [ ] Facebook Webhook已配置

## 🎉 完成！

现在您的应用已经通过容器部署成功了！

## 📚 相关文档

- **详细部署指南**：`docs/deployment/BEGINNER_DEPLOYMENT_GUIDE.md`
- **Docker概念解释**：`docs/deployment/DOCKER_FOR_BEGINNERS.md`
- **部署检查清单**：`docs/deployment/DEPLOYMENT_CHECKLIST.md`

---

**提示**：容器部署是最可靠的方式，您的项目已经准备好了！🎉

