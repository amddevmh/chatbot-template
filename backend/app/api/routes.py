#!/usr/bin/env python3
"""
API routes for the FastAPI starter template
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.hello import HelloAuthenticatedRequest, HelloAuthenticatedResponse
from app.services.hello_service import HelloAuthenticatedService
from app.auth.security import User, get_current_user

router = APIRouter()

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status of the API
    """
    return {"status": "healthy", "message": "API is running"}

# Dependencies to get services
def get_hello_authenticated_service():
    return HelloAuthenticatedService()

# POST endpoint for hello_authenticated has been removed

@router.get("/hello_authenticated", response_model=HelloAuthenticatedResponse)
async def say_hello_authenticated_get(
    current_user: User = Depends(get_current_user),
    service: HelloAuthenticatedService = Depends(get_hello_authenticated_service)
):
    """
    Get a simple greeting (GET method)
    
    Args:
        current_user: The authenticated user
        service: The hello authenticated service
        
    Returns:
        A personalized greeting response
    """
    response = await service.say_hello(None, current_user.username)
    return response
