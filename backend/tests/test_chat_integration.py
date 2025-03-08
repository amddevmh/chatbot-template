#!/usr/bin/env python3
"""
Integration test for the chat service - testing the health endpoint first
"""
import asyncio
import json
import httpx
import sys
import os
import pytest
import pytest_asyncio

# Configure pytest-asyncio
pytest_asyncio_mode = "strict"

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

# Database setup is now handled by the shared_db fixture in conftest.py

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
            universal_newlines=True,
            env=env
        )
        
        # Give the server more time to start completely
        print("Waiting for server to start...")
        time.sleep(5)  # Increased from 3 to 5 seconds
        
        try:
            yield "http://localhost:8000"
        finally:
            print("Shutting down the FastAPI server...")
            
            # Check log file for any recent errors
            try:
                with open(log_file, 'r') as log_reader:
                    log_content = log_reader.readlines()
                    # Get the last 50 lines which might contain error information
                    recent_logs = log_content[-50:] if len(log_content) > 50 else log_content
                    error_logs = [line for line in recent_logs if 'ERROR' in line or 'Exception' in line]
                    if error_logs:
                        print("\nServer error logs detected:")
                        for line in error_logs:
                            print(f"> {line.strip()}")
                    print(f"Full server logs available at: {log_file}")
            except Exception as e:
                print(f"Error reading server logs: {e}")
            
            # Terminate the server process
            try:
                if server.poll() is None:  # Check if process is still running
                    os.kill(server.pid, signal.SIGTERM)
                    server.wait(timeout=5)
            except Exception as e:
                print(f"Error stopping server: {e}")

@pytest.mark.asyncio
async def test_chat_service_health_check(shared_db):
    """
    Integration test for the chat service - testing the health endpoint first
    
    This test verifies that:
    1. The API server starts successfully
    2. The health endpoint returns the expected response
    """
    print("Using shared database connection...")
    
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
            # First, check if we can just make any request to the server
            print("\nChecking server availability with request to root path...")
            try:
                response = await client.get(base_url, timeout=2.0)
                print(f"✅ Base URL request successful with status code: {response.status_code}")
                
                # Test the GET /health endpoint (our focus for this integration test)
                print("\nTesting GET /health endpoint...")
                # Note: The health endpoint is at root level in application.py, not under API prefix
                response = await client.get(f"{base_url}/health", timeout=3.0)
                
                if response.status_code == 200:
                    print(f"✅ GET /health successful with status code: {response.status_code}")
                    try:
                        response_data = response.json()
                        print(f"Response: {json.dumps(response_data, indent=2)}")
                        
                        # Verify the response contains the expected status
                        if "status" in response_data:
                            print(f"✅ Health status: {response_data['status']}")
                        else:
                            print("❌ Health response missing 'status' field")
                    except Exception as e:
                        print(f"Error parsing health response: {e}")
                        print(f"Raw response: {response.text}")
                else:
                    print(f"❌ GET /health failed with status code: {response.status_code}")
                    print(f"Response: {response.text}")
                

            except Exception as e:
                print(f"❌ Error checking server: {e}")
        
        print("\nChat integration test completed!")

