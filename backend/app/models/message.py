#!/usr/bin/env python3
"""
Message models for the nutrition assistant
"""
from pydantic import BaseModel, Field
from datetime import date as Date, datetime
from typing import Optional

class MessageRequest(BaseModel):
    """Request model for processing user messages"""
    message: str = Field(..., description="Message content from the user")
    date: Optional[Date] = Field(default_factory=lambda: datetime.now().date(), 
                                description="Date for the message, defaults to today")

class MessageResponse(BaseModel):
    """Response model for processed messages"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    intent: Optional[str] = Field(None, description="Detected intent from the message")
    user_id: Optional[str] = Field(None, description="User ID from authentication")
