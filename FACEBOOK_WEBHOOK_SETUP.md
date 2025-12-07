# 📱 Facebook Webhook 配置详细指南

## 🎯 目标
在 Facebook Developers 中配置 Webhook，使 Facebook 能够向你的应用发送消息事件。

---

## 📍 第一步：进入 Facebook Developers

### 方法 1：直接访问（推荐）

1. **访问 Facebook Developers**
   - 打开浏览器
   - 访问：https://developers.facebook.com/
   - 使用你的 Facebook 账号登录

2. **选择你的应用**
   - 点击顶部导航栏的 **"我的应用"** 或 **"My Apps"**
   - 在应用列表中找到并点击你的应用
   - 如果应用很多，可以使用搜索框搜索应用名称或 App ID

### 方法 2：通过应用 ID 直接访问（最快）

如果你知道应用 ID，可以直接访问应用页面：

**URL 格式：**
```
https://developers.facebook.com/apps/你的应用ID/
```

**示例：**
如果你的应用 ID 是 `848496661333193`，则访问：
```
https://developers.facebook.com/apps/848496661333193/
```

**然后导航到 Webhooks：**
- 点击左侧菜单：**产品** → **Messenger** → **设置** → **Webhooks**
- 或直接访问：`https://developers.facebook.com/apps/你的应用ID/webhooks/`

**如何找到应用 ID：**
1. 在 Facebook Developers 首页，点击 "我的应用"
2. 在应用列表中，应用 ID 显示在应用名称下方（通常是数字）
3. 或者在应用设置页面（设置 → 基本）的顶部可以看到 "App ID"
4. 或者查看应用 URL，URL 中包含应用 ID

---

## 🔍 第二步：找到 Webhooks 设置

### 方式 1：通过左侧菜单（推荐）

1. **进入应用后，查看左侧菜单栏**
   - 你会看到多个选项，如：仪表板、设置、产品等

2. **找到 "产品" 或 "Products" 部分**
   - 在左侧菜单中向下滚动
   - 找到 **"产品"** 或 **"Products"** 部分

3. **点击 "Messenger" 或 "Messaging"**
   - 在 "产品" 部分中，找到 **"Messenger"** 或 **"Messaging"**
   - 点击进入

4. **进入 "设置" 或 "Settings"**
   - 在 Messenger 页面中，点击左侧的 **"设置"** 或 **"Settings"**
   - 或者点击顶部的 **"设置"** 标签

5. **找到 "Webhooks" 部分**
   - 在设置页面中，向下滚动
   - 找到 **"Webhooks"** 部分
   - 你会看到 "添加回调 URL" 或 "Add Callback URL" 按钮

### 方式 2：通过搜索功能

1. **使用页面搜索**
   - 在 Facebook Developers 页面按 `Ctrl+F`（Windows）或 `Cmd+F`（Mac）
   - 搜索 "Webhook" 或 "回调"
   - 点击搜索结果跳转到 Webhook 设置

### 方式 3：直接访问 Webhook 设置页面（最快）

如果你知道应用 ID，可以直接访问：

**URL 格式：**
```
https://developers.facebook.com/apps/你的应用ID/webhooks/
```

**示例：**
如果你的应用 ID 是 `848496661333193`，则访问：
```
https://developers.facebook.com/apps/848496661333193/webhooks/
```

**如何找到应用 ID：**
1. 在 Facebook Developers 首页，点击 "我的应用"
2. 在应用列表中，应用 ID 显示在应用名称下方
3. 或者在应用设置页面（设置 → 基本）的顶部可以看到 App ID
4. 或者直接访问应用，URL 中会包含应用 ID：
   ```
   https://developers.facebook.com/apps/应用ID/
   ```

---

## ⚙️ 第三步：配置 Webhook

### 1. 添加回调 URL

1. **点击 "添加回调 URL" 或 "Add Callback URL"**
   - 在 Webhooks 部分，点击 **"添加回调 URL"** 按钮
   - 会弹出一个对话框或展开一个表单

2. **输入回调 URL**
   - 在 "回调 URL" 或 "Callback URL" 输入框中输入：
     ```
     https://你的域名.zeabur.app/webhook
     ```
   - 例如：`https://my-telegram-bot33.zeabur.app/webhook`
   - ⚠️ **重要：** 必须使用 `https://`，不能使用 `http://`

3. **输入验证令牌**
   - 在 "验证令牌" 或 "Verify Token" 输入框中输入
   - 这个值必须与你在 Zeabur 环境变量中设置的 `FACEBOOK_VERIFY_TOKEN` **完全一致**
   - 例如：如果环境变量是 `FACEBOOK_VERIFY_TOKEN=my_secure_token_2024`
   - 那么这里就输入：`my_secure_token_2024`

