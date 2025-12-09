# 模块化处理器架构指南

## 📋 概述

系统已重构为**模块化处理器架构**，采用管道模式（Pipeline Pattern），将消息处理流程拆分为多个独立的处理器。每个处理器职责单一，便于升级和维护。

## 🏗️ 架构优势

### 1. 高度模块化
- ✅ 每个处理器独立实现
- ✅ 职责清晰，单一职责原则
- ✅ 易于理解和维护

### 2. 易于扩展
- ✅ 添加新功能只需创建新处理器
- ✅ 无需修改现有代码
- ✅ 支持动态添加/移除处理器

### 3. 灵活配置
- ✅ 可以自定义处理器顺序
- ✅ 可以跳过某些处理器
- ✅ 支持条件执行

### 4. 便于测试
- ✅ 每个处理器可以独立测试
- ✅ 模拟上下文进行单元测试
- ✅ 易于集成测试

## 📦 处理器架构

### 处理器基类

所有处理器继承自 `BaseProcessor`：

```python
from src.processors.base import BaseProcessor, ProcessorResult, ProcessorStatus, ProcessorContext

class MyProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("my_processor", "处理器描述")
    
    def get_dependencies(self) -> list:
        return ["dependency_processor"]  # 依赖的处理器
    
    async def process(self, context: ProcessorContext) -> ProcessorResult:
        # 处理逻辑
        return ProcessorResult(
            status=ProcessorStatus.SUCCESS,
            message="处理成功"
        )
```

### 处理器管道

管道管理处理器的执行顺序：

```python
from src.processors.pipeline import MessagePipeline, create_default_pipeline

# 使用默认管道
pipeline = create_default_pipeline()

# 或创建自定义管道
custom_pipeline = MessagePipeline()
custom_pipeline.add_processor(MyProcessor())
```

## 🔄 默认处理器流程

```
1. MessageReceiver（消息接收）
   ↓
2. UserInfoHandler（用户信息处理）
   ↓
3. FilterHandler（过滤处理）
   ↓
4. AIReplyHandler（AI回复）
   ↓
5. DataCollectionHandler（数据收集）
   ↓
6. StatisticsHandler（统计记录）
   ↓
7. NotificationHandler（通知发送）
```

## 🎯 处理器详细说明

### MessageReceiver
- **功能**：接收消息，生成摘要，提取关键信息
- **输出**：消息摘要、提取的信息
- **依赖**：无

### UserInfoHandler
- **功能**：获取或创建客户信息
- **输出**：客户对象、客户ID
- **依赖**：MessageReceiver

### FilterHandler
- **功能**：应用过滤规则，判断是否需要审核
- **输出**：过滤结果、是否需要审核
- **依赖**：UserInfoHandler
- **特殊**：可以跳过后续处理

### AIReplyHandler
- **功能**：生成并发送AI回复，记录高频问题
- **输出**：AI回复内容、是否发送群组邀请
- **依赖**：FilterHandler

### DataCollectionHandler
- **功能**：确认数据收集完成
- **输出**：收集的数据
- **依赖**：MessageReceiver

### StatisticsHandler
- **功能**：记录客户交互统计
- **输出**：交互记录ID
- **依赖**：UserInfoHandler, AIReplyHandler

### NotificationHandler
- **功能**：发送Telegram通知（如果需要审核）
- **输出**：通知发送状态
- **依赖**：FilterHandler

## 🔧 添加自定义处理器

### 示例：添加日志记录处理器

```python
# src/processors/custom_handlers.py
from src.processors.base import BaseProcessor, ProcessorResult, ProcessorStatus, ProcessorContext

class LoggingProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("logging_processor", "日志记录")
    
    def get_dependencies(self) -> list:
        return ["message_receiver"]
    
    async def process(self, context: ProcessorContext) -> ProcessorResult:
        # 记录日志
        logger.info(f"Processing message from {context.platform_name}")
        logger.info(f"Message summary: {context.message_summary[:100]}")
        
        return ProcessorResult(
            status=ProcessorStatus.SUCCESS,
            message="日志记录成功"
        )
```

### 添加到管道

```python
# src/processors/pipeline.py
from .custom_handlers import LoggingProcessor

def create_default_pipeline() -> MessagePipeline:
    pipeline = MessagePipeline()
    pipeline.add_processors([
        MessageReceiver(),
        LoggingProcessor(),  # 添加自定义处理器
        UserInfoHandler(),
        # ... 其他处理器
    ])
    return pipeline
```

## 📊 处理器上下文

`ProcessorContext` 是处理器之间共享的数据容器：

```python
context.platform_name          # 平台名称
context.message_data          # 原始消息数据
context.customer_id           # 客户ID
context.customer              # 客户对象
context.message_summary       # 消息摘要
context.extracted_info        # 提取的信息
context.ai_reply              # AI回复
context.filter_result         # 过滤结果
context.db                    # 数据库会话
context.platform_client       # 平台客户端
```

## 🎨 设计模式

### 1. 管道模式（Pipeline Pattern）
- 将复杂流程拆分为多个步骤
- 每个步骤独立实现
- 按顺序执行

### 2. 策略模式（Strategy Pattern）
- 每个处理器是一种策略
- 可以动态替换处理器
- 支持多种处理方式

### 3. 依赖注入（Dependency Injection）
- 通过上下文传递依赖
- 处理器不直接创建依赖
- 便于测试和替换

## 🔍 调试和监控

### 查看处理器执行结果

```python
result = await pipeline.process("facebook", message_data)
for processor_result in result["results"]:
    print(f"{processor_result['processor']}: {processor_result['status']}")
```

### 日志追踪

每个处理器都会记录日志，可以通过日志追踪执行流程。

## 📚 相关文件

- **基类**: `src/processors/base.py`
- **处理器实现**: `src/processors/handlers.py`
- **管道**: `src/processors/pipeline.py`
- **主处理**: `src/main_processor.py`
- **文档**: `src/processors/README.md`

## 🚀 升级和维护

### 添加新功能

1. 创建新处理器类
2. 实现 `process` 方法
3. 定义依赖关系
4. 添加到管道

### 修改现有功能

1. 找到对应的处理器
2. 修改处理器逻辑
3. 不影响其他处理器

### 优化性能

1. 可以并行执行独立处理器
2. 可以缓存处理器结果
3. 可以跳过不必要的处理器

## ✨ 总结

模块化处理器架构提供了：
- ✅ 清晰的代码组织
- ✅ 易于扩展和维护
- ✅ 便于测试和调试
- ✅ 灵活的配置选项

这使得系统可以轻松适应未来的需求变化和功能升级。




