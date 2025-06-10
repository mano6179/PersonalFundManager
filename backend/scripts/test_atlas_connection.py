import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "personal_fund_manager")

async def test_atlas_connection():
    """Test MongoDB Atlas connection and verify IP address"""
    try:
        # Get current public IP
        current_ip = requests.get('https://api.ipify.org').text
        logger.info(f"Your current public IP address is: {current_ip}")
        
        if current_ip != "49.43.202.97":
            logger.warning(f"Your current IP ({current_ip}) doesn't match the whitelisted IP (49.43.202.97)")
            logger.warning("Please update the IP whitelist in MongoDB Atlas dashboard")
        
        # Test MongoDB connection
        client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
        
        # Try to ping the database
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas!")
        
        # Get database info
        db = client[DATABASE_NAME]
        collections = await db.list_collection_names()
        logger.info(f"Available collections: {collections}")
        
        # Close the connection
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_atlas_connection()) 