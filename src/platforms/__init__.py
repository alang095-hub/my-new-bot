"""平台抽象层模块"""
# 按依赖顺序导入，避免循环导入
from src.platforms.base import (
    PlatformClient,
    PlatformParser,
    PlatformWebhookHandler
)

# 先导入 registry（manager 依赖它）
from src.platforms.registry import PlatformRegistry, registry

# 延迟导入 manager 以避免可能的循环导入问题
# 使用 __getattr__ 实现延迟导入
def __getattr__(name):
    if name in ("PlatformManager", "platform_manager"):
        # 延迟导入，避免在模块初始化时立即导入
        from src.platforms.manager import PlatformManager as _PlatformManager
        from src.platforms.manager import platform_manager as _platform_manager
        
        # 将导入的对象缓存到模块命名空间
        import sys
        current_module = sys.modules[__name__]
        setattr(current_module, "PlatformManager", _PlatformManager)
        setattr(current_module, "platform_manager", _platform_manager)
        
        if name == "PlatformManager":
            return _PlatformManager
        elif name == "platform_manager":
            return _platform_manager
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "PlatformClient",
    "PlatformParser",
    "PlatformWebhookHandler",
    "PlatformRegistry",
    "registry",
    "PlatformManager",
    "platform_manager",
]
