"""页面设置管理 - 管理每个页面的自动回复配置"""
from typing import Dict, Any, List, Optional
from src.config.loader import load_yaml_config
import os


class PageSettings:
    """页面设置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化页面设置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = load_yaml_config(config_path)
        self._page_settings = self.config.get("page_settings", {})
    
    def is_auto_reply_enabled(self, page_id: Optional[str] = None) -> bool:
        """
        检查指定页面是否启用自动回复
        
        Args:
            page_id: 页面ID，如果为None则检查全局设置
            
        Returns:
            是否启用自动回复
        """
        # 先检查全局设置
        auto_reply_config = self.config.get("auto_reply", {})
        global_enabled = auto_reply_config.get("enabled", True)
        
        if not global_enabled:
            return False
        
        # 如果没有指定页面ID，返回全局设置
        if not page_id:
            return global_enabled
        
        # 检查页面特定设置
        page_config = self._page_settings.get(page_id, {})
        
        # 如果页面有特定配置，使用页面配置；否则使用全局配置
        if "auto_reply_enabled" in page_config:
            return page_config.get("auto_reply_enabled", True)
        
        return global_enabled
    
    def get_page_config(self, page_id: str) -> Dict[str, Any]:
        """
        获取页面配置
        
        Args:
            page_id: 页面ID
            
        Returns:
            页面配置字典
        """
        return self._page_settings.get(page_id, {})
    
    def get_all_pages(self) -> List[str]:
        """
        获取所有已配置的页面ID列表
        
        Returns:
            页面ID列表
        """
        return list(self._page_settings.keys())
    
    def add_page(self, page_id: str, auto_reply_enabled: bool = True, **kwargs) -> bool:
        """
        添加或更新页面配置
        
        Args:
            page_id: 页面ID
            auto_reply_enabled: 是否启用自动回复
            **kwargs: 其他页面配置
            
        Returns:
            是否成功
        """
        try:
            # 读取现有配置
            if os.path.exists(self.config_path):
                import yaml
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {}
            
            # 初始化page_settings
            if "page_settings" not in config:
                config["page_settings"] = {}
            
            # 更新页面配置
            config["page_settings"][page_id] = {
                "auto_reply_enabled": auto_reply_enabled,
                **kwargs
            }
            
            # 写回文件
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            # 更新内存中的配置
            self.config = config
            self._page_settings = config.get("page_settings", {})
            
            return True
        except Exception as e:
            print(f"保存页面配置失败: {e}")
            return False
    
    def remove_page(self, page_id: str) -> bool:
        """
        移除页面配置
        
        Args:
            page_id: 页面ID
            
        Returns:
            是否成功
        """
        try:
            if page_id not in self._page_settings:
                return False
            
            # 读取现有配置
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            
            # 移除页面配置
            if "page_settings" in config and page_id in config["page_settings"]:
                del config["page_settings"][page_id]
            
            # 写回文件
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            # 更新内存中的配置
            self.config = config
            self._page_settings = config.get("page_settings", {})
            
            return True
        except Exception as e:
            print(f"移除页面配置失败: {e}")
            return False


# 全局页面设置实例
page_settings = PageSettings()




