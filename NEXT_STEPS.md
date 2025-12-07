# 🎯 下一步行动指南

## 📍 当前状态
- ✅ 代码已优化并推送到仓库
- ✅ 时区问题已修复
- ✅ 应用已部署到 Zeabur
- ⏳ 需要配置环境变量和 Webhook

---

## 🚀 第一步：配置环境变量（必需）

### 在 Zeabur 平台配置

1. **进入 Zeabur 项目页面**
   - 打开你的 Zeabur 项目
   - 点击左侧菜单的 **"Variables"** 或 **"环境变量"**

2. **添加以下必需的环境变量：**

```env
# 数据库（Zeabur 通常会自动提供，检查是否已存在）
DATABASE_URL=自动提供或手动设置

# Facebook API（必需）
FACEBOOK_APP_ID=你的应用ID
FACEBOOK_APP_SECRET=你的应用密钥
FACEBOOK_ACCESS_TOKEN=你的长期访问令牌
FACEBOOK_VERIFY_TOKEN=自定义验证令牌（如：my_secure_token_2024）

# OpenAI API（必需）
OPENAI_API_KEY=sk-你的API密钥
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Telegram Bot（必需）
TELEGRAM_BOT_TOKEN=你的机器人令牌
TELEGRAM_CHAT_ID=你的聊天ID

# 安全密钥（必需）
SECRET_KEY=生成的随机密钥（至少32字符）
ALGORITHM=HS256
```

3. **生成 SECRET_KEY：**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **保存并重新部署**
   - 保存所有环境变量
   - Zeabur 会自动重新部署应用

---

## 🔑 第二步：获取 API 密钥

### 1. Facebook API 密钥

