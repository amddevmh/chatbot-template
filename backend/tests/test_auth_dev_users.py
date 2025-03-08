#!/usr/bin/env python3
"""
Test for dynamic creation of dev test users with custom usernames
"""
import asyncio
import sys
import os
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.auth.security import create_dev_token, get_current_user
from app.models.user import User
from app.database.mongodb import init_db
from fastapi import HTTPException

# Configure pytest-asyncio
pytest_asyncio_mode = "strict"

@pytest.fixture
def mock_user():
    """Return a mock User object"""
    def create_mock_user(username):
        mock_user = AsyncMock()
        mock_user.username = username
        mock_user.email = f"{username}@example.com"
        mock_user.is_verified = True
        mock_user.is_test_user = True
        return mock_user
    return create_mock_user

def test_create_dev_tokens():
    """Test creating dev tokens with different usernames"""
    
    # Create tokens for different test users
    usernames = ["test_user_1", "test_user_2", "test_user_3"]
    tokens = [create_dev_token(username=username) for username in usernames]
    
    print(f"\nCreated {len(tokens)} tokens for different test users")
    for i, (username, token) in enumerate(zip(usernames, tokens)):
        print(f"User {i+1}: {username} -> Token: {token[:15]}...")
    
    # Verify we have the expected number of tokens
    assert len(tokens) == len(usernames), "Number of created tokens doesn't match expected"
    
    print("\n✅ All tokens created successfully!")
    # Don't return tokens, just assert they're correct

def test_create_dev_token_format():
    """Test that create_dev_token generates a valid token with the expected format"""
    
    # Create a token for a test user
    username = "test_user_1"
    token = create_dev_token(username=username)
    
    print(f"\nCreated token for {username}: {token[:15]}...")
    
    # Verify the token is not empty
    assert token, "Token should not be empty"
    
    # Verify the token has the expected format (JWT format with 3 parts separated by dots)
    parts = token.split('.')
    assert len(parts) == 3, "Token should have 3 parts separated by dots"
    
    print("\n✅ Token format verified successfully!")

@pytest.mark.asyncio
async def test_get_current_user_with_dev_token_mocked():
    """Test the dev token authentication flow with mocked dependencies"""
    
    # Create a test username and token
    username = "test_user_1"
    token = create_dev_token(username=username)
    print(f"\nCreated token for {username}: {token[:15]}...")
    
    # Create a mock user object
    mock_user_obj = AsyncMock()
    mock_user_obj.username = username
    mock_user_obj.email = f"{username}@example.com"
    mock_user_obj.is_verified = True
    mock_user_obj.is_test_user = True
    mock_user_obj.save = AsyncMock()  # Add a save method that can be awaited
    
    # Create a mock UserService with a create_user method
    mock_user_service_class = AsyncMock()
    mock_user_service_class.create_user = AsyncMock(return_value=mock_user_obj)
    
    # Patch the User.find_one method to return None (user not found)
    with patch('app.auth.security.User.find_one', new_callable=AsyncMock) as mock_find_one:
        mock_find_one.return_value = None
        
        # Patch the imported UserService inside the function
        with patch.dict('sys.modules', {'app.services.user_service': AsyncMock()}):
            # Patch the UserService class inside the imported module
            with patch('app.services.user_service.UserService') as mock_service_class:
                # Configure the UserService.create_user method
                mock_service_class.create_user = AsyncMock(return_value=mock_user_obj)
                
                # Call get_current_user with the token
                user = await get_current_user(token)
                
                # Verify the user was created with the correct attributes
                assert user is not None, "User should not be None"
                assert user.username == username, "User has incorrect username"
                assert user.email == f"{username}@example.com", "User has incorrect email"
                assert user.is_test_user, "User should be marked as a test user"
                assert user.is_verified, "User should be verified"
                
                # Verify the mock was called with the correct arguments
                mock_service_class.create_user.assert_called_once()
                call_args = mock_service_class.create_user.call_args[1]
                assert call_args['username'] == username
                assert call_args['email'] == f"{username}@example.com"
                
                print(f"Created/Retrieved User: {user.username}, Email: {user.email}")
                print("\n✅ User creation with dev token verified successfully!")

if __name__ == "__main__":
    # Run the tests with pytest
    pytest.main(['-xvs', __file__])
