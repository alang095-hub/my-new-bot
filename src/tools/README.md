# 工具模块文档

## 概述

工具模块提供了统一的工具接口和插件系统，便于扩展和维护。

## 快速开始

### 使用现有工具

```python
from src.tools import TokenManager, ConfigChecker
import asyncio

async def main():
    # 使用令牌管理器
    manager = TokenManager()
    result = await manager.execute(
        action='extract',
        url='http://localhost:8000/oauth/callback#access_token=...'
    )
    
    if result.is_success():
        print(f"令牌: {result.data['access_token']}")

asyncio.run(main())
```

### 命令行使用

```bash
# 列出所有工具
python -m src.tools.cli list

# 使用工具
python -m src.tools.cli token_manager --action extract --url "..."

# 查看帮助
python -m src.tools.cli help token_manager
```

## 创建新工具

### 1. 定义工具类

```python
from src.tools import BaseTool, ToolResult, ToolStatus

class MyTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="我的工具描述"
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        # 实现工具逻辑
        param = kwargs.get('param')
        
        if not param:
            return ToolResult(
                status=ToolStatus.ERROR,
                message="缺少参数",
                errors=["param参数是必需的"]
            )
        
        # 执行操作
        result_data = {'output': f"处理了 {param}"}
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            message="执行成功",
            data=result_data
        )
```

### 2. 注册工具

在 `src/tools/registry.py` 中注册：

```python
from .my_tool import MyTool

registry.register("my_tool", MyTool)
```

### 3. 使用工具

```python
from src.tools import registry

tool = registry.create_tool("my_tool")
result = await tool.execute(param="value")
```

## 工具结果

所有工具返回 `ToolResult` 对象：

```python
@dataclass
class ToolResult:
    status: ToolStatus      # 状态：SUCCESS, WARNING, ERROR, INFO
    message: str           # 消息
    data: Dict[str, Any]   # 数据（可选）
    errors: List[str]      # 错误列表（可选）
```

### 检查结果

```python
result = await tool.execute(...)

if result.is_success():
    print("成功")
elif result.has_warnings():
    print("有警告")
elif result.has_errors():
    print("有错误")
```

## 插件系统

### 创建插件

```python
from src.tools import Plugin, BaseTool

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__("my_plugin", "1.0.0")
    
    def get_tools(self):
        return [MyTool1(), MyTool2()]
    
    def get_dependencies(self):
        return []
```

### 注册插件

```python
from src.tools import plugin_manager, registry

plugin_manager.set_tool_registry(registry)
plugin_manager.register_plugin(MyPlugin())
```

## 可用工具

- `token_manager`: 令牌管理（提取、更新）
- `config_checker`: 配置检查
- `permission_checker`: 权限检查
- `exchange_token`: 令牌交换

## 最佳实践

1. **错误处理**: 始终返回适当的 `ToolResult`
2. **输入验证**: 使用 `validate_input` 方法
3. **文档**: 提供清晰的工具描述
4. **测试**: 为工具编写单元测试






