from fastapi import APIRouter, HTTPException
from app.config.database import get_logs_collection, get_nav_collection, init_db
from datetime import datetime
import logging
from app.models.log_entry import LogEntry, WeeklyProfitLog, IVTrackerLog, TradeLog, MarketUpdateLog

router = APIRouter(
    prefix="/api/logs",
    tags=["logs"]
)

# Constants
INITIAL_NAV = 100.0
INITIAL_INVESTMENT = 400000.0  # ₹4,00,000 initial investment

async def get_latest_nav_data():
    """Get the latest NAV data including outstanding units"""
    try:
        collection = get_nav_collection()
        if collection is None:
            raise RuntimeError("Database not properly initialized")
            
        # Get the most recent NAV record
        cursor = collection.find().sort("timestamp", -1).limit(1)
        latest_nav = await cursor.to_list(length=1)
        
        if not latest_nav:
            # If no NAV records exist, return initial state
            initial_units = INITIAL_INVESTMENT / INITIAL_NAV
            return {
                "nav_value": INITIAL_NAV,
                "outstanding_units": initial_units,
                "fund_value": INITIAL_INVESTMENT
            }
            
        return {
            "nav_value": float(latest_nav[0].get("nav_value", INITIAL_NAV)),
            "outstanding_units": float(latest_nav[0].get("outstanding_units", INITIAL_INVESTMENT / INITIAL_NAV)),
            "fund_value": float(latest_nav[0].get("fund_value", INITIAL_INVESTMENT))
        }
    except Exception as e:
        logging.error(f"Error getting latest NAV: {str(e)}")
        raise

@router.get("/")
async def get_logs():
    try:
        # Ensure database is initialized
        await init_db()
        
        collection = get_logs_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not properly initialized")
            
        cursor = collection.find().sort("timestamp", -1)
        logs = await cursor.to_list(length=50)
        return logs
    except Exception as e:
        logging.error(f"Error fetching logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch logs")

@router.post("/")
async def create_log(log_data: LogEntry):
    try:
        # Ensure database is initialized
        await init_db()
        
        collection = get_logs_collection()
        if collection is None:
            raise HTTPException(status_code=500, detail="Database not properly initialized")
        
        # Convert to dict and ensure timestamp is set
        log_dict = log_data.dict()
        if not log_dict.get("timestamp"):
            log_dict["timestamp"] = datetime.utcnow()
            
        # If this is a weekly profit log, calculate and store the new NAV
        if log_dict["type"] == "weekly_profit":
            try:
                # Get the previous NAV data
                previous_nav_data = await get_latest_nav_data()
                previous_nav = previous_nav_data["nav_value"]
                outstanding_units = previous_nav_data["outstanding_units"]
                previous_fund_value = previous_nav_data["fund_value"]
                
                # Get the weekly update values
                profit = float(log_dict.get("profit", 0.0))
                charges = float(log_dict.get("charges", 0.0))
                funds_in_out = float(log_dict.get("funds_in_out", 0.0))
                
                # Calculate new fund value WITHOUT the new funds
                new_fund_value = previous_fund_value + profit - charges
                
                # Calculate new NAV
                if outstanding_units > 0:
                    new_nav = new_fund_value / outstanding_units
                else:
                    new_nav = previous_nav  # Keep the same NAV if no units
                
                # Calculate units to add/remove if there are funds in/out
                units_change = 0.0
                if funds_in_out != 0:
                    units_change = funds_in_out / new_nav
                    outstanding_units += units_change
                    new_fund_value += funds_in_out  # Add the new funds to the fund value
                
                # Store the new NAV record
                nav_collection = get_nav_collection()
                if nav_collection is None:
                    raise RuntimeError("Database not properly initialized")
                    
                nav_record = {
                    "nav_value": new_nav,
                    "outstanding_units": outstanding_units,
                    "fund_value": new_fund_value,
                    "timestamp": log_dict["timestamp"],
                    "profit": profit,
                    "charges": charges,
                    "funds_in_out": funds_in_out,
                    "units_change": units_change,
                    "previous_nav": previous_nav,
                    "previous_fund_value": previous_fund_value
                }
                
                await nav_collection.insert_one(nav_record)
                logging.info(f"New NAV record created: {nav_record}")
                
            except Exception as e:
                logging.error(f"Error creating NAV record: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to create NAV record: {str(e)}")
            
        # Insert the log entry
        result = await collection.insert_one(log_dict)
        
        if result.inserted_id is None:
            raise HTTPException(status_code=500, detail="Failed to create log entry")
            
        return {"id": str(result.inserted_id), "message": "Log entry created successfully"}
    except Exception as e:
        logging.error(f"Error creating log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create log entry: {str(e)}")

