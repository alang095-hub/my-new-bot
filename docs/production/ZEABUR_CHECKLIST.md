# 📋 Zeabur部署完整检查清单

## 🎯 使用检查脚本（推荐）

### Python脚本（详细检查）

```bash
# 安装依赖
pip install httpx

# 运行检查
python scripts/tools/check_zeabur_deployment.py

# 或指定URL
python scripts/tools/check_zeabur_deployment.py --url https://my-telegram-bot33.zeabur.app

# 保存报告
python scripts/tools/check_zeabur_deployment.py --save-report
```

### Windows批处理脚本（快速检查）

```bash
scripts\tools\check_zeabur_deployment.bat
```

## 📋 手动检查清单

### 1. 服务状态检查

**在Zeabur控制台：**

- [ ] 访问：https://zeabur.com
- [ ] 找到项目：my-telegram-bot33
- [ ] 查看应用服务状态：
  - 🟢 **Running** - 服务运行中 ✅
  - 🟡 **Building** - 正在构建，请等待
  - 🟡 **Restarting** - 正在重启
  - 🔴 **Failed** - 构建失败，需要查看日志

### 2. 环境变量配置检查

**在应用服务设置中，检查以下环境变量：**

#### 必需的环境变量

- [ ] `DATABASE_URL` - 数据库连接（如果使用Zeabur的PostgreSQL，会自动设置）
  - 格式：`postgresql://postgres:xxx@xxx.zeabur.com:5432/postgres`
  - 值应该以 `postgresql://` 开头

- [ ] `FACEBOOK_APP_ID` - Facebook应用ID
- [ ] `FACEBOOK_APP_SECRET` - Facebook应用密钥
- [ ] `FACEBOOK_ACCESS_TOKEN` - Facebook访问令牌（用户级Token）
- [ ] `FACEBOOK_VERIFY_TOKEN` - Webhook验证令牌
- [ ] `OPENAI_API_KEY` - OpenAI API密钥（格式：`sk-...`）
- [ ] `TELEGRAM_BOT_TOKEN` - Telegram Bot令牌
- [ ] `TELEGRAM_CHAT_ID` - Telegram聊天ID
- [ ] `SECRET_KEY` - 应用密钥（至少32字符）
- [ ] `DEBUG` - 设置为 `false`

#### 可选的环境变量

- [ ] `CORS_ORIGINS` - CORS允许的来源（例如：`https://my-telegram-bot33.zeabur.app`）
- [ ] `OPENAI_MODEL` - OpenAI模型（默认：`gpt-4o-mini`）
- [ ] `OPENAI_TEMPERATURE` - OpenAI温度（默认：`0.7`）

### 3. PostgreSQL服务检查

**在项目页面：**

- [ ] PostgreSQL服务已添加
- [ ] PostgreSQL服务状态是 **"Running"**
- [ ] PostgreSQL服务已连接到应用服务
  - 在PostgreSQL服务页面，确认应用服务已列出
  - 或在应用服务页面，确认PostgreSQL服务已列出
- [ ] `DATABASE_URL` 环境变量已自动设置

### 4. 服务日志检查

**在应用服务页面：**

- [ ] 找到 **"Logs"** 或 **"日志"** 标签
- [ ] 查看最新的日志信息
- [ ] 确认看到以下信息：
  ```
  INFO:     Uvicorn running on http://0.0.0.0:XXXX
  INFO:     Application startup complete.
  ```
- [ ] 没有错误信息（ERROR/Exception/Traceback）

### 5. 端点访问检查

**测试以下端点：**

- [ ] `/health/simple` - 简单健康检查
  - URL: `https://my-telegram-bot33.zeabur.app/health/simple`
  - 应该返回：`{"status": "ok", ...}`

- [ ] `/health` - 完整健康检查
  - URL: `https://my-telegram-bot33.zeabur.app/health`
  - 应该返回：`{"status": "healthy", "checks": {...}}`
  - 数据库状态应该是 `"healthy"`

- [ ] `/` - 根路径
  - URL: `https://my-telegram-bot33.zeabur.app/`
  - 应该返回应用信息

- [ ] `/docs` - API文档
  - URL: `https://my-telegram-bot33.zeabur.app/docs`
  - 应该显示API文档界面

- [ ] `/admin/deployment/status` - 部署状态
  - URL: `https://my-telegram-bot33.zeabur.app/admin/deployment/status`
  - 应该返回部署状态信息

- [ ] `/admin/deployment/verify-token` - Token验证
  - URL: `https://my-telegram-bot33.zeabur.app/admin/deployment/verify-token`
  - 应该返回Token验证结果

### 6. 配置文件检查

**确认以下文件存在且正确配置：**

- [ ] `Procfile` - 包含：`web: uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- [ ] `zeabur.json` - 包含正确的启动命令
- [ ] `requirements.txt` - 包含所有依赖
- [ ] `runtime.txt` - 指定Python版本（可选）

### 7. 功能检查

**确认以下功能正常：**

- [ ] Facebook平台已启用（查看日志）
- [ ] 自动回复调度器已启动（查看日志）
- [ ] 数据库连接正常（健康检查端点）
- [ ] 正在扫描页面查找未回复的消息（查看日志）

## 🔍 使用检查脚本

### Python脚本（推荐）

**安装依赖：**
```bash
pip install httpx
```

**运行检查：**
```bash
python scripts/tools/check_zeabur_deployment.py
```

**指定URL：**
```bash
python scripts/tools/check_zeabur_deployment.py --url https://my-telegram-bot33.zeabur.app
```

**保存报告：**
```bash
python scripts/tools/check_zeabur_deployment.py --save-report
```

### Windows批处理脚本

```bash
scripts\tools\check_zeabur_deployment.bat
```

## 🆘 如果检查失败

### 端点无法访问（502错误）

1. **查看服务状态**
   - 确认服务状态是 "Running"
   - 如果状态不是 "Running"，等待或重启服务

2. **查看服务日志**
   - 查找错误信息
   - 检查是否有崩溃日志

3. **检查环境变量**
   - 确认所有必需的环境变量都已配置
   - 确认 `DATABASE_URL` 已设置

### 数据库连接失败

1. **检查PostgreSQL服务**
   - 确认服务状态是 "Running"
   - 确认服务已连接到应用服务

2. **检查DATABASE_URL**
   - 确认环境变量已设置
   - 确认格式正确

### 环境变量缺失

1. **在Zeabur控制台配置**
   - 在应用服务设置中，添加缺失的环境变量
   - 保存并等待服务重启

## 📊 检查报告

运行Python脚本并保存报告：

```bash
python scripts/tools/check_zeabur_deployment.py --save-report
```

报告会保存到 `zeabur_check_report.json`，包含：
- 所有端点的检查结果
- 响应时间
- 错误信息
- 数据库连接状态

## 📚 相关文档

- [服务启动成功指南](SERVICE_STARTED_SUCCESS.md)
- [502错误排查步骤](502_TROUBLESHOOTING_STEPS.md)
- [数据库连接修复](FIX_DATABASE_CONNECTION.md)
- [环境变量配置](ZEABUR_ENV_VARS.md)




