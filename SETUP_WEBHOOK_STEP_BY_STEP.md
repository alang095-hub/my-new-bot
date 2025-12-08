# 🚀 Facebook Webhook 设置 - 详细步骤

## 📋 配置信息

- **回调 URL**: `https://my-telegram-bot33.zeabur.app/webhook`
- **验证令牌**: `J7kP9qR2sT5vW8yZ1bC3dE6fG9hJ2kM4n`

---

## 📍 第一步：启用 Messenger 用例

### 1.1 在当前页面操作

你现在在"定制用例"页面，看到：
- [ ] Messenger from Meta
- [ ] 权限和功能
- [ ] Messenger API 设置
- [ ] API 集成帮手
- [ ] Instagram 设置

**操作：**
1. **找到 "Messenger from Meta" 这一项**
2. **点击前面的复选框，勾选它** ✅
3. **等待页面响应**（可能会刷新或显示新内容）

---

## 📍 第二步：进入 Messenger API 设置

### 方法 1：在当前页面点击

勾选 "Messenger from Meta" 后：

1. **找到 "Messenger API 设置" 这一项**
2. **点击 "Messenger API 设置"**
3. **应该会跳转到 Messenger 设置页面**

### 方法 2：通过左侧菜单

如果左侧菜单出现 "Messenger" 选项：

1. **点击左侧菜单的 "Messenger"**
2. **点击 "设置" 或 "Settings"**
3. **向下滚动找到 "Webhooks" 部分**

### 方法 3：直接访问 URL

如果以上方法都不行，尝试直接访问：

```
https://developers.facebook.com/apps/848496661333193/messenger/settings/
```

或：

```
https://developers.facebook.com/apps/848496661333193/webhooks/
```

---

## ⚙️ 第三步：配置 Webhook

找到 Webhook 设置后（通常在 Messenger API 设置页面中）：

### 3.1 找到 Webhooks 部分

在页面中向下滚动，找到 **"Webhooks"** 或 **"回调 URL"** 部分。

### 3.2 添加回调 URL

1. **找到 "添加回调 URL" 或 "Add Callback URL" 按钮**
2. **点击按钮**
3. **在弹出的对话框中，找到 "回调 URL" 或 "Callback URL" 输入框**
4. **输入以下内容：**
   ```
   https://my-telegram-bot33.zeabur.app/webhook
   ```
   ⚠️ **注意：**
   - 必须以 `https://` 开头
   - 域名后面直接跟 `/webhook`（不要有多余的斜杠）
   - 不要有空格

### 3.3 输入验证令牌

1. **在同一个对话框中，找到 "验证令牌" 或 "Verify Token" 输入框**
2. **完全清空输入框**（如果有默认值，选中所有文本后删除）
3. **输入以下内容：**
   ```
   J7kP9qR2sT5vW8yZ1bC3dE6fG9hJ2kM4n
   ```
   ⚠️ **注意：**
   - 不要有多余的空格
   - 不要有换行符
   - 完整复制上面的值

### 3.4 验证并保存

1. **找到 "验证并保存" 或 "Verify and Save" 按钮**
2. **点击按钮**
3. **等待几秒钟**（Facebook 会向你的 Webhook URL 发送验证请求）

### 3.5 检查验证结果

**成功：**
- ✅ 显示 **"已验证"** 或 **"Verified"**
- ✅ Webhook 状态变为绿色
- ✅ 回调 URL 旁边显示 ✅ 图标

**失败：**
- ❌ 显示错误信息
- 如果失败，参考下面的"故障排查"

---

## 📨 第四步：订阅事件

验证成功后，需要订阅事件：

### 4.1 找到订阅字段

1. **在 Webhook 配置下方，找到 "订阅字段" 或 "Subscription Fields"**
2. **或者点击 Webhook 旁边的 "编辑" 或 "Edit" 按钮**

### 4.2 勾选必需事件

