"""配置检查工具模块"""
import os
from typing import Dict, Any, List, Optional
from .base import BaseTool, ToolResult, ToolStatus


class ConfigChecker(BaseTool):
    """配置检查器 - 检查各种配置是否正确"""
    
    def __init__(self):
        super().__init__(
            name="config_checker",
            description="配置检查和验证工具"
        )
    
    def check_env_file(self) -> ToolResult:
        """检查.env文件是否存在"""
        if os.path.exists(".env"):
            return ToolResult(
                status=ToolStatus.SUCCESS,
                message=".env 文件存在",
                data={'file_exists': True}
            )
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                message=".env 文件不存在",
                errors=["请创建.env文件并配置必要的环境变量"]
            )
    
    def check_env_value(self, key: str, required: bool = True) -> ToolResult:
        """检查环境变量值"""
        value = os.getenv(key)
        
        if not value:
            if required:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    message=f"{key} 未配置",
                    errors=[f"请在.env文件中配置 {key}"]
                )
            else:
                return ToolResult(
                    status=ToolStatus.WARNING,
                    message=f"{key} 未配置（可选）",
                    data={'key': key, 'value': None}
                )
        
        # 检查是否为占位符
        if value.startswith('your_'):
            return ToolResult(
                status=ToolStatus.ERROR,
                message=f"{key} 仍为占位符",
                errors=[f"请将 {key} 替换为实际值"]
            )
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            message=f"{key} 已配置",
            data={'key': key, 'configured': True}
        )
    
    def check_facebook_config(self) -> ToolResult:
        """检查Facebook配置"""
        errors = []
        warnings = []
        data = {}
        
        # 检查必需配置
        required_keys = [
            'FACEBOOK_APP_ID',
            'FACEBOOK_APP_SECRET',
            'FACEBOOK_ACCESS_TOKEN',
            'FACEBOOK_VERIFY_TOKEN'
        ]
        
        for key in required_keys:
            result = self.check_env_value(key, required=True)
            if result.has_errors():
                errors.extend(result.errors or [])
            else:
                data[key] = 'configured'
        
        # 检查可选配置
        optional_keys = [
            'INSTAGRAM_ACCESS_TOKEN',
            'INSTAGRAM_VERIFY_TOKEN',
            'INSTAGRAM_USER_ID'
        ]
        
        for key in optional_keys:
            result = self.check_env_value(key, required=False)
            if result.has_warnings():
                warnings.append(f"{key} 未配置（可选）")
            else:
                data[key] = 'configured'
        
        if errors:
            return ToolResult(
                status=ToolStatus.ERROR,
                message="Facebook配置不完整",
                errors=errors,
                data=data
            )
        elif warnings:
            return ToolResult(
                status=ToolStatus.WARNING,
                message="Facebook配置基本完整，但缺少可选配置",
                errors=warnings,
                data=data
            )
        else:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                message="Facebook配置完整",
                data=data
            )
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行配置检查"""
        check_type = kwargs.get('type', 'all')
        
        if check_type == 'env_file':
            return self.check_env_file()
        elif check_type == 'facebook':
            return self.check_facebook_config()
        elif check_type == 'value':
            key = kwargs.get('key')
            required = kwargs.get('required', True)
            if not key:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    message="缺少key参数",
                    errors=["请指定要检查的环境变量名"]
                )
            return self.check_env_value(key, required)
        elif check_type == 'all':
            # 检查所有配置
            env_result = self.check_env_file()
            if env_result.has_errors():
                return env_result
            
            facebook_result = self.check_facebook_config()
            return facebook_result
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                message=f"未知检查类型: {check_type}",
                errors=[f"支持的类型: env_file, facebook, value, all"]
            )






