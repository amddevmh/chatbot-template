#!/usr/bin/env python3
"""
Setup script for development environment

This script sets up the development environment by:
1. Creating a development user in Supabase
2. Providing the credentials for local development
"""
import os
import sys
import httpx
import asyncio
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Load environment variables
load_dotenv(dotenv_path=os.path.join("app", ".env"))

async def setup_dev_environment():
    """Setup the development environment"""
    print("Setting up development environment...")
    
    # Get API URL from environment
    api_url = os.getenv("API_URL", "http://localhost:8000")
    setup_endpoint = f"{api_url}/api/v1/auth/setup-dev-user"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(setup_endpoint)
            response.raise_for_status()
            result = response.json()
            
            print("\n=== Development User Setup ===")
            print(f"Status: {result['message']}")
            print(f"User ID: {result['user_id']}")
            print(f"Email: {result['email']}")
            print("Password: devpassword123")
            
            print("\nYou can now use these credentials for development.")
            print("To use them in the frontend, add the following to your .env.local file:")
            print("\nVITE_SUPABASE_DEV_EMAIL=dev@example.com")
            print("VITE_SUPABASE_DEV_PASSWORD=devpassword123")
    except Exception as e:
        print(f"\nError setting up development environment: {str(e)}")
        print("\nMake sure the backend server is running and environment variables are set.")
        print("You need to set the following environment variables in app/.env:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")
        print("  - SUPABASE_SERVICE_KEY")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(setup_dev_environment())
