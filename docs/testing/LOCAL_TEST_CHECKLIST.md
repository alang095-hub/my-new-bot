# 本地测试检查清单

本文档提供了本地开发环境测试的详细检查清单，帮助确保系统正常运行。

## 一、环境准备检查

### 1.1 基础环境

- [ ] **Python版本检查**
  ```bash
  python --version
  # 要求: Python 3.9+
  ```

- [ ] **虚拟环境**
  ```bash
  # Windows
  .\venv\Scripts\activate
  # Linux/Mac
  source venv/bin/activate
  ```

- [ ] **依赖安装**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **项目路径**
  - 确认当前目录为项目根目录
  - 确认 `src/` 目录存在
  - 确认 `config/` 目录存在

### 1.2 配置文件

- [ ] **环境变量文件 (`.env`)**
  - [ ] `DATABASE_URL` - 数据库连接字符串
  - [ ] `FACEBOOK_APP_ID` - Facebook应用ID
  - [ ] `FACEBOOK_APP_SECRET` - Facebook应用密钥
  - [ ] `FACEBOOK_ACCESS_TOKEN` - Facebook访问令牌
  - [ ] `FACEBOOK_VERIFY_TOKEN` - Facebook验证令牌
  - [ ] `OPENAI_API_KEY` - OpenAI API密钥
  - [ ] `TELEGRAM_BOT_TOKEN` - Telegram Bot令牌
  - [ ] `TELEGRAM_CHAT_ID` - Telegram聊天ID
  - [ ] `SECRET_KEY` - 应用密钥（至少32字符）
  - [ ] `DEBUG` - 调试模式（开发环境: `true`）

- [ ] **业务配置文件 (`config/config.yaml`)**
  - [ ] 文件存在
  - [ ] 格式正确（YAML）
  - [ ] 包含必需的配置项

### 1.3 数据库

- [ ] **数据库连接**
  ```bash
  # 测试连接
  python -c "from src.core.database.connection import get_db; next(get_db()); print('连接成功')"
  ```

- [ ] **数据库迁移**
  ```bash
  # 运行迁移
  alembic upgrade head
  ```

- [ ] **数据库表**
  - [ ] `customers` 表存在
  - [ ] `conversations` 表存在
  - [ ] `collected_data` 表存在
  - [ ] `reviews` 表存在

## 二、基础功能测试

### 2.1 配置加载

- [ ] **配置加载测试**
  ```bash
  python -c "from src.core.config import settings; print(f'配置加载成功: DEBUG={settings.debug}')"
  ```

- [ ] **配置验证**
  - [ ] 所有必需配置已加载
  - [ ] 配置值格式正确
  - [ ] 无配置错误

### 2.2 模块导入

- [ ] **核心模块**
  ```bash
  python -c "from src.core.database.connection import get_db; print('数据库模块OK')"
  python -c "from src.core.config import settings; print('配置模块OK')"
  python -c "from src.ai.reply_generator import ReplyGenerator; print('AI模块OK')"
  ```

- [ ] **业务模块**
  - [ ] 数据收集器可导入
  - [ ] 过滤引擎可导入
  - [ ] Repository可导入

### 2.3 服务启动

- [ ] **启动服务**
  ```bash
  uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
  ```

- [ ] **启动检查**
  - [ ] 服务成功启动
  - [ ] 无启动错误
  - [ ] 日志正常输出

## 三、API端点测试

### 3.1 基础端点

- [ ] **根路径**
  ```bash
  curl http://localhost:8000/
  # 或浏览器访问: http://localhost:8000/
  ```
  - 预期: 返回系统信息

- [ ] **健康检查**
  ```bash
  curl http://localhost:8000/health
  curl http://localhost:8000/health/simple
  ```
  - 预期: 返回健康状态

- [ ] **性能指标**
  ```bash
  curl http://localhost:8000/metrics
  ```
  - 预期: 返回性能指标

### 3.2 管理API端点

- [ ] **对话列表**
  ```bash
  curl http://localhost:8000/api/v1/admin/conversations?page=1&page_size=10
  ```
  - 预期: 返回对话列表或需要认证

- [ ] **对话详情**
  ```bash
  curl http://localhost:8000/api/v1/admin/conversations/1
  ```
  - 预期: 返回对话详情或404

- [ ] **统计信息**
  ```bash
  curl http://localhost:8000/api/v1/admin/statistics
  ```
  - 预期: 返回统计信息

### 3.3 Webhook端点

- [ ] **Facebook Webhook验证**
  ```bash
  curl "http://localhost:8000/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test"
  ```
  - 预期: 返回challenge值

- [ ] **Instagram Webhook验证**（如果配置）
  ```bash
  curl "http://localhost:8000/instagram/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test"
  ```

## 四、核心功能测试

### 4.1 AI回复功能

- [ ] **回复生成器初始化**
  ```python
  from src.core.database.connection import get_db
  from src.ai.reply_generator import ReplyGenerator
  db = next(get_db())
  generator = ReplyGenerator(db)
  ```

- [ ] **消息处理**
  - [ ] 可以接收消息
  - [ ] 可以生成回复
  - [ ] 回复格式正确

### 4.2 数据收集功能

- [ ] **邮箱提取**
  ```python
  from src.collector.data_collector import DataCollector
  collector = DataCollector()
  result = collector.extract_info_from_message("我的邮箱是 test@example.com")
  assert "email" in result or "emails" in result
  ```

- [ ] **电话提取**
  ```python
  result = collector.extract_info_from_message("我的电话是 13812345678")
  assert "phone" in result or "phones" in result
  ```

