from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import logging
from typing import Optional

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")

DATABASE_NAME = os.getenv("DATABASE_NAME", "PersonalFundManager")

# Initialize MongoDB client
client: Optional[AsyncIOMotorClient] = None
db = None

# Collection references
nav_collection = None
trades_collection = None
investors_collection = None
holdings_collection = None
positions_collection = None
logs_collection = None

async def init_db():
    """Initialize database connection and collections"""
    global client, db, nav_collection, trades_collection, investors_collection, holdings_collection, positions_collection, logs_collection
    
    try:
        # Initialize MongoDB client with server API version
        client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
        
        # Get database reference
        db = client[DATABASE_NAME]
        
        # Initialize collections
        nav_collection = db.nav_history
        trades_collection = db.trades
        investors_collection = db.investors
        holdings_collection = db.holdings
        positions_collection = db.positions
        logs_collection = db.logs
        
        # Verify connection
        await client.admin.command('ping')
        logging.info(f"Successfully connected to MongoDB Atlas - Database: {DATABASE_NAME}")
        
        # Log available collections
        collections = await db.list_collection_names()
        logging.info(f"Available collections: {collections}")
        
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB Atlas: {str(e)}")
        raise

async def get_database():
    """Get database instance"""
    global db
    if db is None:
        await init_db()
    return db

def get_nav_collection():
    """Get NAV collection reference"""
    if nav_collection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return nav_collection

def get_trades_collection():
    """Get trades collection reference"""
    if trades_collection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return trades_collection

def get_investors_collection():
    """Get investors collection reference"""
    if investors_collection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return investors_collection

def get_holdings_collection():
    """Get holdings collection reference"""
    if holdings_collection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return holdings_collection

def get_positions_collection():
    """Get positions collection reference"""
    if positions_collection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return positions_collection

def get_logs_collection():
    """Get logs collection reference"""
    if logs_collection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return logs_collection

async def close_db():
    """Close database connection"""
    if client:
        client.close()
        logging.info("Database connection closed")
