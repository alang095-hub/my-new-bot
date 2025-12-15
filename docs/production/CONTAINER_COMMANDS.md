# 🐳 Zeabur容器内命令指南

## 📍 当前状态

您已经连接到Zeabur容器终端：
```
root@service-xxx:/app#
```

现在可以在容器内执行命令来检查和修复问题。

## 🔍 立即执行的检查命令

### 1. 检查DATABASE_URL环境变量

```bash
echo $DATABASE_URL
```

**预期输出：**
```
postgresql://postgres:xxx@xxx.zeabur.com:5432/postgres
```

**如果输出为空：**
- DATABASE_URL未设置
- 需要在Zeabur控制台配置环境变量

### 2. 测试数据库连接

```bash
python -c "from src.core.database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print('✅ 数据库连接成功'); conn.close()"
```

**预期输出：**
```
✅ 数据库连接成功
```

**如果出现错误：**
- 查看错误信息
- 可能是DATABASE_URL格式错误
- 或数据库服务未启动

### 3. 运行数据库迁移

```bash
alembic upgrade head
```

**预期输出：**
```
INFO  [alembic.runtime.migration] Running upgrade ... -> ..., ...
```

**如果出现错误：**
- 查看错误信息
- 可能是数据库连接失败
- 或迁移文件有问题

### 4. 检查所有环境变量

```bash
env | grep -E '(DATABASE|FACEBOOK|OPENAI|TELEGRAM|SECRET)'
```

**预期输出：**
```
DATABASE_URL=postgresql://...
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
...
```

**如果缺少变量：**
- 需要在Zeabur控制台配置环境变量

### 5. 检查应用是否运行

```bash
ps aux | grep uvicorn
```

**预期输出：**
```
root     1  ... python -m uvicorn src.main:app ...
```

**如果没有输出：**
- 应用未运行
- 查看日志找出原因

## 🛠️ 常用诊断命令

### 检查Python环境

```bash
python --version
which python
```

### 检查已安装的包

```bash
pip list | grep -E '(sqlalchemy|alembic|fastapi|uvicorn)'
```

### 检查数据库连接（使用psql）

如果容器中有psql客户端：

```bash
psql $DATABASE_URL -c "SELECT version();"
```

### 查看应用日志

```bash
tail -f /app/logs/app.log
```

或查看标准输出：

```bash
# 如果应用在运行，日志会输出到标准输出
```

### 检查端口监听

```bash
netstat -tlnp | grep 8000
# 或
ss -tlnp | grep 8000
```

### 手动启动应用（测试用）

```bash
cd /app
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 🔧 修复常见问题

### 问题1：DATABASE_URL未设置

**检查：**
```bash
echo $DATABASE_URL
```

**如果为空，解决方法：**
1. 在Zeabur控制台配置环境变量
2. 或手动设置（临时）：
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:5432/db"
   ```

### 问题2：数据库连接失败

**测试连接：**
```bash
python -c "from src.core.database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print('OK'); conn.close()"
```

**如果失败，检查：**
1. DATABASE_URL格式是否正确
2. 数据库服务是否已启动
3. 网络连接是否正常

### 问题3：数据库迁移未运行

**运行迁移：**
```bash
alembic upgrade head
```

**检查迁移状态：**
```bash
alembic current
alembic history
```

### 问题4：应用未启动

**检查进程：**
```bash
ps aux | grep uvicorn
```

**如果未运行，手动启动（测试）：**
```bash
cd /app
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

## 📋 完整检查清单

在容器内执行以下命令，检查所有配置：

```bash
# 1. 检查环境变量
echo "=== 环境变量 ==="
env | grep -E '(DATABASE|FACEBOOK|OPENAI|TELEGRAM|SECRET|DEBUG)'

# 2. 测试数据库连接
echo -e "\n=== 数据库连接 ==="
python -c "from src.core.database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print('✅ 数据库连接成功'); conn.close()" 2>&1

# 3. 检查数据库迁移
echo -e "\n=== 数据库迁移 ==="
alembic current

# 4. 检查应用进程
echo -e "\n=== 应用进程 ==="
ps aux | grep uvicorn

# 5. 检查端口
echo -e "\n=== 端口监听 ==="
netstat -tlnp 2>/dev/null | grep -E '(8000|$PORT)' || ss -tlnp 2>/dev/null | grep -E '(8000|$PORT)'
```

## 🆘 需要帮助？

如果遇到问题，请提供：

1. **命令输出**（特别是错误信息）
2. **环境变量检查结果**
3. **数据库连接测试结果**
4. **应用进程状态**

## 📚 相关文档

- [数据库连接修复](FIX_DATABASE_CONNECTION.md)
- [DATABASE_URL格式说明](DATABASE_URL_FORMAT.md)
- [502错误排查步骤](502_TROUBLESHOOTING_STEPS.md)




