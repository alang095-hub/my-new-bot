# 生产环境日志查看指南

## 📋 目录

- [日志文件位置](#日志文件位置)
- [基本查看命令](#基本查看命令)
- [实时监控日志](#实时监控日志)
- [日志分析](#日志分析)
- [不同部署方式的日志](#不同部署方式的日志)
- [日志轮转](#日志轮转)
- [常见日志查看场景](#常见日志查看场景)

---

## 日志文件位置

### 默认日志位置

项目日志文件位于 `logs/` 目录：

```
logs/
├── app.log              # 应用主日志（所有日志）
├── app.log.1            # 轮转备份1
├── app.log.2            # 轮转备份2
├── access.log           # 访问日志（如果使用Gunicorn）
└── error.log            # 错误日志（如果使用Gunicorn）
```

### 日志配置

日志配置在 `src/main.py` 中：
- **日志文件**: `logs/app.log`
- **最大文件大小**: 10MB
- **备份数量**: 10个
- **日志级别**: INFO（生产环境）

---

## 基本查看命令

### 1. 查看完整日志

**Linux/macOS:**
```bash
cat logs/app.log
```

**Windows PowerShell:**
```powershell
Get-Content logs/app.log
```

### 2. 查看最后N行

**Linux/macOS:**
```bash
tail -n 100 logs/app.log        # 最后100行
tail -n 50 logs/app.log         # 最后50行
```

**Windows PowerShell:**
```powershell
Get-Content logs/app.log -Tail 100
```

### 3. 查看前N行

**Linux/macOS:**
```bash
head -n 100 logs/app.log
```

**Windows PowerShell:**
```powershell
Get-Content logs/app.log -Head 100
```

### 4. 分页查看

**Linux/macOS:**
```bash
less logs/app.log               # 使用less分页器
more logs/app.log               # 使用more分页器
```

**Windows PowerShell:**
```powershell
Get-Content logs/app.log | more
```

---

## 实时监控日志

### 1. 实时跟踪日志（推荐）

**Linux/macOS:**
```bash
tail -f logs/app.log
```

**Windows PowerShell:**
```powershell
Get-Content logs/app.log -Wait -Tail 50
```

### 2. 实时跟踪并过滤

**Linux/macOS:**
```bash
# 只显示ERROR级别
tail -f logs/app.log | grep ERROR

# 只显示特定模块
tail -f logs/app.log | grep "auto_reply"

# 只显示Facebook相关
tail -f logs/app.log | grep "facebook"
```

**Windows PowerShell:**
```powershell
# 只显示ERROR级别
Get-Content logs/app.log -Wait -Tail 50 | Select-String "ERROR"

# 只显示特定模块
Get-Content logs/app.log -Wait -Tail 50 | Select-String "auto_reply"
```

### 3. 使用项目提供的工具

**Windows:**
```powershell
# 使用项目提供的日志查看脚本
.\scripts\tools\view_logs.ps1

# 或使用批处理文件
.\scripts\tools\quick_view_logs.bat
```

**Linux/macOS:**
```bash
# 刷新日志（清除并重新加载）
python scripts/tools/monitor_logs.py
```

---

## 日志分析

### 1. 查看错误日志

**Linux/macOS:**
```bash
grep ERROR logs/app.log
grep ERROR logs/app.log | tail -n 50    # 最近50个错误
```

**Windows PowerShell:**
```powershell
Select-String -Path logs/app.log -Pattern "ERROR"
```

### 2. 统计错误数量

**Linux/macOS:**
```bash
grep -c ERROR logs/app.log              # 错误总数
grep ERROR logs/app.log | wc -l         # 错误总数（另一种方式）
```

**Windows PowerShell:**
```powershell
(Select-String -Path logs/app.log -Pattern "ERROR").Count
```

### 3. 查看特定时间段的日志

**Linux/macOS:**
```bash
# 查看今天的日志
grep "$(date +%Y-%m-%d)" logs/app.log

# 查看特定日期的日志
grep "2025-12-13" logs/app.log

# 查看特定时间段的日志
grep "2025-12-13 20:" logs/app.log
```

**Windows PowerShell:**
```powershell
# 查看今天的日志
Get-Content logs/app.log | Select-String (Get-Date -Format "yyyy-MM-dd")

# 查看特定日期的日志
Get-Content logs/app.log | Select-String "2025-12-13"
```

### 4. 查看特定模块的日志

**Linux/macOS:**
```bash
# 查看自动回复调度器日志
grep "auto_reply" logs/app.log

# 查看Facebook API日志
grep "facebook.api_client" logs/app.log

# 查看AI回复生成器日志
grep "reply_generator" logs/app.log
```

**Windows PowerShell:**
```powershell
Select-String -Path logs/app.log -Pattern "auto_reply"
Select-String -Path logs/app.log -Pattern "facebook.api_client"
```

### 5. 查看特定关键词

**Linux/macOS:**
```bash
# 查看Token相关日志
grep -i "token" logs/app.log

# 查看Webhook相关日志
grep -i "webhook" logs/app.log

# 查看消息处理日志
grep -i "message" logs/app.log
```

**Windows PowerShell:**
```powershell
Select-String -Path logs/app.log -Pattern "token" -CaseSensitive:$false
Select-String -Path logs/app.log -Pattern "webhook" -CaseSensitive:$false
```

### 6. 统计不同类型的日志

**Linux/macOS:**
```bash
# 统计各日志级别
grep -c "ERROR" logs/app.log
grep -c "WARNING" logs/app.log
grep -c "INFO" logs/app.log
grep -c "DEBUG" logs/app.log

# 统计各模块日志
grep -o "src\.[a-z_]*" logs/app.log | sort | uniq -c | sort -rn
```

**Windows PowerShell:**
```powershell
# 统计各日志级别
(Select-String -Path logs/app.log -Pattern "ERROR").Count
(Select-String -Path logs/app.log -Pattern "WARNING").Count
(Select-String -Path logs/app.log -Pattern "INFO").Count
```

---

## 不同部署方式的日志

### 1. 直接运行（python run.py）

日志位置：
- `logs/app.log`

查看方式：
```bash
tail -f logs/app.log
```

### 2. 使用Gunicorn

日志位置：
- `logs/access.log` - 访问日志
- `logs/error.log` - 错误日志
- `logs/app.log` - 应用日志（如果配置了）

查看方式：
```bash
# 访问日志
tail -f logs/access.log

# 错误日志
tail -f logs/error.log

# 应用日志
tail -f logs/app.log
```

### 3. 使用Systemd服务

日志位置：
- `logs/app.log` - 应用日志
- Systemd日志: `journalctl`

查看方式：
```bash
# 应用日志
tail -f logs/app.log

# Systemd日志
sudo journalctl -u facebook-customer-service -f

# 查看最近100行
sudo journalctl -u facebook-customer-service -n 100

# 查看今天的日志
sudo journalctl -u facebook-customer-service --since today
```

### 4. 使用Docker

日志位置：
- Docker容器日志

查看方式：
```bash
# 实时查看容器日志
docker logs -f facebook-customer-service

# 查看最近100行
docker logs --tail 100 facebook-customer-service

# 查看特定时间段的日志
docker logs --since "2025-12-13T20:00:00" facebook-customer-service
```

---

## 日志轮转

### 自动轮转

系统配置了自动日志轮转：
- **最大文件大小**: 10MB
- **备份数量**: 10个
- **轮转后**: 自动创建新文件

轮转后的文件命名：
```
logs/app.log          # 当前日志
logs/app.log.1        # 第1个备份（最新的备份）
logs/app.log.2        # 第2个备份
...
logs/app.log.10       # 第10个备份（最旧的备份）
```

### 手动清理旧日志

**Linux/macOS:**
```bash
# 删除所有备份，只保留当前日志
rm logs/app.log.*

# 删除7天前的备份
find logs/ -name "app.log.*" -mtime +7 -delete
```

**Windows PowerShell:**
```powershell
# 删除所有备份
Remove-Item logs/app.log.*

# 删除7天前的备份
Get-ChildItem logs/app.log.* | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item
```

---

## 常见日志查看场景

### 1. 检查服务是否正常运行

```bash
# 查看最近的日志
tail -n 50 logs/app.log

# 检查是否有错误
grep ERROR logs/app.log | tail -n 20
```

### 2. 调试消息处理问题

```bash
# 查看消息接收日志
grep "Received webhook" logs/app.log | tail -n 20

# 查看消息处理日志
grep "Processing message" logs/app.log | tail -n 20

# 查看AI回复日志
grep "AI reply" logs/app.log | tail -n 20
```

### 3. 检查自动回复调度器

```bash
# 查看扫描日志
grep "Scanning.*pages" logs/app.log | tail -n 20

# 查看回复统计
grep "Auto-reply scan completed" logs/app.log | tail -n 20
```

### 4. 检查Facebook API问题

```bash
# 查看API错误
grep "Facebook API.*error" logs/app.log | tail -n 20

# 查看Token问题
grep "Token" logs/app.log | tail -n 20

# 查看400错误
grep "400 error" logs/app.log | tail -n 20
```

### 5. 检查数据库问题

```bash
# 查看数据库错误
grep -i "database\|sql\|connection" logs/app.log | tail -n 20
```

### 6. 性能监控

```bash
# 查看响应时间
grep "took.*ms\|took.*seconds" logs/app.log

# 查看慢查询
grep "slow\|timeout" logs/app.log
```

### 7. 查看特定客户的对话

```bash
# 查看特定客户ID的日志
grep "customer_id.*123" logs/app.log

# 查看特定页面的日志
grep "page.*474610872412780" logs/app.log
```

---

## 高级日志分析

### 1. 使用awk分析日志

**Linux/macOS:**
```bash
# 统计每小时的消息数
awk '/INFO.*Received webhook/ {print $1, $2}' logs/app.log | cut -d: -f1 | uniq -c

# 统计错误类型
grep ERROR logs/app.log | awk '{print $NF}' | sort | uniq -c | sort -rn
```

### 2. 导出日志到文件

```bash
# 导出错误日志
grep ERROR logs/app.log > errors_$(date +%Y%m%d).txt

# 导出特定时间段的日志
grep "2025-12-13 20:" logs/app.log > logs_2025-12-13_20h.txt
```

### 3. 使用项目提供的监控工具

```bash
# 监控AI回复
python scripts/tools/monitor_ai_reply.ps1  # Windows
bash scripts/tools/monitor_ai_reply.sh     # Linux/macOS

# 监控完整工作流
python scripts/tools/monitor_full_workflow.ps1  # Windows
```

---

## 日志格式说明

### 标准日志格式

```
YYYY-MM-DD HH:MM:SS - module.name - LEVEL - message
```

示例：
```
2025-12-13 20:30:45 - src.auto_reply.auto_reply_scheduler - INFO - Auto-reply scan completed: scanned 3 pages, found 0 unreplied messages, replied to 0, errors: 0
```

### 日志级别

- **DEBUG**: 调试信息（开发环境）
- **INFO**: 一般信息（正常运行）
- **WARNING**: 警告信息（需要注意但不影响运行）
- **ERROR**: 错误信息（需要处理）
- **CRITICAL**: 严重错误（系统可能无法继续运行）

---

## 快速参考

### 最常用的命令

```bash
# 实时查看日志
tail -f logs/app.log

# 查看最近100行
tail -n 100 logs/app.log

# 查看错误
grep ERROR logs/app.log | tail -n 50

# 查看特定模块
grep "auto_reply" logs/app.log | tail -n 50
```

### Windows PowerShell快速命令

```powershell
# 实时查看日志
Get-Content logs/app.log -Wait -Tail 50

# 查看错误
Select-String -Path logs/app.log -Pattern "ERROR" | Select-Object -Last 50

# 查看特定模块
Select-String -Path logs/app.log -Pattern "auto_reply" | Select-Object -Last 50
```

---

## 故障排除

### 问题：日志文件不存在

**原因**: 服务未启动或日志目录未创建

**解决**:
```bash
# 检查日志目录
ls -la logs/

# 如果不存在，创建目录
mkdir -p logs

# 检查服务是否运行
ps aux | grep "python.*run.py"
```

### 问题：日志文件太大

**原因**: 日志轮转未正常工作

**解决**:
```bash
# 手动清理旧日志
rm logs/app.log.*

# 或压缩旧日志
gzip logs/app.log.*
```

### 问题：无法实时查看日志

**原因**: 权限问题或文件被锁定

**解决**:
```bash
# 检查文件权限
ls -la logs/app.log

# 检查文件是否被锁定
lsof logs/app.log  # Linux/macOS
```

---

**最后更新**: 2025-12-13  
**版本**: 2.0.0


