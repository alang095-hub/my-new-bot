# 🔧 修复数据库连接问题

## 🚨 问题说明

如果应用服务无法连接到数据库，可能的原因：
1. `DATABASE_URL` 环境变量未设置
2. `DATABASE_URL` 格式错误
3. PostgreSQL服务未正确连接到应用服务
4. 网络连接问题
5. 数据库服务未完全启动

## 🔍 立即排查步骤

### 步骤1：检查DATABASE_URL环境变量

**在Zeabur应用服务设置中：**

1. 访问：**https://zeabur.com**
2. 找到项目：**my-telegram-bot33**
3. 点击您的**应用服务**（不是PostgreSQL服务）
4. 找到 **"Settings"** → **"Environment Variables"**
5. 查找 `DATABASE_URL` 变量

**应该看到：**
- 变量名：`DATABASE_URL`
- 变量值：类似 `postgresql://postgres:xxx@xxx.zeabur.com:5432/postgres`
- 值应该以 `postgresql://` 开头

**如果DATABASE_URL不存在：**

#### 解决方法A：检查服务连接

1. 在PostgreSQL服务页面
2. 确认已连接到应用服务
3. 或在应用服务页面，确认已连接到PostgreSQL服务
4. 等待1-2分钟，让Zeabur自动设置

#### 解决方法B：手动设置（不推荐）

如果Zeabur没有自动设置，您可以：

1. 在PostgreSQL服务页面，找到连接信息
2. 手动创建 `DATABASE_URL` 环境变量
3. 格式：`postgresql://用户名:密码@主机:端口/数据库名`

**注意：** 通常不需要手动设置，Zeabur会自动处理。

### 步骤2：检查PostgreSQL服务状态

1. 在Zeabur项目页面，查看PostgreSQL服务状态
2. 确认状态是 **"Running"**
3. 如果状态不是 "Running"，等待服务启动

### 步骤3：检查服务连接

**确认PostgreSQL服务和应用服务已连接：**

1. 在PostgreSQL服务页面
2. 查看 **"Connected Services"** 或 **"连接的服务"**
3. 确认应用服务已列出

**或：**

1. 在应用服务页面
2. 查看 **"Connected Services"** 或 **"连接的服务"**
3. 确认PostgreSQL服务已列出

### 步骤4：查看应用服务日志

在应用服务页面，找到 **"Logs"** 标签，查找错误信息：

#### 常见错误1：环境变量缺失

**日志显示：**
```
Field required [type=missing, input_value=..., input_type=dict]
database_url
```

**解决：**
1. 确认 `DATABASE_URL` 环境变量已设置
2. 如果使用Zeabur的PostgreSQL服务，等待自动设置
3. 如果仍未设置，检查服务连接

#### 常见错误2：数据库连接失败

**日志显示：**
```
Database connection failed
OperationalError: could not connect to server
could not connect to server: Connection refused
```

**解决：**
1. 确认PostgreSQL服务状态是 "Running"
2. 确认 `DATABASE_URL` 格式正确
3. 确认服务已正确连接
4. 等待服务完全启动（可能需要1-2分钟）

#### 常见错误3：认证失败

**日志显示：**
```
password authentication failed
FATAL: password authentication failed for user
```

**解决：**
1. 确认 `DATABASE_URL` 中的密码正确
2. 如果使用Zeabur的PostgreSQL服务，让Zeabur自动设置
3. 不要手动修改密码

#### 常见错误4：数据库不存在

**日志显示：**
```
database "xxx" does not exist
FATAL: database "xxx" does not exist
```

**解决：**
1. 确认 `DATABASE_URL` 中的数据库名正确
2. 如果使用Zeabur的PostgreSQL服务，使用默认数据库名 `postgres`

### 步骤5：测试数据库连接

如果应用服务已启动，访问健康检查端点：

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
      "message": "Database connection OK"
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

## 🛠️ 详细解决方案

### 方案1：重新连接服务

如果服务未正确连接：

1. 在PostgreSQL服务页面
2. 找到 **"Connect"** 或 **"连接"** 选项
3. 选择应用服务
4. 确认连接

**或：**

1. 在应用服务页面
2. 找到 **"Connect"** 或 **"连接"** 选项
3. 选择PostgreSQL服务
4. 确认连接

### 方案2：重启服务

如果连接仍然失败：

1. 在PostgreSQL服务页面，点击 **"Restart"**
2. 等待服务重启（约1-2分钟）
3. 在应用服务页面，点击 **"Restart"**
4. 等待服务重启（约1-2分钟）
5. 检查连接状态

### 方案3：检查网络配置

如果使用外部数据库：

1. 确认数据库服务器允许来自Zeabur的连接
2. 检查防火墙设置
3. 确认端口5432已开放

## 📋 检查清单

- [ ] PostgreSQL服务状态是 "Running"
- [ ] 应用服务状态是 "Running" 或 "Building"
- [ ] PostgreSQL服务和应用服务已连接
- [ ] `DATABASE_URL` 环境变量已设置
- [ ] `DATABASE_URL` 格式正确（以 `postgresql://` 开头）
- [ ] 应用服务日志中没有数据库连接错误
- [ ] 健康检查显示数据库连接正常

## 🆘 需要的信息

如果问题仍然存在，请提供：

1. **DATABASE_URL是否已设置**（是/否）
2. **PostgreSQL服务状态**（Running/Failed）
3. **应用服务状态**（Running/Building/Failed）
4. **应用服务日志中的错误信息**（完整错误堆栈）
5. **健康检查响应**（如果服务已启动）
6. **服务连接情况**（是否已连接）

## 📚 相关文档

- [DATABASE_URL格式说明](DATABASE_URL_FORMAT.md)
- [数据库连接指南](ZEABUR_DATABASE_CONNECTION.md)
- [数据库就绪检查](DATABASE_READY_CHECK.md)
- [502错误排查步骤](502_TROUBLESHOOTING_STEPS.md)




