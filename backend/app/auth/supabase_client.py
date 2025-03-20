#!/usr/bin/env python3
"""
Supabase client for authentication
"""
from supabase import create_client, Client
from app.config import settings

def get_supabase_client() -> Client:
    """
    Get a Supabase client instance
    
    Returns:
        Supabase client instance
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Create a singleton instance
supabase = get_supabase_client()
