# 🐳 Zeabur Docker 容器使用指南

## 📖 什么是 Zeabur 的 Docker 容器？

Zeabur 将您的应用运行在 **Docker 容器**中。容器是一个独立的运行环境，包含：
- 您的应用代码
- Python 运行环境
- 所有依赖包
- 环境变量配置

## 🎯 如何访问 Zeabur 的 Docker 容器？

### 方法1：通过 Zeabur 控制台终端（推荐）⭐

**步骤：**

1. **访问 Zeabur 控制台**
   - 打开：https://zeabur.com
   - 登录您的账号
   - 找到项目：my-telegram-bot33

2. **打开应用服务**
   - 点击应用服务（不是 PostgreSQL 服务）
   - 进入服务详情页

3. **打开终端**
   - 在服务页面顶部，找到 **"Terminal"** 或 **"终端"** 标签
   - 点击打开终端窗口

4. **连接容器**
   - 终端会自动连接到运行中的容器
   - 看到类似这样的提示符：
     ```
     root@service-xxx:/app#
     ```
   - 表示已成功连接 ✅

5. **开始使用**
   - 现在可以在终端中输入命令
   - 所有命令都在容器内执行

### 方法2：通过 Zeabur CLI（高级）

如果您安装了 Zeabur CLI：

```bash
# 安装 Zeabur CLI
npm install -g zeabur

# 登录
zeabur login

# 连接到服务
zeabur connect <service-id>
```

## 🔍 容器内可以做什么？

### 1. 检查环境变量

```bash
# 查看单个环境变量
echo $DATABASE_URL
echo $PORT
echo $FACEBOOK_APP_ID

# 查看所有环境变量
env

# 查看特定前缀的环境变量
env | grep FACEBOOK
env | grep DATABASE
```

### 2. 检查文件系统

```bash
# 查看当前目录
pwd
# 输出：/app

# 列出文件
ls -la

# 查看项目结构
tree -L 2
# 或
find . -maxdepth 2 -type f -name "*.py" | head -20
```

### 3. 检查 Python 环境

```bash
# 查看 Python 版本
python --version

# 查看 Python 路径
which python

# 查看已安装的包
pip list

# 查看特定包
pip show fastapi
pip show sqlalchemy
```

### 4. 测试数据库连接

```bash
# 方法1：使用 Python
python -c "from src.core.database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print('✅ 数据库连接成功'); conn.close()"

# 方法2：使用 psql（如果已安装）
psql $DATABASE_URL -c "SELECT version();"
```

### 5. 运行数据库迁移

```bash
# 查看当前迁移版本
alembic current

# 查看迁移历史
alembic history

# 运行迁移
alembic upgrade head

# 回滚迁移（谨慎使用）
alembic downgrade -1
```

### 6. 检查应用进程

```bash
# 查看所有进程
ps aux

# 查看 uvicorn 进程
ps aux | grep uvicorn

# 查看进程树
pstree
```

### 7. 检查端口监听

```bash
# 查看监听的端口
netstat -tlnp

# 或使用 ss 命令
ss -tlnp

# 查看特定端口（例如 8080）
netstat -tlnp | grep 8080
ss -tlnp | grep 8080
```

### 8. 查看日志文件

```bash
# 查看应用日志（如果有）
tail -f /app/logs/app.log

# 查看最近的日志
tail -n 100 /app/logs/app.log

# 查看系统日志
journalctl -u your-service
```

### 9. 手动启动应用（测试用）

```bash
# 进入应用目录
cd /app

# 手动启动应用
python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT

# 或使用 run.py（如果有）
python run.py
```

### 10. 运行 Python 脚本

```bash
# 运行单个 Python 命令
python -c "print('Hello from container')"

# 运行 Python 脚本
python scripts/tools/check_database.py

# 进入 Python 交互式环境
python
```

## 🛠️ 常用诊断命令组合

### 完整系统检查

```bash
# 1. 检查环境变量
echo "=== 环境变量 ==="
env | grep -E '(DATABASE|FACEBOOK|OPENAI|TELEGRAM|SECRET|PORT|DEBUG)'

# 2. 检查 Python 环境
echo -e "\n=== Python 环境 ==="
python --version
which python

# 3. 检查依赖包
echo -e "\n=== 依赖包 ==="
pip list | grep -E '(fastapi|uvicorn|sqlalchemy|alembic)'

# 4. 测试数据库连接
echo -e "\n=== 数据库连接 ==="
python -c "from src.core.database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print('✅ 数据库连接成功'); conn.close()" 2>&1

# 5. 检查应用进程
echo -e "\n=== 应用进程 ==="
ps aux | grep uvicorn

# 6. 检查端口监听
echo -e "\n=== 端口监听 ==="
netstat -tlnp 2>/dev/null | grep -E '(8000|8080)' || ss -tlnp 2>/dev/null | grep -E '(8000|8080)'

# 7. 检查数据库迁移
echo -e "\n=== 数据库迁移 ==="
alembic current 2>&1
```

### 快速健康检查

