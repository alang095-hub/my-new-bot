# 项目重构指南

## 概述

本项目已完成全面重构，采用了更清晰的模块化架构，提升了代码的可维护性和可扩展性。

## 新的目录结构

```
src/
├── core/                    # 核心基础模块
│   ├── config/             # 统一配置管理
│   │   ├── settings.py      # 环境变量配置
│   │   ├── loader.py        # YAML配置加载
│   │   ├── validators.py    # 配置验证
│   │   └── constants.py     # 常量定义
│   ├── database/           # 数据库相关
│   │   ├── connection.py   # 数据库连接
│   │   ├── models.py        # 数据模型
│   │   ├── statistics_models.py  # 统计模型
│   │   └── repositories/   # Repository模式（数据访问层）
│   │       ├── base.py
│   │       ├── customer_repo.py
│   │       └── conversation_repo.py
│   ├── exceptions/         # 异常定义
│   │   ├── base.py
│   │   ├── api.py
│   │   └── business.py
│   └── logging/            # 日志配置
│       └── config.py
├── services/               # 业务服务层
│   ├── ai/                 # AI服务
│   ├── collector/          # 数据收集服务
│   ├── notification/       # 通知服务
│   └── statistics/         # 统计服务
├── api/                    # API路由
│   ├── v1/                 # API版本管理
│   │   ├── webhooks/       # Webhook路由
│   │   ├── admin/          # 管理API
│   │   ├── monitoring/     # 监控API
│   │   └── statistics/     # 统计API
│   └── middleware/         # 中间件
├── platforms/              # 平台集成
├── processors/             # 消息处理器
├── business/               # 业务模块
└── main.py                 # 应用入口
```

## 主要改进

### 1. 统一配置管理

**新路径**: `src.core.config`

所有配置相关的功能都统一在 `core/config/` 目录下：

```python
# 使用新的导入路径
from src.core.config import settings, yaml_config, ConfigValidator
from src.core.config.constants import DEFAULT_OPENAI_MODEL, DB_POOL_SIZE
```

**向后兼容**: 旧的导入路径仍然可用（通过 `src/config.py` 重定向）

### 2. Repository模式

**新路径**: `src.core.database.repositories`

引入了Repository模式来管理数据访问：

```python
from src.core.database.repositories import CustomerRepository, ConversationRepository

# 使用Repository
customer_repo = CustomerRepository(db)
customer = customer_repo.get_or_create(
    platform=Platform.FACEBOOK,
    platform_user_id="123456",
    name="John Doe"
)
```

**优势**:
- 统一的数据访问接口
- 更好的错误处理
- 易于测试和维护

### 3. 统一异常处理

**新路径**: `src.core.exceptions`

所有异常都定义在 `core/exceptions/` 目录下：

```python
from src.core.exceptions import APIError, DatabaseError, ProcessingError, ValidationError

# 使用异常
raise APIError(
    message="API调用失败",
    status_code=500,
    api_name="Facebook"
)
```

**向后兼容**: 旧的导入路径仍然可用（通过 `src/utils/exceptions.py` 重定向）

### 4. 规范化日志系统

**新路径**: `src.core.logging`

日志配置统一管理：

```python
from src.core.logging import setup_logging, get_logger

# 设置日志
setup_logging(
    log_level="INFO",
    log_file=Path("logs/app.log"),
    use_json=False
)

# 获取日志记录器
logger = get_logger(__name__)
```

### 5. API路由重组

**新路径**: `src.api.v1`

所有API路由按功能模块组织：

```python
from src.api.v1.webhooks.facebook import router as facebook_router
from src.api.v1.admin.api import router as admin_router
from src.api.v1.monitoring.api import router as monitoring_router
```

## 迁移指南

### 更新导入路径

#### 配置相关
```python
# 旧路径
from src.config import settings
from src.config import yaml_config

# 新路径（推荐）
from src.core.config import settings, yaml_config
```

#### 数据库相关
```python
# 旧路径
from src.database.database import get_db, engine, Base
from src.database.models import Customer, Conversation

# 新路径（推荐）
from src.core.database.connection import get_db, engine, Base
from src.core.database.models import Customer, Conversation
```

#### 异常处理
```python
# 旧路径
from src.utils.exceptions import APIError, ProcessingError

# 新路径（推荐）
from src.core.exceptions import APIError, ProcessingError
```

#### 日志配置
```python
# 旧路径
from src.utils.logging_config import setup_logging

# 新路径（推荐）
from src.core.logging import setup_logging
```

### 使用Repository模式

**之前**（直接数据库访问）:
```python
customer = db.query(Customer).filter(
    Customer.platform == Platform.FACEBOOK,
    Customer.platform_user_id == user_id
).first()

if not customer:
    customer = Customer(platform=Platform.FACEBOOK, platform_user_id=user_id)
    db.add(customer)
    db.commit()
```

**现在**（使用Repository）:
```python
from src.core.database.repositories import CustomerRepository

customer_repo = CustomerRepository(db)
customer = customer_repo.get_or_create(
    platform=Platform.FACEBOOK,
    platform_user_id=user_id
)
```

## 向后兼容性

为了确保平滑迁移，所有旧的导入路径都通过 `__init__.py` 文件重定向到新路径：

- `src/config.py` → `src.core.config`
- `src/database/database.py` → `src.core.database.connection`
- `src/utils/exceptions.py` → `src.core.exceptions`
- `src/utils/logging_config.py` → `src.core.logging`

**建议**: 逐步迁移到新路径，但旧代码仍然可以正常工作。

## 测试

运行测试确保所有功能正常：

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_database_models.py -v
```

## 常见问题

### Q: 我应该立即更新所有导入路径吗？

A: 不需要。向后兼容层确保旧代码仍然可以工作。建议逐步迁移，优先更新新代码。

### Q: Repository模式是必须的吗？

A: 不是必须的，但强烈推荐。它提供了更好的代码组织和错误处理。

### Q: 如何添加新的Repository？

A: 继承 `BaseRepository` 并实现特定方法：

```python
from src.core.database.repositories.base import BaseRepository

class MyRepository(BaseRepository[MyModel]):
    def __init__(self, db: Session):
        super().__init__(db, MyModel)
    
    def custom_method(self):
        # 自定义方法
        pass
```

## 下一步

1. 逐步更新导入路径到新路径
2. 使用Repository模式替换直接数据库访问
3. 使用新的异常处理系统
4. 运行测试确保功能正常
5. 更新文档和注释

## 相关文档

- [架构文档](architecture/MODULAR_ARCHITECTURE.md)
- [系统功能](architecture/SYSTEM_FEATURES.md)
- [部署指南](deployment/DEPLOYMENT_GUIDE.md)

