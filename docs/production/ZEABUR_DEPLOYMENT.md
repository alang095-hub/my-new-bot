# Zeabur 部署指南

## 概述

Zeabur 是一个现代化的云平台，支持从 GitHub 仓库一键部署应用。本指南将帮助您将系统部署到 Zeabur。

## 部署前准备

### 0. 本地测试（强烈推荐）

**在部署到Zeabur之前，强烈建议在本地进行完整测试！**

```bash
# 运行部署前测试
# Windows
scripts\test\pre_deployment_test.bat

# Linux/Mac
chmod +x scripts/test/pre_deployment_test.sh
./scripts/test/pre_deployment_test.sh
```

**测试内容：**
- 环境配置验证
- 数据库连接测试
- 多页面Token配置检查
- 服务启动测试
- 完整功能测试

**详细说明：** 参考 [部署前本地测试指南](PRE_DEPLOYMENT_TESTING.md)

### 1. 必需的环境变量清单

在 Zeabur 部署前，请准备以下环境变量：

#### 数据库配置
```
DATABASE_URL=postgresql://user:password@host:port/database
DATABASE_ECHO=false
```

#### Facebook配置
```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_VERIFY_TOKEN=your_verify_token
```

#### OpenAI配置
```
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
```

#### Telegram配置
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

#### 安全配置
```
SECRET_KEY=your_secret_key_at_least_32_characters_long
DEBUG=false
```

#### CORS配置（生产环境必需）
```
CORS_ORIGINS=https://your-app-name.zeabur.app,https://yourdomain.com
```

#### 服务器配置（可选，Zeabur会自动设置）
```
HOST=0.0.0.0
PORT=8000  # Zeabur会自动设置PORT环境变量
```

### 2. 代码准备

确保代码已推送到 GitHub 仓库：

```bash
# 检查Git状态
git status

# 提交所有更改
git add .
git commit -m "准备部署到Zeabur"

# 推送到GitHub
git push origin main
```

### 3. 配置文件检查

确保以下文件存在且正确配置：

- [ ] `Procfile` - 启动命令配置
- [ ] `requirements.txt` - Python依赖
- [ ] `config/config.yaml` - 业务规则配置（需要提交到仓库或使用环境变量）

## 部署步骤

### 步骤1：创建Zeabur项目

