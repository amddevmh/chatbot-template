#!/usr/bin/env python3
"""
Integration tests for the session management API endpoints
"""
import asyncio
import os
import sys
import uuid
import pytest
import httpx
import time
import signal
import subprocess
from datetime import datetime, timedelta
import jwt
from contextlib import contextmanager

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

from app.config import settings
from app.models.user import User
from app.models.chat_session import ChatSessionMetadata
from app.database.mongodb import init_db
from app.auth.security import create_dev_token

@contextmanager
def start_app_server():
    """Start the FastAPI app in a separate process"""
    print("Starting the FastAPI server...")
    # Use the absolute path to run_app.py
    run_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'run_app.py'))
    
    # Start with more verbose output and set environment variables for testing
    env = os.environ.copy()
    env['LOG_LEVEL'] = 'DEBUG'  # Set debug log level for more detailed output
    
    # Create a log file to capture server output
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"server_test_{int(time.time())}.log")
    
    # Open log file and server process
    with open(log_file, 'w') as log_handle:
        print(f"Server logs will be written to: {log_file}")
        
        server = subprocess.Popen(
            ["python", run_app_path], 
            stdout=log_handle, 
            stderr=log_handle,
            env=env
        )
        
        # Give the server some time to start
        time.sleep(3)
        
        try:
            yield "http://localhost:8000"
        finally:
            print("Shutting down the FastAPI server...")
            # Terminate the server process
            os.kill(server.pid, signal.SIGTERM)
            server.wait()
            print(f"Server process exited with code {server.returncode}")

# Helper function to create a test JWT token
def create_test_token(username: str = "test_user", expire_minutes: int = 30):
    """Create a test JWT token for authentication"""
    expiration = datetime.utcnow() + timedelta(minutes=expire_minutes)
    payload = {
        "sub": username,
        "exp": expiration,
        "is_dev_token": True  # Mark as development token
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

@pytest.mark.asyncio
async def test_session_api_endpoints(shared_db):
    """Test the session management API endpoints"""
    # Skip direct MongoDB initialization as it's already done by the shared_db fixture
    # and we'll use the server's connection instead
    
    # Create a unique test username
    test_username = f"test_user_{uuid.uuid4().hex[:8]}"
    
    # Create a test token
    token = create_test_token(username=test_username)
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # Start the app server in a separate process
    with start_app_server() as base_url:
        # Use httpx.AsyncClient for making requests
        async with httpx.AsyncClient() as client:
            # Test 1: Create a new session
            create_response = await client.post(
                f"{base_url}/api/v1/chat/sessions",
                json={"name": "Test Session API"},
                headers=auth_headers,
                timeout=10.0
            )
            assert create_response.status_code == 200, f"Failed to create session: {create_response.text}"
            session_data = create_response.json()
            assert "session_id" in session_data
            assert session_data["name"] == "Test Session API"
            assert session_data["session_id"].startswith(f"{test_username}_")
            
            # Store the session ID for later tests
            session_id = session_data["session_id"]
            
            # Test 2: List sessions for the user
            list_response = await client.get(
                f"{base_url}/api/v1/chat/sessions", 
                headers=auth_headers,
                timeout=10.0
            )
            assert list_response.status_code == 200
            response_data = list_response.json()
            assert "sessions" in response_data, f"Response does not contain 'sessions' key: {response_data}"
            sessions = response_data["sessions"]
            assert isinstance(sessions, list), f"'sessions' is not a list: {sessions}"
            assert len(sessions) >= 1, f"No sessions found in response: {sessions}"
            assert any(s["session_id"] == session_id for s in sessions), f"Session {session_id} not found in sessions list: {sessions}"
            
            # Test 3: Send a message using the session
            chat_response = await client.post(
                f"{base_url}/api/v1/chat",
                json={"message": "Hello, this is a test message", "session_id": session_id},
                headers=auth_headers,
                timeout=15.0  # Longer timeout for chat response
            )
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            assert "response" in chat_data
            assert "session_id" in chat_data
            assert chat_data["session_id"] == session_id
            
            # Test 4: Get session history
            history_response = await client.get(
                f"{base_url}/api/v1/chat/sessions/{session_id}/history",
                headers=auth_headers,
                timeout=10.0
            )
            assert history_response.status_code == 200
            history_data = history_response.json()
            assert "messages" in history_data, f"Response does not contain 'messages' key: {history_data}"
            messages = history_data["messages"]
            assert isinstance(messages, list), f"'messages' is not a list: {messages}"
            assert len(messages) >= 2, f"Expected at least 2 messages in history: {messages}"  # Should have at least the user message and response
            
            # Test 5: Send a message without specifying session_id (should create new session)
            new_chat_response = await client.post(
                f"{base_url}/api/v1/chat",
                json={"message": "Create a new session for me"},
                headers=auth_headers,
                timeout=15.0  # Longer timeout for chat response
            )
            assert new_chat_response.status_code == 200
            new_chat_data = new_chat_response.json()
            assert "response" in new_chat_data
            assert "session_id" in new_chat_data
            assert new_chat_data["session_id"] != session_id  # Should be a different session
            
            # Check that we now have at least 2 sessions
            list_response_2 = await client.get(
                f"{base_url}/api/v1/chat/sessions",
                headers=auth_headers,
                timeout=10.0
            )
            response_data_2 = list_response_2.json()
            assert "sessions" in response_data_2, f"Response does not contain 'sessions' key: {response_data_2}"
            sessions_2 = response_data_2["sessions"]
            assert isinstance(sessions_2, list), f"'sessions' is not a list: {sessions_2}"
            assert len(sessions_2) >= 2, f"Expected at least 2 sessions: {sessions_2}"


async def run_test():
    """Run the test with proper setup and teardown"""
    try:
        # Import the fixture to use it directly
        from conftest import shared_db as get_shared_db
        
        # Get the fixture
        db = await get_shared_db()
        
        # Run the test
        await test_session_api_endpoints(db)
        
        print("✅ All session API integration tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    # When run directly as a script, run the test with asyncio
    asyncio.run(run_test())
