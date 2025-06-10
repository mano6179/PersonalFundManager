import asyncio
from datetime import datetime, date
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import json
import os

# MongoDB connection string
MONGODB_URL = "mongodb+srv://manoharmeesala6179:xw9momNJ0YaAocFF@personalfundmanager.y4hlu4o.mongodb.net/?retryWrites=true&w=majority&appName=PersonalFundManager"

# Create MongoDB client
client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
db = client.personalfundmanager

# Collections
investors_collection = db.investors
nav_collection = db.nav_history
trades_collection = db.trades
holdings_collection = db.holdings
positions_collection = db.positions

# Sample initial data (from your existing mock data)
initial_investors = [
    {
        "id": 1,
        "name": "John Doe",
        "initial_capital": 1000000,
        "current_capital": 1150000,
        "join_date": date(2023, 1, 15).isoformat(),
        "profit_share": 20,
        "is_active": True
    },
    {
        "id": 2,
        "name": "Jane Smith",
        "initial_capital": 500000,
        "current_capital": 575000,
        "join_date": date(2023, 3, 10).isoformat(),
        "profit_share": 15,
        "is_active": True
    }
]

async def init_db():
    """Initialize database with collections and indexes"""
    try:
        # Verify the connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")

        # Create indexes
        await investors_collection.create_index("id", unique=True)
        await nav_collection.create_index([("investor_id", 1), ("date", -1)])
        await trades_collection.create_index([("trade_id", 1)], unique=True)
        await holdings_collection.create_index([("tradingsymbol", 1), ("user_id", 1)])
        await positions_collection.create_index([("tradingsymbol", 1), ("user_id", 1)])

        # Import initial data
        if await investors_collection.count_documents({}) == 0:
            await investors_collection.insert_many(initial_investors)
            print("Imported initial investors data")

        # Import existing trades if any
        trades_file = "zerodha_trades.json"
        if os.path.exists(trades_file):
            with open(trades_file, 'r') as f:
                trades_data = json.load(f)
                if trades_data:
                    await trades_collection.insert_many(trades_data)
                    print(f"Imported {len(trades_data)} trades from {trades_file}")

        print("Database initialization completed successfully!")

    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

async def main():
    await init_db()
    
if __name__ == "__main__":
    asyncio.run(main())