4. **点击 "验证并保存" 或 "Verify and Save"**
   - Facebook 会立即向你的 Webhook URL 发送验证请求
   - 如果配置正确，会显示 ✅ "已验证" 或 "Verified"
   - 如果验证失败，检查：
     - URL 是否正确（包含 `https://`）
     - 应用是否正在运行
     - Verify Token 是否匹配

### 2. 订阅事件

验证成功后，需要订阅事件：

1. **找到 "订阅字段" 或 "Subscription Fields"**
   - 在 Webhook 配置下方，找到订阅字段部分
   - 或者点击 Webhook 旁边的 **"编辑"** 或 **"Edit"** 按钮

2. **勾选以下事件：**
   - ✅ **`messages`** - 接收用户发送的消息
   - ✅ **`messaging_postbacks`** - 接收按钮点击事件
   - ✅ **`message_deliveries`** - 接收消息送达通知
   - ✅ **`message_reads`** - 接收消息已读通知

3. **保存订阅**
   - 点击 **"保存更改"** 或 **"Save Changes"**

---

## ✅ 第四步：验证配置

### 1. 检查 Webhook 状态

在 Webhooks 设置页面，你应该看到：
- ✅ 回调 URL 显示为 "已验证" 或 "Verified"
- ✅ 订阅的事件列表显示已勾选
- ✅ Webhook 状态为 "活跃" 或 "Active"

### 2. 测试 Webhook

1. **在 Facebook 页面发送测试消息**
   - 打开你的 Facebook 页面
   - 发送一条测试消息
   - 系统应该自动回复（如果 AI 已配置）

2. **查看应用日志**
   - 在 Zeabur 项目页面查看日志
   - 应该能看到收到消息的日志记录

3. **使用 Facebook 测试工具**
   - 在 Webhook 设置页面，点击 **"测试"** 或 **"Test"** 按钮
   - Facebook 会发送测试事件到你的 Webhook

---

## 🗺️ 完整导航路径

### 路径 1：通过产品菜单
```
Facebook Developers
  → 我的应用
    → 选择你的应用
      → 产品 (Products)
        → Messenger
          → 设置 (Settings)
            → Webhooks
```

### 路径 2：通过设置菜单
```
Facebook Developers
  → 我的应用
    → 选择你的应用
      → 设置 (Settings)
        → 基本 (Basic)
          → 向下滚动找到 Webhooks
```

---

## 📝 配置检查清单

完成以下所有步骤：

- [ ] 已登录 Facebook Developers
- [ ] 已选择正确的应用
- [ ] 已找到 Webhooks 设置页面
- [ ] 已添加回调 URL（格式：`https://你的域名.zeabur.app/webhook`）
- [ ] 已输入验证令牌（与 `FACEBOOK_VERIFY_TOKEN` 一致）
- [ ] Webhook 验证成功（显示 ✅ "已验证"）
- [ ] 已订阅必需事件（`messages`, `messaging_postbacks` 等）
- [ ] 已保存所有更改
- [ ] 已测试 Webhook（发送测试消息）

---

## ⚠️ 常见问题

### 问题 1: 找不到 Webhooks 设置

**可能原因：**
- Messenger 产品未添加到应用
- 应用权限不足

**解决方法：**
1. 在应用页面，点击 **"添加产品"** 或 **"Add Product"**
2. 找到 **"Messenger"** 并点击 **"设置"** 或 **"Set Up"**
3. 添加 Messenger 产品后，Webhooks 选项会出现

### 问题 2: Webhook 验证失败

**可能原因：**
- URL 格式错误（缺少 `https://`）
- 应用未运行
- Verify Token 不匹配

**解决方法：**
1. 确认 URL 格式：`https://你的域名.zeabur.app/webhook`
2. 检查应用是否正在运行（访问 `/health` 端点）
3. 确认 Verify Token 与 Zeabur 环境变量中的值完全一致
4. 查看 Zeabur 日志，检查是否有错误

### 问题 3: 收不到消息事件

**可能原因：**
- 未订阅相应事件
- 页面未关联到应用
- 权限不足

**解决方法：**
1. 确认已订阅 `messages` 事件
2. 在 Messenger 设置中，确认页面已关联
3. 检查应用权限，确保有 `pages_messaging` 权限

---

## 🔗 快速链接

- **Facebook Developers**: https://developers.facebook.com/
- **应用列表**: https://developers.facebook.com/apps/
- **Webhook 文档**: https://developers.facebook.com/docs/graph-api/webhooks

---

## 📚 相关文档

- [下一步行动指南](./NEXT_STEPS.md)
- [Zeabur 部署指南](./ZEABUR_DEPLOYMENT.md)
- [配置清单](./SETUP_CHECKLIST.md)

---

配置完成后，你的应用就可以接收 Facebook 消息了！🎉

