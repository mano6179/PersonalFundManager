from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class TradeLog(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    trade_id: str
    symbol: str
    entry_date: datetime
    exit_date: Optional[datetime] = None
    entry_price: float
    exit_price: Optional[float] = None
    quantity: int
    pnl: Optional[float] = None
    strategy: str
    notes: Optional[str] = None
    status: str = "OPEN"  # OPEN, CLOSED, CANCELLED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "trade_id": "TRADE001",
                "symbol": "RELIANCE",
                "entry_date": "2024-03-20T10:00:00",
                "entry_price": 2500.50,
                "quantity": 100,
                "strategy": "Swing Trade",
                "notes": "Strong support at 2500"
            }
        } 