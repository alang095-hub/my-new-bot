# AI自动回复故障排除指南

## 📋 目录

- [问题诊断](#问题诊断)
- [常见问题](#常见问题)
- [解决方案](#解决方案)
- [验证步骤](#验证步骤)

---

## 问题诊断

### 1. 快速诊断工具

#### 检查Token配置
```bash
python scripts/tools/diagnose_page_token_mismatch.py
```

#### 检查API端点可用性（推荐）
```bash
python scripts/tools/diagnose_page_token_api.py
```

这个工具直接测试 `/conversations` 端点，比Token验证更准确。

### 2. 检查日志

查看最近的错误日志：
```bash
# Linux/macOS
grep "AI\|OpenAI\|auto_reply" logs/app.log | tail -n 50

# Windows PowerShell
Select-String -Path logs/app.log -Pattern "AI|OpenAI|auto_reply" | Select-Object -Last 50
```

### 3. 检查配置

验证OpenAI API Key：
```bash
python scripts/tools/verify_production_config.py
```

---

## 常见问题

### 问题1: AI不自动回复

**症状**：
- 收到消息但没有AI回复
- 日志中没有AI回复记录

**可能原因**：
1. OpenAI API Key未配置或无效
2. 消息被误判为垃圾信息
3. 页面自动回复被禁用
4. OpenAI API调用失败

**诊断步骤**：

1. **检查OpenAI配置**
   ```bash
   python scripts/tools/verify_production_config.py
   ```
   确认 `OPENAI_API_KEY` 已配置且不是占位符。

2. **检查页面设置**
   ```python
   from src.config.page_settings import page_settings
   page_id = "your_page_id"
   print(f"自动回复启用: {page_settings.is_auto_reply_enabled(page_id)}")
   ```

3. **检查消息是否被过滤**
   查看日志中是否有 "Skipping spam message" 或 "Detected spam" 的记录。

4. **测试AI回复生成**
   ```bash
   python scripts/tools/test_ai_reply_quick.py
   ```

### 问题2: Facebook 24小时消息发送窗口限制

**症状**：
```
Facebook API error: (#10) 这条消息是在消息发送时间窗以外发送的 (code: 10, subcode: 2018278)
或
超过24小时消息发送窗口限制（错误码2018278）
```

**原因**：
- Facebook Messenger Platform限制：用户必须在24小时内发送消息给页面
- 页面才能使用RESPONSE类型回复用户
- 如果超过24小时，页面只能使用消息标签（Message Tags）发送特定类型的消息

**解决方案**：

1. **这是正常限制，不是错误**
   - 系统会自动跳过这些消息
   - 不会计入错误统计
   - 日志中会显示警告而不是错误

2. **如果需要回复超过24小时的消息**：
   - 使用消息标签（Message Tags）
   - 可用的标签类型：
     - `CONFIRMED_EVENT_UPDATE` - 确认事件更新
     - `POST_PURCHASE_UPDATE` - 购买后更新
     - `ACCOUNT_UPDATE` - 账户更新
     - `HUMAN_AGENT` - 人工客服
   - 需要修改代码使用标签发送消息

3. **最佳实践**：
   - 在用户发送消息后尽快回复（5分钟内）
   - 对于超过24小时的消息，等待用户再次发送消息
   - 或使用消息标签发送重要通知

### 问题3: Facebook API Token不匹配错误

**症状**：
```
Facebook API 400 error for page XXX: (#10) Requested Page Does Not Match Page Access Token
```

**原因**：
- Token属于其他页面
- Token已过期
- Token权限不足

**解决方案**：

1. **运行诊断工具**
   ```bash
   python scripts/tools/diagnose_page_token_api.py
   ```

2. **如果Token不匹配**：
   - 访问 https://developers.facebook.com/tools/debug/accesstoken/
   - 输入Token检查其实际所属页面
   - 获取正确的页面Token
   - 更新 `.page_tokens.json` 文件

3. **如果Token过期**：
   - 获取新的长期Token
   - 运行：`python scripts/tools/convert_to_long_lived_token.py`

### 问题4: OpenAI API调用失败

**症状**：
```
OpenAI API error: ...
AI回复生成失败: ...
```

**可能原因**：
1. API Key无效或过期
2. API额度不足
3. 网络连接问题
4. API调用频率过高

**解决方案**：

1. **检查API Key**
   - 访问 https://platform.openai.com/api-keys
   - 确认Key有效且有额度

2. **检查网络连接**
   ```bash
   curl https://api.openai.com/v1/models
   ```

3. **查看详细错误日志**
   ```bash
   grep "OpenAI API error" logs/app.log | tail -n 20
   ```

### 问题5: 消息被误判为垃圾信息

**症状**：
- 有效消息没有收到回复
- 日志显示 "Skipping spam message"

**原因**：
- 垃圾信息检测过于严格
- 消息内容不符合业务关键词

**解决方案**：

1. **检查消息内容**
   查看日志中标记为垃圾信息的消息内容。

2. **调整垃圾信息检测规则**
   编辑 `src/ai/reply_generator.py` 中的 `_is_spam_or_invalid` 方法。

3. **添加业务关键词**
   在 `src/auto_reply/auto_reply_scheduler.py` 中的 `PRODUCT_KEYWORDS` 列表添加关键词。

---

## 解决方案

### 方案1: 修复Token不匹配

如果诊断工具显示Token不匹配：

1. **自动修复（如果Token被交换）**
   ```bash
   python scripts/tools/fix_page_token_mismatch.py
   ```

2. **手动修复**
   - 访问 https://developers.facebook.com/tools/debug/accesstoken/
   - 检查每个Token的实际所属页面
   - 更新 `.page_tokens.json` 文件

### 方案2: 重新配置OpenAI

如果OpenAI API调用失败：

1. **获取新的API Key**
   - 访问 https://platform.openai.com/api-keys
   - 创建新的API Key

2. **更新环境变量**
   ```bash
   # 编辑 .env 文件
   OPENAI_API_KEY=sk-your_new_api_key
   ```

3. **重启服务**
   ```bash
   # 重启服务使配置生效
   ```

### 方案3: 启用页面自动回复

如果页面自动回复被禁用：

1. **使用配置工具**
   ```bash
   python scripts/tools/manage_pages.py
   ```

2. **直接编辑配置文件**
   编辑 `config/config.yaml`，确保页面设置中 `auto_reply_enabled: true`

---

## 验证步骤

### 1. 验证配置

```bash
python scripts/tools/verify_production_config.py
```

确认所有必需配置都已正确设置。

### 2. 验证Token

```bash
python scripts/tools/diagnose_page_token_api.py
```

确认所有页面的API端点可用。

### 3. 测试AI回复

```bash
python scripts/tools/test_ai_reply_quick.py
```

测试AI回复生成功能。

### 4. 检查服务状态

```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 或查看日志
tail -f logs/app.log
```

### 5. 发送测试消息

在Facebook页面上发送测试消息，观察：
- 是否收到AI回复
- 日志中是否有错误
- 回复内容是否合理

---

## 监控和日志

### 查看实时日志

```bash
# Linux/macOS
tail -f logs/app.log

# Windows PowerShell
Get-Content logs/app.log -Wait -Tail 50
```

### 查看AI回复统计

```bash
grep "Auto-reply scan completed" logs/app.log | tail -n 10
```

### 查看错误日志

```bash
# Linux/macOS
grep ERROR logs/app.log | tail -n 50

# Windows PowerShell
Select-String -Path logs/app.log -Pattern "ERROR" | Select-Object -Last 50
```

---

## 预防措施

### 1. 定期检查Token

建议每周运行一次诊断工具：
```bash
python scripts/tools/diagnose_page_token_api.py
```

### 2. 监控OpenAI额度

定期检查OpenAI API使用情况：
- 访问 https://platform.openai.com/usage
- 设置使用限额警报

### 3. 备份配置

定期备份重要配置文件：
- `.env`
- `.page_tokens.json`
- `config/config.yaml`

### 4. 设置告警

配置Telegram通知，及时接收错误告警。

---

## 联系支持

如果问题仍然无法解决：

1. 收集以下信息：
   - 错误日志（最近50行）
   - 诊断工具输出
   - 配置文件（隐藏敏感信息）

2. 检查文档：
   - `docs/deployment/DEPLOYMENT_GUIDE.md`
   - `docs/troubleshooting/TOKEN_MISMATCH_FIX.md`

3. 查看GitHub Issues（如果有）

---

**最后更新**: 2025-12-13  
**版本**: 1.0.0

