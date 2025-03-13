#!/usr/bin/env python3
"""
Simple test to verify database connection
"""
import os
import pytest
from app.models.user import User
from app.database.mongodb import init_db
from dotenv import load_dotenv

# Configuration is now in pytest.ini

@pytest.mark.asyncio(loop_scope="session")
async def test_db_connection(shared_db):
    """Test the database connection
    
    This test verifies that:
    1. The database connection is established successfully
    2. We can perform basic operations like counting users
    
    The shared_db fixture handles the database initialization and cleanup.
    """
    print("Testing database connection using shared fixture...")
    
    # Load environment variables (consider moving this to conftest.py if needed by multiple tests)
    load_dotenv("app/.env")
    
    print("Counting users in database...")
    
    try:
        # Count users with the Beanie model
        count = await User.count()
        print(f"✅ User count: {count}")
        
        print("\n=== DATABASE CONNECTION TEST COMPLETED SUCCESSFULLY ===")
        
    except Exception as e:
        print(f"❌ Database operation failed: {type(e).__name__}")
        # Avoid printing the full error message as it might contain sensitive information
        print(f"Error type: {type(e).__name__}")
        print("\n=== DATABASE CONNECTION TEST FAILED ===")
        raise

if __name__ == "__main__":
    # Run the test with pytest
    pytest.main(['-xvs', __file__])
