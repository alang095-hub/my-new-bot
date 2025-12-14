# 🚀 快速部署到Zeabur

## 当前状态检查

✅ **已配置：**
- Facebook Token（用户级，已同步3个页面）
- Facebook App ID
- OpenAI API Key
- Telegram Bot Token

## 部署步骤（5分钟）

### 1️⃣ 准备GitHub仓库

```bash
# 提交所有更改
git add .
git commit -m "准备部署到Zeabur"
git push origin main
```

### 2️⃣ 在Zeabur创建项目

1. 访问 https://zeabur.com
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub"**
4. 选择您的仓库
5. 选择 `main` 分支

### 3️⃣ 添加PostgreSQL数据库

1. 在项目页面点击 **"Add Service"**
2. 选择 **"PostgreSQL"**
3. 等待数据库启动（约1-2分钟）

### 4️⃣ 配置环境变量

在项目设置中找到 **"Environment Variables"**，添加：

```env
# Facebook配置（使用用户级Token）
FACEBOOK_APP_ID=你的App ID
FACEBOOK_APP_SECRET=你的App Secret
FACEBOOK_ACCESS_TOKEN=你的用户级Token（有pages_show_list权限）
FACEBOOK_VERIFY_TOKEN=你的验证令牌

# OpenAI配置
OPENAI_API_KEY=sk-你的密钥
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Telegram配置
TELEGRAM_BOT_TOKEN=你的Bot Token
TELEGRAM_CHAT_ID=你的Chat ID

# 应用配置
SECRET_KEY=生成一个32字符的密钥
DEBUG=false
```

**生成SECRET_KEY：**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 5️⃣ 等待部署完成

- 查看构建日志
- 等待服务启动（约2-3分钟）
- 获取应用URL（格式：`https://xxx.zeabur.app`）

### 6️⃣ 运行数据库迁移

在Zeabur终端中运行：

```bash
alembic upgrade head
```

### 7️⃣ 同步所有页面Token（重要！）

```bash
python scripts/tools/manage_pages.py sync
```

这会自动同步所有10+页面的Token。

### 8️⃣ 更新Facebook Webhook

1. 登录 Facebook Developer Console
2. 更新Webhook URL为：`https://your-app-name.zeabur.app/webhook`
3. 确认Verify Token一致

### 9️⃣ 验证部署

访问：`https://your-app-name.zeabur.app/health`

应该看到：
```json
{
  "status": "healthy",
  ...
}
```

## ⚠️ 重要提示

### 多页面配置

由于您管理10+个页面，**必须使用用户级Token**：

1. `FACEBOOK_ACCESS_TOKEN` 必须是用户级Token（有`pages_show_list`权限）
2. 部署后运行 `python scripts/tools/manage_pages.py sync` 同步所有页面
3. 系统会自动为所有页面启用自动回复

### 环境变量优先级

- Zeabur环境变量 > 本地.env文件
- 部署后，所有配置都从Zeabur环境变量读取

## 📋 部署检查清单

- [ ] 代码已推送到GitHub
- [ ] Zeabur项目已创建
- [ ] PostgreSQL数据库已添加
- [ ] 所有环境变量已配置
- [ ] 部署成功完成
- [ ] 数据库迁移已运行
- [ ] 所有页面Token已同步
- [ ] Facebook Webhook已更新
- [ ] 健康检查通过
- [ ] 测试消息自动回复正常

## 🔗 相关文档

- [详细部署步骤](ZEABUR_DEPLOY_STEPS.md)
- [部署检查清单](ZEABUR_DEPLOY_CHECKLIST.md)
- [多页面配置指南](ZEABUR_MULTI_PAGE_SETUP.md)

## 🆘 遇到问题？

查看 [Zeabur部署指南](ZEABUR_DEPLOYMENT.md) 中的"常见问题"部分。
