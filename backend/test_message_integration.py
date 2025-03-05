#!/usr/bin/env python3
"""
Integration test for message processing with dev token authentication
"""
import asyncio
import json
import subprocess
import time
import requests
from datetime import datetime

from app.models.user import User
from app.models.message import MessageRequest
from app.models.nutrition import NutritionProfile, NutritionTracker
from app.database.mongodb import init_db
from app.auth.security import create_dev_token

async def setup_database():
    """Initialize the database with required models"""
    print("Initializing database connection...")
    await init_db([User, NutritionProfile, NutritionTracker])
    print("Database initialized")

def test_process_message_with_dev_token():
    """Test the process_message endpoint with dev token authentication"""
    # Run database setup
    asyncio.run(setup_database())
    
    # Start the API server
    print("\n=== STARTING API SERVER ===\n")
    server_process = subprocess.Popen(
        ["uvicorn", "app.application:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Generate a dev token
        dev_token = create_dev_token()
        print("\n=== DEVELOPMENT TOKEN ===")
        print(f"Bearer {dev_token}")
        print("=========================\n")
        
        # Create a test message request
        message_request = {
            "message": "What's my nutrition data for today?",
            "date": datetime.now().date().isoformat()
        }
        
        # Set up the authorization header with the dev token
        headers = {
            "Authorization": f"Bearer {dev_token}",
            "Content-Type": "application/json"
        }
        
        # Make the request to the process_message endpoint
        print("\n=== SENDING REQUEST TO PROCESS_MESSAGE ENDPOINT ===\n")
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/messages/process",
            headers=headers,
            json=message_request
        )
        
        # Print the response
        print(f"Status code: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
            
            # Assert that the request was successful
            assert response.status_code == 200
            assert response_json["success"] == True
            
            # Check for the personalized greeting in the response
            assert "Hello dev_test_user!" in response_json["message"]
            print(f"\nVerified greeting: 'Hello dev_test_user!' is in the response")
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
            print(f"Response content: {response.content.decode('utf-8')}")
            raise
        
        print("\n=== TEST COMPLETED SUCCESSFULLY ===\n")
    finally:
        # Stop the server
        print("\n=== STOPPING API SERVER ===\n")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    # Run the test
    test_process_message_with_dev_token()
