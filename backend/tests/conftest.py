"""Central pytest configuration for all tests"""
import os
import sys
import asyncio
import pytest
import pytest_asyncio

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.database.mongodb import init_db, close_db_connection

# Configure pytest-asyncio
pytest_asyncio_mode = "strict"

# Set default fixture loop scope to function to ensure proper isolation
pytest_asyncio.default_fixture_loop_scope = "function"

@pytest.fixture(scope="session")
def event_loop_policy():
    """Configure the event loop policy for the test session"""
    policy = asyncio.get_event_loop_policy()
    return policy

@pytest_asyncio.fixture(scope="session")
async def shared_db():
    """Initialize the database once for all tests"""
    try:
        print("\nInitializing shared database connection...")
        await init_db([User])
        print("Database initialized successfully for all tests")
        yield
    finally:
        print("\nClosing shared database connection...")
        await close_db_connection()
