#!/usr/bin/env python3
"""
Security utilities for JWT authentication
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Annotated

from app.config import settings
from app.models.user import User

# API Key header for token extraction
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

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


def create_dev_token(username: str = "dev_test_user") -> str:
    """
    Create a permanent development token that doesn't expire
    
    This token is used for development and testing purposes only.
    When used, method get_current_user will automatically create a test user in the database
    with the following properties if it doesn't already exist:
    - Username: The provided username (defaults to "dev_test_user")
    - Email: {username}@example.com
    - Verified: True
    - Active: True
    
    Args:
        username: Optional custom username for the test user, defaults to "dev_test_user"
    
    Returns:
        JWT token string with no expiration
    """
    # Create a token with the specified username
    to_encode = {"sub": username}
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

async def get_current_user(authorization: Optional[str] = Depends(api_key_header)) -> User:
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
    if not authorization:
        raise credentials_exception
        
    # Extract token from Bearer header
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization  # Try to use the raw value if no Bearer prefix
    
    # Check if auth bypass is enabled and validate the token
    if settings.AUTH_BYPASS_ENABLED:
        try:
            # Decode without verification to check username
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False}  # Don't verify expiration for this check
            )
            username = payload.get("sub")
            if username:  # Any username in a valid token can be used for dev/test
                is_dev_token = True
                dev_username = username
        except JWTError:
            pass
    
    if settings.AUTH_BYPASS_ENABLED and 'is_dev_token' in locals() and is_dev_token:
        # This is a dev token, get or create the test user
        test_user = await User.find_one({"username": dev_username})
        
        if test_user is None:
            # Create a test user with the username from the token
            from app.services.user_service import UserService
            try:
                test_user = await UserService.create_user(
                    username=dev_username,
                    email=f"{dev_username}@example.com",
                    password="devpassword123"
                )
                # Mark as a test user and set appropriate flags
                test_user.is_test_user = True
                test_user.is_verified = True
                test_user.is_active = True
                await test_user.save()
            except ValueError:
                # User might have been created in another process
                test_user = await User.find_one({"username": dev_username})
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
