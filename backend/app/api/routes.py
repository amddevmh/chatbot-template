#!/usr/bin/env python3
"""
API routes for the chatbot backend template
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.hello import HelloAuthenticatedRequest, HelloAuthenticatedResponse
from app.models.chat import ChatRequest, ChatResponse
from app.services.hello_service import HelloAuthenticatedService
from app.services.chat_service import ChatService
from app.auth.security import User, get_current_user

router = APIRouter()

# Dependency providers
def get_hello_service():
    """Provide HelloAuthenticatedService instance"""
    return HelloAuthenticatedService()

def get_chat_service():
    """Provide ChatService instance"""
    return ChatService()

# Health check endpoint
@router.get("/health")
async def health_check():
    """Check API health"""
    return {"status": "healthy", "message": "API is running"}

# Authenticated hello endpoint
@router.get("/hello_authenticated", response_model=HelloAuthenticatedResponse)
async def say_hello_authenticated(
    current_user: User = Depends(get_current_user),
    service: HelloAuthenticatedService = Depends(get_hello_service)
):
    """Return a personalized greeting for authenticated users"""
    response = await service.say_hello(None, current_user.username)
    return response

# Chat endpoint
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    """Handle chat requests with the LLM"""
    try:
        llm_response = await service.get_chat_response(request.message)
        return {"response": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))