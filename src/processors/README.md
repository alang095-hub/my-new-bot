# 消息处理器模块文档

## 📋 概述

消息处理器模块采用**管道模式（Pipeline Pattern）**，将消息处理流程拆分为多个独立的处理器，每个处理器负责一个特定功能。

## 🏗️ 架构设计

### 处理器管道

```
消息接收 → 用户信息处理 → 过滤处理 → AI回复 → 数据收集 → 统计记录 → 通知发送
```

每个处理器：
- 独立实现，职责单一
- 通过上下文（Context）传递数据
- 可以控制是否继续后续处理
- 支持依赖关系管理

## 📦 处理器列表

### 1. MessageReceiver（消息接收）
- **职责**：接收消息，生成摘要，提取关键信息
- **依赖**：无
- **输出**：消息摘要、提取的信息

### 2. UserInfoHandler（用户信息处理）
- **职责**：获取或创建客户信息
- **依赖**：MessageReceiver
- **输出**：客户对象、客户ID

### 3. FilterHandler（过滤处理）
- **职责**：应用过滤规则，判断是否需要审核
- **依赖**：UserInfoHandler
- **输出**：过滤结果、是否需要审核

### 4. AIReplyHandler（AI回复）
- **职责**：生成并发送AI回复，记录高频问题
- **依赖**：FilterHandler
- **输出**：AI回复内容、是否发送群组邀请

### 5. DataCollectionHandler（数据收集）
- **职责**：确认数据收集完成
- **依赖**：MessageReceiver
- **输出**：收集的数据

### 6. StatisticsHandler（统计记录）
- **职责**：记录客户交互统计
- **依赖**：UserInfoHandler, AIReplyHandler
- **输出**：交互记录ID

### 7. NotificationHandler（通知发送）
- **职责**：发送Telegram通知（如果需要审核）
- **依赖**：FilterHandler
- **输出**：通知发送状态

## 🔧 创建自定义处理器

### 步骤1：创建处理器类

```python
from src.processors.base import BaseProcessor, ProcessorResult, ProcessorStatus, ProcessorContext

class MyCustomProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("my_processor", "我的自定义处理器")
    
    def get_dependencies(self) -> list:
        return ["user_info_handler"]  # 依赖的处理器
    
    async def process(self, context: ProcessorContext) -> ProcessorResult:
        # 实现处理逻辑
        try:
            # 使用context中的数据
            customer_id = context.customer_id
            message = context.message_summary
            
            # 执行处理
            # ...
            
            return ProcessorResult(
                status=ProcessorStatus.SUCCESS,
                message="处理成功",
                data={"result": "..."}
            )
        except Exception as e:
            return ProcessorResult(
                status=ProcessorStatus.ERROR,
                message=f"处理失败: {str(e)}",
                error=e
            )
```

### 步骤2：添加到管道

```python
from src.processors.pipeline import MessagePipeline
from .my_processor import MyCustomProcessor

pipeline = MessagePipeline()
pipeline.add_processor(MyCustomProcessor())
```

## 🎯 处理器上下文

`ProcessorContext` 包含所有处理器共享的数据：

```python
@dataclass
class ProcessorContext:
    platform_name: str           # 平台名称
    message_data: Dict           # 原始消息数据
    customer_id: int             # 客户ID
    customer: Customer           # 客户对象
    user_info: Dict              # 用户信息
    message_summary: str         # 消息摘要
    extracted_info: Dict         # 提取的信息
    ai_reply: str                # AI回复
    filter_result: Dict          # 过滤结果
    ai_replied: bool             # 是否AI回复
    group_invitation_sent: bool  # 是否发送群组邀请
    should_review: bool          # 是否需要审核
    db: Session                  # 数据库会话
    platform_client: Any         # 平台客户端
```

## 🔄 处理器执行流程

1. **依赖解析**：根据依赖关系排序处理器
2. **顺序执行**：按顺序执行每个处理器
3. **上下文传递**：每个处理器可以读取和修改上下文
4. **流程控制**：处理器可以决定是否继续后续处理

## 📊 优势

### 1. 模块化
- 每个处理器独立实现
- 职责清晰，易于理解
- 便于测试和维护

### 2. 可扩展性
- 添加新功能只需创建新处理器
- 无需修改现有代码
- 支持动态添加/移除处理器

### 3. 灵活性
- 可以自定义处理器顺序
- 可以跳过某些处理器
- 支持条件执行

### 4. 可维护性
- 代码组织清晰
- 易于定位问题
- 便于升级和优化

## 🔍 调试

### 查看处理器执行结果

处理结果包含每个处理器的执行状态：

```python
result = await pipeline.process("facebook", message_data)
print(result["results"])  # 查看每个处理器的执行结果
```

### 日志

每个处理器都会记录日志，可以通过日志追踪执行流程。

## 📚 相关文件

- **基类**: `src/processors/base.py`
- **处理器实现**: `src/processors/handlers.py`
- **管道**: `src/processors/pipeline.py`
- **主处理**: `src/main_processor.py`




