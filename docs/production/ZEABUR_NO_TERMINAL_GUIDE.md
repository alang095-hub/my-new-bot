# Zeabur 无终端部署后操作指南

## 问题

Zeabur可能不提供终端功能，无法直接运行命令行工具。

## 解决方案

我们创建了**API端点**，可以通过HTTP请求执行所有部署后操作，无需终端！

## 📡 使用API端点

### 前提条件

1. 应用已部署并运行
2. 获取应用URL（格式：`https://your-app-name.zeabur.app`）

### 方法1：使用浏览器（最简单）

直接在浏览器中访问以下URL：

#### 1. 同步所有页面Token

```
https://your-app-name.zeabur.app/admin/deployment/sync-pages
```

**操作：**
- 在浏览器中打开上述URL
- 会看到JSON响应，表示同步任务已启动
- 等待几秒钟后，使用下面的状态检查URL查看结果

#### 2. 查看部署状态

```
https://your-app-name.zeabur.app/admin/deployment/status
```

**显示：**
- 数据库连接状态
- 已配置的页面列表
- Token配置状态
- 同步任务状态

#### 3. 验证Token

```
https://your-app-name.zeabur.app/admin/deployment/verify-token
```

**显示：**
- Token类型（USER或PAGE）
- 是否可以管理多个页面
- 页面数量

### 方法2：使用curl命令（如果有命令行）

```bash
# 同步所有页面Token
curl -X POST https://your-app-name.zeabur.app/admin/deployment/sync-pages

# 查看部署状态
curl https://your-app-name.zeabur.app/admin/deployment/status

# 验证Token
curl https://your-app-name.zeabur.app/admin/deployment/verify-token
```

### 方法3：使用Postman或类似工具

1. 打开Postman
2. 创建新请求
3. 选择方法（GET或POST）
4. 输入URL
5. 发送请求

## 📋 完整操作流程

### 步骤1：更新长期Token到Zeabur

1. 在Zeabur项目设置中
2. 更新 `FACEBOOK_ACCESS_TOKEN` 环境变量
3. 保存并等待服务重启

### 步骤2：验证Token（可选）

访问：
```
https://your-app-name.zeabur.app/admin/deployment/verify-token
```

应该看到：
```json
{
  "success": true,
  "token_type": "USER",
  "can_manage_pages": true,
  "pages_count": 12,
  "is_user_token": true
}
```

### 步骤3：同步所有页面Token

访问：
```
https://your-app-name.zeabur.app/admin/deployment/sync-pages
```

**响应：**
```json
{
  "success": true,
  "message": "页面同步任务已启动，正在后台执行",
  "note": "请稍后查看日志或使用 /admin/deployment/status 检查状态"
}
```

### 步骤4：检查同步状态

等待10-20秒后，访问：
```
https://your-app-name.zeabur.app/admin/deployment/status
```

**应该看到：**
```json
{
  "success": true,
  "status": {
    "pages": {
      "total": 12,
      "enabled": 12,
      "pages": [...]
    },
    "sync": {
      "running": false,
      "last_result": {
        "success": true,
        "pages_synced": 12,
        "pages_enabled": 12
      }
    }
  }
}
```

### 步骤5：更新Facebook Webhook URL

1. 登录 Facebook Developer Console
2. 更新 Webhook URL 为：`https://your-app-name.zeabur.app/webhook`
3. 确认 Verify Token 一致

### 步骤6：验证部署

访问健康检查：
```
https://your-app-name.zeabur.app/health
```

## 🔍 API端点说明

### POST /admin/deployment/sync-pages

**功能：** 同步所有页面Token

**方法：** POST

**响应：**
```json
{
  "success": true,
  "message": "页面同步任务已启动，正在后台执行"
}
```

**注意：** 这是后台任务，需要等待几秒钟完成

### GET /admin/deployment/status

**功能：** 获取部署状态

**方法：** GET

**响应：**
```json
{
  "success": true,
  "status": {
    "database": {...},
    "pages": {...},
    "token": {...},
    "sync": {...}
  }
}
```

### GET /admin/deployment/verify-token

**功能：** 验证Token类型和权限

**方法：** GET

**响应：**
```json
{
  "success": true,
  "token_type": "USER",
  "can_manage_pages": true,
  "pages_count": 12
}
```

## ⚠️ 重要提示

1. **数据库迁移**：已在 `zeabur.json` 的 `postDeploy` 中自动执行，无需手动操作

2. **同步任务**：是后台任务，需要等待10-20秒完成

3. **检查状态**：使用 `/admin/deployment/status` 查看同步结果

4. **如果同步失败**：
   - 检查Token是否有 `pages_show_list` 权限
   - 使用 `/admin/deployment/verify-token` 验证Token
   - 查看应用日志确认错误信息

## 🎯 快速操作清单

- [ ] 更新长期Token到Zeabur
- [ ] 访问 `/admin/deployment/verify-token` 验证Token
- [ ] 访问 `/admin/deployment/sync-pages` 同步页面
- [ ] 等待10-20秒
- [ ] 访问 `/admin/deployment/status` 检查结果
- [ ] 更新Facebook Webhook URL
- [ ] 访问 `/health` 验证部署

## 📚 相关文档

- [部署后操作步骤](POST_DEPLOYMENT_STEPS.md)
- [多页面配置](ZEABUR_MULTI_PAGE_SETUP.md)
- [环境变量说明](ZEABUR_ENV_VARS.md)




