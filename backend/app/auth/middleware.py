#!/usr/bin/env python3
"""
Authentication middleware
"""
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from jose import JWTError, jwt
from app.config import settings
from app.models.user import User
from app.auth.security import verify_token


async def verify_user_middleware(request: Request) -> None:
    """
    Middleware to verify user authentication
    
    This middleware:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token
    3. Retrieves the user from the database
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
            
    try:
        scheme, token = authorization.split()
        
        # Check if this is a dev token
        try:
            # Just decode without verification to check if it's our dev token
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False}  # Don't verify expiration for this check
            )
            if payload.get("sub") == "dev_test_user":
                print("\n=== DEV USER DETECTED IN MIDDLEWARE ===\n")
                print(f"Request path: {request.url.path}")
                print(f"Method: {request.method}")
                print("=== Using dev_test_user for authentication ===\n")
        except Exception:
            # Ignore any errors in dev detection
            pass
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verify token
        token_data = verify_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user from database
        user = await User.find_one({"username": token_data.sub})
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
            
        # Attach user to request state
        request.state.user = user
        
    except (ValueError, JWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_from_request(request: Request) -> Optional[User]:
    """
    Get the user from the request state
    
    This function can be used as a dependency in route handlers
    
    Args:
        request: The FastAPI request object
        
    Returns:
        The user object if authenticated, None otherwise
    """
    return getattr(request.state, "user", None)


def require_active_user(user: Optional[User] = Depends(get_user_from_request)) -> User:
    """
    Require an active user for a route
    
    This function can be used as a dependency in route handlers
    
    Args:
        user: The user object from the request state
        
    Returns:
        The user object if active
        
    Raises:
        HTTPException: If user is not authenticated or not active
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
        
    return user


def require_verified_user(user: User = Depends(require_active_user)) -> User:
    """
    Require a verified user for a route
    
    This function can be used as a dependency in route handlers
    
    Args:
        user: The user object from the request state
        
    Returns:
        The user object if verified
        
    Raises:
        HTTPException: If user is not verified
    """
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
        
    return user
