#!/usr/bin/env python3
"""
Hello authenticated models for the FastAPI starter template
"""
from pydantic import BaseModel, Field
from typing import Optional

class HelloAuthenticatedRequest(BaseModel):
    """Hello authenticated request model"""
    message: Optional[str] = Field(None, description="Optional message from the user")

class HelloAuthenticatedResponse(BaseModel):
    """Hello authenticated response model"""
    message: str = Field(..., description="Greeting message")
    username: str = Field(..., description="Username that was greeted")
