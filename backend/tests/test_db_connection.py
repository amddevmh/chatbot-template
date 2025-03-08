#!/usr/bin/env python3
"""
Simple test to verify database connection
"""
import asyncio
import os
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.database.mongodb import init_db
from dotenv import load_dotenv

# Configure pytest-asyncio
pytest_asyncio_mode = "strict"

@pytest.mark.asyncio
async def test_db_connection(shared_db):
    """Test the database connection"""
    print("Testing database connection using shared fixture...")
    
    # Load environment variables
    load_dotenv("app/.env")
    
    # Print the MongoDB URI and database name for debugging
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db = os.getenv("MONGODB_DATABASE")
    print(f"MongoDB URI: {mongodb_uri}")
    print(f"MongoDB Database: {mongodb_db}")
    
    try:
        # We're already connected via the shared_db fixture
        print("✅ Database connection successful via shared fixture!")
        
        # Try to ping the database
        print("Pinging database...")
        client = AsyncIOMotorClient(mongodb_uri)
        await client.admin.command('ping')
        print("✅ Database ping successful!")
        
        # Try to count users
        print("Counting users in database...")
        count = await User.count()
        print(f"✅ User count: {count}")
        
        print("\n=== DATABASE CONNECTION TEST COMPLETED SUCCESSFULLY ===")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n=== DATABASE CONNECTION TEST FAILED ===")

if __name__ == "__main__":
    # Run the test with pytest
    pytest.main(['-xvs', __file__])
