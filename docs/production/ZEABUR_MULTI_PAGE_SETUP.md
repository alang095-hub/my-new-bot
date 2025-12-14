# Zeabur 多页面自动回复配置指南

## 概述

当系统需要为多个Facebook页面提供自动回复时，每个页面都需要使用自己的Token。本指南说明如何在Zeabur上配置多页面Token。

## 重要说明

**对于多页面系统，`FACEBOOK_ACCESS_TOKEN` 环境变量的作用：**

1. **作为默认Token**：用于未配置特定Token的页面
2. **用于同步Token**：如果有用户级别Token，可以自动获取所有页面的Token
3. **作为备用Token**：如果找不到页面特定Token，会使用默认Token

## 配置方法

### 方法1：使用用户Token自动同步（推荐）

如果您有用户级别的Token（有 `pages_show_list` 权限），可以一次性同步所有页面的Token。

#### 步骤1：设置环境变量

在Zeabur控制台设置：

```
FACEBOOK_ACCESS_TOKEN=你的用户级别Token（有pages_show_list权限）
```

**注意：** 这个Token需要有以下权限：
- `pages_show_list` - 查看页面列表
- `pages_messaging` - 发送消息（可选，如果Token本身有权限）

#### 步骤2：部署后运行同步脚本

部署完成后，通过Zeabur的终端/SSH连接，运行：

```bash
# 同步所有页面的Token
python scripts/tools/manage_page_tokens.py sync
```

这会：
- 自动获取所有可管理的页面
- 获取每个页面的Token
- 保存到 `.page_tokens.json` 文件

#### 步骤3：验证配置

```bash
# 查看已配置的页面
python scripts/tools/manage_page_tokens.py list
```

### 方法2：手动配置每个页面的Token

如果无法使用自动同步，可以手动配置每个页面的Token。

#### 步骤1：准备Token信息

为每个页面准备：
- 页面ID（例如：`474610872412780`）
- 页面Token（长期Token，60天有效期）

#### 步骤2：在Zeabur上配置

**选项A：通过环境变量配置（不推荐，因为Token很多）**

如果只有2-3个页面，可以在Zeabur环境变量中设置：

```
FACEBOOK_ACCESS_TOKEN=默认Token（用于未配置的页面）

# 如果Zeabur支持，可以设置页面特定Token（需要代码支持）
FACEBOOK_PAGE_TOKEN_474610872412780=页面1的Token
FACEBOOK_PAGE_TOKEN_732287003311432=页面2的Token
FACEBOOK_PAGE_TOKEN_849418138246708=页面3的Token
```

**选项B：通过文件配置（推荐）**

1. 在本地创建 `.page_tokens.json` 文件：

```json
{
  "tokens": {
    "default": "EAAB...默认Token",
    "474610872412780": "EAAB...页面1的Token",
    "732287003311432": "EAAB...页面2的Token",
    "849418138246708": "EAAB...页面3的Token"
  },
  "page_info": {
    "474610872412780": {
      "name": "页面1名称",
      "updated_at": "2025-12-14"
    },
    "732287003311432": {
      "name": "页面2名称",
      "updated_at": "2025-12-14"
    },
    "849418138246708": {
      "name": "页面3名称",
      "updated_at": "2025-12-14"
    }
  }
}
```

2. 将文件添加到GitHub仓库（**注意：如果包含敏感信息，使用Zeabur的Secret管理**）

3. 或者通过Zeabur的文件上传功能上传

4. 或者通过SSH连接后手动创建文件

#### 步骤3：通过SSH手动添加Token

```bash
# 连接到Zeabur终端
# 运行管理脚本
python scripts/tools/manage_page_tokens.py add 474610872412780 EAAB... "页面1名称"
python scripts/tools/manage_page_tokens.py add 732287003311432 EAAB... "页面2名称"
python scripts/tools/manage_page_tokens.py add 849418138246708 EAAB... "页面3名称"
```

### 方法3：使用Zeabur的Secret管理（最佳实践）

对于生产环境，建议使用Zeabur的Secret管理功能：

1. **不要将Token提交到GitHub**
2. **使用Zeabur的环境变量或Secret功能**
3. **在部署后通过脚本配置**

## 环境变量配置示例

### 最小配置（使用默认Token）

如果所有页面使用同一个Token：

```
FACEBOOK_ACCESS_TOKEN=EAAB...你的Token
```

系统会自动使用这个Token作为所有页面的默认Token。

### 推荐配置（多页面）

