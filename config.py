from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ESB Configuration
    esb1_base_url: str = "http://localhost:8001"  # ESB1 for IMS routing
    esb3_base_url: str = "http://localhost:8003"  # ESB3 for DMS routing
    
    # Database Configuration
    database_url: str = "sqlite:///./wms.db"
    
    # API Configuration
    app_title: str = "ShipOra WMS API"
    app_version: str = "1.0.0"
    app_description: str = "Warehouse Management System for ShipOra Platform"
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    # External Service Timeouts
    ims_timeout: float = 30.0
    dms_timeout: float = 30.0
    dms_max_retries: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
