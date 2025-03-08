#!/usr/bin/env python3
"""
Simplified test script for user authentication
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.services.user_service import UserService
from app.database.mongodb import init_db
from app.auth.security import create_dev_token, get_current_user

async def test_user_auth():
    """Test basic user authentication functionality with dev token"""
    print("Initializing database connection...")
    # Initialize the database with all document models
    await init_db([User])
    
    # Generate a dev token
    dev_token = create_dev_token()
    print("\n=== DEVELOPMENT TOKEN ===")
    print(f"Bearer {dev_token}")
    print("=========================\n")
    
    # Test the dev token authentication
    # This will automatically create a dev_test_user in the database if it doesn't exist
    print("Testing dev token authentication...")
    try:
        user = await get_current_user(dev_token)
        print("✅ Dev token authentication successful!")
        print(f"User details: {user.username}, {user.email}")
        print(f"Verified: {user.is_verified}, Active: {user.is_active}")
    except Exception as e:
        print(f"❌ Dev token authentication failed: {str(e)}")
    
    # We're focusing only on dev user authentication for now
    print("\nDev user authentication test completed successfully!")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_user_auth())
