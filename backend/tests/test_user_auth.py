#!/usr/bin/env python3
"""
Test Supabase authentication functionality

This test verifies that:
1. We can create a development user in Supabase
2. We can authenticate with the development user
3. We can get user information from the token
"""
import asyncio
import sys
import os
import pytest
import httpx
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.auth.models import AuthUser
from app.auth.middleware import verify_user_middleware
from app.config import settings

# Skip tests if Supabase credentials are not set
pytestmark = pytest.mark.skipif(
    not settings.SUPABASE_URL or not settings.SUPABASE_KEY,
    reason="Supabase credentials not set"
)

# Create a test app
app = FastAPI()

# Add middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    await verify_user_middleware(request)
    return await call_next(request)

# Add a test endpoint
@app.get("/test-auth")
async def test_auth(request: Request):
    user = request.state.user
    return {
        "authenticated": True,
        "user_id": user.id,
        "email": user.email,
        "name": user.name
    }

# Test client
client = TestClient(app)

@pytest.mark.asyncio
async def test_supabase_auth():
    """Test Supabase authentication"""
    print("Testing Supabase authentication...")
    
    # Setup: Create a development user via the API
    api_url = os.getenv("API_URL", "http://localhost:8000")
    setup_endpoint = f"{api_url}/api/v1/auth/setup-dev-user"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(setup_endpoint)
            response.raise_for_status()
            result = response.json()
            
            print(f"Dev user setup: {result['message']}")
            print(f"User ID: {result['user_id']}")
            print(f"Email: {result['email']}")
    except Exception as e:
        pytest.skip(f"Could not setup dev user: {str(e)}")
    
    # Test: Sign in with the development user
    from app.auth.supabase_client import supabase
    
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": "dev@example.com",
            "password": "devpassword123"
        })
        
        # Assert that we got a valid session
        assert auth_response.session is not None, "Should get a session from sign in"
        assert auth_response.user is not None, "Should get a user from sign in"
        
        # Get the access token
        access_token = auth_response.session.access_token
        
        # Assert that we got a token
        assert access_token, "Access token should not be empty"
        assert isinstance(access_token, str), "Access token should be a string"
        
        # Test the token authentication
        print("Testing token authentication...")
        
        # Get the user from the token
        user_response = supabase.auth.get_user(access_token)
        
        # Assert that we got a valid user
        assert user_response.user is not None, "Should get a user object from the token"
        assert user_response.user.email == "dev@example.com", "User should have email 'dev@example.com'"
        
        # Test the middleware
        print("Testing authentication middleware...")
        
        # Create a test client
        test_client = TestClient(app)
        
        # Make a request with the token
        response = test_client.get(
            "/test-auth",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        # Assert that the request was successful
        assert response.status_code == 200, f"Request should succeed, got {response.status_code}: {response.text}"
        
        # Assert that we got the expected response
        data = response.json()
        assert data["authenticated"] is True, "Should be authenticated"
        assert data["email"] == "dev@example.com", "Should have the correct email"
        
        # Log user details for debugging
        print(f"User authenticated: {data['email']}")
        
        print("\nSupabase authentication test completed successfully!")
        
    except Exception as e:
        pytest.fail(f"Authentication test failed: {str(e)}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_supabase_auth())
