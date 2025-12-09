"""配置加载器 - 加载YAML等配置文件"""
import os
from typing import Dict, Any
import yaml


def load_yaml_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """加载 YAML 配置文件
    
    Args:
        config_path: YAML配置文件路径
        
    Returns:
        配置字典，如果文件不存在则返回空字典
    """
    if not os.path.exists(config_path):
        return {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config if config is not None else {}
    except (yaml.YAMLError, IOError) as e:
        print(f"⚠️  加载YAML配置文件失败: {e}")
        return {}


# 全局YAML配置
yaml_config = load_yaml_config()






