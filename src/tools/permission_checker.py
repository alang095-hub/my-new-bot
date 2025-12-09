"""权限检查工具模块"""
import httpx
from typing import Dict, Any, List, Optional
from .base import BaseTool, ToolResult, ToolStatus


# 定义所需权限
REQUIRED_PERMISSIONS = {
    "基础权限": [
        "pages_messaging",
        "pages_read_engagement",
        "pages_manage_metadata"
    ],
    "帖子管理": [
        "pages_manage_posts"
    ],
    "广告管理": [
        "ads_read",
        "ads_management"
    ]
}


class PermissionChecker(BaseTool):
    """权限检查器 - 检查Facebook访问令牌的权限"""
    
    def __init__(self):
        super().__init__(
            name="permission_checker",
            description="Facebook权限检查工具"
        )
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def check_permissions(self, access_token: str) -> ToolResult:
        """检查访问令牌的权限"""
        if not access_token:
            return ToolResult(
                status=ToolStatus.ERROR,
                message="访问令牌不能为空",
                errors=["请提供有效的访问令牌"]
            )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 获取权限列表
                url = f"{self.base_url}/me/permissions"
                params = {"access_token": access_token}
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                permissions: List[Dict[str, Any]] = data.get("data", [])
                
                # 检查每个权限
                granted_permissions: Dict[str, bool] = {}
                for perm in permissions:
                    perm_name = perm.get("permission", "unknown")
                    status = perm.get("status", "unknown")
                    granted_permissions[perm_name] = status == "granted"
                
                # 检查所需权限
                missing_permissions = []
                granted_required = []
                
                for category, perms in REQUIRED_PERMISSIONS.items():
                    for perm in perms:
                        if perm in granted_permissions:
                            if granted_permissions[perm]:
                                granted_required.append(perm)
                            else:
                                missing_permissions.append(f"{perm} (未授予)")
                        else:
                            missing_permissions.append(f"{perm} (未找到)")
                
                # 获取令牌信息
                token_info = {}
                try:
                    debug_url = f"{self.base_url}/debug_token"
                    debug_params = {
                        "input_token": access_token,
                        "access_token": access_token
                    }
                    
                    debug_response = await client.get(debug_url, params=debug_params)
                    debug_response.raise_for_status()
                    debug_data = debug_response.json().get("data", {})
                    
                    token_info = {
                        'app_id': debug_data.get('app_id'),
                        'user_id': debug_data.get('user_id'),
                        'type': debug_data.get('type'),
                        'expires_at': debug_data.get('expires_at', 0),
                        'scopes': debug_data.get("scopes", [])
                    }
                except Exception:
                    pass
                
                if missing_permissions:
                    return ToolResult(
                        status=ToolStatus.WARNING,
                        message="部分权限未授予",
                        errors=missing_permissions,
                        data={
                            'granted_permissions': granted_required,
                            'missing_permissions': missing_permissions,
                            'all_permissions': list(granted_permissions.keys()),
                            'token_info': token_info
                        }
                    )
                else:
                    return ToolResult(
                        status=ToolStatus.SUCCESS,
                        message="所有必需权限已授予",
                        data={
                            'granted_permissions': granted_required,
                            'all_permissions': list(granted_permissions.keys()),
                            'token_info': token_info
                        }
                    )
                
        except httpx.HTTPStatusError as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                message=f"API请求失败: {e.response.status_code}",
                errors=[f"错误信息: {e.response.text}"]
            )
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                message=f"检查失败: {str(e)}",
                errors=[str(e)]
            )
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行权限检查"""
        access_token = kwargs.get('access_token')
        
        if not access_token:
            return ToolResult(
                status=ToolStatus.ERROR,
                message="缺少访问令牌",
                errors=["请提供access_token参数"]
            )
        
        return await self.check_permissions(access_token)






