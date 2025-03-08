#!/usr/bin/env python3
"""
Pydantic models for chat-related endpoints
"""
from pydantic import BaseModel

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str