# 修复 502: SERVICE_UNAVAILABLE 错误

## 🔍 问题说明

502错误表示服务无响应，可能的原因：
1. 服务未正常启动
2. 服务崩溃
3. 端口配置问题
4. 环境变量配置问题导致启动失败
5. 代码错误导致服务无法启动

## 📋 立即排查步骤

### 步骤1：在Zeabur控制台查看服务状态

1. 访问您的Zeabur项目页面
2. 点击您的服务
3. 查看服务状态：
   - 🔴 **Failed** - 服务启动失败
   - 🟡 **Restarting** - 服务正在重启
   - 🟢 **Running** - 但可能内部错误

### 步骤2：查看服务日志（最重要！）

在Zeabur服务页面：
1. 找到 **"Logs"** 或 **"日志"** 标签
2. 查看最新的日志信息
3. **查找错误信息**（这是关键！）

### 步骤3：常见错误和解决方案

#### 错误1：环境变量未配置

**日志可能显示：**
```
Field required [type=missing, input_value=...]
```

**解决：**
1. 检查所有必需的环境变量是否已配置
2. 参考 `ZEABUR_ENV_VARS.md` 配置所有变量
3. 保存后等待服务重启

#### 错误2：数据库连接失败

**日志可能显示：**
```
Database connection failed
OperationalError: could not connect to server
```

**解决：**
1. 确认PostgreSQL服务已启动
2. 确认 `DATABASE_URL` 已自动设置（Zeabur会自动设置）
3. 检查数据库服务状态

#### 错误3：代码错误导致崩溃

**日志可能显示：**
```
SyntaxError: ...
ImportError: ...
IndentationError: ...
```

**解决：**
1. 查看完整的错误堆栈
2. 根据错误信息修复代码
3. 重新部署

#### 错误4：端口配置问题

**日志可能显示：**
```
Address already in use
Port not available
```

**解决：**
1. Zeabur会自动设置 `$PORT` 环境变量
2. 确认 `Procfile` 或启动命令使用 `$PORT`
3. 检查 `zeabur.json` 配置

#### 错误5：依赖安装失败

**日志可能显示：**
```
ModuleNotFoundError: No module named '...'
Package installation failed
```

**解决：**
1. 检查 `requirements.txt` 是否完整
2. 查看构建日志确认依赖安装成功
3. 确认Python版本兼容

## 🔧 快速修复步骤

### 如果看到环境变量错误

1. **在Zeabur中配置所有环境变量**
   - 参考 `ZEABUR_ENV_VARS_TEMPLATE.txt`
   - 确保所有必需变量都已配置

2. **保存并等待重启**
   - 环境变量更改后会自动重启
   - 等待1-2分钟

### 如果看到数据库连接错误

1. **检查PostgreSQL服务**
   - 确认服务已启动
   - 确认服务状态是 "Running"

2. **检查DATABASE_URL**
   - Zeabur应该自动设置
   - 如果未设置，检查服务连接

### 如果看到代码错误

1. **查看完整错误堆栈**
2. **修复代码**
3. **提交并推送**
4. **等待Zeabur自动重新部署**

## 📊 检查清单

在Zeabur控制台中：

- [ ] 查看服务状态
- [ ] 查看最新日志
- [ ] 查找错误信息
- [ ] 检查环境变量配置
- [ ] 检查数据库服务状态
- [ ] 查看构建日志（如果有错误）

## 🆘 需要的信息

请提供以下信息以便诊断：

1. **服务状态**（Failed/Restarting/Running）
2. **日志中的最新错误信息**（最重要！）
3. **构建日志中的错误**（如果有）
4. **环境变量配置情况**（是否都已配置）

## 📝 日志查看技巧

### 查找关键错误

在日志中查找：
- `ERROR` - 错误信息
- `Exception` - 异常信息
- `Traceback` - 错误堆栈
- `Failed` - 失败信息
- `Field required` - 环境变量缺失

### 正常启动日志

服务正常启动应该看到：
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

如果看不到这些，说明服务未正常启动。

## 🔄 如果问题持续

### 方案1：重新部署

1. 在Zeabur项目页面
2. 找到 **"Redeploy"** 或 **"重新部署"** 选项
3. 触发重新部署

### 方案2：检查代码

1. 确认代码已推送到GitHub
2. 确认没有语法错误
3. 确认所有依赖都在 `requirements.txt` 中

### 方案3：简化配置

1. 暂时移除可选的环境变量
2. 只配置必需的变量
3. 确认服务可以启动
4. 再逐步添加其他配置

## 📚 相关文档

- [环境变量配置](ZEABUR_ENV_VARS.md)
- [环境变量快速修复](ZEABUR_ENV_QUICK_FIX.md)
- [部署后操作步骤](POST_DEPLOYMENT_STEPS.md)
- [故障排查](TROUBLESHOOTING_BROWSER.md)




