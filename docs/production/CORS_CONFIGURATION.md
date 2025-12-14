# CORS配置指南

## 概述

CORS（跨域资源共享）配置用于控制哪些域名可以访问您的API。在生产环境中，应该限制允许的来源，而不是允许所有来源（`*`）。

## 配置方法

### 1. 通过环境变量配置

在 `.env` 文件中添加 `CORS_ORIGINS` 环境变量：

```bash
# 单个域名
CORS_ORIGINS=https://yourdomain.com

# 多个域名（逗号分隔）
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com,https://app.yourdomain.com

# 包含端口
CORS_ORIGINS=https://yourdomain.com:3000,https://yourdomain.com:8080
```

### 2. 配置示例

#### 开发环境
```bash
# 开发环境可以允许所有来源（不推荐用于生产）
CORS_ORIGINS=*
# 或者
DEBUG=true  # 开发模式下会自动允许所有来源
```

#### 生产环境
```bash
# 只允许特定域名
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 如果有管理后台
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

### 3. 验证配置

配置后，重启服务并检查日志：

```bash
# 查看启动日志
tail -f logs/app.log | grep CORS
```

应该看到类似以下信息：
```
INFO - CORS已配置，允许的来源: ['https://yourdomain.com']
```

### 4. 测试CORS配置

使用浏览器开发者工具或curl测试：

```bash
# 测试CORS预检请求
curl -X OPTIONS http://localhost:8000/health \
  -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

应该看到 `Access-Control-Allow-Origin` 头包含您的域名。

## 安全建议

1. **不要使用通配符 `*`**：在生产环境中，永远不要使用 `CORS_ORIGINS=*`
2. **只允许必要的域名**：只添加实际需要访问API的域名
3. **使用HTTPS**：生产环境应该只允许HTTPS来源
4. **定期审查**：定期检查CORS配置，移除不再需要的域名

## 常见问题

### Q: 如果我不配置CORS_ORIGINS会怎样？

A: 如果未配置且 `DEBUG=false`，系统将拒绝所有跨域请求。这对于纯Webhook服务（无前端界面）是可以接受的。

### Q: 如何允许本地开发？

A: 可以在开发环境配置：
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Q: 如何临时允许所有来源？

A: 不推荐，但如果必须：
```bash
CORS_ORIGINS=*
```
**注意：这仅用于紧急情况，应该尽快修复为具体域名。**

## 相关文件

- `src/main.py` - CORS中间件配置
- `src/core/config/settings.py` - CORS配置加载

