# Zeabur部署安全指南

## 🚨 部署前必须完成的安全检查

在部署到Zeabur之前，**必须**确保没有敏感信息泄露。

## ⚡ 快速检查（推荐）

运行一键安全检查脚本：

```bash
# Windows
scripts\deployment\pre_deploy_security_check.bat

# 或手动运行
python scripts/tools/check_sensitive_data.py
```

## 📋 详细检查步骤

### 1. 运行敏感信息检查

```bash
python scripts/tools/check_sensitive_data.py
```

**必须看到**：`✅ 未发现敏感信息泄露！`

### 2. 检查关键文件

确保以下文件**不在Git仓库中**：

```bash
git status
```

不应该看到：
- `.env`
- `.env.local`
- `config/config.yaml`
- `.page_tokens.json`
- `logs/` 目录
- `*.log` 文件

### 3. 如果发现敏感文件已提交

**立即处理**：

```bash
# 1. 从Git中移除（但保留本地文件）
git rm --cached .page_tokens.json
git rm --cached config/config.yaml
git rm -r --cached logs/

# 2. 提交移除操作
git commit -m "Remove sensitive files from Git"

# 3. 推送到远程
git push
```

### 4. 撤销已泄露的密钥

如果发现真实密钥已泄露：

1. **Facebook Token**：
   - 访问：https://developers.facebook.com/tools/accesstoken/
   - 撤销旧Token
   - 生成新Token

2. **OpenAI API Key**：
   - 访问：https://platform.openai.com/api-keys
   - 删除旧Key
   - 创建新Key

3. **Telegram Bot Token**：
   - 访问：https://t.me/BotFather
   - 使用 `/revoke` 撤销
   - 使用 `/newtoken` 生成新Token

## ✅ 部署前最终检查清单

- [ ] 运行 `python scripts/tools/check_sensitive_data.py` 通过
- [ ] `git status` 没有敏感文件
- [ ] `.gitignore` 包含所有敏感文件
- [ ] 文档中没有真实密钥
- [ ] 代码中没有硬编码密钥
- [ ] 已撤销所有泄露的密钥（如果发现）

## 🔒 安全配置

### Zeabur环境变量配置

在Zeabur中配置环境变量，**不要**在代码中硬编码：

1. 访问Zeabur项目页面
2. 点击您的服务
3. 找到 "Environment Variables"
4. 添加所有必需的环境变量：
   - `FACEBOOK_APP_ID`
   - `FACEBOOK_APP_SECRET`
   - `FACEBOOK_ACCESS_TOKEN`
   - `FACEBOOK_VERIFY_TOKEN`
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `SECRET_KEY`
   - `DATABASE_URL`（Zeabur自动设置）

### 配置文件

- ✅ 提交 `config/config.yaml.example`（示例文件）
- ❌ **不要**提交 `config/config.yaml`（真实配置）

## 🚀 安全部署流程

1. **本地检查**：
   ```bash
   python scripts/tools/check_sensitive_data.py
   ```

2. **提交代码**：
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

3. **推送到GitHub**：
   ```bash
   git push
   ```

4. **在Zeabur中配置环境变量**（不要通过代码）

5. **部署**：
   - Zeabur会自动从GitHub拉取代码
   - 使用Zeabur中配置的环境变量

## ⚠️ 常见错误

### 错误1：提交了 .env 文件

**解决**：
```bash
git rm --cached .env
git commit -m "Remove .env file"
git push
```

### 错误2：提交了 config/config.yaml

**解决**：
```bash
git rm --cached config/config.yaml
git commit -m "Remove config.yaml"
git push
```

### 错误3：文档中有真实密钥

**解决**：
1. 编辑文档，替换为占位符
2. 提交更改
3. 撤销泄露的密钥

## 📚 相关文档

- [安全检查清单](SECURITY_CHECKLIST.md)
- [敏感信息检查脚本](../../scripts/tools/check_sensitive_data.py)
- [部署准备检查](../../scripts/deployment/prepare_deployment.py)

---

**重要**：部署前必须完成安全检查，确保没有敏感信息泄露！

