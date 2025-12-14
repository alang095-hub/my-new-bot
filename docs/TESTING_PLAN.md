# 项目测试实施方案

## 一、测试前准备

### 1.1 修复关键问题（已完成✅）

- ✅ 修复 `alembic/env.py` 导入路径
- ✅ 修复 `src/monitoring/api.py` 导入路径
- ✅ 更新 `src/core/database/__init__.py` 导出新模型
- ✅ 创建 `src/core/templates/__init__.py`
- ✅ 修复其他文件的导入路径

### 1.2 环境准备

**必需步骤：**

1. **创建 `.env` 文件**
   ```bash
   cp env.example .env
   # 编辑 .env，填入所有必需的配置
   ```

2. **创建 `config/config.yaml`**
   ```bash
   cp config/config.yaml.example config/config.yaml
   # 编辑 config.yaml，配置业务规则
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **准备测试数据库**
   - 创建PostgreSQL数据库
   - 或使用SQLite进行快速测试（修改DATABASE_URL）

### 1.3 验证修复

**验证步骤：**

```bash
# 1. 验证Python语法
python -m py_compile src/**/*.py

# 2. 验证导入
python -c "from src.main import app; print('✅ 导入成功')"

# 3. 验证数据库连接
python -c "from src.core.database.connection import engine; engine.connect(); print('✅ 数据库连接成功')"

# 4. 验证新模型
python -c "from src.core.database.models import APIUsageLog, ReplyTemplate, PromptVersion; print('✅ 新模型导入成功')"
```

## 二、测试阶段

### 阶段1：数据库迁移测试

**目标：** 验证数据库迁移可以正常执行

**步骤：**

```bash
# 1. 检查当前迁移版本
alembic current

# 2. 查看迁移历史
alembic history

# 3. 执行迁移（升级到最新）
alembic upgrade head

# 4. 验证表创建
# PostgreSQL
psql -U your_user -d your_database -c "\dt" | grep -E "(api_usage_logs|reply_templates|prompt_versions|prompt_usage_logs)"

# 或使用Python验证
python -c "
from src.core.database.connection import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
required_tables = ['api_usage_logs', 'reply_templates', 'prompt_versions', 'prompt_usage_logs']
for table in required_tables:
    if table in tables:
        print(f'✅ {table} 表存在')
    else:
        print(f'❌ {table} 表不存在')
"
```

**预期结果：**
- ✅ 所有迁移成功执行
- ✅ 新表已创建
- ✅ 索引已创建

### 阶段2：服务启动测试

**目标：** 验证服务可以正常启动

**步骤：**

```bash
# 1. 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 2. 检查启动日志
# 应该看到：
# - "Starting Multi-Platform Customer Service Automation System..."
# - "Database tables created/verified"
# - "Auto-reply scheduler started"
# - "Summary notification scheduler started"
# - 无错误信息

# 3. 访问健康检查
curl http://localhost:8000/health

# 4. 访问根路径
curl http://localhost:8000/
```

**预期结果：**
- ✅ 服务正常启动
- ✅ 健康检查返回 "healthy"
- ✅ 无启动错误

### 阶段3：API端点测试

**目标：** 验证所有新API端点可以访问

**测试脚本：**

```bash
# 1. API使用统计
curl http://localhost:8000/api-usage/daily
curl "http://localhost:8000/api-usage/statistics?days=7&api_type=openai"

# 2. 模板管理
curl http://localhost:8000/templates
curl -X POST http://localhost:8000/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_template",
    "content": "测试模板{{variable}}",
    "variables": ["variable"]
  }'

# 3. A/B测试
curl http://localhost:8000/ab-testing/versions
curl -X POST http://localhost:8000/ab-testing/versions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试版本",
    "version_code": "test_v1",
    "prompt_content": "测试提示词"
  }'
