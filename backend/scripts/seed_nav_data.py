from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection string
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")

# Mock NAV data to be migrated
mock_nav_data = [
    {
        "date": datetime.strptime("2023-01-15", "%Y-%m-%d"),
        "nav_value": 1000.00,
        "investor_id": 1
    },
    {
        "date": datetime.strptime("2023-02-15", "%Y-%m-%d"),
        "nav_value": 1050.00,
        "investor_id": 1
    },
    {
        "date": datetime.strptime("2023-03-15", "%Y-%m-%d"),
        "nav_value": 1150.00,
        "investor_id": 1
    },
    {
        "date": datetime.strptime("2023-04-15", "%Y-%m-%d"),
        "nav_value": 1200.00,
        "investor_id": 1
    }
]

async def seed_nav_data():
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
        db = client.personalfundmanager
        
        # Clear existing NAV data
        await db.nav_history.delete_many({})
        logger.info("Cleared existing NAV data")
        
        # Insert mock data
        result = await db.nav_history.insert_many(mock_nav_data)
        logger.info(f"Successfully inserted {len(result.inserted_ids)} NAV records")
        
        # Verify insertion
        count = await db.nav_history.count_documents({})
        logger.info(f"Total NAV records in database: {count}")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"Error seeding NAV data: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_nav_data())