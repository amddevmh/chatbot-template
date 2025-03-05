#!/usr/bin/env python3
"""
Message processing service for the nutrition assistant
"""
from app.models.message import MessageRequest, MessageResponse
from typing import Dict, Set, Optional
from datetime import date as Date

class MessageService:
    """Service for processing user messages"""
    
    def __init__(self):
        # No need for user validation here anymore - handled by auth system
        pass
    
    async def process_message(self, request: MessageRequest, username: str) -> MessageResponse:
        """
        Process a user message
        
        Args:
            request: The message request containing message and date
            username: The authenticated username
            
        Returns:
            A message response with success status, message, and detected intent
        """
        # Simple intent detection (placeholder)
        intent = "query" if "?" in request.message else "statement"
        
        # Create a personalized greeting message
        greeting = f"Hello {username}! "
        response_message = f"{greeting}Successfully processed message on {request.date}"
        
        return MessageResponse(
            success=True,
            message=response_message,
            intent=intent,
            user_id=username
        )
    
