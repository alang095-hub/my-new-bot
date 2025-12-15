# 🔗 Zeabur 数据库连接指南

## 📍 应用URL

您的应用URL是：
```
https://my-telegram-bot33.zeabur.app
```

## 🎯 两种连接方式

### 方式1：使用Zeabur的PostgreSQL服务（推荐）⭐

这是最简单的方式，Zeabur会自动配置所有连接信息。

#### 步骤1：添加PostgreSQL服务

1. 访问Zeabur控制台：**https://zeabur.com**
2. 登录您的账号
3. 找到项目：**my-telegram-bot33**
4. 在项目页面，点击 **"Add Service"** 或 **"添加服务"**
5. 选择 **"PostgreSQL"**
6. 等待数据库服务启动（约1-2分钟）

#### 步骤2：确认自动配置

✅ **Zeabur会自动完成以下操作：**
- 创建PostgreSQL数据库实例
- 自动设置 `DATABASE_URL` 环境变量
- 将数据库服务连接到您的应用服务
- 配置网络连接

**您无需手动配置任何内容！**

#### 步骤3：验证连接

1. 等待服务重启（配置环境变量后会自动重启）
2. 访问健康检查端点：
   ```
   https://my-telegram-bot33.zeabur.app/health
   ```
3. 查看数据库状态：
   ```json
   {
     "checks": {
       "database": {
         "status": "healthy",
         "message": "Database connection OK"
       }
     }
   }
   ```

---

### 方式2：使用外部数据库（高级）

如果您有自己的PostgreSQL数据库，可以手动配置连接。

#### 步骤1：准备数据库连接信息

您需要以下信息：
- 数据库主机地址（host）
- 端口（通常是5432）
- 数据库名称（database）
- 用户名（username）
- 密码（password）

#### 步骤2：配置DATABASE_URL环境变量

在Zeabur服务设置中，添加环境变量：

**变量名：** `DATABASE_URL`

**变量值格式：**
```
postgresql://用户名:密码@主机:端口/数据库名
```

**示例：**
```
postgresql://myuser:mypassword@db.example.com:5432/mydatabase
```

#### 步骤3：保存并重启

1. 保存环境变量
2. 等待服务自动重启
3. 验证连接（同方式1的步骤3）

---

## 🔍 检查数据库连接状态

### 方法1：通过健康检查API（最简单）

访问：
```
https://my-telegram-bot33.zeabur.app/health
```

**正常响应：**
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection OK",
      "response_time_ms": 5.23
    }
  }
}
```

**异常响应：**
```json
{
  "status": "unhealthy",
  "checks": {
    "database": {
      "status": "unhealthy",
      "message": "Database connection failed: ...",
      "error": "..."
    }
  }
}
```

### 方法2：通过部署状态API

访问：
```
https://my-telegram-bot33.zeabur.app/admin/deployment/status
```

**正常响应：**
```json
{
  "success": true,
  "status": {
    "database": {
      "connected": true,
      "status": "healthy"
    }
  }
}
```

### 方法3：查看Zeabur日志

1. 在Zeabur控制台，进入服务页面
2. 找到 **"Logs"** 标签
3. 查找以下信息：
   - ✅ `Database connection OK` - 连接正常
   - ❌ `Database connection failed` - 连接失败
   - ❌ `OperationalError` - 数据库操作错误

---

## 🛠️ 常见问题排查

### 问题1：PostgreSQL服务未启动

**症状：**
- 健康检查显示数据库连接失败
- 日志显示 "could not connect to server"

**解决：**
1. 在Zeabur项目页面检查PostgreSQL服务状态
2. 确认服务状态是 **"Running"**
3. 如果未启动，等待启动完成（约1-2分钟）

### 问题2：DATABASE_URL未设置

**症状：**
- 应用启动失败
- 日志显示 "Field required [type=missing, input_value=..., input_type=dict]"
- 错误信息包含 "database_url"

**解决：**
1. 确认已添加PostgreSQL服务到项目
2. 检查环境变量中是否有 `DATABASE_URL`
3. 如果没有，确认PostgreSQL服务已正确连接

### 问题3：数据库迁移未运行

**症状：**
- 数据库连接正常，但查询失败
- 错误信息显示 "relation does not exist" 或 "table does not exist"

**解决：**
1. 数据库迁移应该在 `postDeploy` 中自动运行
2. 如果未运行，可以通过API触发：
   ```
   POST https://my-telegram-bot33.zeabur.app/admin/deployment/sync-pages
   ```
3. 或等待服务重启后自动运行

### 问题4：连接数过多

**症状：**
- 错误信息显示 "too many connections"
- 数据库响应变慢

**解决：**
1. 检查连接池配置（已在代码中优化）
2. 等待连接释放
3. 重启服务

---

## 📋 快速检查清单

- [ ] 已添加PostgreSQL服务到Zeabur项目
- [ ] PostgreSQL服务状态是 "Running"
- [ ] `DATABASE_URL` 环境变量已自动设置（或手动配置）
- [ ] 访问 `/health` 端点，确认数据库状态为 "healthy"
- [ ] 数据库迁移已运行（查看日志确认）

---

## 🎯 推荐操作流程

### 第一次部署

1. ✅ 添加PostgreSQL服务（Zeabur自动配置）
2. ✅ 配置其他环境变量
3. ✅ 等待服务重启
4. ✅ 访问 `/health` 验证数据库连接
5. ✅ 如果连接失败，查看日志排查问题

### 日常检查

1. ✅ 定期访问 `/health` 检查数据库状态
2. ✅ 查看响应时间（应该 < 100ms）
3. ✅ 如果发现问题，查看日志并排查

---

## 📚 相关文档

- [检查数据库状态](CHECK_ZEABUR_DATABASE.md)
- [环境变量配置](ZEABUR_ENV_VARS.md)
- [部署后操作步骤](POST_DEPLOYMENT_STEPS.md)
- [故障排查指南](FIX_502_ERROR.md)

---

## 🆘 需要帮助？

如果数据库连接仍然失败，请提供：

1. **PostgreSQL服务状态**（Running/Failed）
2. **健康检查响应**（访问 `/health` 的结果）
3. **日志中的错误信息**（如果有）
4. **DATABASE_URL配置情况**（是否已设置）




