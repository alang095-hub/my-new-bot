"""Telegram Bot 消息处理"""
from fastapi import APIRouter, Request
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.core.database.connection import get_db
from src.telegram.command_processor import CommandProcessor
from src.telegram.notification_sender import NotificationSender
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def handle_telegram_webhook(request: Request):
    """
    处理 Telegram Webhook 消息
    
    接收来自 Telegram 的消息和命令
    """
    try:
        body = await request.json()
        logger.info(f"Received Telegram webhook: {body}")
        
        # 提取消息信息
        message = body.get("message", {})
        if not message:
            return {"status": "ok"}
        
        text = message.get("text", "")
        chat = message.get("chat", {})
        from_user = message.get("from", {})
        
        # 只处理文本消息
        if not text or not text.startswith("/"):
            return {"status": "ok"}
        
        # 获取数据库会话
        db = next(get_db())
        processor = CommandProcessor(db)
        
        # 处理命令
        reviewer = from_user.get("username", from_user.get("first_name", "unknown"))
        result = processor.process_command(text, reviewer)
        
        # 发送回复（如果需要）
        if result.get("success"):
            # 这里可以调用 Telegram API 发送回复消息
            logger.info(f"Command processed: {result.get('message')}")
        else:
            logger.warning(f"Command failed: {result.get('message')}")
        
        return {
            "status": "ok",
            "result": result
        }
    
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


