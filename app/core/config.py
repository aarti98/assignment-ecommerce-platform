import os
from typing import Any, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "E-Commerce API"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    
    # For SQLAlchemy
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if v:
            return v
        return info.data.get("DATABASE_URL")

    # Security settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev_secret_key")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 