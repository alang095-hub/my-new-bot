"""Instagram Webhook 处理器（FastAPI路由）"""
from fastapi import APIRouter, Request, Response, HTTPException, Query, BackgroundTasks
from typing import Dict, Any
import logging
from src.instagram.api_client import InstagramAPIClient
from src.instagram.message_parser import InstagramMessageParser
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/instagram/webhook", tags=["instagram"])


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    """
    Instagram Webhook 验证端点
    
    Instagram 在订阅 Webhook 时会调用此端点进行验证
    """
    client = InstagramAPIClient()
    try:
        challenge = await client.verify_webhook(
            hub_mode,
            hub_verify_token,
            hub_challenge
        )
        
        if challenge:
            logger.info("Instagram webhook verified successfully")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.warning("Instagram webhook verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")
    finally:
        await client.close()


@router.post("")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Instagram Webhook 接收端点
    
    接收来自 Instagram 的所有事件（私信等）
    """
    try:
        body = await request.json()
        logger.info(f"Received Instagram webhook event: {body}")
        
        # 解析事件
        parser = InstagramMessageParser()
        parsed_messages = parser.parse_webhook_event(body)
        
        if not parsed_messages:
            logger.info("No Instagram messages to process")
            return {"status": "ok"}
        
        # 在后台处理消息（使用统一处理器）
        from src.main_processor import process_platform_message
        for message_data in parsed_messages:
            # 添加平台标识
            message_data["platform"] = "instagram"
            background_tasks.add_task(process_platform_message, "instagram", message_data)
        
        return {
            "status": "ok",
            "processed_count": len(parsed_messages)
        }
    
    except Exception as e:
        logger.error(f"Error processing Instagram webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))