```bash
# 一键检查脚本
cat << 'EOF' > /tmp/check.sh
#!/bin/bash
echo "=== 环境变量 ==="
env | grep -E '(DATABASE|PORT)' | head -5
echo -e "\n=== 应用进程 ==="
ps aux | grep uvicorn | grep -v grep
echo -e "\n=== 端口监听 ==="
ss -tlnp 2>/dev/null | grep -E '(8000|8080)' || netstat -tlnp 2>/dev/null | grep -E '(8000|8080)'
EOF
chmod +x /tmp/check.sh
/tmp/check.sh
```

## 🔧 修复常见问题

### 问题1：环境变量未设置

**检查：**
```bash
echo $DATABASE_URL
```

**如果为空，解决方法：**
1. 在 Zeabur 控制台配置环境变量
2. 重启服务使环境变量生效

### 问题2：数据库连接失败

**测试连接：**
```bash
python -c "from src.core.database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print('OK'); conn.close()"
```

**如果失败，检查：**
1. DATABASE_URL 格式是否正确
2. 数据库服务是否已启动
3. 网络连接是否正常

### 问题3：应用未启动

**检查进程：**
```bash
ps aux | grep uvicorn
```

**如果未运行，手动启动（测试）：**
```bash
cd /app
python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

### 问题4：端口不匹配

**检查监听的端口：**
```bash
ss -tlnp | grep -E '(8000|8080)'
```

**如果应用监听 8000，但 Zeabur 期望 8080：**
1. 设置 `PORT=8080` 环境变量
2. 重启服务

### 问题5：依赖包缺失

**检查已安装的包：**
```bash
pip list | grep fastapi
```

**如果缺失，重新安装：**
```bash
pip install -r requirements.txt
```

**注意：** 容器重启后，手动安装的包会丢失。需要在 `requirements.txt` 中添加。

## 📋 容器文件系统结构

```
/app/                    # 应用根目录
├── src/                 # 源代码
│   ├── main.py         # 应用入口
│   ├── api/            # API 路由
│   ├── core/           # 核心模块
│   └── ...
├── alembic/            # 数据库迁移
├── scripts/            # 脚本文件
├── requirements.txt    # Python 依赖
├── runtime.txt         # Python 版本
├── Procfile            # 启动命令
└── zeabur.json         # Zeabur 配置
```

## ⚠️ 重要注意事项

### 1. 容器是临时的

- **容器重启后，手动修改的文件会丢失**
- 所有代码修改需要通过 Git 提交和部署
- 环境变量需要在 Zeabur 控制台配置

### 2. 不要在生产环境手动启动应用

- 应用应该通过 Zeabur 自动启动
- 手动启动的应用在容器重启后会丢失
- 只在调试时手动启动

### 3. 权限限制

- 您以 `root` 用户运行，有完全权限
- 但某些系统文件可能无法修改（只读文件系统）

### 4. 资源限制

- 容器有 CPU 和内存限制
- 长时间运行的命令可能被终止
- 大文件操作可能失败

## 🎓 实用技巧

### 技巧1：使用别名简化命令

```bash
# 创建别名
alias check-db='python -c "from src.core.database.connection import engine; from sqlalchemy import text; conn = engine.connect(); print(\"✅ OK\"); conn.close()"'
alias check-env='env | grep -E "(DATABASE|FACEBOOK|OPENAI|TELEGRAM|SECRET|PORT)"'

# 使用别名
check-db
check-env
```

### 技巧2：保存常用命令到文件

```bash
# 创建检查脚本
cat << 'EOF' > /tmp/quick-check.sh
#!/bin/bash
echo "环境变量："
env | grep PORT
echo "进程："
ps aux | grep uvicorn
echo "端口："
ss -tlnp | grep 8080
EOF

chmod +x /tmp/quick-check.sh

# 使用
/tmp/quick-check.sh
```

### 技巧3：查看命令历史

```bash
# 查看命令历史
history

# 搜索历史命令
history | grep alembic

# 重新执行历史命令
!123  # 执行第123条命令
```

### 技巧4：重定向输出到文件

```bash
# 保存输出到文件
env > /tmp/env-vars.txt
ps aux > /tmp/processes.txt

# 查看文件
cat /tmp/env-vars.txt
```

## 🆘 获取帮助

### 在容器内获取帮助

```bash
# 命令帮助
man <command>
<command> --help

# Python 帮助
python -h
pip --help
```

### 常见命令帮助

```bash
# 查看所有可用命令
ls /usr/bin | head -20

# 查看 Python 模块
python -c "help('modules')"

# 查看已安装的包
pip list
```

## 📚 相关文档

- [容器内命令指南](CONTAINER_COMMANDS.md)
- [终端使用基础教程](TERMINAL_BASICS.md)
- [终端无法输入解决方案](TERMINAL_CANNOT_INPUT.md)
- [数据库连接修复](FIX_DATABASE_CONNECTION.md)

## 🎯 快速开始

**现在就试试：**

1. **打开 Zeabur 控制台终端**
   - 访问：https://zeabur.com
   - 找到服务 → 点击 "Terminal" 标签

2. **执行第一个命令**
   ```bash
   echo "Hello from Docker container!"
   ```

3. **检查环境变量**
   ```bash
   echo $PORT
   ```

4. **查看应用进程**
   ```bash
   ps aux | grep uvicorn
   ```

**恭喜！您已经成功使用 Zeabur 的 Docker 容器了！** 🎉



