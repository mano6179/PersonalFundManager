from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

class WeeklyProfitLog(BaseModel):
    profit: float
    charges: float
    funds_in_out: float = 0
    previous_nav: float

class IVTrackerLog(BaseModel):
    symbol: str
    strike: float
    expiry: str
    iv: float

class TradeLog(BaseModel):
    symbol: str
    strategy: str
    entry_exit: str
    quantity: int
    premium: float
    date: str
    notes: Optional[str] = None

class MarketUpdateLog(BaseModel):
    title: str
    content: str

class LogEntry(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    type: str  # weekly_profit, iv_tracker, trade, market_update
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Weekly Profit fields
    profit: Optional[float] = None
    charges: Optional[float] = None
    funds_in_out: Optional[float] = None
    previous_nav: Optional[float] = None
    
    # IV Tracker fields
    symbol: Optional[str] = None
    strike: Optional[float] = None
    expiry: Optional[str] = None
    iv: Optional[float] = None
    
    # Trade fields
    strategy: Optional[str] = None
    entry_exit: Optional[str] = None
    quantity: Optional[int] = None
    premium: Optional[float] = None
    date: Optional[str] = None
    notes: Optional[str] = None
    
    # Market Update fields
    title: Optional[str] = None
    content: Optional[str] = None

    class Config:
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "type": "weekly_profit",
                "timestamp": "2024-03-14T12:00:00Z",
                "profit": 1000.0,
                "charges": 50.0,
                "funds_in_out": 0.0,
                "previous_nav": 10000.0
            }
        } 