from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field
from bson import ObjectId

class UserPreferences(BaseModel):
    theme: str = "light"
    notifications: bool = True
    default_view: str = "dashboard"

class User(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    email: str
    password: str  # Will be hashed
    name: str
    role: str = "user"  # user, admin
    last_login: Optional[datetime] = None
    is_active: bool = True
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "role": "user",
                "preferences": {
                    "theme": "dark",
                    "notifications": True,
                    "default_view": "dashboard"
                }
            }
        }

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None