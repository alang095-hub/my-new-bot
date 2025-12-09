# 数据记录指南

## 📋 概述

本文档详细说明系统会记录哪些数据，以及这些数据的用途和存储位置。

## 🗄️ 数据库表结构

系统使用 PostgreSQL 数据库，包含以下主要数据表：

### 1. customers（客户信息表）

记录每个客户的基本信息：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | Integer | 客户唯一ID | 1 |
| `platform` | Enum | 平台类型 | facebook, instagram |
| `platform_user_id` | String | 平台用户ID | 1234567890 |
| `platform_metadata` | JSON | 平台特定数据 | `{"profile_url": "..."}` |
| `facebook_id` | String | Facebook ID（兼容字段） | 1234567890 |
| `name` | String | 客户姓名 | "John Doe" |
| `email` | String | 邮箱地址 | "john@example.com" |
| `phone` | String | 电话号码 | "+1234567890" |
| `company_name` | String | 公司名称 | "ABC Company" |
| `location` | String | 位置信息 | "Manila, Philippines" |
| `created_at` | DateTime | 创建时间 | 2024-01-01 10:00:00 |
| `updated_at` | DateTime | 更新时间 | 2024-01-01 10:00:00 |

**记录时机**：
- 首次收到来自该用户的消息时自动创建
- 从平台API获取用户信息后更新

**数据来源**：
- Facebook/Instagram API 返回的用户信息
- 从对话中提取的信息

---

### 2. conversations（对话记录表）

记录每条消息的详细信息：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | Integer | 对话唯一ID | 1 |
| `customer_id` | Integer | 关联的客户ID | 1 |
| `platform` | Enum | 平台类型 | facebook, instagram |
| `platform_message_id` | String | 平台消息ID | "mid.123456" |
| `facebook_message_id` | String | Facebook消息ID（兼容） | "mid.123456" |
| `message_type` | Enum | 消息类型 | message, comment, ad |
| `content` | Text | 消息内容 | "Hello, I want to borrow..." |
| `raw_data` | JSON | 原始平台数据 | `{"sender": {...}, "message": {...}}` |
| `ai_replied` | Boolean | 是否已AI回复 | true |
| `ai_reply_content` | Text | AI回复内容 | "To speed up the review..." |
| `ai_reply_at` | DateTime | AI回复时间 | 2024-01-01 10:01:00 |
| `is_processed` | Boolean | 是否已处理 | true |
| `priority` | Enum | 优先级 | low, medium, high, urgent |
| `filtered` | Boolean | 是否被过滤 | false |
| `filter_reason` | String | 过滤原因 | "spam keywords detected" |
| `received_at` | DateTime | 接收时间 | 2024-01-01 10:00:00 |
| `created_at` | DateTime | 创建时间 | 2024-01-01 10:00:00 |
| `updated_at` | DateTime | 更新时间 | 2024-01-01 10:00:00 |

**记录时机**：
- 每次收到消息时立即记录
- AI回复后更新 `ai_replied` 和 `ai_reply_content`
- 过滤后更新 `filtered` 和 `filter_reason`

**数据来源**：
- Webhook 接收的原始消息数据
- AI生成的回复内容
- 过滤引擎的分析结果

---

### 3. collected_data（收集的资料表）

记录从对话中提取的结构化数据：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | Integer | 数据唯一ID | 1 |
| `conversation_id` | Integer | 关联的对话ID | 1 |
| `data` | JSON | 收集的数据（JSON格式） | `{"name": "John", "phone": "+123", "inquiry_type": "购买"}` |
| `is_validated` | Boolean | 是否已验证 | true |
| `validation_errors` | JSON | 验证错误信息 | `["phone format invalid"]` |
| `created_at` | DateTime | 创建时间 | 2024-01-01 10:00:00 |
| `updated_at` | DateTime | 更新时间 | 2024-01-01 10:00:00 |

**收集的数据字段**（存储在 `data` JSON 中）：

#### 必需字段（根据配置）：
- `name` - 姓名
- `email` - 邮箱
- `phone` - 电话
- `inquiry_type` - 咨询类型（咨询、购买、投诉、合作）
- `message_content` - 消息内容

#### 可选字段（根据配置）：
- `budget` - 预算
- `timeline` - 时间线
- `location` - 位置
- `company_name` - 公司名称

**记录时机**：
- 每次处理消息时自动提取
- 使用正则表达式和关键词匹配提取信息

**提取规则**：
- 邮箱：匹配邮箱格式
- 电话：匹配电话号码格式
- 姓名：从消息中识别
- 其他：根据关键词匹配

---

### 4. reviews（审核记录表）

记录人工审核信息：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | Integer | 审核唯一ID | 1 |
| `customer_id` | Integer | 关联的客户ID | 1 |
| `conversation_id` | Integer | 关联的对话ID | 1 |
| `status` | Enum | 审核状态 | pending, approved, rejected, processing |
| `reviewed_by` | String | 审核人 | "admin_user" |
| `review_notes` | Text | 审核备注 | "客户信息完整，可以跟进" |
| `ai_assistance` | Boolean | 是否使用AI辅助 | true |
| `ai_suggestion` | Text | AI建议 | "建议优先处理" |
| `created_at` | DateTime | 创建时间 | 2024-01-01 10:00:00 |
| `reviewed_at` | DateTime | 审核时间 | 2024-01-01 10:05:00 |
| `updated_at` | DateTime | 更新时间 | 2024-01-01 10:05:00 |

