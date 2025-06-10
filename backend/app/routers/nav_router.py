from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from app.repositories.database import DatabaseRepository
from app.utils.model_utils import serialize_model, deserialize_model
from app.models.nav import NAVRecord
from app.config.database import get_nav_collection, init_db
import logging

router = APIRouter(
    prefix="/api/nav",
    tags=["nav"],
)
logger = logging.getLogger(__name__)

# Models
class Investor(BaseModel):
    id: int
    name: str
    initial_capital: float
    current_capital: float
    join_date: date
    profit_share: float
    is_active: bool

# Routes
@router.get("/investors", response_model=List[Investor])
async def get_investors():
    """Get all investors"""
    try:
        investors = await DatabaseRepository.get_all_investors()
        return [Investor(**deserialize_model(investor)) for investor in investors]
    except Exception as e:
        logger.error(f"Error fetching investors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch investors")

@router.get("/investors/{investor_id}", response_model=Investor)
async def get_investor(investor_id: int):
    """Get specific investor details"""
    try:
        investor = await DatabaseRepository.get_investor(investor_id)
        if not investor:
            raise HTTPException(status_code=404, detail="Investor not found")
        return Investor(**deserialize_model(investor))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching investor: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch investor")

@router.get("/nav/{investor_id}", response_model=List[NAVRecord])
async def get_nav_history(investor_id: int):
    """Get NAV history for specific investor"""
    try:
        # Check if investor exists
        investor = await DatabaseRepository.get_investor(investor_id)
        if not investor:
            raise HTTPException(status_code=404, detail="Investor not found")
        
        # Get NAV history
        nav_history = await DatabaseRepository.get_nav_history(investor_id)
        return [NAVRecord(**deserialize_model(record)) for record in nav_history]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching NAV history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch NAV history")

@router.get("/history")
async def get_nav_history(include_details: bool = False):
    """Get NAV history with detail level"""
    try:
        logger.info("Fetching NAV history")
        
        # Ensure database is initialized
        await init_db()
        
        # Get collection reference
        collection = get_nav_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not properly initialized")
        
        # Basic query to get NAV records
        cursor = collection.find().sort("timestamp", 1)
        nav_history = await cursor.to_list(length=None)
        
        processed_history = []
        for record in nav_history:
            record_time = record.get("timestamp") or record.get("date")
            if not record_time:
                logger.warning(f"Record missing timestamp: {record}")
                continue
                
            processed_record = {
                "date": record_time,
                "nav_value": float(record.get("nav_value", 0.0)),
                "fund_value": float(record.get("fund_value", 0.0)),
                "outstanding_units": float(record.get("outstanding_units", 0.0)),
                "funds_in_out": float(record.get("funds_in_out", 0.0)),
                "profit": float(record.get("profit", 0.0)),
                "charges": float(record.get("charges", 0.0)),
                "units_change": float(record.get("units_change", 0.0)),
                "previous_nav": float(record.get("previous_nav", 0.0)),
                "previous_fund_value": float(record.get("previous_fund_value", 0.0))
            }
            
            # Include detailed fields if requested
            if include_details:
                processed_record.update({
                    "cash_balance": float(record.get("cash_balance", 0.0)),
                    "equity_value": float(record.get("equity_value", 0.0)),
                    "other_assets": float(record.get("other_assets", 0.0)),
                    "transactions": record.get("transactions", [])
                })
            
            processed_history.append(processed_record)
        
        return processed_history
    except Exception as e:
        logger.error(f"Error fetching NAV history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch NAV history")

@router.post("/investors", response_model=Investor)
async def create_investor(investor: Investor):
    """Create a new investor"""
    try:
        # Prepare investor data
        investor_data = serialize_model(investor)
        
        # Create investor in database
        created_investor = await DatabaseRepository.create_investor(investor_data)
        if not created_investor:
            raise HTTPException(status_code=500, detail="Failed to create investor")
        
        return Investor(**deserialize_model(created_investor))
    except Exception as e:
        logger.error(f"Error creating investor: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create investor")

@router.get("/debug/latest-nav")
async def get_latest_nav():
    """Debug endpoint to check latest NAV entries"""
    try:
        # Ensure database is initialized
        await init_db()
        
        # Get collection reference
        collection = get_nav_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not properly initialized")
        
        # Get the last 5 NAV entries
        cursor = collection.find().sort("timestamp", -1).limit(5)
        latest_entries = await cursor.to_list(length=5)
        
        # Convert ObjectId to string for JSON serialization
        for entry in latest_entries:
            entry["_id"] = str(entry["_id"])
            
        return latest_entries
    except Exception as e:
        logger.error(f"Error fetching latest NAV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nav")
async def add_nav_record(nav_record: NAVRecord):
    """Add a new NAV record"""
    try:
        # Ensure database is initialized
        await init_db()
        
        # Get collection reference
        collection = get_nav_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not properly initialized")
        
        # Store NAV record in MongoDB
        nav_dict = {
            "nav_value": float(nav_record.nav_value),
            "investor_id": nav_record.investor_id,
            "timestamp": datetime.now()
        }
        
        result = await collection.insert_one(nav_dict)
        
        if result.inserted_id:
            # Broadcast update via WebSocket for real-time chart update
            await broadcast_nav_update(nav_dict)
            return {"id": str(result.inserted_id), "status": "success"}
            
    except Exception as e:
        logger.error(f"Error adding NAV record: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def broadcast_nav_update(nav_data):
    """Broadcast NAV update via WebSocket"""
    from app.services.websocket_service import manager
    await manager.broadcast_json({
        "type": "nav_update",
        "data": nav_data
    })

@router.get("/nav/debug")
async def debug_nav_data():
    """Debug endpoint to check NAV collection"""
    try:
        # Ensure database is initialized
        await init_db()
        
        # Get collection reference
        collection = get_nav_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not properly initialized")
        
        # Count total documents
        count = await collection.count_documents({})
        logger.info(f"Total NAV records: {count}")
        
        # Get latest 5 records
        cursor = collection.find().sort("timestamp", -1).limit(5)
        records = await cursor.to_list(length=5)
        
        # Convert ObjectId to string for JSON serialization
        for record in records:
            record["_id"] = str(record["_id"])
        
        return {
            "total_records": count,
            "latest_records": records,
            "collection_name": collection.name,
            "database_name": collection.database.name
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
