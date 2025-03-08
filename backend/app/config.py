#!/usr/bin/env python3
"""
Configuration settings
"""
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import pathlib
from datetime import timedelta
from dotenv import load_dotenv

# Get the app directory path
app_dir = pathlib.Path(__file__).parent

# Load environment variables from .env file in the app directory
load_dotenv(dotenv_path=os.path.join(app_dir, '.env'))

class Settings(BaseModel):
    """Application settings"""
    # App settings
    APP_NAME: str = "FastAPI Starter Template"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]  # In production, replace with specific origins
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretkey")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Auth bypass for testing
    AUTH_BYPASS_ENABLED: bool = Field(default=True, description="Enable auth bypass for testing")
    # AUTH_BYPASS_SECRET removed - use generate_dev_token.py instead
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

# Global settings instance
settings = Settings()
