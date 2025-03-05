#!/usr/bin/env python3
"""
Authentication routes for the nutrition assistant
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from datetime import timedelta

from app.auth.security import (
    create_access_token,
    Token,
    User,
    get_current_user
)
from app.config import settings

router = APIRouter()



@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user

@router.post("/test-token", response_model=Token)
async def get_test_token(test_auth: str = Header(None)):
    """
    Get a test token for development purposes
    
    This endpoint is only available in non-production environments
    """
    if settings.is_production:
        raise HTTPException(status_code=404, detail="Not found")
    
    if test_auth != settings.AUTH_BYPASS_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid test authentication"
        )
    
    access_token = create_access_token(data={"sub": "test_user"})
    return {"access_token": access_token, "token_type": "bearer"}
