# 实际运行测试的准确步骤

## 快速开始（5分钟验证）

### 步骤1：基础环境检查（1分钟）

```bash
# 检查Python版本
python --version

# 检查pytest是否安装
pytest --version
```

### 步骤2：迁移验证（2分钟）

```bash
# 运行迁移验证脚本
python scripts/test_migration.py

# 验证主应用可以导入
python -c "import sys; sys.path.insert(0, '.'); from src.main import app; print('✅ 主应用正常')"
```

### 步骤3：运行一个简单测试（2分钟）

```bash
# 运行数据库模型测试
pytest tests/test_database_models.py -v
```

## 完整测试流程（按顺序执行）

### 阶段一：基础验证（10分钟）

#### 1.1 环境验证
```bash
# Windows PowerShell
python --version
pip list | findstr pytest

# Linux/Mac
python --version
pip list | grep pytest
```

#### 1.2 导入路径验证
```bash
# 验证核心模块导入
python -c "from src.core.config import settings; print('✅ 配置模块正常')"
python -c "from src.core.database.repositories import CustomerRepository; print('✅ Repository正常')"
python -c "from src.core.exceptions import APIError; print('✅ 异常模块正常')"

# 验证向后兼容
python -c "from src.config import settings; print('✅ 向后兼容正常')"
python -c "from src.database.models import Customer; print('✅ 数据库模型兼容正常')"
```

#### 1.3 主应用验证
```bash
# 验证主应用可以正常导入和启动
python -c "import sys; sys.path.insert(0, '.'); from src.main import app; print('✅ 主应用导入成功')"
```

### 阶段二：单元测试（15-20分钟）

#### 2.1 数据库模型测试
```bash
pytest tests/test_database_models.py -v
```

#### 2.2 AI服务测试
```bash
pytest tests/test_ai_reply_generator.py -v
```

#### 2.3 数据收集测试
```bash
pytest tests/test_data_collector.py -v
```

#### 2.4 过滤引擎测试
```bash
pytest tests/test_filter_engine.py -v
```

### 阶段三：系统功能测试（5分钟）

```bash
# 运行系统功能测试
python tests/test_system_functionality.py

# 运行生产就绪性测试
python tests/test_production_readiness.py
```

### 阶段四：完整测试套件（20-30分钟）

```bash
# 运行所有pytest测试（带覆盖率）
pytest tests/ -v --cov=src --cov-report=term --cov-report=html

# 查看覆盖率报告
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### 阶段五：API测试（需要启动服务，15分钟）

#### 5.1 启动应用
```bash
# 在一个终端窗口运行
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5.2 运行API测试
```bash
# 在另一个终端窗口运行
pytest tests/test_api_endpoints.py -v

# 或手动测试
curl http://localhost:8000/health
# 浏览器访问: http://localhost:8000/health
```

### 阶段六：集成测试（10分钟）

```bash
# 运行集成测试
pytest tests/test_integration.py -v

# 运行E2E工作流测试
pytest tests/test_e2e_workflow.py -v
```

## 一键运行命令（快速测试）

### Windows PowerShell
```powershell
# 快速验证（迁移 + 基础测试）
python scripts/test_migration.py; python -c "import sys; sys.path.insert(0, '.'); from src.main import app; print('✅ 主应用正常')"; pytest tests/test_database_models.py -v
```

### Linux/Mac
```bash
# 快速验证（迁移 + 基础测试）
python scripts/test_migration.py && python -c "import sys; sys.path.insert(0, '.'); from src.main import app; print('✅ 主应用正常')" && pytest tests/test_database_models.py -v
```

## 测试结果查看

### 查看测试输出
```bash
# 详细输出
pytest tests/ -v

# 更详细的输出（包括print语句）
pytest tests/ -v -s
```

### 查看覆盖率报告
```bash
# Windows
start htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Mac
open htmlcov/index.html
```

### 查看测试日志
```bash
# 如果存在测试日志
cat logs/test.log
# 或
type logs\test.log  # Windows
```

## 常见问题处理

### 问题1：导入错误
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 确保在项目根目录运行
pwd  # Linux/Mac
cd   # Windows
```

### 问题2：pytest未安装
```bash
pip install pytest pytest-cov pytest-asyncio
```

### 问题3：数据库连接错误
```bash
# 检查环境变量
echo $DATABASE_URL  # Linux/Mac
echo %DATABASE_URL%  # Windows

# 检查.env文件
cat .env  # Linux/Mac
type .env  # Windows
```

### 问题4：测试失败
```bash
# 查看详细错误信息
pytest tests/test_database_models.py -v -s

# 运行单个测试
pytest tests/test_database_models.py::test_customer_model -v
```

## 测试优先级建议

### 必须运行（部署前）
1. ✅ 迁移验证（步骤1.2）
2. ✅ 主应用验证（步骤1.3）
3. ✅ 数据库模型测试（步骤2.1）
4. ✅ 系统功能测试（步骤三）

### 建议运行（开发中）
5. ⚠️ 完整测试套件（步骤四）
6. ⚠️ API测试（步骤五）
7. ⚠️ 集成测试（步骤六）

### 可选运行（优化时）
8. 📊 性能测试
9. 🔒 安全测试
10. 📈 覆盖率分析

## 测试时间估算

- **快速验证**: 5分钟
- **基础测试**: 20-30分钟
- **完整测试**: 1-2小时
- **全面测试（含性能和安全）**: 3-4小时

## 下一步

运行测试后：
1. 查看测试结果
2. 记录失败的测试
3. 分析失败原因
4. 修复问题
5. 重新运行测试
6. 更新测试计划（如需要）

