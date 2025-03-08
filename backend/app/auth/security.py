#!/usr/bin/env python3
"""
Security utilities for JWT authentication
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings
from app.models.user import User

# OAuth2 scheme for token extraction
# Note: We don't have a token URL since we're using dev tokens directly
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="",  # No token URL needed for dev tokens
    auto_error=False  # Don't auto-raise errors for missing tokens (for bypass)
)

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_dev_token() -> str:
    """
    Create a permanent development token that doesn't expire
    
    This token is used for development and testing purposes only.
    When used, it will automatically create a test user in the database
    with the following properties if it doesn't already exist:
    - Username: dev_test_user
    - Email: dev@example.com
    - Verified: True
    - Active: True
    
    Returns:
        JWT token string with no expiration
    """
    # Create a token with a very long expiration (100 years)
    to_encode = {"sub": "dev_test_user"}
    # No expiration date for dev token
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
            
        token_data = TokenData(sub=user_id)
        return token_data
        
    except JWTError:
        return None

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from the token
    
    If the token is a dev token (sub="dev_test_user"), this function will
    automatically create a test user in the database if it doesn't exist.
    
    Args:
        token: JWT token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check for token
    if not token:
        raise credentials_exception
    
    # Check if this is the dev token
    is_dev_token = False
    try:
        # Just decode without verification to check if it's our dev token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False}  # Don't verify expiration for this check
        )
        if payload.get("sub") == "dev_test_user":
            is_dev_token = True
    except JWTError:
        pass
    
    if is_dev_token:
        # This is a dev token, get or create the test user
        test_user = await User.find_one({"username": "dev_test_user"})
        
        if test_user is None:
            # Create a test user
            from app.services.user_service import UserService
            try:
                test_user = await UserService.create_user(
                    username="dev_test_user",
                    email="dev@example.com",
                    password="devpassword123"
                )
                # Automatically verify the test user
                test_user.is_verified = True
                test_user.is_active = True
                await test_user.save()
            except ValueError:
                # User might have been created in another process
                test_user = await User.find_one({"username": "dev_test_user"})
                if test_user is None:
                    raise credentials_exception
        
        return test_user
    else:
        # Normal token flow
        token_data = verify_token(token)
        
        if token_data is None:
            raise credentials_exception
            
        # Look up the user in the database
        user = await User.find_one({"username": token_data.sub})
        
        if user is None:
            raise credentials_exception
            
        return user


async def get_current_active_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active and verified user
    
    Args:
        current_user: Current user from token
        
    Returns:
        User object if active and verified
        
    Raises:
        HTTPException: If user is not active or verified
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    
    return current_user