1. 访问 [Zeabur](https://zeabur.com)
2. 注册/登录账号
3. 点击 "New Project" 创建新项目
4. 选择 "Deploy from GitHub"

### 步骤2：连接GitHub仓库

1. 授权Zeabur访问您的GitHub账号
2. 选择包含项目代码的仓库
3. 选择分支（通常是 `main` 或 `master`）

### 步骤3：配置环境变量

在Zeabur项目设置中，添加所有必需的环境变量：

**方法1：通过Zeabur控制台**
1. 进入项目设置
2. 找到 "Environment Variables" 部分
3. 逐个添加环境变量

**方法2：批量导入（如果有.env文件）**
1. 在项目设置中找到环境变量导入功能
2. 上传 `.env` 文件（注意：不要上传包含敏感信息的.env到GitHub）

**重要环境变量：**
```
DATABASE_URL=postgresql://...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_VERIFY_TOKEN=...
OPENAI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
SECRET_KEY=...
DEBUG=false
CORS_ORIGINS=https://your-app-name.zeabur.app
```

### 步骤4：添加PostgreSQL数据库

1. 在Zeabur项目中，点击 "Add Service"
2. 选择 "PostgreSQL"
3. Zeabur会自动创建数据库并设置 `DATABASE_URL` 环境变量
4. 如果使用自己的数据库，手动设置 `DATABASE_URL`

### 步骤5：配置构建和启动

Zeabur会自动检测Python项目，但您可以手动配置：

**构建命令（可选）：**
```bash
pip install -r requirements.txt
```

**启动命令：**
Zeabur会使用 `Procfile` 中的配置，或自动检测。确保 `Procfile` 包含：
```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### 步骤6：运行数据库迁移

Zeabur支持在部署时运行命令。您需要：

**方法1：使用Zeabur的Post-Deploy Hook**
在项目设置中添加部署后命令：
```bash
alembic upgrade head
```

**方法2：在启动脚本中运行迁移**
修改启动命令（不推荐，但可行）：
```bash
alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

**方法3：手动运行迁移**
1. 连接到Zeabur的终端/SSH
2. 运行：`alembic upgrade head`

### 步骤7：部署

1. 点击 "Deploy" 按钮
2. 等待构建和部署完成
3. 查看部署日志，确认无错误

## 部署后配置

### 1. 获取应用URL

部署完成后，Zeabur会提供一个URL，格式类似：
```
https://your-app-name.zeabur.app
```

### 2. 配置Facebook Webhook

1. 登录 Facebook Developer Console
2. 进入您的应用设置
3. 配置 Webhook URL：
   ```
   https://your-app-name.zeabur.app/webhook
   ```
4. 设置 Verify Token（与 `FACEBOOK_VERIFY_TOKEN` 环境变量一致）

### 3. 验证部署

```bash
# 健康检查
curl https://your-app-name.zeabur.app/health

# API文档
https://your-app-name.zeabur.app/docs

# 性能指标
curl https://your-app-name.zeabur.app/metrics
```

### 4. 运行测试

```bash
# 使用部署的URL运行测试
python scripts/test/production_test.py --test all --url https://your-app-name.zeabur.app
```

## 配置文件说明

### Procfile

Zeabur会使用 `Procfile` 来确定如何启动应用：

```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### requirements.txt

确保所有依赖都在 `requirements.txt` 中列出。

### config/config.yaml

**重要：** 如果 `config/config.yaml` 包含敏感信息，不要提交到GitHub。可以：

1. 使用环境变量替代配置
2. 使用Zeabur的Secret管理
3. 在部署后通过SSH上传配置文件

## 环境变量详细说明

### 必需的环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DATABASE_URL` | PostgreSQL连接字符串 | `postgresql://user:pass@host:5432/db` |
| `FACEBOOK_APP_ID` | Facebook应用ID | `123456789` |
| `FACEBOOK_APP_SECRET` | Facebook应用密钥 | `abc123...` |
| `FACEBOOK_ACCESS_TOKEN` | Facebook访问令牌 | `EAABwz...` |
| `FACEBOOK_VERIFY_TOKEN` | Webhook验证令牌 | `your_verify_token` |
| `OPENAI_API_KEY` | OpenAI API密钥 | `sk-...` |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot令牌 | `123456:ABC...` |
| `TELEGRAM_CHAT_ID` | Telegram聊天ID | `-1001234567890` |
| `SECRET_KEY` | 应用密钥（至少32字符） | `your_secret_key_32_chars_min` |
| `DEBUG` | 调试模式（生产环境必须false） | `false` |

### 可选的环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `CORS_ORIGINS` | CORS允许的来源 | 空（拒绝所有） |
| `OPENAI_MODEL` | OpenAI模型 | `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | OpenAI温度 | `0.7` |
| `HOST` | 服务器主机 | `0.0.0.0` |
| `PORT` | 服务器端口 | Zeabur自动设置 |

## 常见问题

### Q1: 如何查看部署日志？

A: 在Zeabur控制台的 "Logs" 标签页查看实时日志。

### Q2: 数据库迁移失败怎么办？

A: 
1. 检查 `DATABASE_URL` 是否正确
2. 确认数据库服务已启动
3. 手动连接到容器运行迁移：
   ```bash
   alembic upgrade head
   ```

### Q3: 如何更新代码？

A: 
1. 推送代码到GitHub
2. Zeabur会自动检测并重新部署
3. 或手动触发部署

### Q4: 如何配置自定义域名？

A: 
1. 在Zeabur项目设置中找到 "Domains"
2. 添加您的自定义域名
3. 按照提示配置DNS记录

### Q5: 如何备份数据库？

A: 
1. 使用Zeabur的数据库备份功能
2. 或通过SSH连接到数据库服务
3. 运行 `pg_dump` 命令

### Q6: 如何查看应用性能？

A: 
1. 使用Zeabur的监控面板
2. 访问 `/metrics` 端点
3. 运行性能监控脚本：
   ```bash
   python scripts/monitoring/performance_monitor.py --url https://your-app-name.zeabur.app
   ```

## 安全建议

1. **不要提交敏感信息到GitHub**
   - 使用 `.gitignore` 排除 `.env` 文件
   - 使用Zeabur的环境变量管理

2. **使用强密码和密钥**
   - `SECRET_KEY` 至少32字符
   - 数据库密码足够复杂

3. **配置CORS**
   - 只允许必要的域名
   - 不要使用 `*` 通配符

4. **启用HTTPS**
   - Zeabur默认提供HTTPS
   - 确保所有API调用使用HTTPS

5. **定期更新依赖**
   - 定期检查并更新 `requirements.txt`
   - 修复安全漏洞

## 监控和维护

### 查看日志

在Zeabur控制台查看：
- 应用日志
- 构建日志
- 错误日志

### 性能监控

```bash
# 运行性能监控
python scripts/monitoring/performance_monitor.py \
  --url https://your-app-name.zeabur.app \
  --interval 60
```

### 告警配置

配置Zeabur的告警功能，监控：
- 应用崩溃
- 高错误率
- 资源使用过高

## 回滚

如果需要回滚到之前的版本：

1. 在Zeabur控制台找到 "Deployments"
2. 选择之前的成功部署
3. 点击 "Redeploy"

## 相关文档

- [完整部署指南](DEPLOYMENT_GUIDE.md)
- [部署检查清单](DEPLOYMENT_CHECKLIST.md)
- [CORS配置](CORS_CONFIGURATION.md)
- [PostgreSQL迁移](POSTGRESQL_MIGRATION.md)

## 快速检查清单

部署前确认：

- [ ] 代码已推送到GitHub
- [ ] 所有环境变量已准备
- [ ] `Procfile` 存在且正确
- [ ] `requirements.txt` 完整
- [ ] `config/config.yaml` 已配置（或使用环境变量）
- [ ] Facebook Webhook URL已更新
- [ ] 数据库已创建或连接字符串已配置

部署后验证：

- [ ] 健康检查通过
- [ ] API端点可访问
- [ ] 数据库迁移成功
- [ ] Facebook Webhook验证通过
- [ ] 功能测试通过

