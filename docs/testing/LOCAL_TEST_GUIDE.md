# 本地测试指南

本文档提供了本地开发环境测试的详细指南，帮助开发者快速验证系统功能。

## 目录

1. [快速开始](#快速开始)
2. [环境准备](#环境准备)
3. [测试步骤](#测试步骤)
4. [测试脚本使用](#测试脚本使用)
5. [手动测试](#手动测试)
6. [问题排查](#问题排查)
7. [测试报告](#测试报告)

## 快速开始

### 5分钟快速测试

```bash
# 1. 激活虚拟环境
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 2. 检查环境
python --version
python -c "from src.core.config import settings; print('配置OK')"

# 3. 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 在另一个终端运行快速测试
python scripts/test/local_test.py
```

## 环境准备

### 1. Python环境

**要求**: Python 3.9+

**检查**:
```bash
python --version
```

**安装虚拟环境**（如果未安装）:
```bash
python -m venv venv
```

### 2. 依赖安装

```bash
# 激活虚拟环境
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 环境变量配置

创建 `.env` 文件（参考 `env.example`）:

```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# 或使用SQLite进行快速测试
# DATABASE_URL=sqlite:///./test.db

# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_VERIFY_TOKEN=your_verify_token

# OpenAI
OPENAI_API_KEY=your_openai_key

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 安全
SECRET_KEY=your_secret_key_at_least_32_chars

# 调试
DEBUG=true
```

### 4. 数据库设置

**使用PostgreSQL**:
```bash
# 创建数据库
createdb your_database_name

# 运行迁移
alembic upgrade head
```

**使用SQLite（快速测试）**:
```bash
# 修改 .env 中的 DATABASE_URL
DATABASE_URL=sqlite:///./test.db

# 运行迁移
alembic upgrade head
```

### 5. 配置文件

创建 `config/config.yaml`（参考 `config/config.yaml.example`）:

```yaml
telegram_groups:
  main_group: "https://t.me/your_group"

auto_reply:
  enabled: true
  templates:
    - name: "welcome"
      content: "欢迎咨询！"
```

## 测试步骤

### 阶段1: 基础功能测试

#### 1.1 数据库连接测试

```bash
python -c "from src.core.database.connection import get_db; next(get_db()); print('✅ 数据库连接成功')"
```

**预期结果**: 输出 "✅ 数据库连接成功"

**如果失败**:
- 检查 `DATABASE_URL` 环境变量
- 确认数据库服务运行中
- 检查网络连接

#### 1.2 配置加载测试

```bash
python -c "from src.core.config import settings; print(f'✅ 配置加载成功: DEBUG={settings.debug}')"
```

**预期结果**: 输出配置信息

**如果失败**:
- 检查 `.env` 文件是否存在
- 验证必需的环境变量已配置

#### 1.3 模块导入测试

```bash
# 测试核心模块
python -c "from src.core.database.connection import get_db; print('✅ 数据库模块OK')"
python -c "from src.core.config import settings; print('✅ 配置模块OK')"
python -c "from src.ai.reply_generator import ReplyGenerator; print('✅ AI模块OK')"
python -c "from src.collector.data_collector import DataCollector; print('✅ 收集器模块OK')"
```

### 阶段2: 服务启动测试

#### 2.1 启动服务

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**预期输出**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 2.2 健康检查

在另一个终端运行:

```bash
# 简单健康检查
curl http://localhost:8000/health/simple

# 完整健康检查
curl http://localhost:8000/health
```

**预期结果**: 返回JSON格式的健康状态

### 阶段3: API端点测试

#### 3.1 基础端点

```bash
# 根路径
curl http://localhost:8000/

# 健康检查
curl http://localhost:8000/health

# 性能指标
curl http://localhost:8000/metrics
```

#### 3.2 管理API

```bash
# 对话列表
curl "http://localhost:8000/api/v1/admin/conversations?page=1&page_size=10"

# 统计信息
curl http://localhost:8000/api/v1/admin/statistics
```

#### 3.3 Webhook端点

```bash
# Facebook Webhook验证
curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test"
```

**预期结果**: 返回challenge值

### 阶段4: 核心功能测试

#### 4.1 AI回复功能

创建测试脚本 `test_ai_reply.py`:

```python
from src.core.database.connection import get_db
from src.ai.reply_generator import ReplyGenerator

db = next(get_db())
generator = ReplyGenerator(db)

# 测试回复生成
reply = generator.generate_reply(
    message_content="我想咨询贷款",
    customer_id=1,
    conversation_history=[]
)
print(f"生成的回复: {reply}")
```

运行:
```bash
python test_ai_reply.py
```

#### 4.2 数据收集功能

创建测试脚本 `test_data_collector.py`:

```python
from src.collector.data_collector import DataCollector

collector = DataCollector()

# 测试信息提取
message = "我的邮箱是 test@example.com，电话是 13812345678"
result = collector.extract_info_from_message(message)
print(f"提取的信息: {result}")
```

运行:
```bash
python test_data_collector.py
```

#### 4.3 过滤功能

创建测试脚本 `test_filter.py`:

```python
from src.collector.filter_engine import FilterEngine
from src.core.config import yaml_config

filter_engine = FilterEngine(yaml_config)

# 测试消息过滤
result = filter_engine.filter_message("我想咨询贷款")
print(f"过滤结果: {result}")
```

## 测试脚本使用

### 快速测试脚本

**用途**: 快速验证基础功能

**运行**:
```bash
python scripts/test/local_test.py
```

**测试内容**:
- 数据库连接
- 配置加载
- 核心模块导入
- Repository模式
- API健康检查（如果服务运行）

**输出示例**:
```
============================================================
本地快速测试
============================================================
测试时间: 2025-01-XX XX:XX:XX

阶段1: 基础功能测试
------------------------------------------------------------
✅ 数据库连接 (0.023s)
   连接成功，响应时间: 0.023s
✅ 配置加载 (0.001s)
   配置加载成功，已加载: 3 个关键配置
...
```

### 完整测试脚本

**用途**: 全面测试所有功能

**运行**:
```bash
python scripts/test/full_local_test.py
```

**测试内容**:
- 环境检查
- 数据库测试
- Repository模式测试
- 核心功能测试
- API端点测试
- 性能测试

**输出**: 详细的测试报告和JSON格式的测试结果

## 手动测试

### 使用API文档

1. 启动服务:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. 打开浏览器访问:
   ```
   http://localhost:8000/docs
   ```

3. 在Swagger UI中测试各个端点

### 使用curl

**基础请求**:
```bash
# GET请求
curl http://localhost:8000/health

# POST请求
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"entry": [...]}'
```

**带参数的请求**:
```bash
curl "http://localhost:8000/api/v1/admin/conversations?page=1&page_size=10"
```

### 使用Python脚本

创建 `test_manual.py`:

```python
import httpx

# 测试健康检查
response = httpx.get("http://localhost:8000/health/simple")
print(response.json())

# 测试对话列表
response = httpx.get("http://localhost:8000/api/v1/admin/conversations?page=1&page_size=10")
print(response.json())
```

运行:
```bash
python test_manual.py
```

## 问题排查

### 问题1: 数据库连接失败

**症状**: 
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案**:
1. 检查 `DATABASE_URL` 环境变量
2. 确认数据库服务运行中
3. 检查网络连接
4. 验证数据库用户权限

### 问题2: 配置加载失败

**症状**:
```
pydantic.ValidationError: Field required
```

**解决方案**:
1. 检查 `.env` 文件是否存在
2. 验证所有必需的环境变量已配置
3. 检查环境变量格式（无多余空格）
4. 确认环境变量名称正确

### 问题3: 服务启动失败

**症状**:
```
ERROR: [Errno 48] Address already in use
```

**解决方案**:
1. 检查端口是否被占用: `netstat -an | grep 8000`
2. 使用其他端口: `--port 8001`
3. 关闭占用端口的进程

### 问题4: 模块导入失败

**症状**:
```
ModuleNotFoundError: No module named 'src'
```

**解决方案**:
1. 确认在项目根目录运行
2. 检查 `PYTHONPATH` 环境变量
3. 确认虚拟环境已激活
4. 重新安装依赖: `pip install -r requirements.txt`

### 问题5: API端点返回错误

**症状**: HTTP 500 或 404 错误

**解决方案**:
1. 检查服务日志
2. 验证API路径正确
3. 检查请求格式
4. 验证认证配置

## 测试报告

### 自动生成报告

运行完整测试后，报告会自动保存到:
```
data/test_reports/local_test_YYYYMMDD_HHMMSS.json
```

### 报告内容

- 测试时间
- 测试总数
- 通过/失败/跳过/警告数量
- 每个测试的详细结果
- 错误信息

### 查看报告

```bash
# 查看最新报告
ls -lt data/test_reports/ | head -1

# 查看报告内容
cat data/test_reports/local_test_*.json | python -m json.tool
```

## 最佳实践

### 1. 测试顺序

1. 先运行快速测试验证基础功能
2. 启动服务进行API测试
3. 运行完整测试进行全面验证
4. 进行手动测试验证业务流程

### 2. 测试环境

- 使用独立的测试数据库
- 使用测试用的API密钥（如果可用）
- 定期清理测试数据

### 3. 测试数据

- 使用模拟数据而非真实数据
- 测试后清理测试数据
- 保存测试数据用于回归测试

### 4. 持续测试

- 每次代码更改后运行快速测试
- 提交代码前运行完整测试
- 定期运行性能测试

## 下一步

测试通过后，可以:

1. **部署到测试环境** - 参考部署文档
2. **运行生产环境测试** - 参考生产测试文档
3. **性能优化** - 根据测试结果优化性能
4. **功能扩展** - 添加新功能并测试

---

**需要帮助?** 查看 [测试检查清单](LOCAL_TEST_CHECKLIST.md) 或提交Issue。

