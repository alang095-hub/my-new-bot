"""令牌管理工具模块"""
import urllib.parse
import os
from typing import Optional, Dict, Any
from .base import BaseTool, ToolResult, ToolStatus


class TokenManager(BaseTool):
    """令牌管理器 - 处理访问令牌的提取、交换和管理"""
    
    def __init__(self):
        super().__init__(
            name="token_manager",
            description="Facebook访问令牌管理工具"
        )
    
    def extract_token_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """从重定向 URL 中提取 access_token
        
        Args:
            url: 包含访问令牌的重定向URL
            
        Returns:
            包含访问令牌信息的字典，如果提取失败则返回None
        """
        if not url or not isinstance(url, str):
            return None
            
        try:
            # 分离 fragment（# 后面的部分）
            if '#' in url:
                fragment = url.split('#', 1)[1]
                params = urllib.parse.parse_qs(fragment)
            else:
                # 尝试从查询参数中提取
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)

            if 'access_token' not in params or not params['access_token']:
                return None

            access_token = params['access_token'][0]
            expires_in = params.get('expires_in', ['N/A'])[0]
            token_type = params.get('token_type', ['bearer'])[0]

            return {
                'access_token': access_token,
                'expires_in': expires_in,
                'token_type': token_type
            }
        except (ValueError, KeyError, IndexError):
            return None
        except Exception:
            return None
    
    def read_env_value(self, key: str, default_placeholder: str = "") -> Optional[str]:
        """从.env文件读取配置值"""
        if not os.path.exists(".env"):
            return None
        
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(f"{key}="):
                        value = line.split("=", 1)[1].strip()
                        if value and value != default_placeholder:
                            return value
        except (IOError, ValueError):
            pass
        
        return None
    
    def update_env_file(self, key: str, value: str) -> bool:
        """更新 .env 文件中的值"""
        env_file = ".env"

        if not os.path.exists(env_file):
            return False

        try:
            # 读取文件
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 更新或添加配置
            updated = False
            new_lines = []
            for line in lines:
                if line.strip().startswith(f"{key}="):
                    new_lines.append(f"{key}={value}\n")
                    updated = True
                else:
                    new_lines.append(line)

            if not updated:
                # 如果不存在，添加到文件末尾
                new_lines.append(f"{key}={value}\n")

            # 写回文件
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            return True
        except Exception:
            return False
    
    def format_expires_time(self, expires_in: Any) -> str:
        """格式化过期时间"""
        if isinstance(expires_in, str) and expires_in.isdigit():
            expires_in = int(expires_in)
        elif not isinstance(expires_in, int):
            return "N/A"
        
        days = expires_in // 86400
        hours = (expires_in % 86400) // 3600
        
        if days > 0:
            return f"约 {days} 天 {hours} 小时"
        else:
            return f"约 {hours} 小时"
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行令牌管理操作"""
        action = kwargs.get('action', 'extract')
        
        if action == 'extract':
            url = kwargs.get('url')
            if not url:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    message="缺少URL参数",
                    errors=["url参数是必需的"]
                )
            
            token_info = self.extract_token_from_url(url)
            if token_info:
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    message="令牌提取成功",
                    data=token_info
                )
            else:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    message="无法从URL中提取访问令牌",
                    errors=["URL格式可能不正确"]
                )
        
        elif action == 'update_env':
            key = kwargs.get('key')
            value = kwargs.get('value')
            
            if not key or not value:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    message="缺少必需参数",
                    errors=["key和value参数是必需的"]
                )
            
            if self.update_env_file(key, value):
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    message=f"已更新 {key} 到 .env 文件",
                    data={'key': key}
                )
            else:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    message="更新 .env 文件失败",
                    errors=["无法写入.env文件"]
                )
        
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                message=f"未知操作: {action}",
                errors=[f"支持的操作: extract, update_env"]
            )






