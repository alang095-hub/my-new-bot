# 🔧 持续502错误修复指南

## 🚨 问题说明

如果502错误持续存在，说明服务可能：
1. 启动时崩溃
2. 无法监听正确端口
3. 健康检查失败导致负载均衡器拒绝请求
4. 启动事件中有未捕获的异常

## 🔍 立即排查步骤

### 步骤1：查看Zeabur日志中的启动信息

在Zeabur控制台的日志中，查找以下关键信息：

**正常启动应该看到：**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXX
```

**如果没有看到这些，说明服务未正常启动！**

### 步骤2：查找启动错误

在日志中查找：
- `ERROR` - 任何错误信息
- `Exception` - 异常信息
- `Traceback` - 错误堆栈
- `Failed to` - 失败的操作
- `Field required` - 环境变量缺失

### 步骤3：检查常见启动问题

#### 问题1：环境变量缺失

**日志显示：**
```
Field required [type=missing, input_value=...]
```

**解决：**
1. 检查所有必需的环境变量是否已配置
2. 参考 `docs/production/ZEABUR_ENV_VARS.md`
3. 确保以下变量都已配置：
   - `DATABASE_URL`
   - `FACEBOOK_APP_ID`
   - `FACEBOOK_APP_SECRET`
   - `FACEBOOK_ACCESS_TOKEN`
   - `FACEBOOK_VERIFY_TOKEN`
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `SECRET_KEY`

#### 问题2：数据库连接失败

**日志显示：**
```
OperationalError: could not connect to server
Database connection failed
```

**解决：**
1. 确认PostgreSQL服务已启动
2. 检查 `DATABASE_URL` 是否正确
3. 确认数据库服务状态是 "Running"

#### 问题3：启动事件异常

**日志显示：**
```
Failed to initialize...
Error in startup event...
```

**解决：**
1. 查看完整的错误堆栈
2. 根据错误信息修复问题
3. 启动事件中的错误不应该阻止服务启动（已用try-except包裹）

#### 问题4：端口配置问题

**日志显示：**
```
Address already in use
Port not available
```

**解决：**
1. Zeabur会自动设置 `$PORT` 环境变量
2. 确认 `Procfile` 和 `zeabur.json` 使用 `$PORT`
3. 不要手动设置 `PORT` 环境变量

## 🔧 已实施的修复

### 修复1：健康检查端点优化

已修改 `/health` 端点，使其在数据库连接失败时也能返回响应，避免502错误。

**新的健康检查端点：**
- `/health` - 完整健康检查（数据库失败时返回degraded状态）
- `/health/simple` - 简单健康检查（完全不依赖数据库）

### 修复2：启动事件错误处理

启动事件中的所有初始化操作都已用try-except包裹，不会导致服务崩溃。

## 📋 诊断检查清单

在Zeabur控制台中：

- [ ] 查看服务状态（Failed/Restarting/Running）
- [ ] 查看最新日志
- [ ] 查找 "Uvicorn running" 消息
- [ ] 查找任何 ERROR/Exception/Traceback
- [ ] 检查环境变量配置
- [ ] 检查数据库服务状态
- [ ] 查看构建日志（如果有错误）

## 🧪 测试服务是否运行

### 方法1：使用简单健康检查端点

```bash
curl https://your-app-name.zeabur.app/health/simple
```

**应该返回：**
```json
{
  "status": "ok",
  "timestamp": "...",
  "message": "Service is running"
}
```

### 方法2：使用完整健康检查端点

```bash
curl https://your-app-name.zeabur.app/health
```

**可能返回：**
- `200 OK` - 服务正常
- `200 OK` 但 `status: "degraded"` - 服务运行但数据库有问题

### 方法3：访问根路径

```bash
curl https://your-app-name.zeabur.app/
```

**应该返回应用信息**

## 🆘 如果问题仍然存在

### 需要提供的信息

1. **服务状态**（Failed/Restarting/Running）
2. **完整的启动日志**（从服务启动到现在的所有日志）
3. **任何错误信息**（ERROR/Exception/Traceback）
4. **环境变量配置情况**（是否都已配置）
5. **数据库服务状态**

### 临时解决方案

如果服务持续502，可以尝试：

1. **重新部署**
   - 在Zeabur项目页面
   - 找到 "Redeploy" 选项
   - 触发重新部署

2. **检查代码**
   - 确认代码已推送到GitHub
   - 确认没有语法错误
   - 确认所有依赖都在 `requirements.txt` 中

3. **简化配置**
   - 暂时移除可选的环境变量
   - 只配置必需的变量
   - 确认服务可以启动

## 📚 相关文档

- [502错误修复指南](FIX_502_ERROR.md)
- [502错误诊断指南](DIAGNOSE_502_ERROR.md)
- [Zeabur控制台使用指南](ZEABUR_CONSOLE_GUIDE.md)
- [环境变量配置](ZEABUR_ENV_VARS.md)

## 🔄 下一步

1. **查看Zeabur日志**，找到具体的错误信息
2. **测试健康检查端点**，确认服务是否真的在运行
3. **提供错误信息**，我会帮您解决具体问题




