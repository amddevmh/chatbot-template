#!/usr/bin/env python3
"""
User model for authentication and user management
"""
from datetime import datetime
from typing import Optional, List
from pydantic import Field, EmailStr, validator
from beanie import Document, PydanticObjectId
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Document):
    """User model for authentication and profile management"""
    username: str = Field(..., description="Username for login", index=True)
    email: EmailStr = Field(..., description="User's email address", index=True)
    hashed_password: str = Field(..., description="Hashed password")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    is_active: bool = Field(True, description="Whether the user account is active")
    is_verified: bool = Field(False, description="Whether the user's email is verified")
    verification_token: Optional[str] = Field(None, description="Token for email verification")
    roles: List[str] = Field(default_factory=lambda: ["user"], description="User roles")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('username')
    def username_must_be_valid(cls, v):
        """Validate username format"""
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not v.isalnum() and not "_" in v and not "-" in v:
            raise ValueError("Username must contain only alphanumeric characters, underscores, or hyphens")
        return v
    
    class Settings:
        name = "users"
        indexes = [
            "username",
            "email",
            [
                ("username", 1),
                ("email", 1),
            ],
        ]
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password for storing"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str) -> bool:
        """Verify a stored password against a provided password"""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        """Get a user by email"""
        return await cls.find_one({"email": email})
    
    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        """Get a user by username"""
        return await cls.find_one({"username": username})
    
    @classmethod
    async def authenticate(cls, username_or_email: str, password: str) -> Optional["User"]:
        """Authenticate a user with username/email and password"""
        # Try to find user by username or email
        user = await cls.get_by_username(username_or_email)
        if not user:
            user = await cls.get_by_email(username_or_email)
        
        # Verify password if user exists
        if user and user.verify_password(password):
            return user
        
        return None
