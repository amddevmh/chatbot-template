#!/usr/bin/env python3
"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr

from app.auth.models import AuthUser
from app.auth.security import require_auth
from app.auth.supabase_client import supabase
from app.config import settings

router = APIRouter()


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    name: str
    metadata: Dict[str, Any] = {}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: AuthUser = Depends(require_auth)):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        metadata=current_user.user_metadata
    )


class SetupDevUserResponse(BaseModel):
    """Response model for setup dev user"""
    message: str
    user_id: str
    email: str


@router.post("/setup-dev-user", response_model=SetupDevUserResponse)
async def setup_dev_user():
    """
    Create a development user in Supabase
    
    This endpoint is used for setting up the development environment.
    It creates a user in Supabase and returns the user data.
    """
    if settings.is_production:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available in development mode"
        )
    
    # Use service role key for admin operations
    from supabase import create_client
    admin_supabase = create_client(
        settings.SUPABASE_URL, 
        settings.SUPABASE_SERVICE_KEY
    )
    
    email = "dev@example.com"
    password = "devpassword123"
    
    try:
        # Check if user exists
        response = admin_supabase.auth.admin.get_user_by_email(email)
        if response.user:
            # User exists, return it
            return SetupDevUserResponse(
                message="Development user already exists",
                user_id=response.user.id,
                email=response.user.email
            )
    except Exception:
        # User doesn't exist, create it
        pass
    
    # Create user with auto-confirmed email
    response = admin_supabase.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {
            "name": "Development User",
            "avatar": "https://avatars.githubusercontent.com/u/1?v=4"
        }
    })
    
    return SetupDevUserResponse(
        message="Development user created successfully",
        user_id=response.user.id,
        email=response.user.email
    )
