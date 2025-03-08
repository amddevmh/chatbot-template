#!/usr/bin/env python3
"""
Integration test for the hello_authenticated service using dev user authentication
"""
import asyncio
import json
import httpx
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.auth.security import create_dev_token
from app.database.mongodb import init_db
from app.models.user import User
from app.config import settings
import subprocess
import time
import signal
from contextlib import contextmanager

async def setup_database():
    """Initialize the database connection for testing"""
    print("Initializing database connection...")
    await init_db([User])
    print("Database initialized successfully")

@contextmanager
def start_app_server():
    """Start the FastAPI app in a separate process"""
    print("Starting the FastAPI server...")
    # Use the absolute path to run_app.py
    run_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run_app.py'))
    server = subprocess.Popen(["python", run_app_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give the server some time to start
    time.sleep(2)
    
    try:
        yield "http://localhost:8000"
    finally:
        print("Shutting down the FastAPI server...")
        # Terminate the server process
        os.kill(server.pid, signal.SIGTERM)
        server.wait()

async def test_hello_authenticated_service_integration():
    """
    Integration test for the hello_authenticated service with dev user authentication
    
    This test verifies that:
    1. The dev token authentication works correctly
    2. The hello_authenticated service GET endpoint returns the expected greeting
    
    Note: This test will automatically create a dev_test_user in the database if it doesn't exist.
    """
    # Setup the database
    await setup_database()
    
    # Generate a dev token
    # When this token is used, it will automatically create a dev_test_user in the database if it doesn't exist
    dev_token = create_dev_token()
    print("\n=== DEVELOPMENT TOKEN ===")
    print(f"Bearer {dev_token}")
    print("=========================\n")
    
    # Set up the authorization header
    headers = {
        "Authorization": f"Bearer {dev_token}",
        "Content-Type": "application/json"
    }
    
    # Start the FastAPI server in a separate process
    with start_app_server() as base_url:
        # Create an HTTP client
        async with httpx.AsyncClient() as client:
            # Test the GET /hello_authenticated endpoint
            print("\nTesting GET /hello_authenticated endpoint...")
            response = await client.get(f"{base_url}{settings.API_PREFIX}/hello_authenticated", headers=headers)
            
            if response.status_code == 200:
                print(f"✅ GET /hello_authenticated successful with status code: {response.status_code}")
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
                
                # Verify the response contains the expected greeting
                expected_username = "dev_test_user"
                expected_greeting = f"Hello {expected_username}!"
                
                if response_data.get("username") == expected_username and expected_greeting in response_data.get("message", ""):
                    print("✅ GET /hello_authenticated response contains the expected greeting")
                else:
                    print("❌ GET /hello_authenticated response does not contain the expected greeting")
                    print(f"Expected username: {expected_username}, got: {response_data.get('username')}")
                    print(f"Expected greeting to contain: {expected_greeting}")
                    print(f"Actual message: {response_data.get('message')}")
            else:
                print(f"❌ GET /hello_authenticated failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
        
        print("\nHello_authenticated service integration test completed!")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_hello_authenticated_service_integration())
