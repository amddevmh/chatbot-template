#!/usr/bin/env python3
"""
API routes for the nutrition assistant
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.message import MessageRequest, MessageResponse
from app.services.message_service import MessageService
from app.auth.security import User, get_current_user

router = APIRouter()

# Dependency to get the message service
def get_message_service():
    return MessageService()

@router.post("/messages/process", response_model=MessageResponse)
async def process_message(
    request: MessageRequest,
    current_user: User = Depends(get_current_user),
    service: MessageService = Depends(get_message_service)
):
    """
    Process a user message
    
    Args:
        request: The message request
        current_user: The authenticated user
        service: The message service
        
    Returns:
        The processed message response
    """
    response = await service.process_message(request, current_user.username)
    return response