async def insert_historical_nav_data():
    """Insert historical NAV data"""
    try:
        nav_collection = get_nav_collection()
        if nav_collection is None:
            raise RuntimeError("Database not properly initialized")

        # Historical data
        historical_data = [
            {
                "timestamp": datetime(2025, 4, 1),
                "nav_value": 100.00,
                "outstanding_units": 4000,
                "fund_value": 400000.00,
                "profit": 0.00,
                "charges": 0.00,
                "funds_in_out": 400000.00,
                "units_change": 4000,
                "previous_nav": 100.00,
                "previous_fund_value": 0.00
            },
            {
                "timestamp": datetime(2025, 4, 5),
                "nav_value": 102.74,
                "outstanding_units": 4000,
                "fund_value": 410965.37,
                "profit": 11400.00,
                "charges": 434.63,
                "funds_in_out": 0.00,
                "units_change": 0,
                "previous_nav": 100.00,
                "previous_fund_value": 400000.00
            },
            {
                "timestamp": datetime(2025, 4, 12),
                "nav_value": 107.88,
                "outstanding_units": 4000,
                "fund_value": 431514.40,
                "profit": 20745.00,
                "charges": 195.97,
                "funds_in_out": 0.00,
                "units_change": 0,
                "previous_nav": 102.74,
                "previous_fund_value": 410965.37
            },
            {
                "timestamp": datetime(2025, 4, 19),
                "nav_value": 103.52,
                "outstanding_units": 4000,
                "fund_value": 414073.98,
                "profit": -17261.25,
                "charges": 179.17,
                "funds_in_out": 0.00,
                "units_change": 0,
                "previous_nav": 107.88,
                "previous_fund_value": 431514.40
            },
            {
                "timestamp": datetime(2025, 4, 26),
                "nav_value": 101.77,
                "outstanding_units": 4000,
                "fund_value": 407060.38,
                "profit": -6397.50,
                "charges": 616.10,
                "funds_in_out": 0.00,
                "units_change": 0,
                "previous_nav": 103.52,
                "previous_fund_value": 414073.98
            },
            {
                "timestamp": datetime(2025, 5, 3),
                "nav_value": 102.70,
                "outstanding_units": 4000,
                "fund_value": 410813.88,
                "profit": 4110.00,
                "charges": 356.50,
                "funds_in_out": 300000.00,
                "units_change": 2921.030808,
                "previous_nav": 101.77,
                "previous_fund_value": 407060.38
            },
            {
                "timestamp": datetime(2025, 5, 10),
                "nav_value": 104.46,
                "outstanding_units": 6921.030808,
                "fund_value": 722963.88,
                "profit": 12892.50,
                "charges": 742.50,
                "funds_in_out": 0.00,
                "units_change": 0,
                "previous_nav": 102.70,
                "previous_fund_value": 710813.88
            },
            {
                "timestamp": datetime(2025, 5, 17),
                "nav_value": 96.73,
                "outstanding_units": 6921.030808,
                "fund_value": 669471.16,
                "profit": -52215.00,
                "charges": 1277.72,
                "funds_in_out": 0.00,
                "units_change": 0,
                "previous_nav": 104.46,
                "previous_fund_value": 722963.88
            },
            {
                "timestamp": datetime(2025, 5, 24),
                "nav_value": 97.09,
                "outstanding_units": 6921.030808,
                "fund_value": 671954.57,
                "profit": 2767.50,
                "charges": 284.09,
                "funds_in_out": 0.00,
                "units_change": 0,
                "previous_nav": 96.73,
                "previous_fund_value": 669471.16
            },
            {
                "timestamp": datetime(2025, 5, 31),
                "nav_value": 99.27,
                "outstanding_units": 6921.030808,
                "fund_value": 687056.44,
                "profit": 15337.50,
                "charges": 235.63,
                "funds_in_out": 0.00,
                "units_change": 0,
                "previous_nav": 97.09,
                "previous_fund_value": 671954.57
            },
            {
                "timestamp": datetime(2025, 6, 7),
                "nav_value": 101.73,
                "outstanding_units": 6921.030808,
                "fund_value": 704057.19,
                "profit": 17268.75,
                "charges": 268.00,
                "funds_in_out": 100000.00,
                "units_change": 982.797208,
                "previous_nav": 99.27,
                "previous_fund_value": 687056.44
            }
        ]

        # Clear existing data
        await nav_collection.delete_many({})
        
        # Insert new data
        result = await nav_collection.insert_many(historical_data)
        logging.info(f"Inserted {len(result.inserted_ids)} historical NAV records")
        
        return {"message": f"Successfully inserted {len(result.inserted_ids)} historical NAV records"}
    except Exception as e:
        logging.error(f"Error inserting historical NAV data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to insert historical NAV data: {str(e)}")

@router.post("/insert-historical-nav")
async def insert_historical_nav():
    """Endpoint to insert historical NAV data"""
    return await insert_historical_nav_data()