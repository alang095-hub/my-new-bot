# 📋 配置清单 - 接下来需要设置的内容

## ✅ 已完成
- [x] 代码优化和时区修复
- [x] 数据库时区配置（UTC）
- [x] 日志时区配置（UTC+8）
- [x] 前端时间显示修复

## 🔧 必需配置（必须设置）

### 1. 数据库配置 ⚠️
```env
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名
```
**获取方式：**
- Zeabur/Railway: 平台会自动提供 `DATABASE_URL`
- 本地部署: 需要创建 PostgreSQL 数据库

### 2. Facebook API 配置 ⚠️
```env
FACEBOOK_APP_ID=你的应用ID
FACEBOOK_APP_SECRET=你的应用密钥
FACEBOOK_ACCESS_TOKEN=你的访问令牌
FACEBOOK_VERIFY_TOKEN=你的Webhook验证令牌（可自定义）
```

**获取步骤：**
1. 访问 [Facebook Developers](https://developers.facebook.com/)
2. 创建应用或选择现有应用
3. 获取 `App ID` 和 `App Secret`
4. 生成长期访问令牌（Long-lived Access Token）
5. 设置 Webhook 验证令牌（自定义字符串，如：`my_secure_token_2024`）

### 3. OpenAI API 配置 ⚠️
```env
OPENAI_API_KEY=sk-你的API密钥
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
```

**获取步骤：**
1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录并创建新的 API 密钥
3. 复制密钥（以 `sk-` 开头）

### 4. Telegram Bot 配置 ⚠️
```env
TELEGRAM_BOT_TOKEN=你的机器人令牌
TELEGRAM_CHAT_ID=你的聊天ID
```

**获取步骤：**
1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取 `Bot Token`（格式：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）
5. 获取 `Chat ID`：
   - 将机器人添加到群组或频道
   - 发送消息后访问：`https://api.telegram.org/bot<TOKEN>/getUpdates`
   - 查找 `chat.id` 字段

### 5. 安全密钥 ⚠️
```env
SECRET_KEY=随机生成的密钥（至少32字符）
ALGORITHM=HS256
```

**生成方式：**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📝 可选配置（根据需要）

### 6. Instagram 配置（可选）
```env
INSTAGRAM_ACCESS_TOKEN=你的Instagram访问令牌
INSTAGRAM_VERIFY_TOKEN=你的Instagram验证令牌
INSTAGRAM_USER_ID=你的Instagram用户ID
```
**注意：** 如果未设置，系统会使用 Facebook 的配置

### 7. 第三方集成（可选）
```env
# ManyChat 集成
MANYCHAT_API_KEY=你的ManyChat API密钥

# Botcake 集成
BOTCAKE_API_KEY=你的Botcake API密钥
```

## 🚀 配置步骤

### 方式 1: Zeabur 平台配置

1. **进入 Zeabur 项目页面**
2. **点击 "Variables" 标签**
3. **添加以下环境变量：**

```env
# 必需配置
DATABASE_URL=自动提供（或手动设置）
FACEBOOK_APP_ID=你的应用ID
FACEBOOK_APP_SECRET=你的应用密钥
FACEBOOK_ACCESS_TOKEN=你的访问令牌
FACEBOOK_VERIFY_TOKEN=你的验证令牌
OPENAI_API_KEY=sk-你的密钥
TELEGRAM_BOT_TOKEN=你的机器人令牌
TELEGRAM_CHAT_ID=你的聊天ID
SECRET_KEY=生成的随机密钥

# 可选配置
INSTAGRAM_USER_ID=你的Instagram用户ID
```

4. **保存并重新部署**

### 方式 2: 本地配置

1. **创建 `.env` 文件**（如果不存在）
2. **复制 `env.example` 的内容**
3. **替换所有占位符值**
4. **保存文件**

## 🔍 配置验证

### 检查配置是否正确

运行以下命令验证配置：

```bash
# 检查环境变量
python -c "from src.config import settings; print('配置加载成功！')"
```

### 常见错误

1. **`ValueError: 请配置有效的Facebook参数`**
   - 原因：使用了占位符值（如 `your_facebook_app_id`）
   - 解决：替换为真实的 API 密钥

2. **`数据库连接失败`**
   - 原因：`DATABASE_URL` 格式错误或数据库未启动
   - 解决：检查数据库连接字符串格式

3. **`OpenAI API密钥无效`**
   - 原因：密钥格式错误或已过期
   - 解决：重新生成 API 密钥

## 📱 Facebook Webhook 配置

配置完环境变量后，还需要设置 Facebook Webhook：

### 1. 获取 Webhook URL

- **Zeabur**: `https://你的域名.zeabur.app/webhook`
- **Railway**: `https://你的域名.railway.app/webhook`
- **本地**: `https://你的域名/webhook`（需要 ngrok 等工具）

### 2. 在 Facebook Developer Console 配置

1. 进入 [Facebook Developers](https://developers.facebook.com/)
2. 选择你的应用
3. 进入 "Webhooks" 设置
4. 添加 Webhook URL
5. 输入 `VERIFY_TOKEN`（与 `.env` 中的 `FACEBOOK_VERIFY_TOKEN` 一致）
6. 订阅以下事件：
   - `messages`
   - `messaging_postbacks`
   - `message_deliveries`
   - `message_reads`

## 🎯 优先级顺序

1. **第一优先级（必须）：**
   - ✅ 数据库配置
   - ✅ Facebook API 配置
   - ✅ OpenAI API 配置
   - ✅ Telegram Bot 配置
   - ✅ 安全密钥

2. **第二优先级（推荐）：**
   - 📱 Facebook Webhook 配置
   - 📊 监控面板测试

3. **第三优先级（可选）：**
   - 📸 Instagram 配置
   - 🔗 第三方集成

## 📚 相关文档

- [环境变量配置指南](./CONFIGURE_ENV.md)
- [Facebook Webhook 配置](./CONFIGURE_REDIRECT_URI.md)
- [AI 回复配置](./CONFIGURE_AI_REPLY.md)
- [实时监控指南](./REALTIME_MONITORING_GUIDE.md)

## ⚠️ 安全提示

1. **永远不要**将 `.env` 文件提交到 Git
2. **定期轮换**API 密钥
3. **使用不同密钥**用于开发和生产环境
4. **限制访问权限**，只给必要的人员

---

配置完成后，重启应用即可开始使用！

