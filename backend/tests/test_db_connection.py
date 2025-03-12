#!/usr/bin/env python3
"""
Simple test to verify database connection
"""
import os
import pytest
from app.models.user import User
from app.database.mongodb import init_db
from dotenv import load_dotenv

# Configure pytest-asyncio
pytest_asyncio_mode = "strict"

@pytest.mark.asyncio(loop_scope="session")
async def test_db_connection(shared_db):
    """Test the database connection"""
    print("Testing database connection using shared fixture...")
    
    # Load environment variables
    load_dotenv("app/.env")
    
    # Print the MongoDB database name for debugging (avoid printing full URI with credentials)
    mongodb_db = os.getenv("MONGODB_DATABASE")
    print(f"MongoDB Database: {mongodb_db}")
    
    try:        
        # Try to count users by accessing the database collection directly
        print("Counting users in database...")
        
        try:
            # Try to count users with the Beanie model
            count = await User.count()
            print(f"✅ User count: {count}")
            
            print("\n=== DATABASE CONNECTION TEST COMPLETED SUCCESSFULLY ===")
            
        except RuntimeError as e:
            if "attached to a different loop" in str(e):
                print("❌ Event loop error detected: The database connection is using a different event loop")
                print("   than the test function. This is a common issue with pytest-asyncio and Beanie.")
                print("   To fix this, we need to ensure both are using the same event loop.")
                
                # For debugging purposes, print a simplified version of the error
                error_msg = str(e)
                simplified_msg = "Event loop mismatch: Task is using one loop, but Future is attached to a different loop"
                print(f"\nSimplified error: {simplified_msg}")
                
                print("\n=== DATABASE CONNECTION TEST FAILED (EVENT LOOP ISSUE) ===")
                raise
            else:
                raise
            
    except Exception as e:
        print(f"❌ Database connection failed: {type(e).__name__}: {str(e)}")
        print("\n=== DATABASE CONNECTION TEST FAILED ===")

if __name__ == "__main__":
    # Run the test with pytest
    pytest.main(['-xvs', __file__])