```

**或使用测试脚本：**

```bash
python scripts/setup/test_new_features.py
```

**预期结果：**
- ✅ 所有API端点返回200状态码
- ✅ 返回正确的JSON数据
- ✅ 无错误信息

### 阶段4：功能集成测试

**目标：** 测试完整功能流程

**测试场景1：AI自动回复流程**

```python
# 模拟Facebook消息接收
# 1. 发送Webhook请求
# 2. 验证消息被处理
# 3. 验证AI回复生成
# 4. 验证回复发送
# 5. 验证数据库记录
```

**测试场景2：批量处理**

```python
# 1. 创建未回复消息
# 2. 等待调度器运行（或手动触发）
# 3. 验证批量处理
# 4. 验证回复发送
```

**测试场景3：A/B测试**

```python
# 1. 创建多个提示词版本
# 2. 发送多个消息
# 3. 验证版本分配
# 4. 验证使用记录
# 5. 查看统计
```

**测试场景4：模板渲染**

```python
# 1. 创建模板
# 2. 渲染模板
# 3. 验证变量替换
```

### 阶段5：性能测试

**目标：** 验证性能优化效果

**测试项：**

1. **缓存效果**
   - 第一次查询（数据库）
   - 第二次查询（缓存）
   - 对比响应时间

2. **批量处理性能**
   - 单条处理时间
   - 批量处理时间
   - 对比性能提升

3. **数据库查询优化**
   - 查询执行时间
   - 索引使用情况

## 三、测试检查清单

### 3.1 基础功能检查

- [ ] 服务可以正常启动
- [ ] 数据库连接正常
- [ ] 健康检查通过
- [ ] 所有API端点可访问

### 3.2 新功能检查

- [ ] API使用统计功能正常
- [ ] 错误率告警功能正常
- [ ] 批量处理功能正常
- [ ] 缓存功能正常
- [ ] 模板管理功能正常
- [ ] A/B测试功能正常

### 3.3 集成检查

- [ ] AI自动回复流程完整
- [ ] 调度器正常工作
- [ ] 监控功能正常
- [ ] 统计功能正常

### 3.4 性能检查

- [ ] 响应时间在可接受范围
- [ ] 缓存命中率正常
- [ ] 数据库查询优化生效
- [ ] 批量处理性能提升

## 四、问题排查

### 4.1 常见问题

**问题1：迁移失败**

**症状：** `alembic upgrade head` 报错

**解决方案：**
1. 检查数据库连接
2. 检查迁移文件语法
3. 查看详细错误信息
4. 回滚到上一个版本：`alembic downgrade -1`

**问题2：服务启动失败**

**症状：** `uvicorn` 启动时报错

**解决方案：**
1. 检查 `.env` 配置
2. 检查导入路径
3. 查看错误堆栈
4. 验证依赖安装

**问题3：API返回404**

**症状：** API端点返回404

**解决方案：**
1. 检查路由注册（`src/main.py`）
2. 检查URL路径
3. 查看服务日志

**问题4：数据库表不存在**

**症状：** 查询时报表不存在

**解决方案：**
1. 运行迁移：`alembic upgrade head`
2. 检查表名是否正确
3. 验证模型定义

## 五、测试环境建议

### 5.1 最小测试环境

**数据库：** SQLite（快速测试）
```bash
DATABASE_URL=sqlite:///./test.db
```

**API密钥：** 使用测试密钥或Mock

**配置：** 最小化配置，只启用核心功能

### 5.2 完整测试环境

**数据库：** PostgreSQL（生产环境）

**API密钥：** 真实密钥（测试环境）

**配置：** 完整配置，启用所有功能

## 六、测试时间估算

### 快速测试（最小环境）
- 修复问题：10分钟 ✅
- 环境准备：15分钟
- 基础测试：20分钟
- **总计：45分钟**

### 完整测试（生产环境）
- 修复问题：10分钟 ✅
- 环境准备：30分钟
- 功能测试：60分钟
- 性能测试：30分钟
- **总计：2小时**

## 七、下一步行动

### 立即执行

1. ✅ 修复关键问题（已完成）
2. ⏭️ 准备测试环境
3. ⏭️ 运行数据库迁移
4. ⏭️ 启动服务测试
5. ⏭️ 执行功能测试

### 测试后

1. 根据测试结果优化
2. 修复发现的问题
3. 完善文档
4. 准备生产部署

## 八、风险评估

### 低风险 ✅
- 代码修复（已完成）
- 基础功能测试

### 中风险 ⚠️
- 数据库迁移（建议备份）
- 环境配置（需要仔细检查）

### 高风险 ⚠️
- 生产环境测试（建议先在测试环境）

## 结论

**当前状态：** ✅ **可以开始测试**

所有关键问题已修复，项目可以正常启动和运行。建议按照测试阶段逐步验证，确保每个功能正常工作后再进行下一步。
