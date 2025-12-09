"""插件系统基类 - 支持动态扩展"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .base import BaseTool


class Plugin(ABC):
    """插件基类 - 所有插件都应继承此类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        初始化插件
        
        Args:
            name: 插件名称
            version: 插件版本
        """
        self.name = name
        self.version = version
    
    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """
        获取插件提供的工具列表
        
        Returns:
            工具列表
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        获取插件依赖
        
        Returns:
            依赖插件名称列表
        """
        pass
    
    def on_load(self):
        """插件加载时调用"""
        pass
    
    def on_unload(self):
        """插件卸载时调用"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取插件信息
        
        Returns:
            插件信息字典
        """
        return {
            'name': self.name,
            'version': self.version,
            'tools': [tool.name for tool in self.get_tools()]
        }


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.tool_registry = None  # 将在初始化时设置
    
    def set_tool_registry(self, registry):
        """设置工具注册器"""
        self.tool_registry = registry
    
    def register_plugin(self, plugin: Plugin):
        """
        注册插件
        
        Args:
            plugin: 插件实例
        """
        # 检查依赖
        dependencies = plugin.get_dependencies()
        for dep in dependencies:
            if dep not in self.plugins:
                raise ValueError(f"插件 {plugin.name} 依赖 {dep}，但该插件未注册")
        
        # 注册插件
        self.plugins[plugin.name] = plugin
        
        # 加载插件
        plugin.on_load()
        
        # 注册插件提供的工具
        if self.tool_registry:
            for tool in plugin.get_tools():
                self.tool_registry.register(tool.name, tool.__class__)
    
    def unregister_plugin(self, plugin_name: str):
        """
        卸载插件
        
        Args:
            plugin_name: 插件名称
        """
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.on_unload()
            del self.plugins[plugin_name]
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        列出所有已注册的插件
        
        Returns:
            插件信息列表
        """
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        获取插件
        
        Args:
            name: 插件名称
            
        Returns:
            插件实例，如果不存在则返回None
        """
        return self.plugins.get(name)


# 全局插件管理器实例
plugin_manager = PluginManager()






