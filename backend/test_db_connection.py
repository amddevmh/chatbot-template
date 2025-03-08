#!/usr/bin/env python3
"""
Simple test to verify database connection
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.database.mongodb import init_db
from dotenv import load_dotenv

async def test_db_connection():
    """Test the database connection"""
    print("Testing database connection...")
    
    # Load environment variables
    load_dotenv("app/.env")
    
    # Print the MongoDB URI and database name for debugging
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db = os.getenv("MONGODB_DATABASE")
    print(f"MongoDB URI: {mongodb_uri}")
    print(f"MongoDB Database: {mongodb_db}")
    
    try:
        # Try to initialize the database
        print("Initializing database connection...")
        await init_db([User])
        print("✅ Database connection successful!")
        
        # Try to ping the database
        print("Pinging database...")
        client = AsyncIOMotorClient(mongodb_uri)
        await client.admin.command('ping')
        print("✅ Database ping successful!")
        
        # Try to initialize Beanie with the User model
        print("Initializing Beanie ODM...")
        await init_beanie(database=client[mongodb_db], document_models=[User])
        print("✅ Beanie initialization successful!")
        
        # Try to count users
        print("Counting users in database...")
        count = await User.count()
        print(f"✅ User count: {count}")
        
        print("\n=== DATABASE CONNECTION TEST COMPLETED SUCCESSFULLY ===")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n=== DATABASE CONNECTION TEST FAILED ===")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_db_connection())
