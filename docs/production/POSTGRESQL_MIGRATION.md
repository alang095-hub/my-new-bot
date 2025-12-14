# PostgreSQL迁移指南

## 概述

本指南将帮助您从SQLite迁移到PostgreSQL数据库，以获得更好的生产环境性能和并发处理能力。

## 为什么使用PostgreSQL？

1. **更好的并发性能**：PostgreSQL支持真正的并发读写
2. **更好的数据完整性**：更强的约束和事务支持
3. **更好的扩展性**：支持更大的数据集和更复杂的查询
4. **生产环境标准**：大多数生产环境使用PostgreSQL或类似数据库

## 迁移步骤

### 1. 安装PostgreSQL

#### Windows
下载并安装：https://www.postgresql.org/download/windows/

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS
```bash
brew install postgresql
```

### 2. 创建数据库

```bash
# 登录PostgreSQL
sudo -u postgres psql

# 创建数据库
CREATE DATABASE customer_service;

# 创建用户
CREATE USER service_user WITH PASSWORD 'your_secure_password';

# 授权
GRANT ALL PRIVILEGES ON DATABASE customer_service TO service_user;

# 退出
\q
```

### 3. 安装Python依赖

确保已安装PostgreSQL适配器：

```bash
pip install psycopg2-binary
# 或
pip install psycopg2
```

### 4. 更新环境变量

在 `.env` 文件中更新 `DATABASE_URL`：

```bash
# 从SQLite
DATABASE_URL=sqlite:///facebook_customer_service.db

# 改为PostgreSQL
DATABASE_URL=postgresql://service_user:your_secure_password@localhost:5432/customer_service
```

**格式说明：**
```
postgresql://用户名:密码@主机:端口/数据库名
```

### 5. 备份现有数据（如果适用）

如果已有SQLite数据库，先备份：

```bash
# 备份SQLite数据库
cp facebook_customer_service.db facebook_customer_service.db.backup

# 导出数据（可选）
sqlite3 facebook_customer_service.db .dump > backup.sql
```

### 6. 运行数据库迁移

```bash
# 运行迁移创建表结构
alembic upgrade head
```

### 7. 迁移数据（如果适用）

如果有现有数据需要迁移，可以使用数据迁移脚本：

```bash
python scripts/tools/migrate_sqlite_to_postgresql.py
```

### 8. 验证迁移

```bash
# 测试数据库连接
python -c "from src.core.database.connection import engine; engine.connect(); print('✅ PostgreSQL连接成功')"

# 检查表
python -c "
from src.core.database.connection import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'✅ 找到 {len(tables)} 个表')
for table in tables:
    print(f'  - {table}')
"
```

### 9. 更新连接池配置

PostgreSQL迁移后，连接池配置会自动生效。可以在 `src/core/config/constants.py` 中调整：

```python
# 生产环境推荐配置
DB_POOL_SIZE = 20  # 连接池大小
DB_MAX_OVERFLOW = 40  # 最大溢出连接
DB_POOL_RECYCLE = 3600  # 连接回收时间（秒）
DB_POOL_TIMEOUT = 30  # 连接超时（秒）
```

## 性能优化建议

### 1. 连接池配置

根据应用负载调整连接池大小：

```python
# 小型应用
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20

# 中型应用
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 40

# 大型应用
DB_POOL_SIZE = 50
DB_MAX_OVERFLOW = 100
```

### 2. 索引优化

确保关键字段有索引：

```sql
-- 检查现有索引
SELECT tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public';

-- 创建索引（如果需要）
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_customer_id ON conversations(customer_id);
```

### 3. 查询优化

使用 `EXPLAIN ANALYZE` 分析慢查询：

```sql
EXPLAIN ANALYZE SELECT * FROM conversations WHERE customer_id = 1;
```

## 回滚方案

如果需要回滚到SQLite：

1. 恢复 `.env` 中的 `DATABASE_URL`
2. 重启服务
3. 运行迁移：`alembic upgrade head`

**注意：** 回滚会丢失PostgreSQL中的数据，请确保已备份。

## 常见问题

### Q: 迁移后性能没有提升？

A: 检查连接池配置，确保使用了PostgreSQL连接池而不是SQLite的NullPool。

### Q: 如何监控PostgreSQL性能？

A: 可以使用以下命令：
```sql
-- 查看活动连接
SELECT * FROM pg_stat_activity;

-- 查看数据库大小
SELECT pg_size_pretty(pg_database_size('customer_service'));

-- 查看表大小
SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables WHERE schemaname = 'public';
```

### Q: 如何备份PostgreSQL数据库？

A: 使用 `pg_dump`：
```bash
pg_dump -U service_user -d customer_service > backup_$(date +%Y%m%d).sql
```

### Q: 如何恢复备份？

A: 使用 `psql`：
```bash
psql -U service_user -d customer_service < backup_20251214.sql
```

## 相关文件

- `src/core/database/connection.py` - 数据库连接配置
- `src/core/config/constants.py` - 连接池常量
- `alembic/` - 数据库迁移文件

