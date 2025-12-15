# Zeabur 配置步骤（项目已创建）

## 📍 当前状态

您已经在Zeabur创建了项目，现在需要完成以下配置：

## 🔧 配置步骤

### 步骤1：确认服务状态

在Zeabur项目页面：
1. 确认服务已连接GitHub仓库
2. 确认代码已部署（查看构建日志）
3. 记录应用URL（格式：`https://xxx.zeabur.app`）

### 步骤2：添加PostgreSQL数据库（如果还没有）

1. 在项目页面，点击 **"Add Service"** 或 **"添加服务"**
2. 选择 **"PostgreSQL"**
3. 等待数据库服务启动（约1-2分钟）
4. ✅ Zeabur会自动设置 `DATABASE_URL` 环境变量

### 步骤3：配置环境变量

在服务设置页面，找到 **"Environment Variables"** 或 **"环境变量"**：

#### 必需的环境变量列表

点击 **"Add Variable"** 逐个添加以下变量：

```
FACEBOOK_APP_ID=你的Facebook应用ID
FACEBOOK_APP_SECRET=你的Facebook应用密钥
FACEBOOK_ACCESS_TOKEN=你的用户级Token（有pages_show_list权限）
FACEBOOK_VERIFY_TOKEN=你的Webhook验证令牌
OPENAI_API_KEY=sk-你的OpenAI密钥
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
TELEGRAM_BOT_TOKEN=你的Telegram Bot令牌
TELEGRAM_CHAT_ID=你的Telegram聊天ID
SECRET_KEY=Smo8m91c4R60Ir8I6TvXfZEtH-Et0IJIhmRqaiGOROg
DEBUG=false
CORS_ORIGINS=https://your-app-name.zeabur.app
```

**注意：**
- `CORS_ORIGINS` 中的URL需要替换为您的实际应用URL
- `DATABASE_URL` 由Zeabur自动设置，无需手动配置

### 步骤4：等待服务重启

配置环境变量后，服务会自动重启。等待重启完成（约1-2分钟）。

### 步骤5：运行数据库迁移

1. 在服务页面，找到 **"Terminal"** 或 **"终端"** 选项
2. 打开终端
3. 运行以下命令：

```bash
alembic upgrade head
```

**预期输出：**
```
INFO  [alembic.runtime.migration] Running upgrade ... -> ..., ...
```

### 步骤6：同步所有页面Token（重要！）

在同一个终端中运行：

```bash
python scripts/tools/manage_pages.py sync
```

**预期输出：**
```
从用户Token同步了 X 个页面Token
```

### 步骤7：验证配置

```bash
python scripts/tools/manage_pages.py status
```

应该看到所有10+页面都已配置。

### 步骤8：更新Facebook Webhook URL

1. 登录 **Facebook Developer Console**：https://developers.facebook.com
2. 进入您的应用设置
3. 找到 **Webhook** 配置
4. 更新 **Webhook URL** 为：`https://your-app-name.zeabur.app/webhook`
   - 将 `your-app-name` 替换为您的实际应用名称
5. 确认 **Verify Token** 与 `FACEBOOK_VERIFY_TOKEN` 环境变量一致
6. 点击 **"Verify and Save"**

### 步骤9：验证部署

访问健康检查端点：

```
https://your-app-name.zeabur.app/health
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

## ✅ 配置检查清单

- [ ] PostgreSQL数据库已添加
- [ ] 所有环境变量已配置
- [ ] 服务已重启
- [ ] 数据库迁移已运行
- [ ] 所有页面Token已同步
- [ ] Facebook Webhook URL已更新
- [ ] 健康检查通过

## 🆘 常见问题

### 问题1：环境变量在哪里配置？

**答案：**
1. 在Zeabur项目页面
2. 点击您的服务
3. 找到 **"Environment Variables"** 或 **"环境变量"** 标签
4. 点击 **"Add Variable"** 添加变量

### 问题2：如何访问终端？

**答案：**
1. 在服务页面
2. 找到 **"Terminal"** 或 **"终端"** 选项
3. 点击打开终端窗口

### 问题3：如何查看应用URL？

**答案：**
1. 在服务页面
2. 查看 **"Domains"** 或 **"域名"** 部分
3. 或查看服务概览页面

### 问题4：构建失败怎么办？

**答案：**
1. 查看构建日志
2. 检查 `requirements.txt` 是否完整
3. 确认Python版本兼容
4. 检查是否有语法错误

## 📝 环境变量快速参考

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `FACEBOOK_APP_ID` | ✅ | Facebook应用ID |
| `FACEBOOK_APP_SECRET` | ✅ | Facebook应用密钥 |
| `FACEBOOK_ACCESS_TOKEN` | ✅ | 用户级Token（有pages_show_list权限） |
| `FACEBOOK_VERIFY_TOKEN` | ✅ | Webhook验证令牌 |
| `OPENAI_API_KEY` | ✅ | OpenAI API密钥 |
| `OPENAI_MODEL` | ⚠️ | 默认：gpt-4o-mini |
| `OPENAI_TEMPERATURE` | ⚠️ | 默认：0.7 |
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram Bot令牌 |
| `TELEGRAM_CHAT_ID` | ✅ | Telegram聊天ID |
| `SECRET_KEY` | ✅ | 已生成：`Smo8m91c4R60Ir8I6TvXfZEtH-Et0IJIhmRqaiGOROg` |
| `DEBUG` | ✅ | 必须设置为：`false` |
| `CORS_ORIGINS` | ⚠️ | 部署后设置（应用URL） |
| `DATABASE_URL` | ✅ | Zeabur自动设置 |

## 🎉 完成！

配置完成后，您的系统将：
- ✅ 自动接收Facebook/Instagram消息
- ✅ 使用AI自动回复
- ✅ 支持10+个页面同时运行
- ✅ 发送Telegram通知
- ✅ 记录统计信息

祝配置顺利！🚀

