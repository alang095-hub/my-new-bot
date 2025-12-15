"""令牌交换工具模块"""
import requests
from typing import Optional, Dict, Any
from .base import BaseTool, ToolResult, ToolStatus
from .token_manager import TokenManager


class ExchangeTokenTool(BaseTool):
    """令牌交换工具 - 将短期令牌交换为长期令牌"""
    
    def __init__(self):
        super().__init__(
            name="exchange_token",
            description="Facebook短期令牌交换长期令牌工具"
        )
        self.token_manager = TokenManager()
        from src.core.config.constants import FACEBOOK_GRAPH_API_BASE_URL
        self.base_url = FACEBOOK_GRAPH_API_BASE_URL
    
    def get_config_value(self, key: str, placeholder: str = "") -> Optional[str]:
        """获取配置值"""
        # 先尝试从环境变量
        import os
        value = os.getenv(key)
        if value and value != placeholder:
            return value
        
        # 从.env文件读取
        return self.token_manager.read_env_value(key, placeholder)
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行令牌交换"""
        short_token = kwargs.get('short_token')
        app_id = kwargs.get('app_id')
        app_secret = kwargs.get('app_secret')
        
        # 如果没有提供，尝试从配置读取
        if not short_token:
            short_token = self.get_config_value("FACEBOOK_ACCESS_TOKEN", "your_facebook_access_token")
        
        if not app_id:
            app_id = self.get_config_value("FACEBOOK_APP_ID", "your_facebook_app_id")
        
        if not app_secret:
            app_secret = self.get_config_value("FACEBOOK_APP_SECRET", "your_facebook_app_secret")
        
        # 验证必需参数
        if not all([short_token, app_id, app_secret]):
            missing = []
            if not short_token:
                missing.append("short_token 或 FACEBOOK_ACCESS_TOKEN")
            if not app_id:
                missing.append("app_id 或 FACEBOOK_APP_ID")
            if not app_secret:
                missing.append("app_secret 或 FACEBOOK_APP_SECRET")
            
            return ToolResult(
                status=ToolStatus.ERROR,
                message="缺少必需参数",
                errors=[f"缺少: {', '.join(missing)}"]
            )
        
        # 交换令牌
        url = f"{self.base_url}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "access_token" in data:
                long_token = data["access_token"]
                expires_in = data.get("expires_in", "N/A")
                
                # 格式化过期时间
                expires_str = self.token_manager.format_expires_time(expires_in)
                
                result_data = {
                    'access_token': long_token,
                    'expires_in': expires_in,
                    'expires_str': expires_str
                }
                
                # 询问是否自动更新（如果是在交互模式下）
                auto_update = kwargs.get('auto_update', False)
                if auto_update:
                    if self.token_manager.update_env_file("FACEBOOK_ACCESS_TOKEN", long_token):
                        result_data['env_updated'] = True
                    else:
                        result_data['env_updated'] = False
                
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    message="令牌交换成功",
                    data=result_data
                )
            else:
                error_msg = data.get("error", {}).get("message", "未知错误")
                return ToolResult(
                    status=ToolStatus.ERROR,
                    message=f"交换失败: {error_msg}",
                    errors=[str(data.get("error", {}))]
                )
                
        except requests.exceptions.Timeout:
            return ToolResult(
                status=ToolStatus.ERROR,
                message="请求超时",
                errors=["请检查网络连接后重试"]
            )
        except requests.exceptions.RequestException as e:
            error_details = []
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_details.append(str(error_data))
                except:
                    error_details.append(e.response.text)
            else:
                error_details.append(str(e))
            
            return ToolResult(
                status=ToolStatus.ERROR,
                message="请求失败",
                errors=error_details
            )
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                message=f"发生未知错误: {str(e)}",
                errors=[str(e)]
            )









