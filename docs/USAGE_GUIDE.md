# 新功能使用指南

## 一、数据库迁移

### 1.1 检查当前迁移状态

```bash
# 查看当前迁移版本
alembic current

# 查看所有迁移
alembic history
```

### 1.2 执行迁移

```bash
# 升级到最新版本（推荐）
alembic upgrade head

# 或者逐步升级
alembic upgrade 007  # API使用追踪
alembic upgrade 008  # 数据库优化
alembic upgrade 009  # 模板和A/B测试
```

### 1.3 回滚（如需要）

```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade 006
```

### 1.4 验证迁移

```bash
# 检查数据库表是否创建成功
# PostgreSQL
psql -U your_user -d your_database -c "\dt"

# 应该看到新表：
# - api_usage_logs
# - reply_templates
# - prompt_versions
# - prompt_usage_logs
```

## 二、测试API端点

### 2.1 启动服务

```bash
# 开发环境
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 或使用
python -m src.main
```

### 2.2 测试API使用统计

```bash
# 获取今日统计
curl http://localhost:8000/api-usage/daily

# 获取7天统计（OpenAI）
curl "http://localhost:8000/api-usage/statistics?days=7&api_type=openai"

# 获取所有API统计
curl "http://localhost:8000/api-usage/statistics?days=1"
```

**预期响应：**
```json
{
  "success": true,
  "data": {
    "openai": {
      "total_calls": 100,
      "success_calls": 95,
      "error_calls": 5,
      "success_rate": 95.0,
      "avg_response_time_ms": 500.5,
      "total_cost_usd": 0.0123,
      "total_tokens": 15000
    },
    "facebook": {...},
    "total": {...}
  }
}
```

### 2.3 测试模板管理

```bash
# 列出所有模板
curl http://localhost:8000/templates

# 创建模板
curl -X POST http://localhost:8000/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "greeting_template",
    "category": "greeting",
    "content": "您好{{customer_name}}！欢迎咨询我们的服务。",
    "variables": ["customer_name"],
    "description": "问候模板",
    "priority": 10
  }'

# 渲染模板
curl -X POST http://localhost:8000/templates/render \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "greeting_template",
    "variables": {
      "customer_name": "张三"
    }
  }'
```

### 2.4 测试A/B测试

```bash
# 列出所有版本
curl http://localhost:8000/ab-testing/versions

# 创建版本
curl -X POST http://localhost:8000/ab-testing/versions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "正式版",
    "version_code": "v1",
    "prompt_content": "你是一个专业的客服助手...",
    "traffic_percentage": 50,
    "description": "正式版本"
  }'

# 获取版本统计
curl "http://localhost:8000/ab-testing/versions/1/statistics?start_date=2025-01-01&end_date=2025-01-31"

# 对比版本
curl -X POST http://localhost:8000/ab-testing/compare \
  -H "Content-Type: application/json" \
  -d '{
    "version_ids": [1, 2],
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  }'
```

### 2.5 使用测试脚本

```bash
# 运行自动化测试脚本
python scripts/setup/test_new_features.py
```

## 三、配置功能

### 3.1 创建回复模板

**通过API创建：**

```python
import requests

# 创建问候模板
response = requests.post("http://localhost:8000/templates", json={
    "name": "greeting_template",
    "category": "greeting",
    "content": "您好{{customer_name}}！很高兴为您服务。",
    "variables": ["customer_name"],
    "priority": 10
})

# 创建价格咨询模板
response = requests.post("http://localhost:8000/templates", json={
    "name": "price_inquiry",
    "category": "price",
    "content": "我们的{{product_name}}价格从{{min_price}}起，具体价格根据型号不同。",
    "variables": ["product_name", "min_price"],
    "priority": 5
})
```

**常用模板示例：**

1. **问候模板**
   ```
   名称: greeting_template
   内容: 您好{{customer_name}}！欢迎咨询我们的iPhone贷款服务。
   变量: customer_name
   ```

2. **价格模板**
   ```
   名称: price_template
   内容: {{product_name}}的价格根据型号和容量不同，从{{min_price}}到{{max_price}}。
   变量: product_name, min_price, max_price
   ```

3. **型号模板**
   ```
   名称: model_template
   内容: 我们提供iPhone {{models}}等型号，您想了解哪个型号？
   变量: models
   ```

### 3.2 创建A/B测试版本

**步骤1：创建版本A（正式版）**

