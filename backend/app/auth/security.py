#!/usr/bin/env python3
"""
Security utilities for JWT authentication
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
import logging

from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Annotated, Optional

from app.config import settings
from app.models.user import User
from app.auth.supabase_client import supabase
from app.auth.models import AuthUser

# Get logger for this module
logger = logging.getLogger(__name__)

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

async def get_current_user(authorization: Optional[str] = Depends(api_key_header)) -> AuthUser:
    """
    Get the current user from the token using Supabase authentication
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token with Supabase
    3. Creates an AuthUser object with the user information
    
    If the token is a dev token and AUTH_BYPASS_ENABLED is true, this function will
    use the legacy JWT verification.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        AuthUser object
        
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
        logger.warning("401 Unauthorized: No authorization header provided")
        raise credentials_exception
        
    # Extract token from Bearer header
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        logger.info(f"Bearer token provided: {token[:10]}...")
    else:
        token = authorization  # Try to use the raw value if no Bearer prefix
        logger.info(f"Raw token provided: {token[:10]}...")
    
    # First try Supabase authentication
    try:
        # Verify token with Supabase
        response = supabase.auth.get_user(token)
        supabase_user = response.user
        
        if not supabase_user:
            logger.warning(f"401 Unauthorized: Supabase returned no user for token")
            raise credentials_exception
        
        logger.info(f"User verified with Supabase: {supabase_user.email}")
        
        # Create AuthUser object directly from Supabase user
        auth_user = AuthUser(
            id=supabase_user.id,
            email=supabase_user.email,
            user_metadata=supabase_user.user_metadata or {},
            app_metadata=supabase_user.app_metadata or {}
        )
        
        return auth_user
        
    except Exception as e:
        logger.warning(f"Supabase authentication failed: {str(e)}")
        
        # Fall back to legacy JWT verification if Supabase fails
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
                    logger.info(f"Using dev token for user: {dev_username}")
            except JWTError as jwt_err:
                logger.warning(f"JWT decode error (bypass check): {str(jwt_err)}")
                raise credentials_exception
            
            # For legacy JWT tokens, create an AuthUser directly
            logger.info(f"Creating AuthUser from legacy JWT token for: {dev_username}")
            
            # Create a simple AuthUser with the username from the token
            auth_user = AuthUser(
                id=dev_username,  # Use username as ID for legacy tokens
                email=f"{dev_username}@example.com",
                user_metadata={"is_test_user": True},
                app_metadata={"legacy_auth": True}
            )
            
            return auth_user
        else:
            # No auth bypass, so we fail
            logger.warning("401 Unauthorized: Both Supabase and legacy authentication failed")
            raise credentials_exception


async def get_current_active_verified_user(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """
    Get the current active and verified user
    
    When using Supabase authentication, all users are considered active and verified
    by default, as this is managed by Supabase.
    
    Args:
        current_user: Current user from token
        
    Returns:
        AuthUser object
    """
    # With Supabase, we assume all authenticated users are active and verified
    # If we need to check specific roles or permissions, we can look at user_metadata or app_metadata
    
    # Example: Check if user is banned
    if current_user.app_metadata.get("banned", False):
        raise HTTPException(status_code=403, detail="User is banned")
    
    return current_user


def get_user_from_request(request: Request) -> Optional[AuthUser]:
    """
    Get the user from the request state
    
    This function can be used as a dependency in route handlers
    
    Args:
        request: The FastAPI request object
        
    Returns:
        The AuthUser object if authenticated, None otherwise
    """
    return getattr(request.state, "user", None)


def require_auth(user: Optional[AuthUser] = Depends(get_user_from_request)) -> AuthUser:
    """
    Require an authenticated user for a route
    
    This function can be used as a dependency in route handlers
    
    Args:
        user: The user from the request state
        
    Returns:
        The AuthUser object if authenticated
        
    Raises:
        HTTPException: If not authenticated
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(role: str):
    """
    Require a specific role for a route
    
    This function returns a dependency that can be used in route handlers
    
    Args:
        role: The required role
        
    Returns:
        A dependency function that checks if the user has the required role
    """
    def _require_role(user: AuthUser = Depends(require_auth)) -> AuthUser:
        if not user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return user
    
    return _require_role
