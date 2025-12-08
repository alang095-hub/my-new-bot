# 📱 配置 Messenger 用例和 Webhook

## 🎯 当前页面：定制用例

你看到的是 Facebook 的"定制用例"页面。需要先启用 Messenger 用例，然后才能配置 Webhook。

---

## 📋 第一步：启用 Messenger 用例

### 1.1 勾选 Messenger from Meta

在页面上找到：
- [ ] **Messenger from Meta**

**操作：**
1. **勾选这个复选框**（点击方框打勾 ✅）
2. 页面可能会刷新或显示更多选项

### 1.2 完成 Messenger 设置

勾选后，可能会要求你：
- 选择用例类型
- 确认权限
- 完成基本设置

按照页面提示完成设置。

---

## 📋 第二步：进入 Messenger API 设置

启用 Messenger 用例后：

### 方法 1：通过用例设置

1. **在 "Messenger from Meta" 下方，找到 "Messenger API 设置"**
2. **点击 "Messenger API 设置"**
3. **应该能看到 Webhook 配置选项**

### 方法 2：通过左侧菜单

启用 Messenger 后，左侧菜单应该会出现 "Messenger" 选项：

1. **左侧菜单 → Messenger**
2. **点击 "设置" 或 "Settings"**
3. **向下滚动找到 "Webhooks" 部分**

### 方法 3：直接访问 URL

启用 Messenger 后，尝试直接访问：
```
https://developers.facebook.com/apps/848496661333193/webhooks/
```

---

## ⚙️ 第三步：配置 Webhook

找到 Webhook 设置后：

### 3.1 添加回调 URL

1. **点击 "添加回调 URL" 或 "Add Callback URL"**
2. **输入回调 URL：**
   ```
   https://my-telegram-bot33.zeabur.app/webhook
   ```

### 3.2 输入验证令牌

1. **在验证令牌输入框中输入：**
   ```
   J7kP9qR2sT5vW8yZ1bC3dE6fG9hJ2kM4n
   ```
2. **确保没有多余空格**

### 3.3 验证并保存

1. **点击 "验证并保存"**
2. **等待验证结果**
3. **应该显示 ✅ "已验证"**

---

## 📋 完整操作流程

### 步骤 1：勾选 Messenger from Meta

```
当前页面 → 找到 "Messenger from Meta" → 勾选 ✅
```

### 步骤 2：完成 Messenger 设置

按照页面提示完成 Messenger 的基本设置。

### 步骤 3：进入 Messenger API 设置

```
点击 "Messenger API 设置" 
或
左侧菜单 → Messenger → 设置
```

### 步骤 4：配置 Webhook

```
找到 "Webhooks" 部分
→ 添加回调 URL: https://my-telegram-bot33.zeabur.app/webhook
→ 输入验证令牌: J7kP9qR2sT5vW8yZ1bC3dE6fG9hJ2kM4n
→ 验证并保存
```

---

## 🔍 如果勾选后没有反应

### 检查清单：

1. **确认已勾选 "Messenger from Meta"**
   - 复选框应该显示 ✅

2. **查看页面是否有变化**
   - 是否出现新的选项？
   - 是否显示设置表单？

3. **尝试刷新页面**
   - 按 `F5` 刷新
   - 查看左侧菜单是否出现 "Messenger"

4. **尝试直接访问 Messenger 设置**
   - 访问：`https://developers.facebook.com/apps/848496661333193/messenger/`
   - 或：`https://developers.facebook.com/apps/848496661333193/messenger/settings/`

---

## 🎯 现在开始操作

### 立即操作：

1. **勾选 "Messenger from Meta" 复选框** ✅
2. **告诉我页面发生了什么变化**
3. **查看左侧菜单是否出现 "Messenger" 选项**

---

## 📝 配置信息（保存备用）

当你找到 Webhook 设置后，使用以下信息：

- **回调 URL**: `https://my-telegram-bot33.zeabur.app/webhook`
- **验证令牌**: `J7kP9qR2sT5vW8yZ1bC3dE6fG9hJ2kM4n`

---

## 🆘 需要帮助？

如果勾选后遇到问题，请告诉我：

1. **勾选后页面发生了什么变化？**
2. **左侧菜单是否出现 "Messenger" 选项？**
3. **是否能看到 "Messenger API 设置" 选项？**
4. **任何错误信息或提示？**

我可以根据你的具体情况继续指导。