在订阅字段列表中，勾选以下事件：

1. ✅ **`messages`** - 接收用户发送的消息（**必须勾选**）
2. ✅ **`messaging_postbacks`** - 接收按钮点击事件（建议勾选）
3. ✅ **`message_deliveries`** - 接收消息送达通知（可选）
4. ✅ **`message_reads`** - 接收消息已读通知（可选）

### 4.3 保存订阅

1. **点击 "保存更改" 或 "Save Changes" 按钮**
2. **确认保存成功**

---

## ✅ 第五步：验证配置

### 5.1 检查 Webhook 状态

在 Webhooks 设置页面，确认：

- ✅ 回调 URL 显示为 **"已验证"** 或 **"Verified"**
- ✅ 订阅的事件列表显示已勾选
- ✅ Webhook 状态为 **"活跃"** 或 **"Active"**

### 5.2 测试 Webhook（可选）

1. **在你的 Facebook 页面发送测试消息**
   - 打开你的 Facebook 页面
   - 发送一条测试消息，例如：`你好`

2. **查看 Zeabur 日志**
   - 在 Zeabur 项目页面 → Logs
   - 应该看到类似日志：
     ```
     收到 Facebook 消息事件
     处理消息: 你好
     ```

3. **检查 AI 回复**
   - 在 Facebook Messenger 中查看
   - 应该收到 AI 自动生成的回复

---

## 🔧 故障排查

### 问题 1：找不到 Webhook 设置

**解决方法：**

1. **确认已勾选 "Messenger from Meta"**
2. **尝试直接访问 URL：**
   ```
   https://developers.facebook.com/apps/848496661333193/webhooks/
   ```
3. **或访问 Messenger 设置：**
   ```
   https://developers.facebook.com/apps/848496661333193/messenger/settings/
   ```

### 问题 2：验证失败

**可能原因：**
- 验证令牌不匹配
- URL 格式错误
- 应用未运行

**解决步骤：**

1. **检查验证令牌**
   - 确认输入的是：`J7kP9qR2sT5vW8yZ1bC3dE6fG9hJ2kM4n`
   - 确认没有多余空格

2. **检查 URL 格式**
   - 确认是：`https://my-telegram-bot33.zeabur.app/webhook`
   - 确认没有多余的空格或斜杠

3. **测试应用可访问性**
   - 访问：`https://my-telegram-bot33.zeabur.app/health`
   - 应该返回：`{"status":"healthy"}`

---

## 📋 完整操作清单

按照以下顺序操作：

- [ ] 1. 勾选 "Messenger from Meta" ✅
- [ ] 2. 进入 Messenger API 设置
- [ ] 3. 找到 Webhooks 部分
- [ ] 4. 添加回调 URL：`https://my-telegram-bot33.zeabur.app/webhook`
- [ ] 5. 输入验证令牌：`J7kP9qR2sT5vW8yZ1bC3dE6fG9hJ2kM4n`
- [ ] 6. 点击 "验证并保存"
- [ ] 7. 确认显示 "已验证" ✅
- [ ] 8. 订阅 `messages` 事件
- [ ] 9. 保存所有更改
- [ ] 10. 测试发送消息

---

## 🎯 快速参考

### 配置信息（复制使用）

**回调 URL：**
```
https://my-telegram-bot33.zeabur.app/webhook
```

**验证令牌：**
```
J7kP9qR2sT5vW8yZ1bC3dE6fG9hJ2kM4n
```

### 直接访问链接

**Webhook 设置页面：**
```
https://developers.facebook.com/apps/848496661333193/webhooks/
```

**Messenger 设置页面：**
```
https://developers.facebook.com/apps/848496661333193/messenger/settings/
```

---

## 🆘 需要帮助？

如果在任何步骤遇到问题，请告诉我：

1. **你当前在哪个页面？**
2. **看到了什么内容？**
3. **遇到了什么错误？**

我可以根据你的具体情况继续指导。

