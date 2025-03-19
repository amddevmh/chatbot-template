#!/usr/bin/env python3
"""
Configuration settings for the chatbot backend
"""
from pydantic import BaseModel, Field
from typing import List
import os
import pathlib
from datetime import timedelta
from dotenv import load_dotenv

# Get the app directory path
app_dir = pathlib.Path(__file__).parent

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(app_dir, '.env'))

class Settings(BaseModel):
    """Application settings"""
    # App settings
    APP_NAME: str = "Chatbot Backend Template"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # CORS settings
    # When using credentials, specific origins must be listed (can't use wildcard "*")
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretkey")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Auth bypass for testing
    AUTH_BYPASS_ENABLED: bool = Field(default=True, description="Enable auth bypass for testing")
    
    # LLM settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Default model, configurable
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

# Global settings instance
settings = Settings()