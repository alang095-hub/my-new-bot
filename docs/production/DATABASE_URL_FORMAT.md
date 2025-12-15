# 📝 DATABASE_URL 格式说明

## 🎯 如果您使用Zeabur的PostgreSQL服务

**✅ 好消息：DATABASE_URL会自动设置，您无需手动配置！**

当您在Zeabur项目中添加PostgreSQL服务后：
1. Zeabur会自动创建数据库实例
2. 自动生成连接信息
3. 自动设置 `DATABASE_URL` 环境变量
4. 自动连接到您的应用服务

**您只需要：**
- 添加PostgreSQL服务
- 等待服务启动
- 确认 `DATABASE_URL` 已自动设置

---

## 📋 DATABASE_URL 格式

### 基本格式

```
postgresql://用户名:密码@主机:端口/数据库名
```

### 完整示例

```
postgresql://postgres:my_password_123@db-abc123.zeabur.com:5432/postgres
```

### 组成部分说明

| 部分 | 说明 | 示例 |
|------|------|------|
| `postgresql://` | 协议前缀 | 固定值 |
| `postgres` | 用户名 | 通常是 `postgres` |
| `my_password_123` | 密码 | Zeabur自动生成 |
| `db-abc123.zeabur.com` | 主机地址 | Zeabur自动分配 |
| `5432` | 端口 | PostgreSQL默认端口 |
| `postgres` | 数据库名 | 通常是 `postgres` |

---

## 🔍 如何检查DATABASE_URL

### 方法1：在Zeabur控制台查看

1. 访问：**https://zeabur.com**
2. 找到项目：**my-telegram-bot33**
3. 点击您的**应用服务**（不是PostgreSQL服务）
4. 找到 **"Settings"** 或 **"设置"** 标签
5. 找到 **"Environment Variables"** 或 **"环境变量"** 部分
6. 查找 `DATABASE_URL` 变量

**应该看到：**
- 变量名：`DATABASE_URL`
- 变量值：类似 `postgresql://postgres:xxx@xxx.zeabur.com:5432/postgres`

### 方法2：通过健康检查API

如果应用服务已启动，访问：
```
https://my-telegram-bot33.zeabur.app/health
```

查看数据库连接状态（不会显示完整的URL，只显示连接状态）。

---

## ⚠️ 如果DATABASE_URL未自动设置

### 可能原因

1. PostgreSQL服务未正确连接到应用服务
2. 服务还在启动中（等待1-2分钟）
3. 需要手动连接服务

### 解决方法

#### 方法1：检查服务连接

1. 在PostgreSQL服务页面
2. 确认已连接到应用服务
3. 或在应用服务页面，确认已连接到PostgreSQL服务

#### 方法2：手动设置（不推荐）

如果Zeabur没有自动设置，您可以：

1. 在PostgreSQL服务页面，找到连接信息
2. 手动创建 `DATABASE_URL` 环境变量
3. 格式：`postgresql://用户名:密码@主机:端口/数据库名`

**注意：** 通常不需要手动设置，Zeabur会自动处理。

---

## 🔐 安全提示

### ✅ 应该做的

- 让Zeabur自动设置 `DATABASE_URL`
- 不要将 `DATABASE_URL` 提交到Git仓库
- 在生产环境中使用环境变量

### ❌ 不应该做的

- 不要在代码中硬编码 `DATABASE_URL`
- 不要将 `DATABASE_URL` 分享给他人
- 不要将 `DATABASE_URL` 写入 `.env` 文件并提交到Git

---

## 📊 不同环境的DATABASE_URL

### 开发环境（本地）

```
postgresql://postgres:password@localhost:5432/customer_service
```

### 生产环境（Zeabur）

```
postgresql://postgres:auto_generated_password@db-xxx.zeabur.com:5432/postgres
```

**注意：** Zeabur会自动生成密码和主机地址。

---

## 🧪 测试DATABASE_URL

### 如果应用服务已启动

访问健康检查端点：
```
https://my-telegram-bot33.zeabur.app/health
```

**正常响应：**
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

**异常响应：**
```json
{
  "checks": {
    "database": {
      "status": "unhealthy",
      "message": "Database connection failed: ..."
    }
  }
}
```

---

## 🆘 常见问题

### Q1: DATABASE_URL应该在哪里配置？

**A:** 在Zeabur应用服务的环境变量中。如果使用Zeabur的PostgreSQL服务，会自动设置。

### Q2: 如何查看DATABASE_URL的值？

**A:** 在Zeabur应用服务设置中，找到环境变量部分，查看 `DATABASE_URL` 的值。

### Q3: DATABASE_URL格式错误怎么办？

**A:** 
1. 确认格式是 `postgresql://用户名:密码@主机:端口/数据库名`
2. 确认所有特殊字符都已正确转义
3. 如果使用Zeabur的PostgreSQL服务，让Zeabur自动设置

### Q4: 可以使用外部数据库吗？

**A:** 可以。手动设置 `DATABASE_URL` 环境变量，格式同上。

---

## 📚 相关文档

- [数据库连接指南](ZEABUR_DATABASE_CONNECTION.md)
- [PostgreSQL就绪后操作](POSTGRESQL_READY_NEXT_STEPS.md)
- [环境变量配置](ZEABUR_ENV_VARS.md)

---

## ✅ 快速检查清单

- [ ] PostgreSQL服务已添加到项目
- [ ] PostgreSQL服务状态是 "Running"
- [ ] 在应用服务设置中，`DATABASE_URL` 已自动设置
- [ ] `DATABASE_URL` 值以 `postgresql://` 开头
- [ ] 健康检查显示数据库连接正常




