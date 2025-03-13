#!/usr/bin/env python3
"""
Test basic user authentication functionality with dev token

This test verifies that:
1. We can generate a development token
2. The token can be used to authenticate as a dev user
3. The authenticated user has the expected properties
"""
import asyncio
import sys
import os
import pytest

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.auth.security import create_dev_token, get_current_user

@pytest.mark.asyncio(loop_scope="session")
async def test_user_auth(shared_db):
   
    print("Using shared database connection...")
    
    # Generate a dev token
    dev_token = create_dev_token()
    
    # Assert that we got a token
    assert dev_token, "Development token should not be empty"
    assert isinstance(dev_token, str), "Development token should be a string"
    
    # Test the dev token authentication
    print("Testing dev token authentication...")
    
    # Get the user from the token
    # This will automatically create a dev_test_user in the database if it doesn't exist
    user = await get_current_user(dev_token)
    
    # Assert that we got a valid user
    assert user is not None, "Should get a user object from the dev token"
    assert user.username == "dev_test_user", "Dev user should have username 'dev_test_user'"
    assert user.is_active, "Dev user should be active"
    
    # Log user details for debugging
    print(f"User authenticated: {user.username}")
    
    print("\nDev user authentication test completed successfully!")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_user_auth())
