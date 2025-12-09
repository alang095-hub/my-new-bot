# Instagram 平台接入指南

## 概述

系统已成功接入Instagram平台，采用模块化架构设计，支持多平台扩展。

## 架构特点

- **模块化设计**：每个平台独立实现，易于维护和扩展
- **统一接口**：所有平台实现相同的抽象接口
- **向后兼容**：保留原有Facebook功能，不影响现有系统
- **易于扩展**：新平台只需实现三个接口类并注册即可

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置（可选，如果未设置则使用Facebook的配置）：

```env
# Instagram配置（可选）
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_VERIFY_TOKEN=your_instagram_verify_token
INSTAGRAM_USER_ID=your_instagram_user_id
```

**注意**：
- 如果未设置 `INSTAGRAM_ACCESS_TOKEN`，系统将使用 `FACEBOOK_ACCESS_TOKEN`
- 如果未设置 `INSTAGRAM_VERIFY_TOKEN`，系统将使用 `FACEBOOK_VERIFY_TOKEN`
- `INSTAGRAM_USER_ID` 是必需的，用于发送Instagram消息

## Webhook配置

### Instagram Webhook URL

```
https://your-domain.com/instagram/webhook
```

### 订阅事件

在Facebook Developer Console中配置Instagram Webhook时，需要订阅以下事件：
- `messages` - Instagram私信

### 验证令牌

使用配置的 `INSTAGRAM_VERIFY_TOKEN` 或 `FACEBOOK_VERIFY_TOKEN`

## 数据库迁移

运行以下命令进行数据库迁移：

```bash
alembic upgrade head
```

这将：
1. 添加 `Platform` 枚举类型
2. 在 `customers` 表中添加平台相关字段
3. 在 `conversations` 表中添加平台相关字段
4. 将现有数据标记为 `facebook` 平台

## 功能支持

### 已支持的功能

- ✅ Instagram私信接收
- ✅ Instagram私信自动回复
- ✅ 资料自动收集
- ✅ 智能过滤
- ✅ Telegram通知
- ✅ 人工审核

### 暂不支持的功能

- ❌ Instagram评论（Instagram API限制）
- ❌ Instagram广告（需要额外配置）

## API端点

### Webhook验证
```
GET /instagram/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=CHALLENGE
```

### Webhook接收
```
POST /instagram/webhook
```

## 测试

### 1. 检查平台注册

访问根路径查看已注册的平台：
```
GET /
```

响应示例：
```json
{
  "message": "多平台客服自动化系统",
  "version": "2.0.0",
  "status": "running",
  "supported_platforms": ["facebook", "instagram"]
}
```

### 2. 测试Webhook验证

使用curl测试：
```bash
curl "http://localhost:8000/instagram/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test123"
```

### 3. 发送测试消息

通过Instagram发送私信到您的Instagram Business账户，系统应该能够：
1. 接收消息
2. 自动回复
3. 保存到数据库
4. 发送Telegram通知（如果需要审核）

## 故障排除

### 问题1：Instagram消息未接收

**检查项**：
1. Instagram Webhook是否已正确配置
2. Webhook URL是否可访问
3. 验证令牌是否正确
4. Instagram Business账户是否已连接Facebook页面

### 问题2：无法发送Instagram消息

**检查项**：
1. `INSTAGRAM_USER_ID` 是否已配置
2. Instagram访问令牌是否有效
3. 是否具有 `instagram_manage_messages` 权限

### 问题3：数据库迁移失败

**解决方案**：
1. 检查数据库连接
2. 确保PostgreSQL版本 >= 12
3. 查看Alembic日志获取详细错误信息

## 后续扩展

系统架构支持后续轻松接入其他平台：

1. **Twitter/X**：实现 `TwitterAPIClient`, `TwitterMessageParser`, `TwitterWebhookHandler`
2. **LinkedIn**：实现 `LinkedInAPIClient`, `LinkedInMessageParser`, `LinkedInWebhookHandler`
3. **WhatsApp Business**：实现 `WhatsAppAPIClient`, `WhatsAppMessageParser`, `WhatsAppWebhookHandler`

每个新平台只需：
1. 实现三个接口类
2. 创建注册文件
3. 在主应用中导入注册模块
4. 完成！

## 相关文件

- `src/platforms/` - 平台抽象层
- `src/instagram/` - Instagram平台实现
- `src/facebook/` - Facebook平台实现（已重构）
- `src/main_processor.py` - 统一消息处理器
- `alembic/versions/002_add_platform_support.py` - 数据库迁移文件

## 技术支持

如有问题，请检查：
1. 日志文件中的错误信息
2. Facebook Developer Console中的配置
3. 数据库迁移状态







