"""消息处理管道 - 按顺序执行处理器"""
from typing import List, Dict, Any, Optional
from .base import BaseProcessor, ProcessorResult, ProcessorContext, ProcessorStatus
from src.database.database import SessionLocal
from src.platforms.registry import registry
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class MessagePipeline:
    """消息处理管道 - 管理处理器的执行顺序"""
    
    def __init__(self):
        self.processors: List[BaseProcessor] = []
        self.processor_map: Dict[str, BaseProcessor] = {}
    
    def add_processor(self, processor: BaseProcessor):
        """
        添加处理器到管道
        
        Args:
            processor: 处理器实例
        """
        self.processors.append(processor)
        self.processor_map[processor.name] = processor
    
    def add_processors(self, processors: List[BaseProcessor]):
        """批量添加处理器"""
        for processor in processors:
            self.add_processor(processor)
    
    def _resolve_dependencies(self) -> List[BaseProcessor]:
        """
        根据依赖关系排序处理器
        
        Returns:
            排序后的处理器列表
        """
        # 简单的拓扑排序
        sorted_processors = []
        remaining = self.processors.copy()
        added = set()
        
        while remaining:
            progress = False
            for processor in remaining[:]:
                deps = processor.get_dependencies()
                if all(dep in added for dep in deps):
                    sorted_processors.append(processor)
                    added.add(processor.name)
                    remaining.remove(processor)
                    progress = True
            
            if not progress:
                # 如果有循环依赖，按当前顺序添加
                for processor in remaining:
                    sorted_processors.append(processor)
                    added.add(processor.name)
                break
        
        return sorted_processors
    
    async def process(self, platform_name: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理消息
        
        Args:
            platform_name: 平台名称
            message_data: 消息数据
            
        Returns:
            处理结果摘要
        """
        db = SessionLocal()
        platform_client = None
        
        try:
            # 创建处理器上下文
            context = ProcessorContext(
                platform_name=platform_name,
                message_data=message_data,
                db=db
            )
            
            # 创建平台客户端
            if platform_name == "facebook":
                access_token = settings.facebook_access_token
            elif platform_name == "instagram":
                access_token = getattr(settings, 'instagram_access_token', None) or settings.facebook_access_token
            else:
                logger.error(f"Unknown platform: {platform_name}")
                return {"success": False, "error": f"Unknown platform: {platform_name}"}
            
            client_kwargs = {"access_token": access_token}
            if platform_name == "instagram":
                ig_user_id = getattr(settings, 'instagram_user_id', None)
                if ig_user_id:
                    client_kwargs["ig_user_id"] = ig_user_id
            
            platform_client = registry.create_client(platform_name, **client_kwargs)
            if not platform_client:
                logger.error(f"Failed to create client for platform: {platform_name}")
                return {"success": False, "error": "Failed to create platform client"}
            
            context.platform_client = platform_client
            
            # 按依赖关系排序处理器
            sorted_processors = self._resolve_dependencies()
            
            # 执行处理器
            results = []
            for processor in sorted_processors:
                try:
                    # 验证
                    validation_error = processor.validate(context)
                    if validation_error:
                        logger.warning(f"Processor {processor.name} validation failed: {validation_error}")
                        continue
                    
                    # 执行
                    result = await processor.process(context)
                    results.append({
                        "processor": processor.name,
                        "status": result.status.value,
                        "message": result.message
                    })
                    
                    # 如果处理器要求跳过后续处理
                    if result.should_skip():
                        logger.info(f"Processor {processor.name} requested to skip remaining processors")
                        break
                    
                    # 如果处理器失败且不应该继续
                    if result.status == ProcessorStatus.ERROR and not result.should_continue:
                        logger.error(f"Processor {processor.name} failed and stopped pipeline")
                        break
                        
                except Exception as e:
                    logger.error(f"Error in processor {processor.name}: {str(e)}", exc_info=True)
                    results.append({
                        "processor": processor.name,
                        "status": "error",
                        "message": f"Exception: {str(e)}"
                    })
            
            # 返回处理结果
            return {
                "success": True,
                "customer_id": context.customer_id,
                "results": results,
                "summary": {
                    "ai_replied": context.ai_replied,
                    "group_invitation_sent": context.group_invitation_sent,
                    "should_review": context.should_review
                }
            }
        
        except Exception as e:
            logger.error(f"Error in message pipeline: {str(e)}", exc_info=True)
            db.rollback()
            return {"success": False, "error": str(e)}
        
        finally:
            db.close()
            if platform_client:
                await platform_client.close()


# 创建默认管道实例
def create_default_pipeline() -> MessagePipeline:
    """创建默认的消息处理管道"""
    from .handlers import (
        MessageReceiver,
        UserInfoHandler,
        FilterHandler,
        AIReplyHandler,
        DataCollectionHandler,
        StatisticsHandler,
        NotificationHandler
    )
    
    pipeline = MessagePipeline()
    pipeline.add_processors([
        MessageReceiver(),
        UserInfoHandler(),
        FilterHandler(),
        AIReplyHandler(),
        DataCollectionHandler(),
        StatisticsHandler(),
        NotificationHandler()
    ])
    
    return pipeline

# 全局默认管道
default_pipeline = create_default_pipeline()




