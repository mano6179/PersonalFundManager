from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import json

from app.services.zerodha_service_modified import ZerodhaService
from app.models.zerodha import (
    ZerodhaCredentials,
    ZerodhaHolding,
    ZerodhaPosition,
    ZerodhaTrade,
    ZerodhaOrder,
    ZerodhaMargin,
    ZerodhaProfile,
    ZerodhaAuthResponse
)

router = APIRouter(
    prefix="/api/zerodha",
    tags=["zerodha"],
    responses={404: {"description": "Not found"}},
)

# Create a dependency for the Zerodha service
def get_zerodha_service():
    return ZerodhaService()


@router.get("/login", response_class=RedirectResponse)
async def login_to_zerodha(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Redirect to Zerodha login page"""
    login_url = zerodha_service.get_login_url()
    return RedirectResponse(url=login_url)


@router.get("/callback", response_model=ZerodhaAuthResponse)
async def zerodha_callback(
    request_token: str = Query(..., description="Request token from Zerodha"),
    zerodha_service: ZerodhaService = Depends(get_zerodha_service)
):
    """Handle callback from Zerodha after login"""
    return zerodha_service.generate_session(request_token)


@router.post("/set-token", response_model=Dict[str, bool])
async def set_access_token(
    credentials: ZerodhaCredentials,
    zerodha_service: ZerodhaService = Depends(get_zerodha_service)
):
    """Set access token for Zerodha API"""
    if not credentials.access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access token is required"
        )

    zerodha_service.set_access_token(credentials.access_token)
    return {"success": True}


@router.post("/logout", response_model=Dict[str, bool])
async def logout_from_zerodha(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Invalidate Zerodha access token"""
    success = zerodha_service.invalidate_access_token()
    return {"success": success}


@router.get("/profile", response_model=ZerodhaProfile)
async def get_profile(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Get user profile from Zerodha"""
    return zerodha_service.get_profile()


@router.get("/holdings", response_model=List[ZerodhaHolding])
async def get_holdings(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Get user holdings from Zerodha"""
    return zerodha_service.get_holdings()


@router.get("/positions", response_model=Dict[str, List[ZerodhaPosition]])
async def get_positions(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Get user positions from Zerodha"""
    return zerodha_service.get_positions()


@router.get("/orders", response_model=List[ZerodhaOrder])
async def get_orders(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Get user orders from Zerodha"""
    return zerodha_service.get_orders()


@router.get("/trades", response_model=List[ZerodhaTrade])
async def get_trades(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Get user trades from Zerodha"""
    return zerodha_service.get_trades()

@router.post("/load-trades", response_model=Dict[str, Any])
async def load_trades(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Load trades from Zerodha and store them"""
    try:
        # Get the date of the most recent stored trade
        last_trade_date = zerodha_service.get_last_trade_date()

        # Get trades since the last stored trade
        trades = zerodha_service.get_trades(since_date=last_trade_date)

        # Store the trades
        success = zerodha_service.store_trades(trades)

        return {
            "success": success,
            "message": f"Successfully loaded {len(trades)} new trades" if success else "Failed to load trades",
            "trades_count": len(trades)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load trades: {str(e)}"
        )

@router.get("/stored-trades", response_model=Dict[str, Any])
async def get_stored_trades():
    """Get trades from the local storage"""
    try:
        file_path = "zerodha_trades.json"
        if not os.path.exists(file_path):
            return {
                "success": True,
                "message": "No stored trades found",
                "trades": []
            }

        with open(file_path, "r") as f:
            try:
                trades = json.load(f)
            except json.JSONDecodeError:
                trades = []

        return {
            "success": True,
            "message": f"Found {len(trades)} stored trades",
            "trades": trades
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stored trades: {str(e)}"
        )


@router.get("/margins", response_model=ZerodhaMargin)
async def get_margins(zerodha_service: ZerodhaService = Depends(get_zerodha_service)):
    """Get user margin details from Zerodha"""
    return zerodha_service.get_margins()


@router.get("/instruments")
async def get_instruments(
    exchange: Optional[str] = None,
    zerodha_service: ZerodhaService = Depends(get_zerodha_service)
):
    """Get instruments from Zerodha"""
    return zerodha_service.get_instruments(exchange)


@router.get("/historical-data")
async def get_historical_data(
    instrument_token: int,
    from_date: str,
    to_date: str,
    interval: str = "day",
    zerodha_service: ZerodhaService = Depends(get_zerodha_service)
):
    """Get historical data for an instrument"""
    try:
        # Convert string dates to datetime objects
        from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
        to_datetime = datetime.strptime(to_date, "%Y-%m-%d")

        return zerodha_service.get_historical_data(
            instrument_token=instrument_token,
            from_date=from_datetime,
            to_date=to_datetime,
            interval=interval
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD format."
        )
