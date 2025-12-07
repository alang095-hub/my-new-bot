# 使用 ngrok 配置 Facebook Webhook（本地测试）

## 📋 概述

Facebook Webhook 需要 HTTPS 连接。对于本地开发，可以使用 ngrok 创建 HTTPS 隧道。

## 🔧 安装 ngrok

### Windows

1. 访问：https://ngrok.com/download
2. 下载 Windows 版本
3. 解压到任意目录
4. 添加到系统 PATH（可选）

### 注册账号

1. 访问：https://dashboard.ngrok.com/signup
2. 注册免费账号
3. 获取 authtoken

### 配置 authtoken

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

## 🚀 启动 ngrok 隧道

### 方法 1: 命令行启动

```bash
ngrok http 8000
```

### 方法 2: 使用配置文件

创建 `ngrok.yml`:

```yaml
version: "2"
authtoken: YOUR_AUTHTOKEN
tunnels:
  facebook-webhook:
    addr: 8000
    proto: http
```

然后运行：

```bash
ngrok start facebook-webhook
```

## 📝 获取 HTTPS URL

ngrok 启动后会显示：

```
Forwarding  https://xxxx-xx-xx-xx-xx.ngrok.io -> http://localhost:8000
```

复制这个 HTTPS URL（例如：`https://abc123.ngrok.io`）

## 🔗 配置 Facebook Webhook

### 步骤 1: 访问 Facebook Developer Console

1. 访问：https://developers.facebook.com/
2. 选择您的应用
3. 进入 "Webhooks" 设置

### 步骤 2: 添加 Webhook

1. 点击 "Add Callback URL"
2. 输入 Webhook URL: `https://xxxx-xx-xx-xx-xx.ngrok.io/webhook`
3. 输入验证令牌：
   - **本地开发**：从 `.env` 文件中的 `FACEBOOK_VERIFY_TOKEN` 获取
   - **Zeabur 部署**：从 Zeabur 环境变量中的 `FACEBOOK_VERIFY_TOKEN` 获取
   - 这个值必须与你的应用配置完全一致
4. 点击 "Verify and Save"

### 步骤 3: 订阅事件

选择要订阅的事件：
- ✅ `messages` - 接收消息
- ✅ `messaging_postbacks` - 接收回传
- ✅ `messaging_optins` - 接收选择加入

### 步骤 4: 验证

Facebook 会发送验证请求到您的 Webhook URL。如果配置正确，会显示 "Verified"。

## ⚠️ 注意事项

### ngrok 免费版限制

- URL 每次启动都会变化
- 需要重新配置 Facebook Webhook
- 有连接数限制

### ngrok 付费版

- 可以设置固定域名
- 更高的连接数限制
- 更适合生产环境

### 生产环境

生产环境应该使用：
- 真实的 HTTPS 域名
- 稳定的服务器
- 专业的 Webhook 管理

## 🧪 测试 Webhook

### 使用 Facebook 测试工具

1. 在 Facebook Developer Console 中
2. 进入 "Webhooks" 设置
3. 点击 "Test" 按钮
4. 选择要测试的事件
5. 查看服务日志确认接收

### 手动测试

发送测试消息到您的 Facebook 页面，然后：
1. 查看服务日志
2. 检查数据库记录
3. 验证消息处理

## 📚 相关文档

- **TESTING_COMPLETE_GUIDE.md** - 完整测试指南
- **API_TESTING_GUIDE.md** - API 测试指南

