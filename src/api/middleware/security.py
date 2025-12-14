"""安全中间件"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging
from src.utils.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """处理请求"""
        start_time = time.time()
        
        try:
            # 获取客户端IP
            client_ip = request.client.host if request.client else "unknown"
            
            # 限流检查（排除健康检查端点）
            if request.url.path not in ["/health", "/metrics", "/docs", "/openapi.json", "/redoc", "/test/webhook-config"]:
                try:
                    # 使用正确的参数名：default_max 和 default_window
                    if not rate_limiter.is_allowed(f"ip:{client_ip}", default_max=100, default_window=60):
                        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                        return JSONResponse(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            content={
                                "error": "Too many requests",
                                "message": "Rate limit exceeded. Please try again later."
                            }
                        )
                except Exception as e:
                    logger.error(f"Error in rate limiter: {str(e)}", exc_info=True)
                    # 如果限流器出错，继续处理请求（不阻塞）
            
            # 添加安全头
            response = await call_next(request)
            
            # 设置安全响应头
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # 记录请求时间
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            
            return response
        except Exception as e:
            logger.error(f"Error in SecurityMiddleware: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": str(e),
                    "type": type(e).__name__
                }
            )


def rate_limit_middleware(request: Request) -> None:
    """限流中间件装饰器"""
    client_ip = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(f"api:{client_ip}", default_max=60, default_window=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

