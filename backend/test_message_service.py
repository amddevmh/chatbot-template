#!/usr/bin/env python3
"""
Direct test for the message service
"""
import asyncio
from datetime import datetime
from app.models.message import MessageRequest
from app.services.message_service import MessageService

async def test_message_service():
    """Test the message service directly"""
    print("Testing message service directly...")
    
    # Create a message service instance
    service = MessageService()
    
    # Create a test message request
    message_request = MessageRequest(
        message="What's my nutrition data for today?",
        date=datetime.now().date()
    )
    
    # Process the message with a test username
    response = await service.process_message(message_request, "test_user")
    
    # Print the response
    print(f"Success: {response.success}")
    print(f"Message: {response.message}")
    print(f"Intent: {response.intent}")
    print(f"User ID: {response.user_id}")
    
    # Check for the greeting
    if "Hello test_user!" in response.message:
        print("\n✅ Greeting verification passed!")
    else:
        print("\n❌ Greeting verification failed!")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_message_service())
