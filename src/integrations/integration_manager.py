"""集成管理器 - 统一管理多个客服平台"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from src.core.database.models import IntegrationLog
from src.integrations.manychat_client import ManyChatClient
from src.integrations.botcake_client import BotcakeClient
from src.core.config import yaml_config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class IntegrationManager:
    """管理 ManyChat 和 Botcake 集成"""
    
    def __init__(self, db: Session):
        self.db = db
        self.manychat_client = ManyChatClient() if yaml_config.get("integrations", {}).get("manychat", {}).get("enabled", False) else None
        self.botcake_client = BotcakeClient() if yaml_config.get("integrations", {}).get("botcake", {}).get("enabled", False) else None
    
    async def sync_to_manychat(
        self,
        subscriber_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        同步数据到 ManyChat
        
        Args:
            subscriber_id: ManyChat 订阅者 ID
            data: 要同步的数据
        
        Returns:
            是否同步成功
        """
        if not self.manychat_client:
            logger.warning("ManyChat client not initialized")
            return False
        
        try:
            # 同步自定义字段
            for field_name, field_value in data.items():
                await self.manychat_client.set_custom_field(
                    subscriber_id,
                    field_name,
                    field_value
                )
            
            # 记录日志
            self._log_integration("manychat", "sync", "success", data)
            
            return True
        
        except Exception as e:
            logger.error(f"Error syncing to ManyChat: {str(e)}", exc_info=True)
            self._log_integration("manychat", "sync", "failed", data, str(e))
            return False
    
    async def sync_to_botcake(
        self,
        user_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        同步数据到 Botcake
        
        Args:
            user_id: Botcake 用户 ID
            data: 要同步的数据
        
        Returns:
            是否同步成功
        """
        if not self.botcake_client:
            logger.warning("Botcake client not initialized")
            return False
        
        try:
            # 同步用户属性
            for attr_name, attr_value in data.items():
                await self.botcake_client.update_user_attribute(
                    user_id,
                    attr_name,
                    attr_value
                )
            
            # 记录日志
            self._log_integration("botcake", "sync", "success", data)
            
            return True
        
        except Exception as e:
            logger.error(f"Error syncing to Botcake: {str(e)}", exc_info=True)
            self._log_integration("botcake", "sync", "failed", data, str(e))
            return False
    
    async def send_message_via_manychat(
        self,
        subscriber_id: str,
        message: str
    ) -> bool:
        """
        通过 ManyChat 发送消息
        
        Args:
            subscriber_id: 订阅者 ID
            message: 消息内容
        
        Returns:
            是否发送成功
        """
        if not self.manychat_client:
            return False
        
        try:
            await self.manychat_client.send_message(subscriber_id, message)
            self._log_integration("manychat", "send", "success", {"message": message[:100]})
            return True
        except Exception as e:
            logger.error(f"Error sending message via ManyChat: {str(e)}", exc_info=True)
            self._log_integration("manychat", "send", "failed", {"message": message[:100]}, str(e))
            return False
    
    async def send_message_via_botcake(
        self,
        user_id: str,
        message: str
    ) -> bool:
        """
        通过 Botcake 发送消息
        
        Args:
            user_id: 用户 ID
            message: 消息内容
        
        Returns:
            是否发送成功
        """
        if not self.botcake_client:
            return False
        
        try:
            await self.botcake_client.send_message(user_id, message)
            self._log_integration("botcake", "send", "success", {"message": message[:100]})
            return True
        except Exception as e:
            logger.error(f"Error sending message via Botcake: {str(e)}", exc_info=True)
            self._log_integration("botcake", "send", "failed", {"message": message[:100]}, str(e))
            return False
    
    def _log_integration(
        self,
        integration_type: str,
        action: str,
        status: str,
        request_data: Dict[str, Any] = None,
        error_message: str = None
    ):
        """记录集成日志"""
        log = IntegrationLog(
            integration_type=integration_type,
            action=action,
            status=status,
            request_data=request_data,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()
    
    async def close(self):
        """关闭所有客户端"""
        if self.manychat_client:
            await self.manychat_client.close()
        if self.botcake_client:
            await self.botcake_client.close()


