#!/usr/bin/env python3
"""
Authentication models
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class AuthUser(BaseModel):
    """
    User model for authentication
    
    This model represents a user authenticated through Supabase.
    It is attached to the request state and used for authorization.
    """
    id: str
    email: str
    user_metadata: Dict[str, Any] = {}
    app_metadata: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Get the user's name from metadata"""
        if self.user_metadata.get("full_name"):
            return self.user_metadata.get("full_name")
        
        first_name = self.user_metadata.get("first_name", "")
        last_name = self.user_metadata.get("last_name", "")
        
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()
            
        return self.email.split("@")[0]
    
    @property
    def roles(self) -> List[str]:
        """Get the user's roles from metadata"""
        return self.app_metadata.get("roles", ["user"])
    
    def has_role(self, role: str) -> bool:
        """Check if the user has a specific role"""
        return role in self.roles
