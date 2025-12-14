"""配置验证器 - 验证配置的有效性"""
from typing import Dict, Any
from .settings import Settings


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, settings: Settings):
        """
        初始化验证器
        
        Args:
            settings: 设置实例
        """
        self.settings = settings
    
    def validate_facebook_config(self) -> Dict[str, Any]:
        """
        验证Facebook配置
        
        Returns:
            验证结果字典，包含status和errors
        """
        errors = []
        
        # 检查必需配置
        required_fields = [
            ('facebook_app_id', 'FACEBOOK_APP_ID'),
            ('facebook_app_secret', 'FACEBOOK_APP_SECRET'),
            ('facebook_access_token', 'FACEBOOK_ACCESS_TOKEN'),
            ('facebook_verify_token', 'FACEBOOK_VERIFY_TOKEN')
        ]
        
        for field_name, env_name in required_fields:
            value = getattr(self.settings, field_name, None)
            if not value or value.startswith('your_'):
                errors.append(f"{env_name} 未配置或为占位符")
        
        return {
            'status': 'success' if not errors else 'error',
            'errors': errors
        }
    
    def validate_all(self) -> Dict[str, Any]:
        """
        验证所有配置
        
        Returns:
            验证结果字典
        """
        results = {
            'facebook': self.validate_facebook_config(),
            'overall_status': 'success'
        }
        
        all_errors = []
        for section, result in results.items():
            if section != 'overall_status' and result.get('errors'):
                all_errors.extend(result['errors'])
        
        if all_errors:
            results['overall_status'] = 'error'
            results['all_errors'] = all_errors
        
        return results

