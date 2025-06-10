import asyncio
import sqlite3
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")

async def migrate_data():
    try:
        # Check if SQLite database exists
        db_path = os.path.join(os.path.dirname(__file__), '..', 'app.db')
        if not os.path.exists(db_path):
            logger.error(f"SQLite database not found at {db_path}")
            return

        # Connect to SQLite
        sqlite_conn = sqlite3.connect(db_path)
        cursor = sqlite_conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logger.info(f"Found tables: {[table[0] for table in tables]}")
        
        # Connect to MongoDB
        mongo_client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
        db = mongo_client.personalfundmanager
        
        # Try different possible table names for NAV history
        possible_tables = ['nav_history', 'navhistory', 'nav', 'nav_records']
        nav_table = None
        
        for table in possible_tables:
            try:
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                nav_table = table
                break
            except sqlite3.OperationalError:
                continue
        
        if nav_table:
            logger.info(f"Found NAV data in table: {nav_table}")
            # Get column names
            cursor.execute(f"PRAGMA table_info({nav_table})")
            columns = [col[1] for col in cursor.fetchall()]
            logger.info(f"Table columns: {columns}")
            
            # Construct query based on available columns
            query = f"SELECT * FROM {nav_table}"
            cursor.execute(query)
            nav_records = cursor.fetchall()
            
            if nav_records:
                # Map data based on column names
                nav_data = []
                for record in nav_records:
                    data = {}
                    for i, col in enumerate(columns):
                        if col.lower() in ['date', 'timestamp']:
                            data['date'] = datetime.strptime(str(record[i]), "%Y-%m-%d")
                        elif col.lower() in ['nav_value', 'nav', 'value']:
                            data['nav_value'] = float(record[i])
                        elif col.lower() in ['investor_id', 'investorid']:
                            data['investor_id'] = int(record[i])
                    nav_data.append(data)
                
                # Insert into MongoDB
                await db.nav_history.insert_many(nav_data)
                logger.info(f"Migrated {len(nav_data)} NAV records")
            else:
                logger.warning(f"No records found in {nav_table}")
        else:
            logger.error("Could not find NAV history table")
        
        # Close connections
        sqlite_conn.close()
        mongo_client.close()
        
        logger.info("Migration completed")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_data())