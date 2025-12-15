# 测试文档索引

本文档提供了所有测试相关文档的索引。

## 测试文档

### 本地测试

- **[本地测试指南](LOCAL_TEST_GUIDE.md)** - 详细的本地测试指南，包含步骤、示例和问题排查
- **[本地测试检查清单](LOCAL_TEST_CHECKLIST.md)** - 完整的测试检查清单，确保所有功能正常

### 生产环境测试

- **[生产环境测试检查清单](../testing/PRODUCTION_TEST_CHECKLIST.md)** - 生产环境部署前的测试检查清单
- **[生产环境测试流程](../testing/PRODUCTION_TESTING_FLOW.md)** - 生产环境测试流程

## 测试脚本

### 本地测试脚本

- **`scripts/test/local_test.py`** - 快速本地测试脚本
  - 测试数据库连接
  - 测试配置加载
  - 测试核心模块
  - 测试API健康检查

- **`scripts/test/full_local_test.py`** - 完整本地测试脚本
  - 环境检查
  - 数据库测试
  - API端点测试
  - 核心功能测试
  - 性能测试

### 测试辅助工具

- **`scripts/test/test_helpers.py`** - 测试辅助工具
  - 模拟数据生成器
  - 测试环境设置
  - Mock API客户端

## 快速开始

### 5分钟快速测试

```bash
# 1. 激活虚拟环境
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. 运行快速测试
python scripts/test/local_test.py
```

### 完整测试

```bash
# 1. 启动服务（一个终端）
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 2. 运行完整测试（另一个终端）
python scripts/test/full_local_test.py
```

## 测试流程

1. **环境准备** - 参考 [本地测试指南](LOCAL_TEST_GUIDE.md) 的环境准备部分
2. **快速测试** - 运行 `local_test.py` 验证基础功能
3. **完整测试** - 运行 `full_local_test.py` 进行全面测试
4. **手动测试** - 使用API文档或curl进行手动测试
5. **检查清单** - 使用 [测试检查清单](LOCAL_TEST_CHECKLIST.md) 确保所有项完成

## 测试报告

测试报告会自动保存到 `data/test_reports/` 目录，格式为JSON。

查看最新报告:
```bash
ls -lt data/test_reports/ | head -1
```

## 相关文档

- [部署文档](../deployment/DEPLOYMENT_GUIDE.md)
- [架构文档](../architecture/MODULAR_ARCHITECTURE.md)
- [使用指南](../USAGE_GUIDE.md)

