from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
from bson import ObjectId
from pydantic import BaseModel, Field, validator

class ValidatorException(Exception):
    pass

class TradeValidator(BaseModel):
    trade_id: str
    order_id: str
    exchange: str
    tradingsymbol: str
    trade_type: str
    quantity: int
    price: Decimal
    trade_date: datetime

    @validator('exchange')
    def validate_exchange(cls, v):
        valid_exchanges = ['NSE', 'BSE', 'NFO']
        if v not in valid_exchanges:
            raise ValueError(f'Exchange must be one of {valid_exchanges}')
        return v

    @validator('trade_type')
    def validate_trade_type(cls, v):
        valid_types = ['BUY', 'SELL']
        if v not in valid_types:
            raise ValueError(f'Trade type must be one of {valid_types}')
        return v

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class InvestorValidator(BaseModel):
    id: int
    name: str
    initial_capital: Decimal
    current_capital: Decimal
    join_date: date
    profit_share: float
    is_active: bool

    @validator('profit_share')
    def validate_profit_share(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Profit share must be between 0 and 100')
        return v

class NAVValidator(BaseModel):
    date: date
    nav_value: Decimal
    investor_id: int
    
    @validator('nav_value')
    def validate_nav(cls, v):
        if v <= 0:
            raise ValueError('NAV value must be positive')
        return v

class HoldingValidator(BaseModel):
    tradingsymbol: str
    exchange: str
    isin: Optional[str]
    quantity: int
    average_price: Decimal
    last_price: Decimal
    pnl: Decimal

    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v

    @validator('average_price', 'last_price')
    def validate_prices(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

def validate_trade_data(trade_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate trade data against the TradeValidator"""
    try:
        validated = TradeValidator(**trade_data)
        return validated.dict()
    except Exception as e:
        raise ValidatorException(f"Trade validation failed: {str(e)}")

def validate_nav_data(nav_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate NAV data against the NAVValidator"""
    try:
        validated = NAVValidator(**nav_data)
        return validated.dict()
    except Exception as e:
        raise ValidatorException(f"NAV validation failed: {str(e)}")

def validate_holding_data(holding_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate holding data against the HoldingValidator"""
    try:
        validated = HoldingValidator(**holding_data)
        return validated.dict()
    except Exception as e:
        raise ValidatorException(f"Holding validation failed: {str(e)}")
