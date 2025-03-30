#!/usr/bin/env python3
"""
Script to get a JWT token for the dev user
"""
import os
import sys
import asyncio
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv(dotenv_path=os.path.join("app", ".env"))

async def get_dev_token():
    """Get a JWT token for the dev user"""
    print("Getting dev token...")
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in app/.env")
        sys.exit(1)
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Sign in with dev credentials
        response = supabase.auth.sign_in_with_password({
            "email": "dev@example.com",
            "password": "devpassword123"
        })
        
        # Print token information
        print("\n=== Development User Token ===")
        print(f"User ID: {response.user.id}")
        print(f"Email: {response.user.email}")
        print(f"Access Token: {response.session.access_token}")
        print("\nYou can use this token in the Authorization header as:")
        print(f"Bearer {response.session.access_token}")
        
    except Exception as e:
        print(f"\nError getting dev token: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(get_dev_token())
