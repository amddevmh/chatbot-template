#!/usr/bin/env python3
"""
Tests for MongoDB session tracking in ChatService
"""
import sys
import os
import uuid
import pytest
import pytest_asyncio

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chat_service import ChatService
from app.models.chat_session import ChatSessionMetadata
from app.models.user import User
from app.database.mongodb import init_db

# Configure pytest-asyncio
pytest_asyncio_mode = "strict"

@pytest_asyncio.fixture
async def mongodb_chat_service(shared_db):
    """Create a chat service instance with MongoDB persistence for testing."""
    # Make sure ChatSessionMetadata is registered with the database
    # Note: User model is already registered by the shared_db fixture
    await init_db([ChatSessionMetadata])
    
    # Create the service
    service = ChatService()
    
    # Yield the service for test use
    yield service
    
    # Cleanup: Ensure memory resources are properly released
    if hasattr(service, 'memory') and service.memory:
        try:
            # Clear any session data that might have been created
            if hasattr(service.memory, 'checkpoints'):
                service.memory.checkpoints.clear()
        except Exception as e:
            print(f"Warning: Error during chat_service cleanup: {e}")

@pytest.mark.asyncio(loop_scope="session")
class TestMongoDBSessionTracking:

    async def test_session_creation_and_listing(self, mongodb_chat_service):
        """Test creating a session and listing sessions for a user"""
        # Generate a unique username for testing
        test_username = f"test_user_{uuid.uuid4().hex[:8]}"
        
        # Create a new session
        session = await mongodb_chat_service.create_session(
            username=test_username,
            session_name="Test Session"
        )
        
        # Verify session was created correctly
        assert session is not None
        assert "session_id" in session
        assert session["name"] == "Test Session"
        assert session["session_id"].startswith(f"{test_username}_")
        
        # List sessions for the user
        sessions = await mongodb_chat_service.list_user_sessions(test_username)
        
        # Verify session listing works
        assert len(sessions) >= 1
        assert any(s["session_id"] == session["session_id"] for s in sessions)
    
    async def test_chat_with_session_persistence(self, mongodb_chat_service):
        """Test sending messages to a session and retrieving history"""
        # Generate a unique username for testing
        test_username = f"test_user_{uuid.uuid4().hex[:8]}"
        
        # Create a new session
        session = await mongodb_chat_service.create_session(
            username=test_username,
            session_name="Chat Persistence Test"
        )
        session_id = session["session_id"]
        
        # Send a test message
        test_message = "Hello, this is a test message for MongoDB persistence"
        response = await mongodb_chat_service.get_chat_response(
            message=test_message,
            session_id=session_id
        )
        
        # Verify we got a response
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Get session history
        history = await mongodb_chat_service.get_session_history(session_id)
        
        # Verify history contains our message
        assert len(history) >= 2  # Should have at least user message and response
        assert any(test_message in msg["content"] for msg in history)


if __name__ == "__main__":
    # When run directly as a script, run the tests with pytest
    pytest.main(["-xvs", __file__])
