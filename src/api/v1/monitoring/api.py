"""实时监控API接口"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.core.database.connection import get_db
from src.monitoring.realtime import realtime_monitor
import asyncio
import uuid
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/live")
async def live_monitoring_stream(request: Request):
    """
    实时监控流 - Server-Sent Events (SSE)
    
    返回实时AI回复和系统事件的流式数据
    """
    connection_id = str(uuid.uuid4())
    queue = await realtime_monitor.add_connection(connection_id)
    
    async def event_generator():
        try:
            # 发送初始连接消息
            yield f"data: {json.dumps({'type': 'connected', 'connection_id': connection_id})}\n\n"
            
            # 发送最近的回复记录
            recent_replies = await realtime_monitor.get_recent_replies(10)
            if recent_replies:
                yield f"data: {json.dumps({'type': 'initial_data', 'replies': recent_replies})}\n\n"
            
            # 持续发送事件
            while True:
                # 检查客户端是否断开
                if await request.is_disconnected():
                    break
                
                try:
                    # 等待新事件（设置超时避免阻塞）
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield message
                except asyncio.TimeoutError:
                    # 发送心跳保持连接
                    yield f": heartbeat\n\n"
                    continue
                except Exception as e:
                    logger.error(f"Error in event stream: {e}")
                    break
        
        finally:
            # 清理连接
            await realtime_monitor.remove_connection(connection_id)
            logger.info(f"Connection {connection_id} closed")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/stats")
async def get_live_stats(db: Session = Depends(get_db)):
    """
    获取实时统计数据
    
    返回当前的AI回复统计、平台分布等
    """
    try:
        stats = await realtime_monitor.get_live_stats(db)
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Error getting live stats: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


@router.get("/recent-replies")
async def get_recent_replies(limit: int = 20):
    """
    获取最近的AI回复记录
    
    Args:
        limit: 返回的记录数，默认20
    """
    try:
        replies = await realtime_monitor.get_recent_replies(limit)
        return {
            "success": True,
            "data": replies,
            "count": len(replies)
        }
    except Exception as e:
        logger.error(f"Error getting recent replies: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

