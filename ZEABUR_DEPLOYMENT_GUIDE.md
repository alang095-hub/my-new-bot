# Zeabur 云端部署使用指南

## 🎉 系统已成功部署到 Zeabur

## 重要配置检查

### 1. 获取云端服务URL

在Zeabur控制台中：
1. 找到您的服务
2. 复制分配的域名（例如：`your-app.zeabur.app`）
3. 记录完整的URL（包括协议：`https://your-app.zeabur.app`）

### 2. 更新Webhook配置

#### Facebook Webhook配置

在 [Facebook开发者后台](https://developers.facebook.com/)：

1. 进入您的应用
2. 选择产品 → Messenger → 设置
3. 在"Webhooks"部分：
   - **回调URL**: `https://your-app.zeabur.app/webhook`
   - **验证令牌**: 使用您配置的 `FACEBOOK_VERIFY_TOKEN`
4. 点击"验证并保存"
5. 订阅以下事件：
   - `messages`
   - `messaging_postbacks`
   - `message_deliveries`
   - `message_reads`

#### Instagram Webhook配置

在 [Facebook开发者后台](https://developers.facebook.com/)：

1. 进入您的应用
2. 选择产品 → Instagram → 设置
3. 在"Webhooks"部分：
   - **回调URL**: `https://your-app.zeabur.app/instagram/webhook`
   - **验证令牌**: 使用您配置的 `INSTAGRAM_VERIFY_TOKEN` 或 `FACEBOOK_VERIFY_TOKEN`
4. 点击"验证并保存"
5. 订阅以下事件：
   - `messages`

### 3. 环境变量配置

确保在Zeabur中配置了以下环境变量：

#### 必需配置
```env
# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_VERIFY_TOKEN=your_verify_token

# OpenAI
OPENAI_API_KEY=your_openai_key

# Telegram（可选）
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 数据库
DATABASE_URL=your_database_url
```

#### Instagram配置（可选）
```env
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
INSTAGRAM_VERIFY_TOKEN=your_verify_token
INSTAGRAM_USER_ID=your_instagram_user_id
```

### 4. 数据库配置

如果使用Zeabur的数据库服务：
- 确保数据库已创建并运行
- 复制数据库连接URL到 `DATABASE_URL` 环境变量
- 系统启动时会自动运行迁移

## 功能验证

### 1. 健康检查

访问：`https://your-app.zeabur.app/health`

应该返回：
```json
{"status": "healthy"}
```

### 2. API文档

访问：`https://your-app.zeabur.app/docs`

可以查看所有可用的API端点。

### 3. 测试Webhook

#### Facebook Webhook验证
```bash
curl "https://your-app.zeabur.app/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=test123"
```

应该返回：`test123`

#### Instagram Webhook验证
```bash
curl "https://your-app.zeabur.app/instagram/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=test123"
```

应该返回：`test123`

## 日志查看

在Zeabur控制台中：
1. 进入您的服务
2. 点击"日志"标签
3. 查看实时日志，包括：
   - Webhook接收事件
   - AI回复内容
   - 错误信息
   - 系统状态

## 权限配置（如需要）

### 如果需要帖子/广告管理功能

1. **生成授权URL**（在本地运行）：
   ```bash
   python show_auth_url.py
   ```

2. **完成授权**：
   - 复制授权URL
   - 在浏览器中打开并授权
   - 运行 `python extract_token.py` 提取新令牌

3. **更新环境变量**：
   - 在Zeabur控制台中更新 `FACEBOOK_ACCESS_TOKEN`
   - 重启服务使新令牌生效

4. **验证权限**（在本地运行）：
   ```bash
   python check_facebook_permissions.py
   ```

## 常见问题

### 1. Webhook验证失败

**原因**：
- 验证令牌不匹配
- URL配置错误
- HTTPS证书问题

**解决**：
- 检查 `FACEBOOK_VERIFY_TOKEN` 环境变量
- 确认Webhook URL正确
- 确保使用HTTPS（Zeabur默认提供）

### 2. 消息未收到

**原因**：
- Webhook未正确订阅事件
- 权限不足
- 服务未运行

**解决**：
- 检查Facebook开发者后台的事件订阅
- 查看Zeabur日志确认Webhook是否被调用
- 验证访问令牌权限

### 3. 数据库连接失败

**原因**：
- `DATABASE_URL` 配置错误
- 数据库服务未启动
- 网络连接问题

**解决**：
- 检查Zeabur中的数据库服务状态
- 验证 `DATABASE_URL` 格式正确
- 确认数据库已创建表（系统会自动迁移）

## 监控和维护

### 1. 查看服务状态

在Zeabur控制台查看：
- CPU使用率
- 内存使用率
- 请求数量
- 错误率

### 2. 重启服务

如果需要重启服务：
1. 在Zeabur控制台找到服务
2. 点击"重启"按钮
3. 等待服务重新启动

### 3. 更新代码

如果更新了代码：
1. 推送到Git仓库
2. Zeabur会自动检测并重新部署
3. 查看部署日志确认成功

## 安全建议

1. **保护访问令牌**：
   - 不要在代码中硬编码令牌
   - 使用Zeabur的环境变量功能
   - 定期轮换访问令牌

2. **HTTPS**：
   - Zeabur默认提供HTTPS
   - 确保所有Webhook URL使用HTTPS

3. **验证令牌**：
   - 使用强随机字符串作为验证令牌
   - 定期更新验证令牌

## 快速命令参考

```bash
# 本地检查权限
python check_facebook_permissions.py

# 生成授权URL
python show_auth_url.py

# 提取令牌
python extract_token.py

# 验证系统配置
python verify_platform_setup.py
```

## 支持的功能

### ✅ 已启用
- Facebook消息接收和发送
- Instagram消息接收（如果配置了USER_ID）
- AI自动回复
- 资料收集
- 智能过滤
- Telegram通知

### ⚠️ 需要额外权限
- Facebook帖子管理（需要`pages_manage_posts`权限）
- Facebook广告管理（需要`ads_read`和`ads_management`权限）

## 下一步

1. ✅ 确认Webhook URL已更新到云端地址
2. ✅ 验证Webhook在Facebook开发者后台配置正确
3. ✅ 测试消息接收和AI回复
4. ⚠️ 配置权限（如需要帖子/广告管理功能）

---

**系统已在云端运行，可以开始接收和处理消息了！** 🎉


