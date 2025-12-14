# 部署前本地测试指南

## 概述

在部署到Zeabur生产环境之前，**强烈建议**在本地进行完整的真实环境测试，确保所有功能正常工作。

## 为什么需要本地测试？

1. **发现问题**：在本地发现问题比在生产环境发现问题更容易修复
2. **节省成本**：避免在生产环境反复部署和调试
3. **验证配置**：确保所有配置正确，特别是多页面Token配置
4. **功能验证**：确保自动回复、Webhook接收等功能正常

## 测试前准备

### 1. 环境配置

确保本地 `.env` 文件已配置所有必需的环境变量：

```bash
# 检查环境变量
python -c "from src.core.config import settings; print('配置加载成功')"
```

### 2. 数据库准备

```bash
# 运行数据库迁移
alembic upgrade head

# 验证数据库连接
python -c "from src.core.database.connection import engine; engine.connect(); print('数据库连接成功')"
```

### 3. 多页面Token配置（如果适用）

```bash
# 同步所有页面Token
python scripts/tools/manage_pages.py sync

# 查看配置的页面
python scripts/tools/manage_pages.py status
```

## 测试步骤

### 阶段1：基础功能测试

#### 1.1 服务启动测试

```bash
# 启动服务
python run.py
```

**检查项：**
- [ ] 服务正常启动，无错误
- [ ] 看到 "Starting Multi-Platform Customer Service Automation System..."
- [ ] 看到 "Auto-reply scheduler started"
- [ ] 看到 "Summary notification scheduler started"
- [ ] 无启动错误

#### 1.2 健康检查测试

```bash
# 在另一个终端运行
curl http://localhost:8000/health
```

**预期结果：**
- [ ] 返回状态码 200
- [ ] 返回JSON格式数据
- [ ] `status` 为 "healthy"
- [ ] 数据库连接正常

#### 1.3 API端点测试

```bash
# 测试各个端点
curl http://localhost:8000/
curl http://localhost:8000/metrics
curl http://localhost:8000/statistics/daily
```

**预期结果：**
- [ ] 所有端点返回200
- [ ] 返回正确的JSON数据

### 阶段2：多页面Token测试

#### 2.1 验证Token配置

```bash
# 查看已配置的页面
python scripts/tools/manage_pages.py status
```

**检查项：**
- [ ] 所有需要管理的页面都已配置Token
- [ ] 每个页面都有对应的Token
- [ ] 页面自动回复状态正确

#### 2.2 测试Token选择

向不同页面发送测试消息，检查日志确认使用了正确的Token：

```bash
# 查看日志
tail -f logs/app.log | grep "Token"
```

**预期结果：**
- [ ] 每个页面使用自己的Token
- [ ] 日志显示正确的页面ID和Token

### 阶段3：Webhook接收测试

#### 3.1 Facebook Webhook验证

1. 配置本地Webhook URL（使用ngrok等工具暴露本地服务）：
   ```
   https://your-ngrok-url.ngrok.io/webhook
   ```

2. 在Facebook Developer Console配置Webhook

3. 发送测试消息到Facebook页面

**检查项：**
- [ ] Webhook验证成功
- [ ] 消息接收成功
- [ ] 日志显示消息已接收

#### 3.2 消息处理测试

向每个页面发送测试消息：

**测试消息示例：**
- "我想了解iPhone贷款"
- "价格是多少？"
- "如何申请？"

**检查项：**
- [ ] 消息被正确接收
- [ ] 数据库记录创建
- [ ] AI回复生成
- [ ] 回复发送成功

### 阶段4：自动回复功能测试

#### 4.1 实时自动回复测试

1. 向Facebook页面发送包含产品关键词的消息
2. 等待AI回复（通常几秒内）

**检查项：**
- [ ] AI回复生成成功
- [ ] 回复内容符合业务规则
- [ ] 回复已发送到用户
- [ ] 数据库记录更新（`ai_replied = true`）

#### 4.2 自动扫描调度器测试

1. 创建一个未回复的消息（或等待5分钟）
2. 检查调度器是否运行

```bash
# 查看日志
tail -f logs/app.log | grep "auto-reply"
```

**检查项：**
- [ ] 调度器正常运行（每5分钟）
- [ ] 未回复消息被检测到
- [ ] 消息被自动回复
- [ ] 日志记录正确

### 阶段5：多页面功能测试

#### 5.1 向不同页面发送消息

向每个已配置的页面发送测试消息：

**测试步骤：**
1. 向页面1发送消息
2. 向页面2发送消息
3. 向页面3发送消息

**检查项：**
- [ ] 每个页面都能接收消息
- [ ] 每个页面都能自动回复
- [ ] 每个页面使用正确的Token
- [ ] 数据库正确记录页面信息

#### 5.2 页面隔离测试

确认不同页面的消息不会互相干扰：

