import os
import subprocess
from datetime import datetime
import logging
from dotenv import load_dotenv
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")

async def verify_connection():
    """Verify MongoDB connection before backup"""
    try:
        client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {str(e)}")
        return False

def ensure_backup_dir():
    """Ensure backup directory exists"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logger.info(f"Created backup directory at {BACKUP_DIR}")

async def create_backup():
    """Create MongoDB backup using mongodump"""
    try:
        # Verify connection first
        if not await verify_connection():
            return False

        # Ensure backup directory exists
        ensure_backup_dir()

        # Create timestamp for backup file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")

        # Construct mongodump command
        cmd = [
            "mongodump",
            "--uri", MONGODB_URL,
            "--out", backup_path,
            "--gzip"
        ]

        # Execute mongodump
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        if process.returncode == 0:
            logger.info(f"Backup created successfully at {backup_path}")
            
            # Cleanup old backups (keep last 5)
            cleanup_old_backups()
            return True
        else:
            logger.error(f"Backup failed: {process.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during backup: {str(e)}")
        return False

def cleanup_old_backups():
    """Keep only the last 5 backups"""
    try:
        # List all backup directories
        backups = [d for d in os.listdir(BACKUP_DIR) if d.startswith("backup_")]
        backups.sort(reverse=True)  # Sort by name (which includes timestamp)

        # Remove old backups
        for old_backup in backups[5:]:  # Keep only the 5 most recent
            backup_path = os.path.join(BACKUP_DIR, old_backup)
            subprocess.run(["rm", "-rf", backup_path], check=True)
            logger.info(f"Removed old backup: {old_backup}")

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def restore_backup(backup_path):
    """Restore MongoDB from backup"""
    try:
        cmd = [
            "mongorestore",
            "--uri", MONGODB_URL,
            "--gzip",
            backup_path
        ]

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        if process.returncode == 0:
            logger.info(f"Restore completed successfully from {backup_path}")
            return True
        else:
            logger.error(f"Restore failed: {process.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Restore failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during restore: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(create_backup())
