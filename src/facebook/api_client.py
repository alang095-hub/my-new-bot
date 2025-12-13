"""Facebook Graph API 客户端"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class FacebookAPIClient:
    """Facebook Graph API 客户端封装"""

    def __init__(self, access_token: Optional[str] = None):
        """
        初始化Facebook API客户端

        Args:
            access_token: 访问令牌，如果为None则从settings或Token管理器获取
        """
        if access_token:
            self.access_token = access_token
        else:
            # 尝试从Token管理器获取，如果没有则使用默认Token
            from src.config.page_token_manager import page_token_manager
            self.access_token = page_token_manager.get_token() or settings.facebook_access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def send_message(
        self,
        recipient_id: str,
        message: str,
        message_type: str = "RESPONSE",
        page_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送消息到 Facebook

        如果指定了page_id，会自动使用该页面的Token
        """
        # 如果指定了page_id，尝试使用该页面的Token
        if page_id:
            from src.config.page_token_manager import page_token_manager
            page_token = page_token_manager.get_token(page_id)
            if page_token:
                # 临时使用页面Token
                original_token = self.access_token
                self.access_token = page_token
                logger.info(
                    f"使用页面 {page_id} 的专用Token发送消息 (Token前10位: {page_token[:10]}...)")
                try:
                    result = await self._do_send_message(recipient_id, message, message_type, page_id)
                    # 检查是否是24小时窗口限制错误
                    if isinstance(result, dict) and result.get("24h_window_limit"):
                        # 抛出特殊异常，让调用方知道这是24小时窗口限制
                        from src.utils.exceptions import APIError
                        raise APIError(
                            message="24小时消息发送窗口限制",
                            api_name="Facebook",
                            status_code=400,
                            details={"error_subcode": result.get("error", {}).get("error_subcode")}
                        )
                    return result
                finally:
                    # 恢复原始Token
                    self.access_token = original_token
            else:
                logger.warning(
                    f"未找到页面 {page_id} 的Token，使用默认Token (当前Token前10位: {self.access_token[:10]}...)")

        # 使用当前Token发送
        return await self._do_send_message(recipient_id, message, message_type, page_id)

    async def _do_send_message(
        self,
        recipient_id: str,
        message: str,
        message_type: str = "RESPONSE",
        page_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送消息到 Facebook

        Args:
            recipient_id: 接收者 Facebook ID
            message: 消息内容
            message_type: 消息类型 (RESPONSE, UPDATE, MESSAGE_TAG)
            page_id: 页面ID，如果提供则使用页面ID，否则使用 'me'

        Returns:
            API 响应
        """
        # 验证消息格式
        if not recipient_id or not recipient_id.strip():
            raise ValueError("recipient_id不能为空")

        if not message or not message.strip():
            raise ValueError("消息内容不能为空")

        # Facebook消息长度限制为2000字符
        if len(message) > 2000:
            logger.warning(f"消息长度超过2000字符，将被截断: {len(message)}")
            message = message[:1997] + "..."

        # 使用页面ID或 'me'
        endpoint = f"{page_id}/messages" if page_id else "me/messages"
        url = f"{self.base_url}/{endpoint}"

        # 记录调试信息（减少日志量以降低CPU使用）
        logger.debug(
            f"Facebook send_message - page_id={page_id}, endpoint={endpoint}, recipient_id={recipient_id[:10]}...")

        params = {"access_token": self.access_token}
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": message},
            "messaging_type": message_type
        }

        try:
            response = await self.client.post(url, params=params, json=data)

            # 记录详细的错误信息
            if response.status_code != 200:
                error_detail = None
                is_24h_window_error = False
                
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get("error", {})
                    error_code = error_msg.get("code")
                    error_message = error_msg.get("message", "未知错误")
                    error_subcode = error_msg.get("error_subcode")

                    # 检查是否是24小时窗口限制错误
                    if error_code == 10 and error_subcode in [2018001, 2018278]:
                        is_24h_window_error = True
                        logger.warning(
                            f"⚠️ 超过24小时消息发送窗口限制（错误码{error_subcode}）。"
                            f"用户超过24小时未发送消息，无法使用RESPONSE类型回复。"
                            f"如需发送，需要使用消息标签（Message Tags）。"
                        )
                    else:
                        logger.error(
                            f"Facebook API error: {error_message} (code: {error_code}, subcode: {error_subcode})")
                        # 记录完整的错误详情（用于调试）
                        logger.info(f"Full error detail: {error_detail}")
                        logger.error(f"Facebook API 400错误详情: {error_detail}")

                        # 提供更友好的错误提示
                        if error_code == 10:  # OAuth错误
                            # 其他OAuth错误
                            if "权限" in error_message or "permission" in error_message.lower():
                                logger.error(
                                    "权限不足，请检查Access Token是否有pages_messaging权限"
                                )
                            else:
                                logger.error(f"OAuth错误: {error_message}")
                        elif error_code == 100:  # 参数错误
                            logger.error(f"参数错误: {error_message}")

                except Exception as e:
                    error_detail = response.text
                    logger.error(
                        f"Facebook API error (non-JSON): {error_detail[:200]}")

                # 如果是24小时窗口错误，不抛出异常，返回特殊结果
                if is_24h_window_error:
                    return {
                        "error": {
                            "message": "24小时消息发送窗口限制",
                            "code": 10,
                            "error_subcode": error_subcode
                        },
                        "24h_window_limit": True
                    }

                # 记录请求详情（不包含敏感信息）
                logger.error(f"Request URL: {url}")
                logger.error(
                    f"Request data: recipient_id={recipient_id}, message_type={message_type}, message_length={len(message)}")

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # 重新抛出以便上层处理
            raise
        except Exception as e:
            logger.error(f"发送Facebook消息时发生未预期的错误: {str(e)}", exc_info=True)
            raise

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息

        Args:
            user_id: Facebook 用户 ID

        Returns:
            用户信息
        """
        url = f"{self.base_url}/{user_id}"
        params = {
            "access_token": self.access_token,
            "fields": "id,name,first_name,last_name,profile_pic"
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def comment_on_post(
        self,
        post_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        在帖子下评论

        Args:
            post_id: 帖子 ID
            message: 评论内容

        Returns:
            API 响应
        """
        url = f"{self.base_url}/{post_id}/comments"
        params = {"access_token": self.access_token}
        data = {"message": message}

        response = await self.client.post(url, params=params, json=data)
        response.raise_for_status()
        return response.json()

    async def verify_webhook(
        self,
        mode: str,
        token: str,
        challenge: str
    ) -> Optional[str]:
        """
        验证 Webhook 订阅

        Args:
            mode: 验证模式
            token: 验证令牌
            challenge: 挑战字符串

        Returns:
            如果验证成功返回 challenge，否则返回 None
        """
        if mode == "subscribe" and token == settings.facebook_verify_token:
            return challenge
        return None

    async def get_conversations(self, page_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get all conversations for a page
        
        Args:
            page_id: Page ID
            limit: Maximum number of conversations to retrieve (default: 25)
        
        Returns:
            List of conversation objects
        """
        url = f"{self.base_url}/{page_id}/conversations"
        params = {
            "access_token": self.access_token,
            "fields": "id,updated_time,message_count,unread_count",
            "limit": limit
        }
        
        try:
            response = await self.client.get(url, params=params)
            
            # Handle 400 errors gracefully (API endpoint may not be available)
            if response.status_code == 400:
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get("error", {})
                    error_message = error_msg.get("message", "Bad Request")
                    error_code = error_msg.get("code")
                    
                    logger.warning(
                        f"Facebook API 400 error for page {page_id}: {error_message} (code: {error_code}). "
                        f"This endpoint may not be available or may require different permissions. "
                        f"Returning empty list to continue processing other pages."
                    )
                    return []  # Return empty list instead of raising exception
                except:
                    logger.warning(f"Facebook API 400 error for page {page_id}: Unable to parse error details. Returning empty list.")
                    return []
            
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except httpx.HTTPStatusError as e:
            # Handle other HTTP errors
            if e.response.status_code == 403:
                logger.error(f"Permission denied for page {page_id}. Ensure the token has 'pages_messaging' permission.")
                return []  # Return empty list instead of raising
            elif e.response.status_code == 401:
                logger.error(f"Unauthorized for page {page_id}. Token may be expired or invalid.")
                return []  # Return empty list instead of raising
            else:
                logger.error(f"Failed to get conversations for page {page_id}: HTTP {e.response.status_code}")
                return []  # Return empty list to allow other pages to continue
        except Exception as e:
            logger.error(f"Error getting conversations for page {page_id}: {str(e)}", exc_info=True)
            return []  # Return empty list instead of raising
    
    async def get_conversation_messages(
        self, 
        conversation_id: str, 
        page_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get messages in a conversation
        
        Args:
            conversation_id: Conversation ID (PSID format)
            page_id: Page ID (optional, for logging)
            limit: Maximum number of messages to retrieve (default: 10)
        
        Returns:
            List of message objects, ordered by time (newest first)
        """
        url = f"{self.base_url}/{conversation_id}/messages"
        params = {
            "access_token": self.access_token,
            "fields": "id,message,from,created_time,attachments",
            "limit": limit
        }
        
        try:
            response = await self.client.get(url, params=params)
            
            # Handle 400 errors gracefully
            if response.status_code == 400:
                logger.warning(f"Facebook API 400 error for conversation {conversation_id}. Returning empty list.")
                return []
            
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get messages for conversation {conversation_id}: HTTP {e.response.status_code}")
            return []  # Return empty list instead of raising
        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}", exc_info=True)
            return []  # Return empty list instead of raising
    
    async def check_unreplied_messages(
        self, 
        page_id: str, 
        threshold_minutes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Check for unreplied messages in a page's conversations
        
        Args:
            page_id: Page ID
            threshold_minutes: Time threshold in minutes (default: 5)
        
        Returns:
            List of unreplied message objects with conversation info
        """
        from datetime import datetime, timezone, timedelta
        
        unreplied_messages = []
        
        try:
            # Get all conversations
            conversations = await self.get_conversations(page_id, limit=50)
            logger.info(f"Found {len(conversations)} conversations for page {page_id}")
            
            # Calculate threshold time
            threshold_time = datetime.now(timezone.utc) - timedelta(minutes=threshold_minutes)
            
            for idx, conv in enumerate(conversations):
                try:
                    # Add delay between API calls to avoid rate limiting
                    if idx > 0:
                        await asyncio.sleep(0.3)  # 0.3 second delay between conversation API calls
                    
                    # Get the last few messages in the conversation
                    messages = await self.get_conversation_messages(conv["id"], page_id, limit=5)
                    
                    if not messages:
                        continue
                    
                    # Get the most recent message
                    last_message = messages[0]
                    
                    # Check if message has content
                    if not last_message.get("message"):
                        continue
                    
                    # Check if message is from user (not from page)
                    from_info = last_message.get("from", {})
                    message_from_id = from_info.get("id")
                    
                    # If message is from the page itself, skip (we sent it)
                    # Page ID format is numeric, user IDs are also numeric but different
                    # We'll check by comparing with page_id - if they match, it's from the page
                    if message_from_id == page_id:
                        continue
                    
                    # Parse created_time
                    created_time_str = last_message.get("created_time")
                    if not created_time_str:
                        continue
                    
                    # Parse ISO format time
                    try:
                        # Try standard ISO format first
                        if created_time_str.endswith('Z'):
                            created_time = datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
                        else:
                            created_time = datetime.fromisoformat(created_time_str)
                    except:
                        # Try parsing with strptime
                        try:
                            created_time = datetime.strptime(created_time_str, "%Y-%m-%dT%H:%M:%S%z")
                        except:
                            # If all parsing fails, skip this message
                            logger.warning(f"Could not parse time: {created_time_str}")
                            continue
                    
                    # Ensure timezone-aware
                    if created_time.tzinfo is None:
                        created_time = created_time.replace(tzinfo=timezone.utc)
                    
                    # Check if message is older than threshold
                    if created_time <= threshold_time:
                        # This is a potential unreplied message
                        # We need to verify it's from a user, not from the page
                        # For now, we'll include it and let the spam detection filter it
                        unreplied_messages.append({
                            "conversation_id": conv["id"],
                            "message": last_message,
                            "page_id": page_id,
                            "created_time": created_time
                        })
                
                except Exception as e:
                    logger.warning(f"Error processing conversation {conv.get('id')}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(unreplied_messages)} potentially unreplied messages for page {page_id}")
            return unreplied_messages
        
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors gracefully
            if e.response.status_code == 400:
                logger.warning(
                    f"Facebook API 400 error when checking unreplied messages for page {page_id}. "
                    f"This endpoint may not be available. Skipping this page."
                )
            else:
                logger.error(f"HTTP error checking unreplied messages for page {page_id}: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error checking unreplied messages for page {page_id}: {str(e)}", exc_info=True)
            return []

    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
