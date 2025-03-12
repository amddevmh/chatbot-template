"""Central pytest configuration for all tests"""
import os
import sys
import pytest_asyncio

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.database.mongodb import init_db, close_db_connection

# NOTE: pytest-asyncio configuration is now in pytest.ini
# This ensures the settings are loaded at the very beginning of pytest's execution
# See pytest.ini for the following settings:
# - asyncio_mode = strict
# - asyncio_default_fixture_loop_scope = session

@pytest_asyncio.fixture(scope="session")
async def shared_db():
    """Initialize the database once for all tests using the session event loop
    
    This fixture uses the session-scoped event loop provided by pytest-asyncio
    (configured via default_fixture_loop_scope = "session").
    """
    # The current event loop is already set by pytest-asyncio
    
    try:
        print("\nInitializing shared database connection...")
        await init_db([User])
        print("✅ Database initialized successfully for all tests via shared fixture")

        yield
    finally:
        print("\nClosing shared database connection...")
        await close_db_connection()
