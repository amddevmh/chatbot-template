#!/usr/bin/env python3
"""
Pydantic and Beanie models for chat sessions
"""
from datetime import datetime
from typing import List, Optional
from beanie import Document
from pydantic import BaseModel, Field


class ChatSessionMetadata(Document):
    """MongoDB document model for chat session metadata"""
    session_id: str = Field(..., description="Unique session identifier")
    username: str = Field(..., description="Username of the session owner")
    name: str = Field(default="New Chat", description="User-friendly name for the session")
    created_at: datetime = Field(default_factory=datetime.now, description="When the session was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the session was last updated")
    message_count: int = Field(default=0, description="Number of messages in the session")
    
    class Settings:
        name = "chat_sessions"
        indexes = [
            "username",  # Index for faster user-based queries
            "session_id",  # Index for faster session lookups
            [
                ("username", 1),
                ("updated_at", -1)
            ]  # Compound index for sorted user sessions
        ]


class ChatSessionCreate(BaseModel):
    """Request model for creating a new chat session"""
    name: str = Field(default="New Chat", description="User-friendly name for the session")


class ChatSessionResponse(BaseModel):
    """Response model for a single chat session"""
    session_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ChatSessionListResponse(BaseModel):
    """Response model for listing chat sessions"""
    sessions: List[ChatSessionResponse]
