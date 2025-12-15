# 🚨 Zeabur 环境变量快速修复指南

## 当前错误

应用启动失败，因为环境变量未正确配置。错误显示只读取到了 `port: '8080'`，其他所有必需变量都缺失。

## ⚡ 立即修复步骤（5分钟）

### 步骤1：打开Zeabur环境变量配置页面

1. 访问您的Zeabur项目：https://zeabur.com/projects/6934ed22029d15b96dfa8f71
2. 点击您的服务（service）
3. 在服务页面，找到 **"Environment Variables"** 或 **"环境变量"** 标签/按钮
4. 点击进入环境变量配置页面

### 步骤2：添加必需的环境变量

**重要：** 必须添加以下所有变量，缺少任何一个都会导致启动失败。

#### 逐个添加（点击 "Add Variable" 或 "+" 按钮）：

**1. Facebook配置**
```
变量名: FACEBOOK_APP_ID
值: 你的Facebook应用ID（从Facebook Developer Console获取）
```

```
变量名: FACEBOOK_APP_SECRET
值: 你的Facebook应用密钥（从Facebook Developer Console获取）
```

```
变量名: FACEBOOK_ACCESS_TOKEN
值: 你的用户级Token（有pages_show_list权限）
```

```
变量名: FACEBOOK_VERIFY_TOKEN
值: 你的Webhook验证令牌（自定义，例如：my_verify_token_123）
```

**2. OpenAI配置**
```
变量名: OPENAI_API_KEY
值: sk-你的OpenAI密钥（从OpenAI平台获取）
```

```
变量名: OPENAI_MODEL
值: gpt-4o-mini
```

```
变量名: OPENAI_TEMPERATURE
值: 0.7
```

**3. Telegram配置**
```
变量名: TELEGRAM_BOT_TOKEN
值: 你的Telegram Bot令牌（从@BotFather获取）
```

```
变量名: TELEGRAM_CHAT_ID
值: 你的Telegram聊天ID（数字，例如：123456789）
```

**4. 安全配置**
```
变量名: SECRET_KEY
值: 请生成32位以上随机字符串
```

```
变量名: DEBUG
值: false
```

**5. CORS配置（可选，但建议配置）**
```
变量名: CORS_ORIGINS
值: https://your-app-name.zeabur.app
（替换为您的实际应用URL）
```

### 步骤3：保存并重启

1. **保存所有环境变量**（点击"Save"或"保存"按钮）
2. **等待服务自动重启**（约1-2分钟）
3. **查看服务日志**，确认没有错误

### 步骤4：验证配置

访问健康检查端点：
```
https://your-app-name.zeabur.app/health
```

应该看到：
```json
{
  "status": "healthy",
  ...
}
```

## 📋 完整环境变量清单（复制粘贴用）

如果您可以在Zeabur中批量导入，可以使用以下格式：

```
FACEBOOK_APP_ID=你的Facebook应用ID
FACEBOOK_APP_SECRET=你的Facebook应用密钥
FACEBOOK_ACCESS_TOKEN=你的用户级Token
FACEBOOK_VERIFY_TOKEN=你的Webhook验证令牌
OPENAI_API_KEY=sk-你的OpenAI密钥
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
TELEGRAM_BOT_TOKEN=你的Telegram Bot令牌
TELEGRAM_CHAT_ID=你的Telegram聊天ID
SECRET_KEY=请生成32位以上随机字符串
DEBUG=false
CORS_ORIGINS=https://your-app-name.zeabur.app
```

## ⚠️ 常见错误

### 错误1：变量名拼写错误
- ✅ 正确：`FACEBOOK_APP_ID`
- ❌ 错误：`FACEBOOK_APPID`、`facebook_app_id`（虽然不区分大小写，但建议使用大写）

### 错误2：值中有多余空格
- ✅ 正确：`gpt-4o-mini`
- ❌ 错误：` gpt-4o-mini `（前后有空格）

### 错误3：忘记保存
- 添加变量后，**必须点击"Save"或"保存"按钮**
- 只有保存后，服务才会重启并应用新配置

### 错误4：服务未重启
- 环境变量更改后，服务需要重启
- 如果未自动重启，可以手动触发重启

## 🔍 如何验证环境变量已配置

### 方法1：查看服务日志
在Zeabur服务页面查看日志，如果看到：
- ✅ `Application startup complete` - 成功
- ❌ `Field required` - 仍有缺失的变量

### 方法2：访问健康检查
```
https://your-app-name.zeabur.app/health
```
- ✅ 返回JSON响应 - 成功
- ❌ 500错误或无法访问 - 仍有问题

### 方法3：在Zeabur终端中检查
```bash
env | grep FACEBOOK
env | grep OPENAI
env | grep TELEGRAM
env | grep SECRET_KEY
```

## 📝 配置检查清单

在添加环境变量时，请确认：

- [ ] `FACEBOOK_APP_ID` 已添加
- [ ] `FACEBOOK_APP_SECRET` 已添加
- [ ] `FACEBOOK_ACCESS_TOKEN` 已添加
- [ ] `FACEBOOK_VERIFY_TOKEN` 已添加
- [ ] `OPENAI_API_KEY` 已添加
- [ ] `OPENAI_MODEL` 已添加（值：`gpt-4o-mini`）
- [ ] `OPENAI_TEMPERATURE` 已添加（值：`0.7`）
- [ ] `TELEGRAM_BOT_TOKEN` 已添加
- [ ] `TELEGRAM_CHAT_ID` 已添加
- [ ] `SECRET_KEY` 已添加（请生成32位以上随机字符串）
- [ ] `DEBUG` 已添加（值：`false`）
- [ ] 所有变量已保存
- [ ] 服务已重启

## 🆘 如果仍然失败

如果配置完所有环境变量后仍然失败：

1. **检查变量名**：确保完全匹配（可以复制粘贴变量名）
2. **检查变量值**：确保没有多余空格或特殊字符
3. **查看完整错误日志**：在Zeabur服务页面查看详细错误信息
4. **确认服务已重启**：环境变量更改后需要重启
5. **检查DATABASE_URL**：如果使用PostgreSQL，确保数据库服务已启动

## 📚 相关文档

- [环境变量详细说明](ZEABUR_ENV_VARS.md)
- [配置步骤](ZEABUR_CONFIGURATION_STEPS.md)
- [环境变量模板](../ZEABUR_ENV_VARS_TEMPLATE.txt)

