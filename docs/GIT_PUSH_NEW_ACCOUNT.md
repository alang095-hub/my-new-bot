# 推送到新 GitHub 账号仓库

## 方法1：使用 Personal Access Token（推荐）

### 步骤1：创建 Personal Access Token

1. 登录新的 GitHub 账号
2. 访问：https://github.com/settings/tokens
3. 点击 "Generate new token" → "Generate new token (classic)"
4. 设置：
   - Note: `my-fb-bot-push`
   - Expiration: 根据需要选择（建议 90 天或 No expiration）
   - Scopes: 勾选 `repo`（完整仓库访问权限）
5. 点击 "Generate token"
6. **重要**：复制生成的 token（只显示一次）

### 步骤2：更新远程仓库地址

```bash
# 如果新账号的仓库地址不同，先更新
git remote set-url origin https://github.com/新用户名/新仓库名.git

# 或者使用 SSH（如果配置了 SSH 密钥）
git remote set-url origin git@github.com:新用户名/新仓库名.git
```

### 步骤3：使用 Token 推送

```bash
# 推送时，用户名输入新账号的用户名，密码输入 Personal Access Token
git push -u origin main
```

**或者使用 token 直接推送：**
```bash
git push https://你的token@github.com/新用户名/新仓库名.git main
```

## 方法2：使用 GitHub CLI（gh）

### 安装 GitHub CLI

```bash
# Windows (使用 Chocolatey)
choco install gh

# 或下载安装包
# https://cli.github.com/
```

### 登录新账号

```bash
gh auth login
# 选择 GitHub.com
# 选择 HTTPS
# 选择使用浏览器登录或输入 token
```

### 推送代码

```bash
git push -u origin main
```

## 方法3：配置 Git Credential Manager

### Windows

```bash
# 清除旧的凭据
git credential-manager-core erase
# 或
git credential reject https://github.com

# 下次推送时会提示输入新账号的用户名和密码（token）
git push -u origin main
```

## 方法4：在 URL 中直接使用 Token（临时）

```bash
# 格式：https://token@github.com/用户名/仓库名.git
git remote set-url origin https://你的token@github.com/新用户名/新仓库名.git
git push -u origin main

# 推送完成后，建议移除 token（安全考虑）
git remote set-url origin https://github.com/新用户名/新仓库名.git
```

## 当前状态

- ✅ 代码已提交到本地（提交 ID: a1c9311）
- ✅ 远程仓库已设置为：`https://github.com/allan0851/my-fb-bot.git`
- ⚠️ 原账号被暂停，需要切换到新账号

## 快速操作步骤

1. **获取新账号的仓库地址**
   - 如果还没有创建，先在新账号下创建仓库
   - 复制仓库地址，例如：`https://github.com/新用户名/新仓库名.git`

2. **更新远程地址**
   ```bash
   git remote set-url origin https://github.com/新用户名/新仓库名.git
   ```

3. **创建 Personal Access Token**
   - 访问：https://github.com/settings/tokens
   - 创建新 token，勾选 `repo` 权限

4. **推送代码**
   ```bash
   git push -u origin main
   ```
   - 用户名：输入新账号的用户名
   - 密码：输入 Personal Access Token（不是账号密码）

## 安全提示

- ⚠️ Personal Access Token 具有完整仓库访问权限，请妥善保管
- ⚠️ 不要将 token 提交到代码仓库
- ⚠️ 如果 token 泄露，立即在 GitHub 设置中撤销
- ✅ 建议使用 SSH 密钥方式（更安全）

## 使用 SSH 密钥（最安全）

### 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### 添加 SSH 密钥到 GitHub

1. 复制公钥内容：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

2. 访问：https://github.com/settings/keys
3. 点击 "New SSH key"
4. 粘贴公钥内容并保存

### 使用 SSH 推送

```bash
git remote set-url origin git@github.com:新用户名/新仓库名.git
git push -u origin main
```

