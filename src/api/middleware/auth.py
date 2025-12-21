"""认证中间件"""

import hashlib
import hmac
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


def verify_webhook_signature(
    request: Request, signature: Optional[str] = None, secret: Optional[str] = None
) -> bool:
    """
    验证Webhook签名

    Args:
        request: FastAPI请求对象
        signature: 签名（从请求头获取）
        secret: 密钥

    Returns:
        验证是否通过
    """
    if not signature or not secret:
        return False

    # 获取请求体
    body = request.body()
    if not body:
        return False

    # 计算HMAC签名
    expected_signature = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    # 比较签名（使用安全比较避免时序攻击）
    return hmac.compare_digest(signature, expected_signature)


class AuthMiddleware:
    """认证中间件"""

    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """
        验证API Token

        Args:
            credentials: HTTP Bearer凭证

        Returns:
            用户ID或标识
        """
        token = credentials.credentials

        # 简单的Token验证（生产环境应使用JWT等）
        # 这里可以从数据库或Redis验证Token
        api_token = getattr(settings, "api_token", None)
        
        if not api_token:
            logger.warning("API_TOKEN未配置，认证将失败。请在环境变量中设置API_TOKEN")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="API authentication is not configured. Please set API_TOKEN environment variable.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if token == api_token:
            return "api_user"

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
