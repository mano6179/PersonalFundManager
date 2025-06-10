from typing import List, Optional, Dict, Any
from pymongo.errors import PyMongoError, ConnectionFailure, DuplicateKeyError
from app.config.database import (
    investors_collection,
    nav_collection,
    trades_collection,
    holdings_collection,
    positions_collection
)
from app.utils.model_utils import serialize_model, deserialize_model
from app.models.nav import FundEntry, NAVRecord
from app.models.zerodha import (
    ZerodhaHolding,
    ZerodhaPosition,
    ZerodhaTrade
)
from app.exceptions.database_exceptions import (
    DatabaseException,
    ConnectionException,
    QueryException,
    DocumentNotFoundException
)
import logging

logger = logging.getLogger(__name__)

class DatabaseRepository:
    @staticmethod
    async def create_investor(investor_data: dict) -> dict:
        try:
            result = await investors_collection.insert_one(investor_data)
            return await investors_collection.find_one({"_id": result.inserted_id})
        except DuplicateKeyError as e:
            raise DatabaseException(f"Investor already exists: {str(e)}", "create_investor", e)
        except PyMongoError as e:
            raise DatabaseException(f"Failed to create investor: {str(e)}", "create_investor", e)

    @staticmethod
    async def get_investor(investor_id: int) -> Optional[dict]:
        return await investors_collection.find_one({"id": investor_id})

    @staticmethod
    async def get_all_investors() -> List[dict]:
        cursor = investors_collection.find({})
        return [doc async for doc in cursor]

    @staticmethod
    async def update_investor(investor_id: int, investor_data: dict) -> Optional[dict]:
        result = await investors_collection.update_one(
            {"id": investor_id},
            {"$set": investor_data}
        )
        if result.modified_count:
            return await investors_collection.find_one({"id": investor_id})
        return None

    @staticmethod
    async def create_nav_record(nav_data: dict) -> dict:
        result = await nav_collection.insert_one(nav_data)
        return await nav_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    async def get_nav_history(investor_id: int) -> List[dict]:
        cursor = nav_collection.find({"investor_id": investor_id}).sort("date", -1)
        return [doc async for doc in cursor]

    @staticmethod
    async def store_trade(trade_data: dict) -> dict:
        result = await trades_collection.insert_one(trade_data)
        return await trades_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    async def get_trades(user_id: str) -> List[dict]:
        cursor = trades_collection.find({"user_id": user_id}).sort("fill_timestamp", -1)
        return [doc async for doc in cursor]

    @staticmethod
    async def update_holdings(user_id: str, holdings: List[dict]) -> bool:
        # Delete existing holdings
        await holdings_collection.delete_many({"user_id": user_id})
        
        if holdings:
            # Insert new holdings
            await holdings_collection.insert_many(
                [{"user_id": user_id, **holding} for holding in holdings]
            )
        return True

    @staticmethod
    async def update_positions(user_id: str, positions: List[dict]) -> bool:
        # Delete existing positions
        await positions_collection.delete_many({"user_id": user_id})
        
        if positions:
            # Flatten and insert positions
            all_positions = []
            for pos_type, pos_list in positions.items():
                all_positions.extend([{
                    "user_id": user_id,
                    "position_type": pos_type,
                    **position
                } for position in pos_list])
            
            if all_positions:
                await positions_collection.insert_many(all_positions)
        return True

    @staticmethod
    async def get_nav_records(investor_id: int, start_date: str = None, end_date: str = None) -> List[dict]:
        try:
            query = {"investor_id": investor_id}
            if start_date and end_date:
                query["date"] = {"$gte": start_date, "$lte": end_date}
            
            cursor = nav_collection.find(query).sort("date", -1)
            records = await cursor.to_list(length=None)
            if not records:
                raise DocumentNotFoundException(f"No NAV records found for investor {investor_id}")
            return records
        except PyMongoError as e:
            raise DatabaseException(f"Failed to fetch NAV records: {str(e)}", "get_nav_records", e)

    @staticmethod
    async def save_trades(trades: List[ZerodhaTrade], user_id: str) -> None:
        try:
            if not trades:
                return
            
            operations = []
            for trade in trades:
                trade_dict = serialize_model(trade)
                trade_dict["user_id"] = user_id
                operations.append(
                    {"replace_one": {
                        "filter": {"trade_id": trade.trade_id},
                        "replacement": trade_dict,
                        "upsert": True
                    }}
                )
            
            await trades_collection.bulk_write([op["replace_one"] for op in operations])
        except PyMongoError as e:
            raise DatabaseException(f"Failed to save trades: {str(e)}", "save_trades", e)

    @staticmethod
    async def update_holdings(holdings: List[ZerodhaHolding], user_id: str) -> None:
        try:
            if not holdings:
                return
                
            # Delete existing holdings for the user
            await holdings_collection.delete_many({"user_id": user_id})
            
            # Insert new holdings
            holdings_data = [
                {**serialize_model(holding), "user_id": user_id}
                for holding in holdings
            ]
            await holdings_collection.insert_many(holdings_data)
        except PyMongoError as e:
            raise DatabaseException(f"Failed to update holdings: {str(e)}", "update_holdings", e)

    @staticmethod
    async def update_positions(positions: List[ZerodhaPosition], user_id: str) -> None:
        try:
            if not positions:
                return
                
            # Delete existing positions for the user
            await positions_collection.delete_many({"user_id": user_id})
            
            # Insert new positions
            positions_data = [
                {**serialize_model(position), "user_id": user_id}
                for position in positions
            ]
            await positions_collection.insert_many(positions_data)
        except PyMongoError as e:
            raise DatabaseException(f"Failed to update positions: {str(e)}", "update_positions", e)

    @staticmethod
    async def get_holdings(user_id: str) -> List[dict]:
        try:
            cursor = holdings_collection.find({"user_id": user_id})
            holdings = await cursor.to_list(length=None)
            if not holdings:
                logger.info(f"No holdings found for user {user_id}")
                return []
            return holdings
        except PyMongoError as e:
            raise DatabaseException(f"Failed to fetch holdings: {str(e)}", "get_holdings", e)

    @staticmethod
    async def get_positions(user_id: str) -> List[dict]:
        try:
            cursor = positions_collection.find({"user_id": user_id})
            positions = await cursor.to_list(length=None)
            if not positions:
                logger.info(f"No positions found for user {user_id}")
                return []
            return positions
        except PyMongoError as e:
            raise DatabaseException(f"Failed to fetch positions: {str(e)}", "get_positions", e)

    @staticmethod
    async def get_trades(user_id: str, start_date: str = None, end_date: str = None) -> List[dict]:
        try:
            query = {"user_id": user_id}
            if start_date and end_date:
                query["trade_date"] = {"$gte": start_date, "$lte": end_date}
            
            cursor = trades_collection.find(query).sort("trade_date", -1)
            trades = await cursor.to_list(length=None)
            if not trades:
                logger.info(f"No trades found for user {user_id} in the specified date range")
                return []
            return trades
        except PyMongoError as e:
            raise DatabaseException(f"Failed to fetch trades: {str(e)}", "get_trades", e)

    @staticmethod
    async def save_nav_record(nav_record: NAVRecord) -> dict:
        try:
            nav_dict = serialize_model(nav_record)
            result = await nav_collection.replace_one(
                {"investor_id": nav_record.investor_id, "date": nav_record.date},
                nav_dict,
                upsert=True
            )
            return nav_dict
        except PyMongoError as e:
            raise DatabaseException(f"Failed to save NAV record: {str(e)}", "save_nav_record", e)
