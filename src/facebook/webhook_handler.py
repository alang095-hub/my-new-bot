"""Facebook Webhook 处理器（FastAPI路由）"""
from fastapi import APIRouter, Request, Response, HTTPException, Query, BackgroundTasks
from typing import Dict, Any
import logging
from src.facebook.api_client import FacebookAPIClient
from src.facebook.message_parser import FacebookMessageParser
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["facebook"])


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Facebook Webhook 验证端点（兼容路由）
    
    Facebook 在订阅 Webhook 时会调用此端点进行验证
    
    如果缺少必需参数，返回友好的提示信息
    """
    # 检查是否缺少必需参数
    if hub_mode is None or hub_verify_token is None or hub_challenge is None:
        logger.info("Webhook endpoint accessed without required parameters")
        return Response(
            content="Facebook Webhook 验证端点\n\n此端点需要以下查询参数：\n- hub.mode\n- hub.verify_token\n- hub.challenge\n\nFacebook 在验证 Webhook 时会自动发送这些参数。\n\n测试 URL 示例：\n/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test123",
            media_type="text/plain; charset=utf-8"
        )
    
    # 记录验证请求的详细信息
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token[:10]}..., challenge={hub_challenge[:20] if hub_challenge else 'None'}...")
    
    client = FacebookAPIClient()
    try:
        challenge = await client.verify_webhook(
            hub_mode,
            hub_verify_token,
            hub_challenge
        )
        
        if challenge:
            logger.info("Webhook verified successfully")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.warning(f"Webhook verification failed: mode={hub_mode}, token_match=False")
            raise HTTPException(status_code=403, detail="Verification failed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during webhook verification: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        await client.close()


@router.post("")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Facebook Webhook 接收端点（兼容路由）
    
    接收来自 Facebook 的所有事件（消息、评论、广告等）
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook event: {body}")
        
        # 解析事件
        parser = FacebookMessageParser()
        parsed_messages = parser.parse_webhook_event(body)
        
        if not parsed_messages:
            logger.info("No messages to process")
            return {"status": "ok"}
        
        # 在后台处理消息（使用统一处理器）
        from src.main_processor import process_platform_message
        for message_data in parsed_messages:
            # 添加平台标识
            message_data["platform"] = "facebook"
            background_tasks.add_task(process_platform_message, "facebook", message_data)
        
        return {
            "status": "ok",
            "processed_count": len(parsed_messages)
        }
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