**检查项：**
- [ ] 页面1的消息只回复到页面1
- [ ] 页面2的消息只回复到页面2
- [ ] 数据库记录正确的页面ID

### 阶段6：性能测试

#### 6.1 响应时间测试

```bash
# 运行性能测试
python scripts/test/production_test.py --test performance --url http://localhost:8000
```

**检查项：**
- [ ] 响应时间 < 500ms（健康检查）
- [ ] 响应时间 < 5s（AI回复生成）

#### 6.2 并发测试

```bash
# 运行并发测试
python scripts/test/load_test.py --users 10 --requests 5
```

**检查项：**
- [ ] 支持至少10个并发请求
- [ ] 无错误发生
- [ ] 所有请求成功

### 阶段7：完整流程测试

#### 7.1 端到端测试

测试完整的消息处理流程：

1. **发送消息** → 向Facebook页面发送消息
2. **接收消息** → 系统接收Webhook
3. **处理消息** → AI生成回复
4. **发送回复** → 回复发送到用户
5. **记录数据** → 数据库记录更新
6. **Telegram通知** → 通知发送（如果配置）

**检查项：**
- [ ] 所有步骤执行成功
- [ ] 数据一致性正确
- [ ] 无错误发生

## 测试检查清单

### 必须通过的测试（阻塞性问题）

- [ ] 服务可以正常启动
- [ ] 数据库连接正常
- [ ] 健康检查通过
- [ ] 所有API端点可访问
- [ ] Webhook接收正常
- [ ] AI自动回复功能正常
- [ ] 多页面Token配置正确
- [ ] 每个页面都能正常回复
- [ ] 数据库记录正确
- [ ] 无严重错误日志

### 建议通过的测试（非阻塞性）

- [ ] 性能指标正常
- [ ] 并发处理正常
- [ ] 自动扫描调度器正常
- [ ] Telegram通知正常
- [ ] 统计功能正常

## 运行完整测试

### 自动化测试

```bash
# 运行完整生产环境测试
python scripts/test/production_test.py --test all --url http://localhost:8000

# 运行负载测试
python scripts/test/load_test.py --users 20 --requests 10

# 运行性能监控（5分钟）
python scripts/monitoring/performance_monitor.py --duration 300
```

### 手动测试

按照上述阶段逐步测试，并记录结果。

## 测试结果记录

### 测试环境信息

- **测试日期：** ___________
- **测试人员：** ___________
- **测试环境：** 本地环境
- **Python版本：** ___________
- **数据库类型：** ___________

### 测试结果

**基础功能：**
- [ ] 通过
- [ ] 失败
- **备注：** ___________

**多页面功能：**
- [ ] 通过
- [ ] 失败
- **备注：** ___________

**Webhook功能：**
- [ ] 通过
- [ ] 失败
- **备注：** ___________

**自动回复功能：**
- [ ] 通过
- [ ] 失败
- **备注：** ___________

**性能测试：**
- [ ] 通过
- [ ] 失败
- **备注：** ___________

### 发现的问题

**问题1：**
- **描述：** ___________
- **严重程度：** ☐ 高  ☐ 中  ☐ 低
- **是否已修复：** ☐ 是  ☐ 否

**问题2：**
- **描述：** ___________
- **严重程度：** ☐ 高  ☐ 中  ☐ 低
- **是否已修复：** ☐ 是  ☐ 否

## 测试通过标准

### 可以部署的标准

- ✅ 所有必须通过的测试都通过
- ✅ 无阻塞性问题
- ✅ 多页面Token配置正确
- ✅ 所有页面都能正常自动回复
- ✅ 性能指标在可接受范围

### 需要修复后部署

- ❌ 存在阻塞性问题
- ❌ 多页面Token配置错误
- ❌ 自动回复功能异常
- ❌ 数据库连接问题

## 测试后行动

### 如果测试通过

1. **记录测试结果**
2. **备份配置**：备份 `.env`、`.page_tokens.json`、`config/config.yaml`
3. **准备部署**：按照Zeabur部署指南进行部署

### 如果测试失败

1. **记录问题**：详细记录所有问题
2. **修复问题**：优先修复阻塞性问题
3. **重新测试**：修复后重新运行测试
4. **确认通过**：所有测试通过后再部署

## 快速测试脚本

创建 `scripts/test/pre_deployment_test.sh` 和 `.bat` 用于快速测试：

```bash
# 运行快速测试
./scripts/test/pre_deployment_test.sh
```

## 相关文档

- [生产环境测试流程](../testing/PRODUCTION_TESTING_FLOW.md)
- [测试检查清单](../testing/PRODUCTION_TEST_CHECKLIST.md)
- [Zeabur部署指南](ZEABUR_DEPLOYMENT.md)
- [多页面配置指南](ZEABUR_MULTI_PAGE_SETUP.md)

