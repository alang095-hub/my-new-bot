# 修复cost_usd字段长度错误

## ❌ 错误信息

```
sqlalchemy.exc.DataError: (psycopg2.errors.StringDataRightTruncation) 
value too long for type character varying(20)
```

## 🔍 问题原因

**`cost_usd` 字段长度不足**

- 数据库字段定义：`VARCHAR(20)`（20个字符）
- 实际值：`'5.8124999999999997e-05'`（23个字符）
- 当成本值很小时，Python使用科学计数法，字符串长度超过20

## ✅ 修复方案

### 1. 修改数据库模型

**文件**：`src/core/database/models.py`

**修改**：
```python
# 从
cost_usd = Column(String(20))

# 改为
cost_usd = Column(String(50))
```

### 2. 修改保存逻辑

**文件**：`src/monitoring/api_usage_tracker.py`

**修改**：
```python
# 从
cost_usd=str(record.cost_usd) if record.cost_usd else None,

# 改为
cost_usd=f"{record.cost_usd:.10f}" if record.cost_usd else None,
```

**说明**：使用固定格式（`.10f`），避免科学计数法

### 3. 创建数据库迁移

**文件**：`alembic/versions/010_fix_cost_usd_field_length.py`

**内容**：修改字段长度从20到50

## 🚀 部署修复

### 在Zeabur执行迁移

1. **进入Zeabur控制台**
   - 点击应用服务
   - 点击 "Terminal"（终端）

2. **运行迁移**
   ```bash
   alembic upgrade head
   ```

3. **验证修复**
   - 查看日志，确认不再有StringDataRightTruncation错误
   - 测试API调用，确认成本记录正常

## 📋 修复内容

### 代码修改

1. ✅ **模型定义** - `cost_usd` 字段长度从20增加到50
2. ✅ **保存逻辑** - 使用固定格式，避免科学计数法
3. ✅ **数据库迁移** - 创建迁移文件修改字段长度

### 预期效果

- ✅ 不再出现StringDataRightTruncation错误
- ✅ 成本值正确保存（使用固定格式）
- ✅ API使用日志正常记录

## 🆘 如果迁移失败

### 方法1：手动修改数据库

在Zeabur PostgreSQL终端执行：
```sql
ALTER TABLE api_usage_logs 
ALTER COLUMN cost_usd TYPE VARCHAR(50);
```

### 方法2：检查迁移文件

确认迁移文件存在：
- `alembic/versions/010_fix_cost_usd_field_length.py`

## ✅ 验证修复

修复后，检查日志：
- 不再有 `StringDataRightTruncation` 错误
- API使用日志正常记录
- 成本值正确保存

---

**修复完成**：代码已修改，需要运行数据库迁移！🚀

