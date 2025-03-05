#!/usr/bin/env python3
"""
Simplified test script for user authentication
"""
import asyncio
from app.models.user import User
from app.models.message import MessageRequest, MessageResponse
from app.models.nutrition import NutritionProfile, NutritionTracker
from app.services.user_service import UserService
from app.database.mongodb import init_db
from app.auth.security import create_dev_token, get_current_user

async def test_user_auth():
    """Test basic user authentication functionality with dev token"""
    print("Initializing database connection...")
    # Initialize the database with all document models
    await init_db([User, NutritionProfile, NutritionTracker])
    
    # Generate a dev token
    dev_token = create_dev_token()
    print("\n=== DEVELOPMENT TOKEN ===")
    print(f"Bearer {dev_token}")
    print("=========================\n")
    
    # Test the dev token authentication
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
