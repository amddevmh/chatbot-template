#!/usr/bin/env python3
"""
Hello authenticated service for the FastAPI starter template
"""
from app.models.hello import HelloAuthenticatedRequest, HelloAuthenticatedResponse
from typing import Optional

class HelloAuthenticatedService:
    """Hello authenticated service for greeting users by their username"""
    
    def __init__(self):
        # No need for user validation here - handled by auth system
        pass
    
    async def say_hello(self, request: Optional[HelloAuthenticatedRequest], username: str) -> HelloAuthenticatedResponse:
        """
        Generate a greeting for the user
        
        Args:
            request: The hello request (optional)
            username: The authenticated username
            
        Returns:
            A hello response with the greeting message
        """
        # Create a personalized greeting
        custom_message = ""
        if request and request.message:
            custom_message = f" {request.message}"
            
        greeting_message = f"Hello {username}!{custom_message}"
        
        return HelloAuthenticatedResponse(
            message=greeting_message,
            username=username
        )
