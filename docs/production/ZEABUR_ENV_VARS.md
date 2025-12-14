# Zeabur 环境变量配置清单

## 快速复制清单

在Zeabur控制台配置环境变量时，可以使用此清单确保不遗漏任何变量。

## 必需的环境变量

### 数据库配置
```
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_ECHO=false
```

### Facebook配置
```
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_VERIFY_TOKEN=your_facebook_verify_token
```

### OpenAI配置
```
OPENAI_API_KEY=sk-your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
```

### Telegram配置
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 安全配置
```
SECRET_KEY=your_secret_key_at_least_32_characters_long
DEBUG=false
```

### CORS配置
```
CORS_ORIGINS=https://your-app-name.zeabur.app
```

## 可选的环境变量

### 服务器配置（Zeabur会自动设置，通常不需要）
```
HOST=0.0.0.0
PORT=8000
```

### Instagram配置（如果使用）
```
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
INSTAGRAM_VERIFY_TOKEN=your_instagram_verify_token
INSTAGRAM_USER_ID=your_instagram_user_id
```

## 环境变量说明

### DATABASE_URL
- **必需**: 是
- **格式**: `postgresql://用户名:密码@主机:端口/数据库名`
- **示例**: `postgresql://user:pass@db.zeabur.com:5432/customer_service`
- **注意**: 如果使用Zeabur的PostgreSQL服务，会自动设置此变量

### FACEBOOK_APP_ID
- **必需**: 是
- **说明**: Facebook应用的App ID
- **获取方式**: Facebook Developer Console

### FACEBOOK_APP_SECRET
- **必需**: 是
- **说明**: Facebook应用的App Secret
- **获取方式**: Facebook Developer Console

### FACEBOOK_ACCESS_TOKEN
- **必需**: 是
- **说明**: Facebook访问令牌
  - **多页面场景（推荐）**：使用用户级别Token（有`pages_show_list`权限），部署后运行同步脚本自动获取所有页面Token
  - **单页面场景**：直接使用页面Token
  - **作用**：作为默认Token，也用于同步所有页面的Token
- **获取方式**: Facebook Graph API Explorer
- **多页面配置**：部署后运行 `python scripts/tools/manage_page_tokens.py sync` 同步所有页面Token
- **详细说明**：参考 [多页面配置指南](ZEABUR_MULTI_PAGE_SETUP.md)

### FACEBOOK_VERIFY_TOKEN
- **必需**: 是
- **说明**: Webhook验证令牌（自定义）
- **注意**: 必须与Facebook Webhook配置中的Verify Token一致

### OPENAI_API_KEY
- **必需**: 是
- **格式**: `sk-...`
- **获取方式**: https://platform.openai.com/api-keys

### TELEGRAM_BOT_TOKEN
- **必需**: 是
- **格式**: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- **获取方式**: 与 @BotFather 对话创建Bot

### TELEGRAM_CHAT_ID
- **必需**: 是
- **格式**: 数字或负数（群组为负数）
- **获取方式**: 发送消息给Bot，访问 `https://api.telegram.org/bot<TOKEN>/getUpdates`

### SECRET_KEY
- **必需**: 是
- **长度**: 至少32字符
- **生成方式**: 
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```

### DEBUG
- **必需**: 是（生产环境）
- **值**: `false`
- **注意**: 生产环境必须设置为 `false`

### CORS_ORIGINS
- **必需**: 是（如果有前端）
- **格式**: 逗号分隔的URL列表
- **示例**: `https://your-app-name.zeabur.app,https://admin.yourdomain.com`
- **注意**: 不要使用 `*` 通配符

## 配置步骤

### 在Zeabur控制台配置

1. 进入项目设置
2. 找到 "Environment Variables" 部分
3. 点击 "Add Variable"
4. 输入变量名和值
5. 保存

### 批量导入（如果支持）

1. 准备 `.env` 格式文件（不要包含敏感信息）
2. 在Zeabur控制台找到导入功能
3. 上传文件

## 验证配置

部署后，可以通过以下方式验证：

```bash
# 检查环境变量（在Zeabur终端中）
env | grep FACEBOOK
env | grep OPENAI
env | grep TELEGRAM

# 或通过API检查（如果实现了）
curl https://your-app-name.zeabur.app/test/settings
```

## 安全注意事项

1. **不要在代码中硬编码密钥**
2. **不要将.env文件提交到GitHub**
3. **使用Zeabur的Secret管理功能**
4. **定期轮换密钥**
5. **使用强密码和密钥**

## 故障排查

### 问题：环境变量未生效

**解决方案：**
1. 检查变量名拼写是否正确
2. 确认已保存并重新部署
3. 检查是否有空格或特殊字符
4. 查看部署日志确认变量已加载

### 问题：数据库连接失败

**解决方案：**
1. 检查 `DATABASE_URL` 格式是否正确
2. 确认数据库服务已启动
3. 检查网络连接和防火墙设置
4. 验证用户名和密码

### 问题：Facebook Webhook验证失败

**解决方案：**
1. 确认 `FACEBOOK_VERIFY_TOKEN` 与Facebook配置一致
2. 检查Webhook URL是否正确
3. 查看应用日志确认请求已接收

