"""配置模块 - 向后兼容导入"""
# 向后兼容：从新位置导入
from src.core.config import (
    settings,
    Settings,
    load_yaml_config,
    yaml_config,
    ConfigValidator,
)

__all__ = [
    'settings',
    'Settings',
    'load_yaml_config',
    'yaml_config',
    'ConfigValidator',
]
