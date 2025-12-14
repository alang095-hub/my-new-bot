# 告警配置指南

## 概述

告警系统用于监控系统状态并在出现问题时及时通知管理员。本指南介绍如何配置和使用告警机制。

## 告警级别

系统支持以下告警级别：

- **CRITICAL（严重）**：系统无法正常工作，需要立即处理
- **WARNING（警告）**：系统性能下降或存在潜在问题
- **INFO（信息）**：一般信息通知

## 告警渠道

### 1. Telegram告警

通过Telegram Bot发送告警消息。

#### 配置步骤

1. 确保已配置Telegram Bot Token和Chat ID（在 `.env` 文件中）：
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

2. 告警会自动发送到配置的Telegram群组。

### 2. 日志告警

告警信息会记录到日志文件中。

#### 查看告警日志

```bash
# 查看所有告警
grep "ALERT" logs/app.log

# 查看严重告警
grep "CRITICAL" logs/app.log

# 实时监控告警
tail -f logs/app.log | grep "ALERT"
```

### 3. 自定义告警渠道

可以扩展告警系统以支持其他渠道（如邮件、Slack等）。

## 告警触发条件

### 自动告警

系统会在以下情况自动触发告警：

1. **数据库连接失败** - CRITICAL
2. **API配置错误** - CRITICAL
3. **系统资源使用过高** - WARNING
   - CPU使用率 > 80%
   - 内存使用率 > 85%
   - 磁盘使用率 > 90%
4. **响应时间过高** - WARNING
   - 平均响应时间 > 1000ms
5. **错误率过高** - WARNING
   - 错误率 > 5%

### 手动告警

可以通过代码手动触发告警：

```python
from src.monitoring.alerts import alert_manager, AlertLevel

# 发送警告
await alert_manager.send_alert(
    level=AlertLevel.WARNING,
    title="性能警告",
    message="响应时间超过阈值"
)

# 发送严重告警
await alert_manager.send_alert(
    level=AlertLevel.CRITICAL,
    title="系统错误",
    message="数据库连接失败"
)
```

## 告警配置

### 调整告警阈值

可以在 `src/monitoring/health.py` 中调整告警阈值：

```python
# 资源使用阈值
CPU_THRESHOLD = 80.0  # CPU使用率阈值（%）
MEMORY_THRESHOLD = 85.0  # 内存使用率阈值（%）
DISK_THRESHOLD = 90.0  # 磁盘使用率阈值（%）

# 性能阈值
RESPONSE_TIME_THRESHOLD = 1000  # 响应时间阈值（毫秒）
ERROR_RATE_THRESHOLD = 5.0  # 错误率阈值（%）
```

### 禁用特定告警

如果某个告警过于频繁，可以临时禁用它：

```python
# 在健康检查中注释掉相应的告警代码
# if cpu_percent > CPU_THRESHOLD:
#     await alert_manager.send_alert(...)
```

## 告警频率限制

为了避免告警风暴，系统实现了告警频率限制：

- 相同类型的告警在5分钟内最多发送一次
- 严重告警不受频率限制

## 监控和测试

### 测试告警系统

```python
# 测试脚本
python scripts/tools/test_alerts.py
```

### 查看告警历史

告警历史记录在日志文件中，可以使用以下命令查看：

```bash
# 查看最近24小时的告警
grep "ALERT" logs/app.log | tail -100

# 统计告警数量
grep "ALERT" logs/app.log | wc -l

# 按级别统计
grep "CRITICAL" logs/app.log | wc -l
grep "WARNING" logs/app.log | wc -l
```

## 最佳实践

1. **设置合理的阈值**：根据实际系统负载调整告警阈值
2. **定期审查告警**：定期检查告警日志，优化阈值设置
3. **及时响应**：严重告警应该立即处理
4. **告警分组**：对于频繁的告警，考虑分组或汇总
5. **告警文档**：为每个告警类型编写处理文档

## 告警处理流程

1. **接收告警**：通过Telegram或日志接收告警
2. **确认问题**：检查系统状态，确认问题存在
3. **评估影响**：评估问题对系统的影响
4. **处理问题**：根据告警类型采取相应措施
5. **验证修复**：确认问题已解决
6. **记录处理**：在日志中记录处理过程

## 常见告警处理

### CPU使用率过高

**可能原因：**
- 请求量过大
- 数据库查询慢
- 代码效率问题

**处理方法：**
1. 检查当前请求量
2. 优化慢查询
3. 增加服务器资源
4. 优化代码性能

### 内存使用率过高

**可能原因：**
- 内存泄漏
- 缓存过大
- 连接池过大

**处理方法：**
1. 检查内存使用情况
2. 查找内存泄漏
3. 调整缓存大小
4. 优化连接池配置

### 响应时间过高

**可能原因：**
- 数据库查询慢
- 外部API响应慢
- 服务器负载高

**处理方法：**
1. 检查慢查询日志
2. 优化数据库索引
3. 检查外部API状态
4. 增加服务器资源

### 错误率过高

**可能原因：**
- 代码bug
- 外部服务故障
- 配置错误

**处理方法：**
1. 查看错误日志
2. 检查外部服务状态
3. 验证配置正确性
4. 修复代码bug

## 相关文件

- `src/monitoring/alerts.py` - 告警管理器
- `src/monitoring/health.py` - 健康检查和告警触发
- `logs/app.log` - 告警日志

