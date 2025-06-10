from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class MarketUpdate(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    title: str
    content: str
    category: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    author: str
    is_public: bool = False
    tags: List[str] = []

    class Config:
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "title": "Market Update",
                "content": "Market is showing strong momentum",
                "category": "Technical",
                "author": "John Doe",
                "is_public": True,
                "tags": ["NIFTY", "Technical Analysis"]
            }
        } 