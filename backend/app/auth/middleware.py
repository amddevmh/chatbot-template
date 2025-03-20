#!/usr/bin/env python3
"""
Authentication middleware
"""
from typing import Optional, Any
import logging
from fastapi import Request, HTTPException, status, Depends
from app.config import settings
from app.auth.supabase_client import supabase
from app.auth.models import AuthUser

# Get logger for this module
logger = logging.getLogger(__name__)


async def verify_user_middleware(request: Request) -> None:
    """
    Middleware to verify user authentication using Supabase
    
    This middleware:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token with Supabase
    3. Creates an AuthUser object with the user information
    4. Attaches the user to the request state
    
    If any step fails, an appropriate HTTP exception is raised
    """
    # Skip auth for certain paths
    # Documentation paths
    if request.url.path in [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        # API paths that don't need auth
        f"{settings.API_PREFIX}/auth/test-token",
    ]:
        return
        
    # Get token from header
    authorization: str = request.headers.get("Authorization")
    
    if not authorization:
        # No token provided, require authentication
        logger.warning(f"401 Unauthorized: No token provided for path {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
            
    try:
        # Extract token
        if authorization.startswith("Bearer "):
            token = authorization[7:]
            logger.debug(f"Bearer token extracted for path {request.url.path}: {token[:10]}...")
        else:
            token = authorization
            logger.debug(f"Raw token used for path {request.url.path}: {token[:10]}...")
        
        # Verify token with Supabase
        try:
            response = supabase.auth.get_user(token)
            supabase_user = response.user
            
            if not supabase_user:
                logger.warning(f"401 Unauthorized: Supabase returned no user for token on path {request.url.path}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.info(f"User verified: {supabase_user.email}")
            
            # Create AuthUser object
            auth_user = AuthUser(
                id=supabase_user.id,
                email=supabase_user.email,
                user_metadata=supabase_user.user_metadata or {},
                app_metadata=supabase_user.app_metadata or {}
            )
            
            # Attach user to request state
            request.state.user = auth_user
            
        except Exception as e:
            logger.error(f"Token verification exception for path {request.url.path}: {str(e)}")
            logger.debug(f"Token that failed verification (first 10 chars): {token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except Exception as e:
        logger.error(f"General authentication error for path {request.url.path}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
        user: The AuthUser object from the request state
        
    Returns:
        The AuthUser object if authenticated
        
    Raises:
        HTTPException: If user is not authenticated
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