**步骤：**
1. 访问 [Facebook Developers](https://developers.facebook.com/)
2. 创建应用或选择现有应用
3. 在 "设置" → "基本" 中获取：
   - **App ID**
   - **App Secret**（点击"显示"）
4. 在 "工具" → "Graph API Explorer" 中：
   - 选择你的应用
   - 生成长期访问令牌（Long-lived Access Token）
   - 复制 **Access Token**

### 2. OpenAI API 密钥

**步骤：**
1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录账号
3. 点击 "Create new secret key"
4. 复制密钥（以 `sk-` 开头）
5. ⚠️ **重要：** 密钥只显示一次，请立即保存

### 3. Telegram Bot Token

**步骤：**
1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取 **Bot Token**（格式：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）
5. 获取 **Chat ID**：
   - 将机器人添加到群组或频道
   - 发送一条消息
   - 访问：`https://api.telegram.org/bot<TOKEN>/getUpdates`
   - 查找 `chat.id` 字段（群组ID通常是负数，如：`-1001234567890`）

---

## 🔗 第三步：配置 Facebook Webhook

### 1. 获取 Webhook URL

从 Zeabur 项目页面获取你的应用 URL：
```
https://你的域名.zeabur.app/webhook
```

### 2. 在 Facebook Developer Console 配置

1. **进入 Facebook Developers**
   - 选择你的应用
   - 左侧菜单 → **"Webhooks"**

2. **添加 Webhook**
   - 点击 **"Add Callback URL"**
   - 输入 Webhook URL：`https://你的域名.zeabur.app/webhook`
   - 输入 Verify Token：与 `.env` 中的 `FACEBOOK_VERIFY_TOKEN` 一致
   - 点击 **"Verify and Save"**

3. **订阅事件**
   - 在 Webhook 设置中，点击 **"订阅字段"**
   - 勾选以下事件：
     - ✅ `messages` - 接收消息
     - ✅ `messaging_postbacks` - 按钮点击
     - ✅ `message_deliveries` - 消息送达
     - ✅ `message_reads` - 消息已读

4. **验证 Webhook**
   - Facebook 会发送验证请求
   - 如果配置正确，会显示 ✅ "已验证"

---

## ✅ 第四步：验证配置

### 1. 检查应用状态

访问以下 URL 验证应用是否正常运行：

1. **健康检查：**
   ```
   https://你的域名.zeabur.app/health
   ```
   应该返回：`{"status": "healthy"}`

2. **API 文档：**
   ```
   https://你的域名.zeabur.app/docs
   ```
   应该显示 Swagger UI 文档

3. **系统信息：**
   ```
   https://你的域名.zeabur.app/
   ```
   应该返回系统信息

### 2. 检查日志

在 Zeabur 项目页面：
- 点击 **"Logs"** 或 **"日志"**
- 确认没有错误信息
- 应该看到：`Application startup complete`

### 3. 测试 Webhook

在 Facebook Developer Console：
- 进入 Webhook 设置
- 点击 **"Test"** 按钮
- 发送测试消息
- 检查 Zeabur 日志，确认收到消息

---

## 🧪 第五步：测试完整流程

### 1. 发送测试消息

1. 在你的 Facebook 页面发送一条消息
2. 系统应该自动回复（使用 AI 生成）

### 2. 查看实时监控

1. 打开 `monitoring_dashboard.html` 文件
2. 修改 `API_BASE` 为你的 Zeabur 域名：
   ```javascript
   const API_BASE = 'https://你的域名.zeabur.app';
   ```
3. 在浏览器中打开文件
4. 应该能看到：
   - 实时 AI 回复
   - 统计数据
   - 时间显示正确（本地时区）

### 3. 查看统计数据

访问：
```
https://你的域名.zeabur.app/statistics/daily
```

应该返回统计数据（可能是空的，如果还没有数据）

---

## 📊 第六步：监控和维护

### 1. 查看实时监控面板

- 打开 `monitoring_dashboard.html`
- 监控 AI 回复情况
- 查看统计数据

### 2. 定期检查

- **日志检查：** 每天查看 Zeabur 日志
- **API 使用：** 监控 OpenAI API 使用量
- **数据库：** 定期备份数据

---

## ⚠️ 常见问题排查

### 问题 1: 应用无法启动

**检查：**
- 所有必需的环境变量是否已设置
- 环境变量值是否正确（没有占位符）
- 查看 Zeabur 日志中的错误信息

**解决：**
- 检查 `SECRET_KEY` 是否已生成
- 确认所有 API 密钥格式正确
- 重新部署应用

### 问题 2: Webhook 验证失败

**检查：**
- Webhook URL 是否正确
- `FACEBOOK_VERIFY_TOKEN` 是否与 Facebook 设置一致
- 应用是否正在运行

**解决：**
- 确认 Webhook URL 可访问（访问 `/health` 端点）
- 重新验证 Webhook
- 检查 Zeabur 日志

### 问题 3: AI 不回复

**检查：**
- `OPENAI_API_KEY` 是否有效
- OpenAI API 是否有余额
- 查看日志中的错误信息

**解决：**
- 检查 OpenAI 账户余额
- 验证 API 密钥是否有效
- 查看日志中的详细错误

### 问题 4: 数据库连接失败

**检查：**
- `DATABASE_URL` 是否正确
- 数据库服务是否运行
- 查看日志中的数据库错误

**解决：**
- 确认 Zeabur 已添加 PostgreSQL 服务
- 检查 `DATABASE_URL` 格式
- 重新部署应用

---

## 📚 相关文档

- [配置清单](./SETUP_CHECKLIST.md) - 详细的配置说明
- [环境变量配置](./CONFIGURE_ENV.md) - 环境变量详细指南
- [实时监控指南](./REALTIME_MONITORING_GUIDE.md) - 监控面板使用说明
- [Facebook Webhook 配置](./CONFIGURE_REDIRECT_URI.md) - Webhook 配置指南

---

## 🎉 完成检查清单

完成以下所有步骤后，系统就可以正常使用了：

- [ ] 所有环境变量已配置
- [ ] Facebook API 密钥已设置
- [ ] OpenAI API 密钥已设置
- [ ] Telegram Bot 已配置
- [ ] SECRET_KEY 已生成
- [ ] Facebook Webhook 已配置并验证
- [ ] 应用健康检查通过
- [ ] 测试消息可以正常接收和回复
- [ ] 实时监控面板可以正常显示

---

**完成以上步骤后，你的系统就可以开始自动处理 Facebook 消息了！** 🚀

