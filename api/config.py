from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "sqlite:///./ai_roleplay.db"
    
    # JWT配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI服务配置
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    openrouter_api_key: str = ""
    default_ai_model: str = "gpt-3.5-turbo"
    ai_service_provider: str = "openai"
    
    # 应用配置
    app_name: str = "AI角色扮演网站"
    debug: bool = True
    
    # 文件上传配置
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()

# 确保上传目录存在
os.makedirs(settings.upload_dir, exist_ok=True)