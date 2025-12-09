# 统计数据使用指南

## 📋 概述

系统已优化为**不保存详细聊天记录**，只保存关键统计数据和消息摘要。所有统计数据准确可查。

## 🎯 核心功能

### 1. 不保存详细聊天记录
- ✅ 只保存消息摘要（最多500字符）
- ✅ 不保存完整对话内容
- ✅ 不保存原始数据（raw_data）
- ✅ 只保存提取的关键信息

### 2. 每日统计（自动计算）
- ✅ **总接待客户数** - 每天接待了多少客户
- ✅ **总消息数** - 每天收到多少消息
- ✅ **发送群组邀请数** - 发送了多少群组邀请
- ✅ **成功引流数** - 多少客户加入了群组
- ✅ **引流转化率** - 邀请到加入的转化率
- ✅ **总开单数** - 每天开单数量
- ✅ **成功开单数** - 成功完成的订单数
- ✅ **开单转化率** - 引流到开单的转化率

### 3. 高频问题收集
- ✅ 自动识别和分类问题
- ✅ 统计问题出现频率
- ✅ 保存示例回复
- ✅ 支持按分类查看

## 📊 查看统计数据

### 方法1：使用命令行工具（推荐）

```bash
python view_statistics.py
```

功能：
- 查看今日统计
- 查看指定日期统计
- 查看最近7天统计
- 查看高频问题

### 方法2：使用API接口

#### 查看今日统计
```bash
curl http://localhost:8000/statistics/daily
```

#### 查看指定日期统计
```bash
curl http://localhost:8000/statistics/daily?target_date=2024-01-01
```

#### 查看高频问题
```bash
curl http://localhost:8000/statistics/frequent-questions?limit=20
```

#### 查看统计摘要（多日汇总）
```bash
curl http://localhost:8000/statistics/summary?start_date=2024-01-01&end_date=2024-01-07
```

#### 标记客户已加入群组
```bash
curl -X POST "http://localhost:8000/statistics/mark-joined-group?customer_id=123"
```

#### 标记客户已开单
```bash
curl -X POST "http://localhost:8000/statistics/mark-order-created?customer_id=123"
```

### 方法3：访问API文档

访问 `http://localhost:8000/docs`，查看完整的API文档和交互式测试界面。

## 📝 统计数据说明

### 每日统计字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `total_customers` | 总接待客户数 | 50 |
| `total_messages` | 总消息数 | 120 |
| `group_invitations_sent` | 发送的群组邀请数 | 100 |
| `successful_leads` | 成功引流数 | 30 |
| `lead_conversion_rate` | 引流转化率 | "30.0%" |
| `total_orders` | 总开单数 | 15 |
| `successful_orders` | 成功开单数 | 12 |
| `order_conversion_rate` | 开单转化率 | "40.0%" |

### 客户交互记录

每条交互记录包含：
- 消息摘要（最多500字符）
- 提取的关键信息（姓名、电话、需求等）
- 是否AI回复
- 是否发送群组邀请
- 是否加入群组（需手动标记）
- 是否开单（需手动标记）

**不包含**：
- ❌ 完整聊天记录
- ❌ 原始平台数据
- ❌ 详细对话历史

## 🔧 手动标记操作

### 标记客户已加入群组

当您在Telegram群组中确认客户已加入时，可以手动标记：

**方法1：使用API**
```bash
curl -X POST "http://localhost:8000/statistics/mark-joined-group?customer_id=123"
```

**方法2：使用数据库**
```sql
UPDATE customer_interactions 
SET joined_group = true 
WHERE customer_id = 123 AND date = CURRENT_DATE;
```

### 标记客户已开单

当确认客户已成功开单时：

**方法1：使用API**
```bash
curl -X POST "http://localhost:8000/statistics/mark-order-created?customer_id=123"
```

**方法2：使用数据库**
```sql
UPDATE customer_interactions 
SET order_created = true 
WHERE customer_id = 123 AND date = CURRENT_DATE;
```

## 📈 高频问题

系统会自动收集和分类高频问题：

### 问题分类
- **价格咨询** - 包含"价格"、"多少钱"等关键词
- **利息咨询** - 包含"利息"、"利率"等关键词
- **流程咨询** - 包含"怎么"、"如何"等关键词
- **产品咨询** - 包含"型号"、"iPhone"等关键词

### 查看高频问题

```bash
python view_statistics.py
# 选择 4
```

或使用API：
```bash
curl http://localhost:8000/statistics/frequent-questions?limit=20
```

## 🗄️ 数据库表结构

### daily_statistics（每日统计表）
存储每天的统计数据，自动计算和更新。

### customer_interactions（客户交互表）
存储客户交互记录（不包含详细聊天内容）。

### frequent_questions（高频问题表）
存储高频问题及其出现次数。

## 🔄 数据更新

统计数据会在以下情况自动更新：
1. 收到新消息时
2. 发送AI回复时
3. 标记客户加入群组时
4. 标记客户开单时

## ⚙️ 数据库迁移

首次使用需要运行数据库迁移：

```bash
alembic upgrade head
```

这会创建以下新表：
- `daily_statistics`
- `customer_interactions`
- `frequent_questions`

## 📊 示例输出

### 今日统计示例

```
📊 2024-01-15 统计数据
============================================================

👥 接待统计:
  总接待客户数: 50
  新客户数: 30
  回头客数: 20

💬 消息统计:
  总消息数: 120

📢 引流统计:
  发送群组邀请: 100
  成功引流数: 30
  引流转化率: 30.0%

💰 开单统计:
  总开单数: 15
  成功开单数: 12
  开单转化率: 40.0%

❓ 高频问题:
  - 价格是多少: 25次
  - 利息怎么算: 18次
  - 怎么申请: 15次
```

## 🎯 关键指标

### 引流转化率
```
引流转化率 = (成功引流数 / 发送群组邀请数) × 100%
```

### 开单转化率
```
开单转化率 = (成功开单数 / 成功引流数) × 100%
```

## 📚 相关文件

- **统计追踪器**: `src/statistics/tracker.py`
- **统计API**: `src/statistics/api.py`
- **统计模型**: `src/database/statistics_models.py`
- **查看工具**: `view_statistics.py`
- **数据库迁移**: `alembic/versions/003_add_statistics_tables.py`

## ⚠️ 注意事项

1. **手动标记**：客户加入群组和开单需要手动标记
2. **数据准确性**：统计数据基于实际交互记录，确保准确
3. **数据保留**：统计数据会永久保存，便于长期分析
4. **隐私保护**：不保存详细聊天记录，只保存摘要和关键信息




