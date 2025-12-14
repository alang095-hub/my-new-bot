# 生产环境改进快速开始

## 快速配置指南

### 1. 配置CORS（5分钟）

在 `.env` 文件中添加：

```bash
# 替换为您的实际域名
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

重启服务后生效。

### 2. 运行性能监控（立即）

```bash
# 持续监控（60秒间隔）
python scripts/monitoring/performance_monitor.py

# 监控5分钟后停止
python scripts/monitoring/performance_monitor.py --duration 300
```

### 3. 运行负载测试（5分钟）

```bash
# 基本测试
python scripts/test/load_test.py

# 高强度测试（50并发用户）
python scripts/test/load_test.py --users 50 --requests 20
```

### 4. 迁移到PostgreSQL（30分钟）

参考：[PostgreSQL迁移指南](POSTGRESQL_MIGRATION.md)

```bash
# 1. 安装PostgreSQL
# 2. 创建数据库
# 3. 更新 .env 中的 DATABASE_URL
# 4. 运行迁移
alembic upgrade head
```

## 所有改进文档

- [CORS配置指南](CORS_CONFIGURATION.md)
- [PostgreSQL迁移指南](POSTGRESQL_MIGRATION.md)
- [告警配置指南](ALERT_CONFIGURATION.md)
- [改进总结](IMPROVEMENTS_SUMMARY.md)

## 测试验证

```bash
# 运行完整测试
python scripts/test/production_test.py --test all

# 查看测试报告
ls data/test_reports/
```

