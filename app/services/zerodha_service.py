import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from kiteconnect import KiteConnect
from fastapi import HTTPException, status

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
from app.config.zerodha_config import ZERODHA_CONFIG

logger = logging.getLogger(__name__)

# Default API key and secret from configuration
DEFAULT_API_KEY = ZERODHA_CONFIG["api_key"]
DEFAULT_API_SECRET = ZERODHA_CONFIG["api_secret"]


class ZerodhaService:
    """Service for interacting with Zerodha Kite API"""

    def __init__(self, api_key: str = DEFAULT_API_KEY, api_secret: str = DEFAULT_API_SECRET):
        """Initialize the Zerodha service with API credentials"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)
        self.access_token = None
        self.user_id = None
        self.login_time = None
        self.expiry_time = None

    def get_login_url(self) -> str:
        """Get the Zerodha login URL for authentication"""
        return self.kite.login_url()

    def generate_session(self, request_token: str) -> ZerodhaAuthResponse:
        """Generate a session with the request token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)

            # Set the access token for future API calls
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)

            # Store user details
            self.user_id = data.get("user_id")
            self.login_time = data.get("login_time")

            # Set expiry time (typically 1 day from login)
            self.expiry_time = datetime.now() + timedelta(days=1)

            # Return the authentication response
            return ZerodhaAuthResponse(
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token"),
                login_time=data.get("login_time"),
                user_id=data.get("user_id", ""),
                user_name=data.get("user_name"),
                user_shortname=data.get("user_shortname"),
                email=data.get("email"),
                user_type=data.get("user_type"),
                broker=data.get("broker"),
                exchanges=data.get("exchanges", []),
                products=data.get("products", []),
                order_types=data.get("order_types", []),
                avatar_url=data.get("avatar_url"),
                meta=data.get("meta", {})
            )
        except Exception as e:
            logger.error(f"Error generating Zerodha session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to authenticate with Zerodha: {str(e)}"
            )

    def set_access_token(self, access_token: str) -> None:
        """Set the access token for API calls"""
        self.access_token = access_token
        self.kite.set_access_token(access_token)

    def invalidate_access_token(self) -> bool:
        """Invalidate the current access token"""
        try:
            self.kite.invalidate_access_token()
            self.access_token = None
            return True
        except Exception as e:
            logger.error(f"Error invalidating access token: {str(e)}")
            return False

    def get_profile(self) -> ZerodhaProfile:
        """Get the user profile from Zerodha"""
        try:
            profile = self.kite.profile()
            return ZerodhaProfile(**profile)
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch profile: {str(e)}"
            )

    def get_holdings(self) -> List[ZerodhaHolding]:
        """Get the user's holdings from Zerodha"""
        try:
            holdings = self.kite.holdings()
            return [ZerodhaHolding(**holding) for holding in holdings]
        except Exception as e:
            logger.error(f"Error fetching holdings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch holdings: {str(e)}"
            )

    def get_positions(self) -> Dict[str, List[ZerodhaPosition]]:
        """Get the user's positions from Zerodha"""
        try:
            positions = self.kite.positions()

            # Convert positions to our model format
            day_positions = [ZerodhaPosition(**pos) for pos in positions.get("day", [])]
            net_positions = [ZerodhaPosition(**pos) for pos in positions.get("net", [])]

            return {
                "day": day_positions,
                "net": net_positions
            }
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch positions: {str(e)}"
            )

    def get_orders(self) -> List[ZerodhaOrder]:
        """Get the user's orders from Zerodha"""
        try:
            orders = self.kite.orders()
            return [ZerodhaOrder(**order) for order in orders]
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch orders: {str(e)}"
            )

    def get_trades(self) -> List[ZerodhaTrade]:
        """Get the user's trades from Zerodha"""
        try:
            trades = self.kite.trades()
            return [ZerodhaTrade(**trade) for trade in trades]
        except Exception as e:
            logger.error(f"Error fetching trades: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch trades: {str(e)}"
            )

    def get_margins(self) -> ZerodhaMargin:
        """Get the user's margin details from Zerodha"""
        try:
            margins = self.kite.margins()
            return ZerodhaMargin(**margins)
        except Exception as e:
            logger.error(f"Error fetching margins: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch margins: {str(e)}"
            )

    def get_instruments(self, exchange: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get instruments from Zerodha"""
        try:
            if exchange:
                return self.kite.instruments(exchange=exchange)
            else:
                return self.kite.instruments()
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch instruments: {str(e)}"
            )

    def get_historical_data(
        self,
        instrument_token: int,
        from_date: datetime,
        to_date: datetime,
        interval: str
    ) -> List[Dict[str, Any]]:
        """Get historical data for an instrument"""
        try:
            return self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch historical data: {str(e)}"
            )
