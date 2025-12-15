# ⚠️ Zeabur 环境变量紧急配置

## 当前问题

应用启动失败，因为缺少必需的环境变量。错误信息显示缺少以下字段：

- `facebook_app_id`
- `facebook_app_secret`
- `facebook_access_token`
- `facebook_verify_token`
- `openai_api_key`
- `telegram_bot_token`
- `telegram_chat_id`
- `secret_key`

## 🔧 立即解决步骤

### 步骤1：打开Zeabur环境变量配置

1. 在Zeabur项目页面
2. 点击您的服务
3. 找到 **"Environment Variables"** 或 **"环境变量"** 标签
4. 点击 **"Add Variable"** 或 **"添加变量"**

### 步骤2：逐个添加以下环境变量

**复制以下变量名和值，替换为您的实际值：**

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
```

### 步骤3：保存并等待重启

1. 保存所有环境变量
2. Zeabur会自动重启服务
3. 等待重启完成（约1-2分钟）

### 步骤4：验证服务启动

1. 查看服务日志，确认没有错误
2. 访问健康检查：`https://your-app-name.zeabur.app/health`
3. 应该看到 `{"status": "healthy", ...}`

## 📋 环境变量快速复制清单

在Zeabur中，逐个添加以下变量（点击"Add Variable"添加每个）：

| 变量名 | 值（替换为您的实际值） |
|--------|---------------------|
| `FACEBOOK_APP_ID` | 你的Facebook应用ID |
| `FACEBOOK_APP_SECRET` | 你的Facebook应用密钥 |
| `FACEBOOK_ACCESS_TOKEN` | 你的用户级Token |
| `FACEBOOK_VERIFY_TOKEN` | 你的Webhook验证令牌 |
| `OPENAI_API_KEY` | sk-你的OpenAI密钥 |
| `OPENAI_MODEL` | gpt-4o-mini |
| `OPENAI_TEMPERATURE` | 0.7 |
| `TELEGRAM_BOT_TOKEN` | 你的Telegram Bot令牌 |
| `TELEGRAM_CHAT_ID` | 你的Telegram聊天ID |
| `SECRET_KEY` | `Smo8m91c4R60Ir8I6TvXfZEtH-Et0IJIhmRqaiGOROg` |
| `DEBUG` | false |

## ⚠️ 重要提示

1. **所有变量都是必需的**：缺少任何一个都会导致启动失败
2. **SECRET_KEY已生成**：直接使用 `Smo8m91c4R60Ir8I6TvXfZEtH-Et0IJIhmRqaiGOROg`
3. **FACEBOOK_ACCESS_TOKEN**：必须是用户级Token（有`pages_show_list`权限）
4. **DATABASE_URL**：如果已添加PostgreSQL服务，Zeabur会自动设置，无需手动配置

## 🔍 如何获取这些值

### Facebook配置
- **App ID 和 App Secret**：Facebook Developer Console → 您的应用 → 设置
- **Access Token**：Graph API Explorer 或 Facebook Developer Console
- **Verify Token**：自定义值，用于Webhook验证

### OpenAI配置
- **API Key**：https://platform.openai.com/api-keys

### Telegram配置
- **Bot Token**：与 @BotFather 对话创建Bot
- **Chat ID**：发送消息给Bot，访问 `https://api.telegram.org/bot<TOKEN>/getUpdates`

## ✅ 配置完成后

配置完所有环境变量后：

1. **等待服务重启**（约1-2分钟）
2. **运行数据库迁移**（在Zeabur终端中）：
   ```bash
   alembic upgrade head
   ```
3. **同步页面Token**（在Zeabur终端中）：
   ```bash
   python scripts/tools/manage_pages.py sync
   ```
4. **更新Facebook Webhook URL**：
   - 登录 Facebook Developer Console
   - 更新Webhook URL为：`https://your-app-name.zeabur.app/webhook`

## 🆘 如果还有问题

如果配置完环境变量后仍有问题：

1. **检查变量名拼写**：确保完全匹配（区分大小写）
2. **检查变量值**：确保没有多余空格
3. **查看服务日志**：确认具体错误信息
4. **确认服务已重启**：环境变量更改后需要重启

## 📚 相关文档

- [完整环境变量说明](ZEABUR_ENV_VARS.md)
- [详细配置步骤](ZEABUR_CONFIGURATION_STEPS.md)
- [部署检查清单](ZEABUR_DEPLOY_CHECKLIST.md)

