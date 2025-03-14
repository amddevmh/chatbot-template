#!/usr/bin/env python3
"""
Unit tests for the ChatService class
"""
import sys
import os
import uuid
import pytest
import pytest_asyncio

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chat_service import ChatService
from app.database.mongodb import init_db
from app.models.user import User

# Configure pytest-asyncio
pytest_asyncio_mode = "strict"

@pytest_asyncio.fixture(scope="function")
async def chat_service(shared_db):
    """Create a chat service instance for testing with proper cleanup.
    
    This fixture uses the shared_db fixture to ensure it's using the same event loop.
    The function scope ensures a fresh ChatService for each test.
    """
    # Create the service
    service = ChatService()
    
    # Initialize the async memory using the current event loop
    # This is critical to ensure we're using the same event loop as shared_db
    print("Initializing async memory for ChatService...")
    await service.initialize_async_memory()
    print("Async memory initialized successfully")
    
    # Yield the service for test use
    yield service
    
    # Cleanup: Ensure memory resources are properly released
    # This helps prevent memory leaks and event loop issues between tests
    if hasattr(service, 'memory') and service.memory:
        try:
            # Clear any session data that might have been created
            if hasattr(service.memory, 'checkpoints'):
                service.memory.checkpoints.clear()
            print("Cleaned up ChatService memory")
        except Exception as e:
            print(f"Warning: Error during chat_service cleanup: {e}")

@pytest.mark.asyncio(loop_scope="session")
class TestChatService:
    """Test case for the ChatService class."""
    
    async def test_session_isolation(self, chat_service):
        """Test that different session IDs maintain isolated conversation histories."""
        
        # Generate unique session IDs for testing
        session_id_1 = str(uuid.uuid4())
        session_id_2 = str(uuid.uuid4())
        
        # Test 1: Send initial messages for each session
        response_1a = await chat_service.get_chat_response("My name is Alex.", session_id_1)
        response_2a = await chat_service.get_chat_response("My name is Taylor.", session_id_2)
        
        print(f"Session 1 Initial Response: {response_1a}")
        print(f"Session 2 Initial Response: {response_2a}")
        
        # Test 2: Send follow-up messages to test memory
        response_1b = await chat_service.get_chat_response("What's my name?", session_id_1)
        response_2b = await chat_service.get_chat_response("What's my name?", session_id_2)
        
        print(f"Session 1 Memory Test Response: {response_1b}")
        print(f"Session 2 Memory Test Response: {response_2b}")
        
        # Assert that the follow-up responses contain the correct names
        assert "Alex" in response_1b, "ChatService failed to remember name for session 1"
        assert "Taylor" in response_2b, "ChatService failed to remember name for session 2"
        
        # Test 3: Cross-check to ensure no state contamination
        response_1c = await chat_service.get_chat_response("Is my name Taylor?", session_id_1)
        print(f"Session 1 Cross-contamination Test Response: {response_1c}")
        
        # The response should indicate that the user's name is Alex, not Taylor
        assert "Alex" in response_1c, "ChatService response should mention the correct name (Alex)"
        assert "Yes" not in response_1c.lower(), "ChatService should not agree that session 1's name is Taylor"

    async def test_message_history_management(self, chat_service):
        """Test that the message history is properly maintained across multiple interactions."""
        
        # Generate a unique session ID for testing
        session_id = str(uuid.uuid4())
        
        # Send a series of messages to build up history
        messages = [
            "My favorite color is blue.",
            "I enjoy hiking in the mountains.",
            "I have a dog named Rex."
        ]
        
        for message in messages:
            await chat_service.get_chat_response(message, session_id)
        
        # Test recall of information from earlier in the conversation
        response = await chat_service.get_chat_response("What's my favorite color?", session_id)
        print(f"Color Recall Response: {response}")
        assert "blue" in response.lower(), "ChatService failed to recall favorite color from history"
        
        response = await chat_service.get_chat_response("What's my dog's name?", session_id)
        print(f"Dog Name Recall Response: {response}")
        assert "Rex" in response, "ChatService failed to recall dog's name from history"

    async def test_memory_persistence_after_multiple_sessions(self, chat_service):
        """Test that memory persists correctly after handling multiple different sessions."""
        
        # Create three different session IDs
        session_ids = [str(uuid.uuid4()) for _ in range(3)]
        
        # Initialize each session with distinct information
        session_data = {
            session_ids[0]: {"name": "Alice", "hobby": "painting"},
            session_ids[1]: {"name": "Bob", "hobby": "chess"},
            session_ids[2]: {"name": "Charlie", "hobby": "swimming"}
        }
        
        # First round: Set up initial information for each session
        for session_id, data in session_data.items():
            await chat_service.get_chat_response(
                f"My name is {data['name']} and I enjoy {data['hobby']}.", 
                session_id
            )
        
        # Second round: Interleave interactions across sessions
        # This tests if the service can handle switching between sessions without memory contamination
        for i in range(2):  # Two rounds of interleaved messages
            for session_id in session_ids:
                await chat_service.get_chat_response(
                    f"I'm still here, just checking in.", 
                    session_id
                )
        
        # Final round: Verify each session maintained its unique memory
        for session_id, data in session_data.items():
            # Ask about name
            response = await chat_service.get_chat_response("What's my name?", session_id)
            print(f"Session {session_id[:8]}... name recall: {response[:100]}...")
            assert data["name"] in response, f"Failed to recall name '{data['name']}' for session {session_id[:8]}"
            
            # Ask about hobby
            response = await chat_service.get_chat_response("What hobby do I enjoy?", session_id)
            print(f"Session {session_id[:8]}... hobby recall: {response[:100]}...")
            assert data["hobby"] in response.lower(), f"Failed to recall hobby '{data['hobby']}' for session {session_id[:8]}"

if __name__ == "__main__":
    # When run directly as a script, run the tests with pytest
    pytest.main(['-xvs', __file__])
