from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class FundEntry(BaseModel):
    date: date
    realised_pnl: float  # Realised profit/loss for the week
    charges: float       # Charges & taxes
    funds_in_out: float  # New funds added or withdrawn
    previous_nav: Optional[float] = None
    outstanding_units: Optional[float] = None
    fund_value: Optional[float] = None
    nav: Optional[float] = None
    nav_peak: Optional[float] = None
    nav_drawdown: Optional[float] = None

class NAVRecord(BaseModel):
    id: int
    date: datetime
    investor_id: int
    total_value: float
    cash_balance: float
    equity_value: float
    other_assets: float
    nav_value: float

class FundEntryRequest(BaseModel):
    entries: List[FundEntry]

class FundEntryResponse(BaseModel):
    entries: List[FundEntry]