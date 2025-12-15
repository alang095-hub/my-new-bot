# Zeabur环境变量配置详细步骤（小白版）

## 📍 第2步：配置环境变量 - 完整指南

## 第一部分：添加PostgreSQL数据库

### 步骤1：添加数据库服务

1. **在Zeabur项目中**
   - 找到您的项目页面
   - 点击 **"Add Service"**（添加服务）按钮
   - 或者点击 **"+"** 号按钮

2. **选择数据库类型**
   - 在服务列表中找到 **"PostgreSQL"**
   - 点击 **"PostgreSQL"**

3. **等待创建**
   - Zeabur会自动创建PostgreSQL数据库
   - 等待约1-2分钟
   - 看到绿色 **"Running"** 表示创建成功

### 步骤2：获取数据库连接信息

1. **进入数据库服务**
   - 点击刚才创建的PostgreSQL服务
   - 进入服务详情页面

2. **找到连接信息**
   - 在服务页面找到 **"Connection String"** 或 **"DATABASE_URL"**
   - 或者找到 **"Environment Variables"**（环境变量）标签
   - 找到 `DATABASE_URL` 这个变量

3. **复制DATABASE_URL**
   - 点击复制按钮，或者选中文本复制
   - **重要**：完整复制，不要遗漏任何字符
   - 格式类似：`postgresql://postgres:password@host:5432/database`

4. **保存备用**
   - 暂时保存到记事本，后面要用

## 第二部分：配置应用环境变量

### 步骤1：进入应用服务设置

1. **找到应用服务**
   - 在项目中找到您的应用服务（不是数据库服务）
   - 通常显示为您的项目名称或"App"

2. **进入环境变量设置**
   - 点击应用服务
   - 在服务页面找到 **"Environment Variables"**（环境变量）
   - 点击进入环境变量页面

### 步骤2：逐个添加环境变量

按照以下顺序，逐个添加每个环境变量：

---

## 📝 环境变量详细配置

### 1. 数据库配置

#### DATABASE_URL

- **变量名**：`DATABASE_URL`
- **变量值**：粘贴刚才从PostgreSQL服务复制的完整URL
- **示例**：
  ```
  postgresql://postgres:abc123xyz@postgres.zeabur.app:5432/postgres
  ```
- **如何添加**：
  1. 点击 **"Add Variable"**（添加变量）
  2. 在 **"Name"**（名称）输入：`DATABASE_URL`
  3. 在 **"Value"**（值）粘贴数据库URL
  4. 点击 **"Save"**（保存）

---

### 2. Facebook配置

#### FACEBOOK_APP_ID

- **变量名**：`FACEBOOK_APP_ID`
- **变量值**：您的Facebook应用ID
- **如何获取**：
  1. 访问：https://developers.facebook.com
  2. 登录您的账号
  3. 进入您的应用
  4. 在"Settings"（设置）→ "Basic"（基础）中找到"App ID"
  5. 复制这个ID
- **示例**：`1234567890123456`
- **添加步骤**：同上

#### FACEBOOK_APP_SECRET

- **变量名**：`FACEBOOK_APP_SECRET`
- **变量值**：您的Facebook应用密钥
- **如何获取**：
  1. 在Facebook开发者控制台
  2. "Settings"（设置）→ "Basic"（基础）
  3. 找到"App Secret"
  4. 点击"Show"（显示）查看
  5. 复制这个密钥
- **示例**：`abc123def456ghi789jkl012mno345pq`
- **添加步骤**：同上

#### FACEBOOK_ACCESS_TOKEN

- **变量名**：`FACEBOOK_ACCESS_TOKEN`
- **变量值**：您的Facebook访问令牌
- **如何获取**：
  1. 在Facebook开发者控制台
  2. "Tools"（工具）→ "Graph API Explorer"
  3. 选择您的应用
  4. 生成访问令牌
  5. 复制令牌
- **示例**：`EAABwzLixnjYBO7...`（很长的一串字符）
- **添加步骤**：同上

#### FACEBOOK_VERIFY_TOKEN

- **变量名**：`FACEBOOK_VERIFY_TOKEN`
- **变量值**：任意字符串（您自己设置）
- **说明**：这个用于验证Webhook，可以是任何字符串
- **示例**：`my_verify_token_123` 或 `secret_token_2024`
- **重要**：记住这个值，后面配置Webhook要用到相同的值
- **添加步骤**：同上

---

### 3. OpenAI配置

#### OPENAI_API_KEY

- **变量名**：`OPENAI_API_KEY`
- **变量值**：您的OpenAI API密钥
- **如何获取**：
  1. 访问：https://platform.openai.com
  2. 登录您的账号
  3. 点击右上角头像 → "API keys"
  4. 点击 "Create new secret key"（创建新密钥）
  5. 复制密钥（只显示一次，要保存好）
