"""平台管理器 - 统一管理所有平台"""
from typing import Dict, Optional, Any
import logging

# 延迟导入 registry 以避免循环导入
def _get_registry():
    """延迟获取 registry 实例"""
    from src.platforms.registry import registry
    return registry

logger = logging.getLogger(__name__)


class PlatformManager:
    """平台管理器 - 管理平台的初始化、配置和状态"""
    
    def __init__(self):
        """初始化平台管理器"""
        self._initialized_platforms: Dict[str, Dict[str, Any]] = {}
        self._enabled_platforms: Dict[str, bool] = {}
    
    def initialize_platform(
        self,
        platform_name: str,
        access_token: str,
        verify_token: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        初始化平台
        
        Args:
            platform_name: 平台名称（如 'facebook', 'instagram'）
            access_token: 访问令牌
            verify_token: 验证令牌（可选）
            base_url: API基础URL（可选）
            **kwargs: 其他平台特定参数
            
        Returns:
            是否初始化成功
        """
        try:
            # 检查平台是否已注册
            registry = _get_registry()
            client_class = registry.get_client_class(platform_name)
            if not client_class:
                logger.error(f"Platform {platform_name} is not registered")
                return False
            
            # 保存平台配置
            self._initialized_platforms[platform_name] = {
                "access_token": access_token,
                "verify_token": verify_token,
                "base_url": base_url,
                **kwargs
            }
            
            logger.info(f"Platform {platform_name} initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize platform {platform_name}: {str(e)}", exc_info=True)
            return False
    
    def enable_platform(self, platform_name: str) -> bool:
        """
        启用平台
        
        Args:
            platform_name: 平台名称
            
        Returns:
            是否启用成功
        """
        if platform_name not in self._initialized_platforms:
            logger.warning(f"Platform {platform_name} is not initialized, cannot enable")
            return False
        
        self._enabled_platforms[platform_name] = True
        logger.info(f"Platform {platform_name} enabled")
        return True
    
    def disable_platform(self, platform_name: str) -> bool:
        """
        禁用平台
        
        Args:
            platform_name: 平台名称
            
        Returns:
            是否禁用成功
        """
        self._enabled_platforms[platform_name] = False
        logger.info(f"Platform {platform_name} disabled")
        return True
    
    def is_platform_enabled(self, platform_name: str) -> bool:
        """
        检查平台是否已启用
        
        Args:
            platform_name: 平台名称
            
        Returns:
            是否已启用
        """
        return self._enabled_platforms.get(platform_name, False)
    
    def get_platform_config(self, platform_name: str) -> Optional[Dict[str, Any]]:
        """
        获取平台配置
        
        Args:
            platform_name: 平台名称
            
        Returns:
            平台配置字典，如果不存在则返回 None
        """
        return self._initialized_platforms.get(platform_name)
    
    def list_initialized_platforms(self) -> list:
        """
        列出所有已初始化的平台
        
        Returns:
            平台名称列表
        """
        return list(self._initialized_platforms.keys())
    
    def list_enabled_platforms(self) -> list:
        """
        列出所有已启用的平台
        
        Returns:
            平台名称列表
        """
        return [
            name for name, enabled in self._enabled_platforms.items()
            if enabled
        ]


# 全局平台管理器实例
platform_manager = PlatformManager()
