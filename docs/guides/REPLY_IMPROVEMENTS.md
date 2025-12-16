# 回复系统改进说明

## 📋 改进内容

本次更新包含三个重要改进：

### 1. ✅ 强制所有系统回复使用英语

**改进内容**：
- 修改了系统提示词，强制AI使用英语回复，无论客户使用什么语言
- 更新了iPhone贷款业务的专用提示词，明确要求使用英语

**修改文件**：
- `src/ai/prompt_templates.py` - 默认提示词
- `src/ai/prompts/iphone_loan_telegram.py` - iPhone贷款专用提示词

**效果**：
- 所有AI生成的回复都是英语
- 保持专业和一致性
- 便于统一管理和审核

### 2. ✅ 每个页面支持系统自带的自动回复

**改进内容**：
- 为每个页面添加了系统默认回复功能
- 如果页面配置了`default_reply`，将优先使用系统默认回复，而不是AI生成
- 支持全局默认回复配置

**修改文件**：
- `src/config/page_settings.py` - 添加了`get_page_default_reply()`方法
- `src/business/services/auto_reply_service.py` - 优先检查页面默认回复
- `config/config.yaml.example` - 添加了配置示例

**配置方式**：

在`config/config.yaml`中配置：

```yaml
# 全局默认回复（可选）
auto_reply:
  default_reply: "Hello! Thanks for your message. How can I help you today?"

# 页面特定默认回复（优先级更高）
page_settings:
  "1234567890123456":  # Facebook页面ID
    auto_reply_enabled: true
    name: "我的业务页面"
    default_reply: "Hi! Welcome to our page. Please let us know how we can assist you."
```

**优先级**：
1. 页面配置的`default_reply`（最高优先级）
2. 全局配置的`auto_reply.default_reply`
3. AI生成的回复（如果没有配置默认回复）

### 3. ✅ 缩短AI回复长度

**改进内容**：
- 将`max_tokens`从45减少到30（约20-25个英文单词）
- 在提示词中强调保持简短和直接
- 确保回复更加简洁有力

**修改文件**：
- `src/ai/reply_generator.py` - 将`max_tokens`从45改为30
- `src/ai/prompt_templates.py` - 在提示词中强调简短回复
- `src/ai/prompts/iphone_loan_telegram.py` - 更新长度要求

**效果**：
- 回复更加简洁（20-25个英文单词）
- 减少API成本
- 提高回复速度
- 更符合客服场景需求

## 🔧 配置示例

### 完整配置示例

```yaml
# 自动回复配置
auto_reply:
  enabled: true
  default_language: "en"  # 必须使用英语
  response_delay_seconds: 2
  default_reply: "Hello! Thanks for your message. How can I help you today?"  # 全局默认回复

# 页面设置
page_settings:
  "732287003311432":  # 页面ID
    auto_reply_enabled: true
    name: "主业务页面"
    default_reply: "Hi! Welcome! Join our Telegram group: @your_group for faster service."
  
  "849418138246708":  # 另一个页面
    auto_reply_enabled: true
    name: "测试页面"
    default_reply: "Hello! How can I assist you today?"
```

## 📝 使用说明

### 1. 配置页面默认回复

**方法1：直接编辑配置文件**

编辑`config/config.yaml`，在`page_settings`下为每个页面添加`default_reply`：

```yaml
page_settings:
  "页面ID":
    auto_reply_enabled: true
    default_reply: "您的默认回复内容（必须是英语）"
```

**方法2：使用管理工具**

可以使用`scripts/tools/manage_pages.py`工具来管理页面配置。

### 2. 验证配置

配置后，系统会：
1. 首先检查页面是否有`default_reply`
2. 如果有，直接使用系统默认回复
3. 如果没有，使用AI生成回复（英语，20-25个单词）

### 3. 查看日志

在日志中可以看到：
- `使用页面 {page_id} 的系统默认回复` - 表示使用了系统默认回复
- `Generated reply for customer X` - 表示使用了AI生成回复

## ⚠️ 注意事项

1. **默认回复必须是英语**：所有系统默认回复必须使用英语，以保持一致性

2. **回复长度**：系统默认回复建议控制在20-25个英文单词以内

3. **优先级**：页面配置的`default_reply`优先级最高，会覆盖全局配置

4. **配置更新**：修改配置文件后，系统会自动读取新配置，无需重启服务

5. **AI回复长度**：AI生成的回复现在限制在20-25个英文单词，如果发现回复仍然过长，可以进一步调整`max_tokens`参数

## 🔍 故障排查

### 问题1：默认回复没有生效

**检查**：
1. 确认页面ID是否正确
2. 确认`default_reply`配置格式正确
3. 查看日志，确认是否读取了配置

**解决**：
```yaml
# 确保格式正确
page_settings:
  "页面ID":  # 页面ID必须是字符串
    default_reply: "Hello! How can I help?"  # 回复内容必须是字符串
```

### 问题2：AI回复仍然太长

**检查**：
1. 确认`max_tokens=30`已生效
2. 查看提示词是否包含长度限制

**解决**：
- 如果仍然太长，可以进一步减少`max_tokens`（例如改为25）
- 在提示词中更强调"SHORT"和"CONCISE"

### 问题3：回复不是英语

**检查**：
1. 确认提示词已更新
2. 确认配置文件中的`default_language`设置为"en"

**解决**：
- 检查`src/ai/prompt_templates.py`中的提示词
- 确保提示词中包含"MUST REPLY IN ENGLISH ONLY"

## 📚 相关文档

- [页面自动回复配置指南](PAGE_AUTO_REPLY_GUIDE.md)
- [AI回复配置](CONFIGURE_AI_REPLY.md)
- [配置文件说明](../config/config.yaml.example)

---

**更新日期**：2025-01-15
**版本**：v1.0

