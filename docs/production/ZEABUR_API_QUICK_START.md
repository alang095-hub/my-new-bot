# 🚀 Zeabur 无终端快速操作指南

## 问题

Zeabur可能不提供终端功能，无法直接运行命令行工具。

## ✅ 解决方案

我们创建了**API端点**，可以通过浏览器直接访问，无需终端！

## 📡 快速操作（3步完成）

### 前提条件

1. 应用已部署并运行
2. 获取应用URL（格式：`https://your-app-name.zeabur.app`）
3. 已更新长期Token到Zeabur环境变量

### 步骤1：验证Token（可选）

在浏览器中打开：
```
https://your-app-name.zeabur.app/admin/deployment/verify-token
```

**应该看到：**
```json
{
  "success": true,
  "token_type": "USER",
  "can_manage_pages": true,
  "pages_count": 12
}
```

### 步骤2：同步所有页面Token

在浏览器中打开：
```
https://your-app-name.zeabur.app/admin/deployment/sync-pages
```

**会看到：**
```json
{
  "success": true,
  "message": "页面同步任务已启动，正在后台执行"
}
```

**等待10-20秒**让同步任务完成。

### 步骤3：检查同步结果

在浏览器中打开：
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

## ✅ 完成！

所有12个页面已同步并启用自动回复！

## 📋 完整操作清单

- [ ] 更新长期Token到Zeabur环境变量
- [ ] 访问 `/admin/deployment/verify-token` 验证Token
- [ ] 访问 `/admin/deployment/sync-pages` 同步页面
- [ ] 等待10-20秒
- [ ] 访问 `/admin/deployment/status` 检查结果
- [ ] 更新Facebook Webhook URL
- [ ] 访问 `/health` 验证部署

## 🔗 API端点列表

| 端点 | 方法 | 功能 |
|------|------|------|
| `/admin/deployment/verify-token` | GET | 验证Token类型和权限 |
| `/admin/deployment/sync-pages` | POST | 同步所有页面Token |
| `/admin/deployment/status` | GET | 查看部署状态 |
| `/health` | GET | 健康检查 |

## 📚 详细文档

- [无终端操作指南](ZEABUR_NO_TERMINAL_GUIDE.md)
- [部署后操作步骤](POST_DEPLOYMENT_STEPS.md)

