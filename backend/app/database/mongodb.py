import os
import pathlib
from typing import List, Type
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pydantic import BaseModel
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Get the app directory path
app_dir = pathlib.Path(__file__).parent.parent

# Load environment variables from .env file in the app directory
load_dotenv(dotenv_path=os.path.join(app_dir, '.env'))

# MongoDB Atlas connection settings from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "nutrition_assistant")

# MongoDB client with server API version 1
client = AsyncIOMotorClient(MONGODB_URI, server_api=ServerApi('1'))
db = client[DATABASE_NAME]


async def init_db(document_models: List[Type[BaseModel]]) -> None:
    """Initialize the database connection and register document models"""
    try:
        # Test connection with a ping
        await client.admin.command('ping')
        print("Pinged your MongoDB Atlas deployment. Connection successful!")
        
        # Initialize Beanie with the document models
        await init_beanie(
            database=db,
            document_models=document_models
        )
        print(f"Connected to MongoDB Atlas")
        print(f"Using database: {DATABASE_NAME}")
        print(f"Registered {len(document_models)} document models")
    except Exception as e:
        print(f"Failed to connect to MongoDB Atlas: {e}")
        raise


async def close_db_connection() -> None:
    """Close the database connection"""
    client.close()
    print("Closed MongoDB connection")