**记录时机**：
- 需要人工审核的消息自动创建审核记录
- 通过Telegram Bot进行审核操作时更新

---

### 5. integration_logs（集成日志表）

记录与第三方系统（ManyChat/Botcake）的交互：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | Integer | 日志唯一ID | 1 |
| `integration_type` | String | 集成类型 | manychat, botcake |
| `action` | String | 操作类型 | sync, send, receive |
| `status` | String | 状态 | success, failed |
| `request_data` | JSON | 请求数据 | `{"user_id": "123", "message": "..."}` |
| `response_data` | JSON | 响应数据 | `{"status": "ok"}` |
| `error_message` | Text | 错误信息 | "Connection timeout" |
| `created_at` | DateTime | 创建时间 | 2024-01-01 10:00:00 |

**记录时机**：
- 每次与第三方系统交互时记录
- 成功和失败都会记录

---

## 📊 数据流程

### 消息处理流程中的数据记录

```
1. 接收消息
   ↓
   记录到 conversations 表
   - 消息内容
   - 原始数据（raw_data）
   - 消息类型
   - 平台信息
   
2. 获取用户信息
   ↓
   创建/更新 customers 表
   - 用户ID
   - 姓名
   - 平台信息
   
3. AI自动回复
   ↓
   更新 conversations 表
   - ai_replied = true
   - ai_reply_content
   - ai_reply_at
   
4. 资料收集
   ↓
   创建 collected_data 表
   - 提取的字段（JSON格式）
   - 验证状态
   
5. 过滤判断
   ↓
   更新 conversations 表
   - filtered
   - filter_reason
   - priority
   
6. 需要审核
   ↓
   创建 reviews 表
   - 审核状态
   - 审核人
   - 审核备注
```

---

## 🔍 具体记录的数据示例

### 示例1：Facebook私信

**输入**：
```
用户发送："Hello, I want to borrow 8000 PHP. My iPhone is 13 Pro. Phone: +639123456789"
```

**记录的数据**：

**customers 表**：
```json
{
  "platform": "facebook",
  "platform_user_id": "1234567890",
  "name": "John Doe",
  "phone": "+639123456789",
  "created_at": "2024-01-01 10:00:00"
}
```

**conversations 表**：
```json
{
  "platform": "facebook",
  "platform_message_id": "mid.123456",
  "message_type": "message",
  "content": "Hello, I want to borrow 8000 PHP. My iPhone is 13 Pro. Phone: +639123456789",
  "ai_replied": true,
  "ai_reply_content": "To speed up the review process, please join our official TG group first:\n👉 https://t.me/+Yz6RzEdD7JZjOGU1",
  "priority": "medium",
  "filtered": false
}
```

**collected_data 表**：
```json
{
  "data": {
    "phone": "+639123456789",
    "inquiry_type": "购买",
    "message_content": "Hello, I want to borrow 8000 PHP. My iPhone is 13 Pro. Phone: +639123456789",
    "loan_amount": "8000",
    "iphone_model": "iPhone 13 Pro"
  },
  "is_validated": true
}
```

---

## 🔒 数据安全与隐私

### 存储的数据类型

1. **公开信息**：
   - 用户在平台上公开的个人资料（姓名、头像等）
   - 用户主动发送的消息内容

2. **提取信息**：
   - 从消息中提取的联系方式（电话、邮箱）
   - 从对话中识别的需求信息

3. **系统信息**：
   - 消息ID、时间戳
   - 处理状态、优先级
   - AI回复内容

### 数据用途

- **客户服务**：提供更好的客户支持
- **业务分析**：分析客户需求和趋势
- **流程优化**：改进自动回复和过滤规则
- **审核管理**：人工审核和跟进

---

## 📝 配置数据收集

可以在 `config.yaml` 中配置需要收集的字段：

```yaml
data_collection:
  # 需要收集的字段
  required_fields:
    - name
    - email
    - phone
    - inquiry_type
    - message_content
  
  # 可选字段
  optional_fields:
    - budget
    - timeline
    - location
    - company_name
```

---

## 🔍 查看记录的数据

### 方法1：直接查询数据库

```sql
-- 查看所有客户
SELECT * FROM customers;

-- 查看所有对话
SELECT * FROM conversations;

-- 查看收集的数据
SELECT * FROM collected_data;

-- 查看审核记录
SELECT * FROM reviews;
```

### 方法2：使用系统API

访问 `http://localhost:8000/docs` 查看API文档，使用相应的API端点查询数据。

---

## ⚠️ 注意事项

1. **数据保留**：所有数据会永久保存在数据库中，除非手动删除
2. **数据备份**：建议定期备份数据库
3. **隐私保护**：确保遵守相关隐私法规
4. **数据访问**：只有授权用户可以访问数据库

---

## 📚 相关文件

- **数据库模型**：`src/database/models.py`
- **数据收集器**：`src/collector/data_collector.py`
- **对话管理器**：`src/ai/conversation_manager.py`
- **配置文件**：`config.yaml`




