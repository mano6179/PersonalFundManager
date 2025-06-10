from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from ..models.market_update import MarketUpdate
from ..config.database import get_database

class MarketUpdateService:
    def __init__(self):
        self.db = get_database()

    async def create_update(self, update: MarketUpdate) -> MarketUpdate:
        """Create a new market update"""
        result = await self.db.market_updates.insert_one(update.dict())
        update.id = str(result.inserted_id)
        return update

    async def get_update(self, update_id: str) -> MarketUpdate:
        """Get a specific market update by ID"""
        update = await self.db.market_updates.find_one({"_id": update_id})
        if not update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Market update not found"
            )
        return MarketUpdate(**update)

    async def get_updates(
        self,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> List[MarketUpdate]:
        """Get market updates with optional filtering"""
        query = {}
        if category:
            query["category"] = category
        if is_public is not None:
            query["is_public"] = is_public

        cursor = self.db.market_updates.find(query).skip(skip).limit(limit)
        updates = await cursor.to_list(length=limit)
        return [MarketUpdate(**update) for update in updates]

    async def update_update(self, update_id: str, update: MarketUpdate) -> MarketUpdate:
        """Update an existing market update"""
        result = await self.db.market_updates.update_one(
            {"_id": update_id},
            {"$set": update.dict(exclude={"id"})}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Market update not found"
            )
        return await self.get_update(update_id)

    async def delete_update(self, update_id: str) -> bool:
        """Delete a market update"""
        result = await self.db.market_updates.delete_one({"_id": update_id})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Market update not found"
            )
        return True

    async def get_public_updates(
        self,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None
    ) -> List[MarketUpdate]:
        """Get public market updates"""
        return await self.get_updates(skip, limit, category, is_public=True)

    async def search_updates(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[MarketUpdate]:
        """Search market updates by title or content"""
        cursor = self.db.market_updates.find(
            {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}}
                ]
            }
        ).skip(skip).limit(limit)
        updates = await cursor.to_list(length=limit)
        return [MarketUpdate(**update) for update in updates] 