- [ ] **数据验证**
  ```python
  from src.collector.data_validator import DataValidator
  validator = DataValidator()
  is_valid, _ = validator.validate_email("test@example.com")
  assert is_valid == True
  ```

### 4.3 过滤功能

- [ ] **关键词过滤**
  ```python
  from src.collector.filter_engine import FilterEngine
  from src.core.config import yaml_config
  filter_engine = FilterEngine(yaml_config)
  result = filter_engine.filter_message("测试消息")
  ```

- [ ] **优先级判断**
  - [ ] 可以识别高优先级消息
  - [ ] 可以识别低优先级消息

### 4.4 Repository模式

- [ ] **ConversationRepository**
  ```python
  from src.core.database.repositories.conversation_repo import ConversationRepository
  repo = ConversationRepository(db)
  assert hasattr(repo, 'get_by_id')
  assert hasattr(repo, 'create')
  ```

- [ ] **CustomerRepository**
  ```python
  from src.core.database.repositories.customer_repo import CustomerRepository
  repo = CustomerRepository(db)
  assert hasattr(repo, 'get_or_create')
  ```

## 五、性能测试

### 5.1 API响应时间

- [ ] **健康检查响应时间**
  - 目标: < 100ms
  - 测试: `curl -w "@curl-format.txt" http://localhost:8000/health/simple`

- [ ] **API端点响应时间**
  - 目标: < 500ms
  - 测试各个端点

### 5.2 数据库查询性能

- [ ] **简单查询**
  - 目标: < 100ms
  - 测试: Repository的get_by_id方法

- [ ] **复杂查询**
  - 目标: < 500ms
  - 测试: 带过滤和分页的查询

### 5.3 内存使用

- [ ] **服务内存占用**
  - 检查: 服务运行时的内存使用
  - 目标: 无明显内存泄漏

## 六、错误处理测试

### 6.1 数据库错误

- [ ] **连接失败处理**
  - 模拟数据库连接失败
  - 验证错误处理逻辑

- [ ] **查询错误处理**
  - 模拟无效查询
  - 验证错误返回

### 6.2 API错误

- [ ] **无效请求处理**
  - 发送无效的API请求
  - 验证错误响应

- [ ] **认证错误处理**
  - 测试未认证的请求
  - 验证401/403响应

### 6.3 业务逻辑错误

- [ ] **无效消息处理**
  - 发送格式错误的消息
  - 验证错误处理

- [ ] **API调用失败处理**
  - 模拟外部API失败
  - 验证重试机制

## 七、集成测试

### 7.1 完整流程测试

- [ ] **消息接收流程**
  1. 模拟Facebook消息接收
  2. 验证消息保存到数据库
  3. 验证AI回复生成
  4. 验证回复发送
  5. 验证Telegram通知

- [ ] **数据收集流程**
  1. 接收包含客户信息的消息
  2. 验证数据提取
  3. 验证数据验证
  4. 验证数据保存

### 7.2 调度器测试

- [ ] **自动回复调度器**
  - 验证调度器启动
  - 验证定时扫描功能

- [ ] **摘要通知调度器**
  - 验证调度器启动
  - 验证定时通知功能

## 八、自动化测试

### 8.1 快速测试

- [ ] **运行快速测试脚本**
  ```bash
  python scripts/test/local_test.py
  ```
  - 验证所有基础测试通过

### 8.2 完整测试

- [ ] **运行完整测试脚本**
  ```bash
  python scripts/test/full_local_test.py
  ```
  - 验证所有测试通过

### 8.3 单元测试

- [ ] **运行单元测试**
  ```bash
  pytest tests/ -v
  ```
  - 验证所有单元测试通过

## 九、测试报告

### 9.1 测试结果记录

- [ ] **记录测试时间**
- [ ] **记录测试环境信息**
- [ ] **记录测试结果**
- [ ] **记录发现的问题**

### 9.2 问题跟踪

- [ ] **列出所有失败项**
- [ ] **记录错误信息**
- [ ] **记录复现步骤**
- [ ] **记录修复建议**

## 十、测试完成确认

### 10.1 功能确认

- [ ] 所有基础功能正常
- [ ] 所有API端点可访问
- [ ] 核心业务流程正常
- [ ] 错误处理正常

### 10.2 性能确认

- [ ] API响应时间满足要求
- [ ] 数据库查询性能正常
- [ ] 无内存泄漏
- [ ] 日志正常记录

### 10.3 文档确认

- [ ] 测试报告已生成
- [ ] 问题已记录
- [ ] 测试结果已保存

---

## 快速测试命令

```bash
# 1. 环境检查
python --version
python -c "from src.core.config import settings; print('配置OK')"

# 2. 数据库检查
python -c "from src.core.database.connection import get_db; next(get_db()); print('数据库OK')"

# 3. 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 运行快速测试
python scripts/test/local_test.py

# 5. 运行完整测试
python scripts/test/full_local_test.py
```

## 常见问题

### 问题1: 数据库连接失败
**解决方案**:
- 检查 `DATABASE_URL` 环境变量
- 确认数据库服务运行中
- 检查网络连接

### 问题2: 配置加载失败
**解决方案**:
- 检查 `.env` 文件是否存在
- 验证所有必需的环境变量已配置
- 检查环境变量格式

### 问题3: 服务启动失败
**解决方案**:
- 检查端口是否被占用
- 检查依赖是否完整安装
- 查看错误日志

### 问题4: API端点返回错误
**解决方案**:
- 检查服务是否正常运行
- 验证API路径正确
- 检查认证配置

---

**测试完成后，请保存测试报告并记录所有发现的问题。**

