"""应用设置 - 从环境变量加载配置"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ValidationError
from pathlib import Path
import sys


def get_env_name_for_field(field_name: str) -> str:
    """根据字段名获取对应的环境变量名"""
    field_to_env = {
        'database_url': 'DATABASE_URL',
        'facebook_app_id': 'FACEBOOK_APP_ID',
        'facebook_app_secret': 'FACEBOOK_APP_SECRET',
        'facebook_access_token': 'FACEBOOK_ACCESS_TOKEN',
        'facebook_verify_token': 'FACEBOOK_VERIFY_TOKEN',
        'openai_api_key': 'OPENAI_API_KEY',
        'telegram_bot_token': 'TELEGRAM_BOT_TOKEN',
        'telegram_chat_id': 'TELEGRAM_CHAT_ID',
        'secret_key': 'SECRET_KEY',
    }
    return field_to_env.get(field_name, field_name.upper())


class Settings(BaseSettings):
    """应用配置"""
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_echo: bool = Field(False, env="DATABASE_ECHO")
    
    # Facebook
    facebook_app_id: str = Field(..., env="FACEBOOK_APP_ID")
    facebook_app_secret: str = Field(..., env="FACEBOOK_APP_SECRET")
    facebook_access_token: str = Field(..., env="FACEBOOK_ACCESS_TOKEN")
    facebook_verify_token: str = Field(..., env="FACEBOOK_VERIFY_TOKEN")
    
    # Instagram (可选，如果未设置则使用Facebook的配置)
    instagram_access_token: Optional[str] = Field(None, env="INSTAGRAM_ACCESS_TOKEN")
    instagram_verify_token: Optional[str] = Field(None, env="INSTAGRAM_VERIFY_TOKEN")
    instagram_user_id: Optional[str] = Field(None, env="INSTAGRAM_USER_ID")
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    openai_temperature: float = Field(0.7, env="OPENAI_TEMPERATURE")
    
    # Telegram
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(..., env="TELEGRAM_CHAT_ID")
    
    # ManyChat
    manychat_api_key: Optional[str] = Field(None, env="MANYCHAT_API_KEY")
    manychat_api_url: str = Field("https://api.manychat.com", env="MANYCHAT_API_URL")
    
    # Botcake
    botcake_api_key: Optional[str] = Field(None, env="BOTCAKE_API_KEY")
    botcake_api_url: str = Field("https://api.botcake.com", env="BOTCAKE_API_URL")
    
    # Server
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(False, env="DEBUG")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    cors_origins: Optional[str] = Field(None, env="CORS_ORIGINS")  # 逗号分隔的允许来源列表
    
    @field_validator('facebook_access_token', 'facebook_app_id', 'facebook_app_secret')
    @classmethod
    def validate_facebook_config(cls, v: str) -> str:
        """验证Facebook配置不为占位符"""
        if v and v.startswith('your_'):
            raise ValueError(f"请配置有效的Facebook参数，当前为占位符: {v}")
        return v
    
    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        """验证OpenAI API密钥格式"""
        if v and v.startswith('your_'):
            raise ValueError("请配置有效的OpenAI API密钥")
        return v
    
    @field_validator('debug', mode='after')
    @classmethod
    def validate_production_config(cls, v: bool, info) -> bool:
        """验证生产环境配置"""
        # 检查是否在生产环境但启用了DEBUG模式
        import os
        is_production = os.getenv('ENVIRONMENT', '').lower() == 'production' or os.getenv('RAILWAY_ENVIRONMENT', '') or os.getenv('ZEABUR_ENVIRONMENT', '')
        
        if is_production and v:
            import warnings
            warnings.warn(
                "⚠️  警告：生产环境不应启用DEBUG模式！"
                "请设置环境变量 DEBUG=false",
                UserWarning
            )
        
        return v
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """验证SECRET_KEY强度"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY长度至少32字符，请使用更强的密钥")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        validate_assignment = True
    
    @property
    def project_root(self) -> Path:
        """获取项目根目录"""
        return Path(__file__).parent.parent.parent.parent
    
    @property
    def logs_dir(self) -> Path:
        """获取日志目录"""
        return self.project_root / "logs"


# 全局配置实例（带友好错误处理）
def _create_settings():
    """创建Settings实例，提供友好的错误信息"""
    try:
        return Settings()
    except ValidationError as e:
        missing_fields = []
        for error in e.errors():
            if error['type'] == 'missing':
                field_name = error['loc'][0]
                env_name = get_env_name_for_field(field_name)
                missing_fields.append(f"  - {env_name} (对应字段: {field_name})")
        
        if missing_fields:
            error_msg = "\n" + "="*60 + "\n"
            error_msg += "❌ 缺少必需的环境变量！\n"
            error_msg += "="*60 + "\n"
            error_msg += "\n请在Zeabur项目设置中配置以下环境变量：\n\n"
            for field in missing_fields:
                error_msg += field + "\n"
            error_msg += "\n参考文档: docs/production/ZEABUR_ENV_VARS_TEMPLATE.txt\n"
            error_msg += "="*60 + "\n"
            print(error_msg, file=sys.stderr)
        raise

# 创建全局settings实例
settings = _create_settings()

