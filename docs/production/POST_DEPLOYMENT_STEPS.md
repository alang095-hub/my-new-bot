# 部署成功后接下来的步骤

## 📋 部署后操作清单

### ✅ 步骤1：更新长期Token（如果还没更新）

#### 1.1 在Zeabur中更新环境变量

1. 访问您的Zeabur项目页面
2. 点击您的服务
3. 找到 **"Environment Variables"** 或 **"环境变量"**
4. 找到 `FACEBOOK_ACCESS_TOKEN`
5. 更新为长期Token：
   ```
   EAAMDtAYXhMkBQMNGpLwZCxhYjTWYEmz8rMWcIidGfqsSw2rsJt6rZA6qDhKtmpxqRkIwZCAJ1VViE0nYLooDW1KEXhI1YtlVeonUmYkNlHLnxnlSZC7QFByO3tiykskL1kx5R11nZCzAG3yarADaerXMaZCeyYJTXUpsgOMhggypZBFIZAeaVRg51vidZBtiy
   ```
6. 保存并等待服务重启（约1-2分钟）

#### 1.2 验证Token（可选）

在Zeabur终端中运行：
```bash
python scripts/tools/verify_token.py
```

应该看到：
- ✅ Token类型: USER
- ✅ 可以管理 12 个页面

---

### ✅ 步骤2：运行数据库迁移

在Zeabur终端中运行：
```bash
alembic upgrade head
```

**预期输出：**
```
INFO  [alembic.runtime.migration] Running upgrade ... -> ..., ...
```

---

### ✅ 步骤3：同步所有页面Token（重要！）

在Zeabur终端中运行：
```bash
python scripts/tools/manage_pages.py sync
```

**这会：**
- 使用用户级Token自动获取所有12个页面的Token
- 保存到 `.page_tokens.json` 文件
- 自动为所有页面启用自动回复

**预期输出：**
```
✅ 成功同步 12 个页面的Token
✅ 已自动启用 12 个页面的自动回复
```

---

### ✅ 步骤4：验证页面配置

在Zeabur终端中运行：
```bash
python scripts/tools/manage_pages.py status
```

**应该看到：**
- 所有12个页面都已配置
- 所有页面Token都已设置
- 所有页面自动回复都已启用

---

### ✅ 步骤5：更新Facebook Webhook URL

#### 5.1 获取应用URL

在Zeabur项目页面，找到您的应用URL，格式：
```
https://your-app-name.zeabur.app
```

#### 5.2 更新Webhook配置

1. 登录 **Facebook Developer Console**：https://developers.facebook.com
2. 进入您的应用设置
3. 找到 **Webhook** 配置
4. 更新 **Webhook URL** 为：
   ```
   https://your-app-name.zeabur.app/webhook
   ```
5. 确认 **Verify Token** 与 `FACEBOOK_VERIFY_TOKEN` 环境变量一致
6. 点击 **"Verify and Save"**

#### 5.3 订阅事件

确保订阅了以下事件：
- ✅ `messages` - 接收消息
- ✅ `messaging_postbacks` - 接收回传
- ✅ `messaging_optins` - 接收选择加入

---

### ✅ 步骤6：验证部署

#### 6.1 健康检查

访问健康检查端点：
```
https://your-app-name.zeabur.app/health
```

**预期响应：**
```json
{
  "status": "healthy",
  "timestamp": "...",
  "checks": {
    "database": {"status": "healthy"},
    "api_config": {"status": "healthy"},
    "resources": {"status": "healthy"}
  }
}
```

#### 6.2 API文档

访问API文档：
```
https://your-app-name.zeabur.app/docs
```

#### 6.3 测试自动回复

1. 向任意一个已配置的Facebook页面发送消息
2. 等待自动回复（通常几秒内）
3. 检查日志确认消息已处理

---

### ✅ 步骤7：配置CORS（如果有前端）

如果您的应用有前端界面，需要配置CORS：

1. 在Zeabur环境变量中，更新 `CORS_ORIGINS`：
   ```
   CORS_ORIGINS=https://your-app-name.zeabur.app,https://your-frontend-domain.com
   ```
2. 保存并等待服务重启

---

## 📊 验证清单

完成所有步骤后，请确认：

- [ ] 长期Token已更新到Zeabur
- [ ] 数据库迁移已运行
- [ ] 所有12个页面Token已同步
- [ ] 所有页面自动回复已启用
- [ ] Facebook Webhook URL已更新
- [ ] Webhook验证成功
- [ ] 健康检查通过
- [ ] 测试消息自动回复正常

---

## 🔍 监控和维护

### 日常监控

1. **查看服务日志**
   - 在Zeabur项目页面查看实时日志
   - 检查是否有错误或警告

2. **监控性能**
   - 访问：`https://your-app-name.zeabur.app/metrics`
   - 检查响应时间和资源使用

3. **检查自动回复状态**
   ```bash
   python scripts/tools/manage_pages.py status
   ```

### 定期维护

#### 每月任务

1. **同步页面Token**（Token会过期）
   ```bash
   python scripts/tools/manage_pages.py sync
   ```

2. **检查Token有效期**
   ```bash
   python scripts/tools/verify_token.py
   ```

3. **备份数据**
   - 定期备份PostgreSQL数据库

#### Token过期处理

如果Token过期（通常60天）：

1. **获取新Token**
   - 访问：https://developers.facebook.com/tools/explorer/
   - 获取新的用户级Token

2. **转换为长期Token**
   ```bash
   python scripts/tools/exchange_long_token.py [新Token]
   ```

3. **更新Zeabur环境变量**
   - 更新 `FACEBOOK_ACCESS_TOKEN`

4. **重新同步页面**
   ```bash
   python scripts/tools/manage_pages.py sync
   ```

---

## 🆘 常见问题

### 问题1：Webhook验证失败

**症状：** Facebook Webhook验证失败

**解决：**
1. 确认 `FACEBOOK_VERIFY_TOKEN` 与Facebook配置一致
2. 确认Webhook URL正确
3. 检查应用日志

### 问题2：无法同步页面Token

**症状：** `manage_pages.py sync` 返回0个页面

**解决：**
1. 验证Token是否有 `pages_show_list` 权限
2. 运行 `python scripts/tools/verify_token.py` 检查Token
3. 确认Token未过期

### 问题3：自动回复不工作

**症状：** 消息未收到自动回复

**解决：**
1. 检查页面自动回复是否启用：`python scripts/tools/manage_pages.py status`
2. 检查服务日志是否有错误
3. 确认Webhook已正确配置
4. 检查消息是否超过24小时窗口限制

### 问题4：服务无法启动

**症状：** 服务启动失败

**解决：**
1. 检查所有必需的环境变量是否已配置
2. 查看构建日志确认依赖安装成功
3. 检查数据库连接是否正常
4. 运行健康检查确认服务状态

---

## 📚 相关文档

- [部署指南](DEPLOYMENT_GUIDE.md)
- [多页面配置](ZEABUR_MULTI_PAGE_SETUP.md)
- [获取用户Token](GET_USER_TOKEN.md)
- [环境变量说明](ZEABUR_ENV_VARS.md)
- [故障排查](../troubleshooting/)

---

## 🎉 部署完成！

完成所有步骤后，您的系统将：
- ✅ 自动接收Facebook/Instagram消息
- ✅ 使用AI自动回复
- ✅ 支持12个页面同时运行
- ✅ 发送Telegram通知
- ✅ 记录统计信息

祝使用愉快！🚀