```
# 默认Token（用于同步或备用）
FACEBOOK_ACCESS_TOKEN=EAAB...用户级别Token（有pages_show_list权限）

# 其他必需变量
FACEBOOK_APP_ID=你的App ID
FACEBOOK_APP_SECRET=你的App Secret
FACEBOOK_VERIFY_TOKEN=你的Verify Token
```

部署后运行同步脚本获取所有页面Token。

## 完整配置流程

### 1. 在Zeabur设置环境变量

```
FACEBOOK_ACCESS_TOKEN=你的用户Token（用于同步）
FACEBOOK_APP_ID=你的App ID
FACEBOOK_APP_SECRET=你的App Secret
FACEBOOK_VERIFY_TOKEN=你的Verify Token
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
SECRET_KEY=你的32字符密钥
DEBUG=false
CORS_ORIGINS=https://your-app-name.zeabur.app
```

### 2. 部署应用

等待Zeabur完成构建和部署。

### 3. 运行数据库迁移

```bash
alembic upgrade head
```

### 4. 同步页面Token

```bash
python scripts/tools/manage_page_tokens.py sync
```

### 5. 验证配置

```bash
# 查看已配置的页面
python scripts/tools/manage_page_tokens.py list

# 应该看到类似输出：
# 已配置的页面Token
# ======================================================================
# 
# 📄 默认Token: 已配置
# 
# 📋 已配置 3 个页面:
#   ✅ 页面1名称 (ID: 474610872412780)
#   ✅ 页面2名称 (ID: 732287003311432)
#   ✅ 页面3名称 (ID: 849418138246708)
```

### 6. 配置页面自动回复

编辑 `config/config.yaml` 或通过脚本配置：

```yaml
page_settings:
  "474610872412780":
    auto_reply_enabled: true
    name: "页面1"
  "732287003311432":
    auto_reply_enabled: true
    name: "页面2"
  "849418138246708":
    auto_reply_enabled: true
    name: "页面3"
```

## 工作原理

### Token选择流程

1. **接收消息** → 系统从Webhook事件中提取 `page_id`
2. **查找Token** → 在 `.page_tokens.json` 中查找该页面的Token
3. **使用Token** → 如果找到，使用页面Token；否则使用默认Token
4. **发送回复** → 使用找到的Token发送消息

### 自动回复检查

1. **检查全局设置** → `config.yaml` 中的 `auto_reply.enabled`
2. **检查页面设置** → `page_settings` 中该页面的 `auto_reply_enabled`
3. **决定是否回复** → 页面设置优先于全局设置

## 常见问题

### Q1: 我应该设置哪个Token作为 FACEBOOK_ACCESS_TOKEN？

**A:** 
- **推荐**：使用用户级别的Token（有 `pages_show_list` 权限），用于自动同步所有页面Token
- **备选**：使用其中一个页面的Token作为默认Token

### Q2: 如果只有2-3个页面，需要单独配置吗？

**A:** 
- 如果所有页面使用同一个Token，只需设置 `FACEBOOK_ACCESS_TOKEN`
- 如果每个页面有不同Token，建议使用同步功能或手动配置

### Q3: Token会过期吗？

**A:** 
- 页面Token通常有60天有效期
- 建议定期检查Token状态
- 使用长期Token（Long-lived Token）

### Q4: 如何在Zeabur上更新Token？

**A:** 
1. 通过SSH连接到容器
2. 运行同步脚本：`python scripts/tools/manage_page_tokens.py sync`
3. 或手动更新：`python scripts/tools/manage_page_tokens.py add <page_id> <new_token>`

### Q5: 如何查看当前配置的页面？

**A:** 
```bash
python scripts/tools/manage_page_tokens.py list
```

### Q6: 如何为特定页面禁用自动回复？

**A:** 
在 `config/config.yaml` 中配置：

```yaml
page_settings:
  "474610872412780":
    auto_reply_enabled: false  # 禁用这个页面的自动回复
```

## 最佳实践

1. **使用用户Token同步**：最方便，自动获取所有页面Token
2. **定期更新Token**：设置提醒，在Token过期前更新
3. **备份配置**：定期备份 `.page_tokens.json` 文件
4. **监控日志**：查看日志确认每个页面使用正确的Token
5. **测试验证**：部署后向每个页面发送测试消息，确认自动回复正常

## 相关文档

- [多页面Token管理指南](../guides/MULTI_PAGE_TOKEN_MANAGEMENT.md)
- [页面自动回复配置指南](../guides/PAGE_AUTO_REPLY_GUIDE.md)
- [Zeabur部署指南](ZEABUR_DEPLOYMENT.md)

