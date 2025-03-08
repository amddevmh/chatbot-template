#!/usr/bin/env python3
"""
User service for handling user operations and verification
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import secrets
from pydantic import EmailStr

from app.models.user import User
from app.auth.security import create_access_token


class UserService:
    """Service for user operations including registration, verification, and profile management"""
    
    @staticmethod
    async def create_user(
        username: str, 
        email: EmailStr, 
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Create a new user
        
        Args:
            username: Username for the new user
            email: Email address for the new user
            password: Plain text password (will be hashed)
            first_name: Optional first name
            last_name: Optional last name
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username or email already exists
        existing_user = await User.get_by_username(username)
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")
            
        existing_email = await User.get_by_email(email)
        if existing_email:
            raise ValueError(f"Email '{email}' already registered")
            
        # Create verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create and save new user
        user = User(
            username=username,
            email=email,
            hashed_password=User.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            verification_token=verification_token
        )
        
        await user.insert()
        return user
    
    @staticmethod
    async def verify_user(verification_token: str) -> Optional[User]:
        """
        Verify a user's email using the verification token
        
        Args:
            verification_token: Token sent to user's email
            
        Returns:
            User object if verification successful, None otherwise
        """
        user = await User.find_one({"verification_token": verification_token})
        
        if not user:
            return None
            
        # Mark user as verified and remove token
        user.is_verified = True
        user.verification_token = None
        user.updated_at = datetime.now()
        
        await user.save()
        return user
    
    @staticmethod
    async def authenticate_user(username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user and return a token
        
        Args:
            username_or_email: Username or email for login
            password: Plain text password
            
        Returns:
            Dict with access token and token type if authentication successful, None otherwise
        """
        user = await User.authenticate(username_or_email, password)
        
        if not user:
            return None
            
        # Create access token
        access_token = create_access_token(data={"sub": user.username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "username": user.username
        }
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """
        Get a user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        return await User.get(user_id)
    
    @staticmethod
    async def update_user(
        user: User,
        update_data: Dict[str, Any]
    ) -> User:
        """
        Update user information
        
        Args:
            user: User object to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated user object
        """
        # Handle password update separately
        if "password" in update_data:
            user.hashed_password = User.hash_password(update_data.pop("password"))
        
        # Update other fields
        for field, value in update_data.items():
            if hasattr(user, field) and field not in ["id", "created_at", "updated_at"]:
                setattr(user, field, value)
        
        user.updated_at = datetime.now()
        await user.save()
        
        return user
    
    @staticmethod
    async def deactivate_user(user: User) -> User:
        """
        Deactivate a user account
        
        Args:
            user: User object to deactivate
            
        Returns:
            Deactivated user object
        """
        user.is_active = False
        user.updated_at = datetime.now()
        await user.save()
        
        return user
    
    @staticmethod
    async def reactivate_user(user: User) -> User:
        """
        Reactivate a user account
        
        Args:
            user: User object to reactivate
            
        Returns:
            Reactivated user object
        """
        user.is_active = True
        user.updated_at = datetime.now()
        await user.save()
        
        return user