```python
response = requests.post("http://localhost:8000/ab-testing/versions", json={
    "name": "正式版",
    "version_code": "v1_formal",
    "prompt_content": """你是一个专业的客服助手。你的职责是：
1. 回复客户咨询要正式、专业
2. 使用礼貌用语
3. 提供准确信息""",
    "traffic_percentage": 50,
    "description": "正式专业版本"
})
```

**步骤2：创建版本B（友好版）**

```python
response = requests.post("http://localhost:8000/ab-testing/versions", json={
    "name": "友好版",
    "version_code": "v2_friendly",
    "prompt_content": """你是一个友好的客服助手。你的职责是：
1. 回复客户咨询要亲切、热情
2. 使用友好用语
3. 营造轻松氛围""",
    "traffic_percentage": 50,
    "description": "友好亲切版本"
})
```

**步骤3：启用版本**

确保两个版本的 `is_active` 都为 `true`，系统会自动分配流量。

### 3.3 监控API使用情况

**查看实时统计：**

```bash
# 今日统计
curl http://localhost:8000/api-usage/daily

# 本周统计
curl "http://localhost:8000/api-usage/statistics?days=7"
```

**设置告警阈值：**

系统会自动监控：
- API错误率 > 10% → 警告
- API错误率 > 20% → 错误告警
- 回复失败率 > 5% → 警告
- 回复失败率 > 10% → 错误告警

**查看告警：**

告警会通过以下方式发送：
- 日志记录
- Telegram通知（如果配置）

## 四、集成到现有代码

### 4.1 使用模板

模板功能已集成到系统，但需要手动调用：

```python
from src.core.templates.template_manager import TemplateManager

manager = TemplateManager(db)
template = manager.get_template_with_variables(
    name="greeting_template",
    variables={"customer_name": "张三"}
)
```

### 4.2 A/B测试

A/B测试已自动集成到 `ReplyGenerator`，无需额外配置。系统会：
1. 自动为每个客户选择提示词版本
2. 记录使用情况
3. 更新统计信息

### 4.3 缓存

缓存已自动集成，无需手动配置。系统会自动：
- 缓存对话历史（5分钟）
- 缓存客户信息（10分钟）
- 自动清理过期缓存

## 五、常见问题

### Q1: 迁移失败怎么办？

**A:** 检查：
1. 数据库连接是否正常
2. 是否有未完成的迁移
3. 数据库用户是否有足够权限

```bash
# 查看迁移状态
alembic current

# 查看迁移历史
alembic history
```

### Q2: API端点返回404？

**A:** 检查：
1. 路由是否正确注册（查看 `src/main.py`）
2. 服务是否正常启动
3. URL路径是否正确

### Q3: 模板变量不替换？

**A:** 确保：
1. 变量名使用 `{{variable_name}}` 格式
2. 传入的变量字典包含所有需要的变量
3. 变量名大小写匹配

### Q4: A/B测试不工作？

**A:** 检查：
1. 是否有启用的版本（`is_active=True`）
2. 版本是否已创建
3. 查看日志确认版本选择逻辑

## 六、性能监控

### 6.1 查看缓存效果

```python
from src.core.cache import conversation_cache, customer_cache

# 查看缓存统计
print(conversation_cache.get_stats())
print(customer_cache.get_stats())
```

### 6.2 查看数据库查询优化

使用数据库查询分析工具查看：
- 索引使用情况
- 查询执行时间
- 慢查询日志

### 6.3 监控API成本

定期查看：
```bash
curl "http://localhost:8000/api-usage/statistics?days=30&api_type=openai"
```

关注 `total_cost_usd` 字段，设置成本告警。

## 七、最佳实践

1. **模板管理**
   - 使用有意义的模板名称
   - 合理设置优先级
   - 定期审查和更新模板

2. **A/B测试**
   - 同时测试2-3个版本即可
   - 测试周期至少1周
   - 基于数据做决策

3. **缓存管理**
   - 定期清理过期缓存
   - 监控缓存命中率
   - 根据实际情况调整TTL

4. **性能优化**
   - 定期查看慢查询
   - 监控API响应时间
   - 优化高频查询

## 八、下一步

1. ✅ 运行数据库迁移
2. ✅ 测试所有API端点
3. ✅ 创建常用模板
4. ✅ 设置A/B测试版本
5. ✅ 监控系统性能
6. ✅ 根据数据优化配置

如有问题，请查看日志或联系开发团队。

