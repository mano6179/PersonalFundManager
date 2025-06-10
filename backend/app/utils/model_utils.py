from datetime import datetime, date
from bson import ObjectId
from typing import Any

def convert_datetime_to_str(dt: datetime) -> str:
    return dt.isoformat()

def convert_date_to_str(d: date) -> str:
    return d.isoformat()

def serialize_model(model: Any) -> dict:
    """Convert Pydantic models to MongoDB-compatible dictionaries"""
    data = model.dict()
    
    # Convert datetime objects to ISO format strings
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = convert_datetime_to_str(value)
        elif isinstance(value, date):
            data[key] = convert_date_to_str(value)
        elif isinstance(value, ObjectId):
            data[key] = str(value)
    
    return data

def deserialize_model(data: dict) -> dict:
    """Convert MongoDB documents to Pydantic-compatible dictionaries"""
    if data is None:
        return None
    
    # Convert MongoDB ObjectId to string
    if "_id" in data:
        data["_id"] = str(data["_id"])
    
    # Convert ISO format strings back to datetime/date objects
    for key, value in data.items():
        if isinstance(value, str):
            try:
                # Try parsing as datetime first
                data[key] = datetime.fromisoformat(value)
            except ValueError:
                try:
                    # Then try parsing as date
                    data[key] = date.fromisoformat(value)
                except ValueError:
                    pass
    
    return data
