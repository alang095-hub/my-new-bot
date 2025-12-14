"""应用设置 - 从环境变量加载配置"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path


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


# 全局配置实例
settings = Settings()

