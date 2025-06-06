from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class ZerodhaCredentials(BaseModel):
    """Model for storing Zerodha API credentials"""
    api_key: str
    api_secret: str
    request_token: Optional[str] = None
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    login_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None


class ZerodhaHolding(BaseModel):
    """Model for Zerodha holdings data"""
    tradingsymbol: str
    exchange: str
    isin: str
    quantity: int
    t1_quantity: int
    average_price: float
    last_price: float
    pnl: float
    close_price: float
    product: str
    collateral_quantity: int
    collateral_type: Optional[str] = None
    day_change: float = 0.0
    day_change_percentage: float = 0.0


class ZerodhaPosition(BaseModel):
    """Model for Zerodha positions data"""
    tradingsymbol: str
    exchange: str
    product: str
    quantity: int
    overnight_quantity: int
    multiplier: float
    average_price: float
    close_price: float
    last_price: float
    value: float
    pnl: float
    m2m: float
    unrealized: float
    realized: float
    buy_quantity: int
    buy_price: float
    buy_value: float
    sell_quantity: int
    sell_price: float
    sell_value: float
    day_buy_quantity: int
    day_buy_price: float
    day_buy_value: float
    day_sell_quantity: int
    day_sell_price: float
    day_sell_value: float


class ZerodhaTrade(BaseModel):
    """Model for Zerodha trades data"""
    trade_id: str
    order_id: str
    exchange: str
    tradingsymbol: str
    product: str
    average_price: float
    quantity: int
    fill_timestamp: datetime
    exchange_timestamp: datetime
    transaction_type: str


class ZerodhaOrder(BaseModel):
    """Model for Zerodha orders data"""
    order_id: str
    exchange_order_id: Optional[str] = None
    parent_order_id: Optional[str] = None
    status: str
    exchange: str
    tradingsymbol: str
    transaction_type: str
    order_type: str
    variety: str
    product: str
    quantity: int
    disclosed_quantity: int
    price: float
    trigger_price: float
    average_price: float
    filled_quantity: int
    pending_quantity: int
    cancelled_quantity: int
    validity: str
    status_message: Optional[str] = None
    order_timestamp: Optional[datetime] = None
    exchange_timestamp: Optional[datetime] = None
    tag: Optional[str] = None


class ZerodhaMargin(BaseModel):
    """Model for Zerodha margin data"""
    enabled: bool
    net: float
    available: Dict[str, float]
    used: Dict[str, float]
    utilised: Dict[str, float]


class ZerodhaProfile(BaseModel):
    """Model for Zerodha user profile data"""
    user_id: str
    user_name: str
    user_shortname: str
    email: str
    user_type: str
    broker: str
    exchanges: List[str]
    products: List[str]
    order_types: List[str]
    avatar_url: Optional[str] = None
    meta: Dict[str, Any] = {}


class ZerodhaAuthResponse(BaseModel):
    """Model for Zerodha authentication response"""
    access_token: str
    refresh_token: Optional[str] = None
    login_time: Optional[datetime] = None
    user_id: str
    user_name: Optional[str] = None
    user_shortname: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[str] = None
    broker: Optional[str] = None
    exchanges: List[str] = []
    products: List[str] = []
    order_types: List[str] = []
    avatar_url: Optional[str] = None
    meta: Dict[str, Any] = {}
