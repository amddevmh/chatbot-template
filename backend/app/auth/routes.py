#!/usr/bin/env python3
"""
Authentication routes
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

# Test token endpoint removed - use generate_dev_token.py instead