- **示例**：`sk-proj-abc123def456...`（以sk-开头）
- **添加步骤**：同上

#### OPENAI_MODEL（可选）

- **变量名**：`OPENAI_MODEL`
- **变量值**：`gpt-4o-mini`（默认值，可以不填）
- **说明**：使用的AI模型，默认即可
- **添加步骤**：同上（可选）

#### OPENAI_TEMPERATURE（可选）

- **变量名**：`OPENAI_TEMPERATURE`
- **变量值**：`0.7`（默认值，可以不填）
- **说明**：AI回复的创造性，默认即可
- **添加步骤**：同上（可选）

---

### 4. Telegram配置

#### TELEGRAM_BOT_TOKEN

- **变量名**：`TELEGRAM_BOT_TOKEN`
- **变量值**：您的Telegram Bot令牌
- **如何获取**：
  1. 在Telegram中搜索 `@BotFather`
  2. 发送 `/newbot` 命令
  3. 按照提示创建Bot
  4. BotFather会返回Bot Token
  5. 复制这个Token
- **示例**：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- **添加步骤**：同上

#### TELEGRAM_CHAT_ID

- **变量名**：`TELEGRAM_CHAT_ID`
- **变量值**：您的Telegram聊天ID
- **如何获取**：
  1. 在Telegram中，向您的Bot发送一条消息
  2. 访问：`https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
  3. 将`<YOUR_BOT_TOKEN>`替换为您的Bot Token
  4. 在返回的JSON中找到`"chat":{"id":123456789}`
  5. 复制这个ID（数字）
- **示例**：`123456789`（纯数字）
- **添加步骤**：同上

---

### 5. 安全配置

#### SECRET_KEY

- **变量名**：`SECRET_KEY`
- **变量值**：32位以上随机字符串
- **如何生成**：
  - **方法1**：使用在线随机字符串生成器
  - **方法2**：自己输入32位以上的字符和数字组合
  - **方法3**：使用命令（如果有命令行工具）：`openssl rand -hex 32`
- **示例**：`abc123def456ghi789jkl012mno345pqrstuvwxyz678`
- **要求**：至少32个字符
- **添加步骤**：同上

#### DEBUG

- **变量名**：`DEBUG`
- **变量值**：`false`
- **说明**：生产环境必须设置为false
- **添加步骤**：同上

---

### 6. 服务器配置（可选，Zeabur会自动设置）

#### PORT（不需要手动设置）

- **说明**：Zeabur会自动设置端口，不需要手动配置
- **如果必须设置**：使用默认值 `8000`

#### HOST（可选）

- **变量名**：`HOST`
- **变量值**：`0.0.0.0`（默认值）
- **说明**：通常不需要设置，Zeabur会自动处理

---

## ✅ 配置完成检查

### 检查清单

确认以下所有变量都已添加：

- [ ] `DATABASE_URL` - 从PostgreSQL服务复制
- [ ] `FACEBOOK_APP_ID` - 您的Facebook应用ID
- [ ] `FACEBOOK_APP_SECRET` - 您的Facebook应用密钥
- [ ] `FACEBOOK_ACCESS_TOKEN` - 您的Facebook访问令牌
- [ ] `FACEBOOK_VERIFY_TOKEN` - 任意字符串（记住这个值）
- [ ] `OPENAI_API_KEY` - 您的OpenAI密钥
- [ ] `TELEGRAM_BOT_TOKEN` - 您的Telegram Bot令牌
- [ ] `TELEGRAM_CHAT_ID` - 您的Telegram聊天ID
- [ ] `SECRET_KEY` - 32位以上随机字符串
- [ ] `DEBUG` - 设置为 `false`

### 验证方法

1. **在环境变量页面**
   - 确认所有变量都在列表中
   - 确认变量名拼写正确（区分大小写）
   - 确认变量值都已填写

2. **检查格式**
   - 变量名不能有空格
   - 变量值不要有多余的引号
   - 确保复制完整，没有遗漏

## 🎯 下一步

配置完成后：
1. 点击 **"Save"**（保存）或 **"Deploy"**（部署）
2. Zeabur会自动应用这些环境变量
3. 继续第3步：部署应用

## 🆘 常见问题

### Q1: 找不到环境变量设置？

**A**: 
- 确保点击的是**应用服务**，不是数据库服务
- 在服务页面找到"Environment Variables"标签

### Q2: 变量值太长，复制不完整？

**A**: 
- 使用"复制"按钮，不要手动选择
- 确认复制完整后再粘贴

### Q3: 变量名拼写错误？

**A**: 
- 变量名必须完全正确，区分大小写
- 参考上面的列表，逐个检查

### Q4: 不知道如何获取某个API密钥？

**A**: 
- 查看上面的"如何获取"部分
- 或者查看项目的详细文档

---

**提示**：一步一步来，不着急！配置完成后就可以部署了！🎉