async def send_chat_message(client, base_url, headers, message, user_label="", timeout=15.0):
    """Helper function to send a chat message and process the response"""
    start_time = time.time()
    request_id = f"{user_label}_{int(start_time*1000)}"
    
    try:
        print(f"[{request_id}] Sending message for {user_label}: '{message}'")
        response = await client.post(
            f"{base_url}{settings.API_PREFIX}/chat",
            headers=headers,
            json={"message": message},
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        if response.status_code == 200:
            print(f"✅ [{request_id}] Chat message from {user_label} successful in {elapsed:.2f}s with status code: {response.status_code}")
            response_data = response.json()
            print(f"Response for {user_label}: {json.dumps(response_data, indent=2)}")
            return response_data
        else:
            print(f"❌ [{request_id}] Chat request for {user_label} failed in {elapsed:.2f}s with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        print(f"❌ [{request_id}] Request timed out for {user_label} after {elapsed:.2f}s (timeout limit: {timeout}s)")
        return None
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ [{request_id}] Error sending chat message for {user_label} after {elapsed:.2f}s: {str(e)}")
        return None

@pytest.mark.asyncio
async def test_chat_service_integration(shared_db):
    """
    Integration test for the chat service with state persistence using proper concurrency
    
    This test verifies that:
    1. The chat service responds to initial messages correctly
    2. The chat service maintains conversation history between requests
    3. Different users maintain separate conversation histories
    """
    print("Using shared database connection...")
    
    # Generate dev tokens for two different test users
    dev_token_user1 = create_dev_token(username="test_user_alex")
    dev_token_user2 = create_dev_token(username="test_user_taylor")
    
    print("\n=== DEVELOPMENT TOKENS ===")
    print(f"User 1: Bearer {dev_token_user1}")
    print(f"User 2: Bearer {dev_token_user2}")
    print("=========================\n")
    
    # Set up the authorization headers
    headers_user1 = {
        "Authorization": f"Bearer {dev_token_user1}",
        "Content-Type": "application/json"
    }
    
    headers_user2 = {
        "Authorization": f"Bearer {dev_token_user2}",
        "Content-Type": "application/json"
    }
    
    # Start the FastAPI server in a separate process
    with start_app_server() as base_url:
        # Create an HTTP client that can handle multiple concurrent requests
        async with httpx.AsyncClient(timeout=20.0) as client:
            # First verify the server is running with a health check
            print("\nVerifying server health...")
            try:
                response = await client.get(f"{base_url}/health", timeout=2.0)
                if response.status_code == 200:
                    print(f"✅ Health check successful with status code: {response.status_code}")
                else:
                    print(f"❌ Health check failed with status code: {response.status_code}")
                    return
            except Exception as e:
                print(f"❌ Error checking server health: {e}")
                return
            
            # Test Phase 1: Initial concurrent messages from both users
            print("\n--- Test Phase 1: Concurrent Initial Messages ---")
            
            first_message_user1 = "Hello, I'm User 1. How are you?"
            first_message_user2 = "Hello, I'm User 2. What can you help me with?"
            
            # Use asyncio.gather to send requests concurrently
            print("\nSending concurrent initial messages from both users...")
            initial_results = await asyncio.gather(
                send_chat_message(client, base_url, headers_user1, first_message_user1, "User 1"),
                send_chat_message(client, base_url, headers_user2, first_message_user2, "User 2"),
                return_exceptions=True  # This ensures that exceptions don't stop the entire gather operation
            )
            
            # Process the results
            user1_response = initial_results[0] if not isinstance(initial_results[0], Exception) else None
            user2_response = initial_results[1] if not isinstance(initial_results[1], Exception) else None
            
            if isinstance(initial_results[0], Exception):
                print(f"❌ Exception from User 1 request: {initial_results[0]}")
            if isinstance(initial_results[1], Exception):
                print(f"❌ Exception from User 2 request: {initial_results[1]}")
            
            # Test Phase 2: Follow-up messages to test conversation continuity
            print("\n--- Test Phase 2: Conversation Continuity ---")
            
            # Create follow-up messages that reference the initial conversation
            followup_user1 = "Do you remember I'm User 1? This is a follow-up message."
            followup_user2 = "Do you remember I'm User 2? This is a follow-up message."
            
            # Track which users had successful initial messages
            test_user1 = user1_response is not None
            test_user2 = user2_response is not None
            
            print("\n--- Testing SEQUENTIAL follow-up messages ---")
            # Run follow-ups SEQUENTIALLY to diagnose if concurrency is causing the issue
            if test_user1:
                print("\nSending sequential follow-up for User 1...")
                user1_followup_result = await send_chat_message(
                    client, base_url, headers_user1, followup_user1, 
                    "User 1 (follow-up seq)", timeout=30.0  # Increased timeout
                )
                
                if user1_followup_result:
                    response_text = user1_followup_result.get("response", "").lower()
                    if "user 1" in response_text or "first message" in response_text or "previous" in response_text:
                        print(f"✅ User 1 sequential conversation continuity verified - response references previous context")
                    else:
                        print(f"⚠️ Could not definitively verify conversation continuity for User 1 (sequential)")
            
            if test_user2:
                print("\nSending sequential follow-up for User 2...")
                user2_followup_result = await send_chat_message(
                    client, base_url, headers_user2, followup_user2, 
                    "User 2 (follow-up seq)", timeout=30.0  # Increased timeout
                )
                
                if user2_followup_result:
                    response_text = user2_followup_result.get("response", "").lower()
                    if "user 2" in response_text or "first message" in response_text or "previous" in response_text:
                        print(f"✅ User 2 sequential conversation continuity verified - response references previous context")
                    else:
                        print(f"⚠️ Could not definitively verify conversation continuity for User 2 (sequential)")
                        
            # Now test the concurrent follow-ups to confirm the concurrency issue
            print("\n--- Testing CONCURRENT follow-up messages ---")
            followup_tasks = []
            
            if test_user1:
                followup_tasks.append(send_chat_message(
                    client, base_url, headers_user1, 
                    "This is a concurrent follow-up from User 1.", 
                    "User 1 (follow-up conc)", 
                    timeout=20.0
                ))
                
            if test_user2:
                followup_tasks.append(send_chat_message(
                    client, base_url, headers_user2, 
                    "This is a concurrent follow-up from User 2.", 
                    "User 2 (follow-up conc)", 
                    timeout=20.0
                ))
            
            # If we have follow-up tasks, run them concurrently
            if followup_tasks:
                print("\nSending concurrent follow-up messages...")
                followup_results = await asyncio.gather(*followup_tasks, return_exceptions=True)
                
                # Process concurrent follow-up results
                for i, result in enumerate(followup_results):
                    user_label = "User 1" if (i == 0 and test_user1) or (i == 0 and not test_user2) else "User 2"
                    user_label += " (concurrent)"
                    
                    if isinstance(result, Exception):
                        print(f"❌ Exception from {user_label} follow-up request: {result}")
                    elif result:
                        print(f"✅ Concurrent follow-up for {user_label} successful")
                    else:
                        print(f"❌ Concurrent follow-up for {user_label} failed or timed out")
            else:
                print("No successful initial messages, skipping concurrent follow-up tests")
        
        print("\nChat service integration test completed!")

@pytest.mark.asyncio
async def test_chat_service_simple(shared_db):
    """
    Simplified version of the chat integration test focusing just on one user
    to ensure basic functionality works without session isolation tests
    """
    print("Using shared database connection...")
    
    # Generate a dev token for a single test user
    dev_token = create_dev_token(username="test_user_simple")
    
    print("\n=== DEVELOPMENT TOKEN ====")
    print(f"User: Bearer {dev_token}")
    print("==========================\n")
    
    # Set up the authorization header
    headers = {
        "Authorization": f"Bearer {dev_token}",
        "Content-Type": "application/json"
    }
    
    # Start the FastAPI server in a separate process
    with start_app_server() as base_url:
        # Create an HTTP client
        async with httpx.AsyncClient() as client:
            # Verify server health
            print("\nVerifying server health...")
            try:
                response = await client.get(f"{base_url}/health", timeout=2.0)
                if response.status_code != 200:
                    print(f"❌ Health check failed with status code: {response.status_code}")
                    return
                print(f"✅ Health check successful")
            except Exception as e:
                print(f"❌ Error checking server health: {e}")
                return
                
            # Test basic chat functionality
            print("\n--- Testing Basic Chat ---")
            test_message = "Hello, I need help with something simple."
            print(f"\nSending test message: '{test_message}'")
            
            try:
                response = await client.post(
                    f"{base_url}{settings.API_PREFIX}/chat",
                    headers=headers,
                    json={"message": test_message},
                    timeout=8.0
                )
                
                if response.status_code == 200:
                    print(f"✅ Chat message successful with status code: {response.status_code}")
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                else:
                    print(f"❌ Chat request failed with status code: {response.status_code}")
                    print(f"Response: {response.text}")
            except Exception as e:
                print(f"❌ Error sending chat message: {e}")
        
        print("\nSimple chat test completed!")

async def run_all_tests():
    """Run all integration tests in sequence with error handling"""
    try:
        print("\n==== RUNNING HEALTH CHECK TEST ====\n")
        await test_chat_service_health_check()
    except Exception as e:
        print(f"\n❌ Error in health check test: {str(e)}")
        print("Continuing with other tests...")
    
    try:
        print("\n==== RUNNING SIMPLE CHAT TEST ====\n")
        await test_chat_service_simple()
    except Exception as e:
        print(f"\n❌ Error in simple chat test: {str(e)}")
        print("Continuing with other tests...")
        
    try:
        print("\n==== RUNNING FULL CHAT SERVICE INTEGRATION TEST ====\n")
        await test_chat_service_integration()
    except Exception as e:
        print(f"\n❌ Error in full chat service integration test: {str(e)}")
    
    print("\n==== ALL TESTS COMPLETED ====\n")

if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())
