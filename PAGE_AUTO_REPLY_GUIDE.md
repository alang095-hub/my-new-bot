# 页面自动回复配置指南

## 📋 概述

本系统支持为每个 Facebook 页面单独配置是否启用自动回复功能。您可以为不同的页面设置不同的自动回复策略。

## 🎯 配置方式

### 方式1：使用配置工具（推荐）

运行配置工具：

```bash
python configure_page_auto_reply.py
```

工具提供以下功能：
1. **列出所有已配置的页面** - 查看当前所有页面的配置
2. **添加/更新页面配置** - 为页面设置自动回复
3. **移除页面配置** - 删除页面的特定配置
4. **检查页面自动回复状态** - 查看某个页面的当前状态

### 方式2：手动编辑配置文件

编辑 `config.yaml` 文件，添加 `page_settings` 部分：

```yaml
# 页面设置
page_settings:
  "1234567890123456":  # Facebook页面ID
    auto_reply_enabled: true  # 启用自动回复
    name: "我的业务页面"  # 可选，页面名称
  "9876543210987654":  # 另一个页面ID
    auto_reply_enabled: false  # 禁用自动回复
    name: "测试页面"
```

## 📝 配置说明

### 全局设置 vs 页面设置

1. **全局设置** (`auto_reply.enabled`)
   - 控制所有页面的默认行为
   - 如果页面没有单独配置，则使用全局设置

2. **页面设置** (`page_settings`)
   - 为特定页面设置独立的自动回复策略
   - 优先级高于全局设置
   - 如果页面有单独配置，则使用页面配置

### 配置优先级

```
页面配置 > 全局配置
```

例如：
- 全局 `auto_reply.enabled: true`
- 页面A配置 `auto_reply_enabled: false`
- 页面B没有配置

结果：
- 页面A：**不自动回复**（使用页面配置）
- 页面B：**自动回复**（使用全局配置）

## 🔍 如何获取页面ID

### 方法1：从Webhook日志中获取

当收到消息时，日志中会显示 `page_id`：

```
页面ID: 1234567890123456
```

### 方法2：从Facebook开发者工具获取

1. 访问 [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. 使用您的访问令牌
3. 调用 `/me/accounts` 接口
4. 在返回结果中找到 `id` 字段，这就是页面ID

### 方法3：从页面URL获取

某些情况下，页面ID可能包含在页面的URL或设置中。

## 📖 使用示例

### 示例1：启用特定页面的自动回复

```yaml
auto_reply:
  enabled: false  # 全局禁用

page_settings:
  "1234567890123456":
    auto_reply_enabled: true  # 只对这个页面启用
    name: "主要业务页面"
```

### 示例2：禁用特定页面的自动回复

```yaml
auto_reply:
  enabled: true  # 全局启用

page_settings:
  "9876543210987654":
    auto_reply_enabled: false  # 只对这个页面禁用
    name: "测试页面"
```

### 示例3：多个页面不同配置

```yaml
auto_reply:
  enabled: true  # 默认启用

page_settings:
  "1111111111111111":
    auto_reply_enabled: true
    name: "销售页面"
  "2222222222222222":
    auto_reply_enabled: false
    name: "客服页面（人工处理）"
  "3333333333333333":
    auto_reply_enabled: true
    name: "营销页面"
```

## 🛠️ 配置工具使用说明

### 列出所有页面

```bash
python configure_page_auto_reply.py
# 选择 1
```

### 添加页面配置

```bash
python configure_page_auto_reply.py
# 选择 2
# 输入页面ID
# 输入页面名称（可选）
# 选择是否启用自动回复
```

### 检查页面状态

```bash
python configure_page_auto_reply.py
# 选择 4
# 输入页面ID（或留空查看全局设置）
```

## ⚙️ 工作原理

1. **接收消息** - 系统接收到来自某个页面的消息
2. **检查配置** - 系统检查该页面的自动回复配置
3. **决定是否回复**：
   - 如果页面有单独配置，使用页面配置
   - 如果页面没有配置，使用全局配置
   - 如果配置为禁用，跳过AI回复
4. **执行回复** - 如果启用，生成并发送AI回复

## 🔄 实时更新

配置更改后，系统会在下次处理消息时自动读取新配置。**无需重启服务**。

## ⚠️ 注意事项

1. **页面ID格式**：页面ID必须是字符串格式（用引号括起来）
2. **配置验证**：配置工具会自动验证配置格式
3. **备份配置**：修改前建议备份 `config.yaml` 文件
4. **测试建议**：先在测试页面上验证配置是否正确

## 📚 相关文档

- [配置文件说明](config.yaml.example)
- [自动回复配置](CONFIGURE_AI_REPLY.md)
- [系统使用指南](USAGE_GUIDE.md)

## ❓ 常见问题

### Q: 如何临时禁用某个页面的自动回复？

A: 使用配置工具将该页面的 `auto_reply_enabled` 设置为 `false`。

### Q: 配置后需要重启服务吗？

A: 不需要，系统会自动读取最新配置。

### Q: 如何查看所有页面的当前状态？

A: 运行配置工具，选择"检查页面自动回复状态"，留空页面ID即可查看所有页面。

### Q: 页面ID在哪里可以找到？

A: 可以从Webhook日志、Facebook Graph API或页面设置中获取。




