from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.database import get_database

logger = logging.getLogger(__name__)

class Migration:
    def __init__(self, version: str):
        self.version = version
        self.timestamp = datetime.utcnow()

    async def up(self, db):
        """
        Implement the forward migration here
        """
        pass

    async def down(self, db):
        """
        Implement the rollback migration here
        """
        pass

    async def run(self):
        try:
            db = await get_database()
            
            # Check if migration was already applied
            if await self._is_applied(db):
                logger.info(f"Migration {self.version} already applied")
                return
            
            # Run migration
            await self.up(db)
            
            # Record migration
            await self._record_migration(db)
            
            logger.info(f"Successfully applied migration {self.version}")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            await self.down(db)
            raise

    async def _is_applied(self, db):
        return await db.migrations.find_one({"version": self.version}) is not None

    async def _record_migration(self, db):
        await db.migrations.insert_one({
            "version": self.version,
            "applied_at": self.timestamp
        })