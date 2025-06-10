import logging
import hashlib
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

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

# Try to import the config, but don't fail if it doesn't exist
try:
    from backend.app.config.zerodha_config import ZERODHA_CONFIG
    DEFAULT_API_KEY = ZERODHA_CONFIG.get("api_key", "")
    DEFAULT_API_SECRET = ZERODHA_CONFIG.get("api_secret", "")
except ImportError:
    DEFAULT_API_KEY = os.getenv("ZERODHA_API_KEY", "")
    DEFAULT_API_SECRET = os.getenv("ZERODHA_API_SECRET", "")

logger = logging.getLogger(__name__)


class ZerodhaService:
    """Service for interacting with Zerodha Kite API"""

    def __init__(self, api_key: str = DEFAULT_API_KEY, api_secret: str = DEFAULT_API_SECRET):
        """Initialize the Zerodha service with API credentials"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = None
        self.user_id = None
        self.login_time = None
        self.expiry_time = None
        self.root_url = "https://api.kite.trade"
        self.login_url = "https://kite.zerodha.com/connect/login"

    def get_login_url(self) -> str:
        """Get the Zerodha login URL for authentication"""
        try:
            redirect_url = ZERODHA_CONFIG.get("redirect_url", "http://localhost:8000/kite/callback")
            return f"{self.login_url}?api_key={self.api_key}&v=3&redirect_url={redirect_url}"
        except Exception as e:
            logger.error(f"Error generating login URL: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate login URL"
            )

    def generate_session(self, request_token: str) -> ZerodhaAuthResponse:
        """Generate a session with the request token"""
        if not request_token:
            logger.error("No request token provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request token is required"
            )

        try:
            # Create checksum
            data = f"{self.api_key}{request_token}{self.api_secret}"
            h = hashlib.sha256(data.encode('utf-8'))
            checksum = h.hexdigest()

            # Make the request
            url = f"{self.root_url}/session/token"
            headers = {
                "X-Kite-Version": "3",
                "User-Agent": "Steady-Gains-2025/1.0"
            }
            payload = {
                "api_key": self.api_key,
                "request_token": request_token,
                "checksum": checksum
            }
            
            logger.info(f"Attempting to generate session for request_token: {request_token[:5]}...")

            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes

            data = response.json()
            if not data.get("status") == "success":
                logger.error(f"Zerodha API error: {data.get('message', 'Unknown error')}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=data.get("message", "Failed to authenticate with Zerodha")
                )

            session_data = data.get("data", {})
            if not session_data:
                logger.error("No session data received from Zerodha")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No session data received from Zerodha"
                )

            # Set the access token for future API calls
            self.access_token = session_data.get("access_token")
            if not self.access_token:
                logger.error("No access token in response")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No access token received"
                )

            # Store user details
            self.user_id = session_data.get("user_id")
            self.login_time = datetime.now()
            self.expiry_time = datetime.now() + timedelta(days=1)

            logger.info(f"Successfully generated session for user: {self.user_id}")

            # Return the authentication response
            return ZerodhaAuthResponse(
                access_token=session_data.get("access_token", ""),
                refresh_token=session_data.get("refresh_token"),
                login_time=self.login_time,
                user_id=session_data.get("user_id", ""),
                user_name=session_data.get("user_name"),
                user_shortname=session_data.get("user_shortname"),
                email=session_data.get("email"),
                user_type=session_data.get("user_type"),
                broker=session_data.get("broker"),
                exchanges=session_data.get("exchanges", []),
                products=session_data.get("products", []),
                order_types=session_data.get("order_types", []),
                avatar_url=session_data.get("avatar_url"),
                meta=session_data.get("meta", {})
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

    def invalidate_access_token(self) -> bool:
        """Invalidate the current access token"""
        try:
            url = f"{self.root_url}/session/token"
            headers = {
                "X-Kite-Version": "3",
                "Authorization": f"token {self.api_key}:{self.access_token}"
            }

            response = requests.delete(url, headers=headers)

            if response.status_code == 200:
                self.access_token = None
                return True
            else:
                logger.error(f"Error invalidating access token: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error invalidating access token: {str(e)}")
            return False

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request to the Zerodha API"""
        if not self.access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token is required for API calls"
            )

        url = f"{self.root_url}/{endpoint}"
        headers = {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}"
        }

        try:
            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                logger.error(f"API request failed: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"API request failed: {response.text}"
                )
        except Exception as e:
            logger.error(f"Error making API request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error making API request: {str(e)}"
            )

    def get_profile(self) -> ZerodhaProfile:
        """Get the user profile from Zerodha"""
        try:
            profile = self._get("user/profile")
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
            holdings = self._get("portfolio/holdings")
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
            positions = self._get("portfolio/positions")

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
            orders = self._get("orders")
            return [ZerodhaOrder(**order) for order in orders]
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch orders: {str(e)}"
            )

    def get_trades(self, since_date: Optional[datetime] = None) -> List[ZerodhaTrade]:
        """Get the user's trades from Zerodha"""
        try:
            trades = self._get("trades")
            trade_objects = [ZerodhaTrade(**trade) for trade in trades]

            # Filter trades by date if since_date is provided
            if since_date:
                trade_objects = [
                    trade for trade in trade_objects
                    if trade.fill_timestamp and trade.fill_timestamp > since_date
                ]

            return trade_objects
        except Exception as e:
            logger.error(f"Error fetching trades: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch trades: {str(e)}"
            )

    def store_trades(self, trades: List[ZerodhaTrade], file_path: str = "zerodha_trades.json") -> bool:
        """Store trades to a JSON file"""
        try:
            # Read existing trades if file exists
            existing_trades = []
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    try:
                        existing_trades = json.load(f)
                    except json.JSONDecodeError:
                        existing_trades = []

            # Convert trade objects to dictionaries
            trade_dicts = []
            for trade in trades:
                trade_dict = trade.dict()
                # Convert datetime objects to strings
                if trade_dict.get("fill_timestamp"):
                    trade_dict["fill_timestamp"] = trade_dict["fill_timestamp"].isoformat()
                if trade_dict.get("exchange_timestamp"):
                    trade_dict["exchange_timestamp"] = trade_dict["exchange_timestamp"].isoformat()
                trade_dicts.append(trade_dict)

            # Combine existing and new trades
            all_trades = existing_trades + trade_dicts

            # Remove duplicates based on trade_id
            unique_trades = {}
            for trade in all_trades:
                unique_trades[trade.get("trade_id")] = trade

            # Write to file
            with open(file_path, "w") as f:
                json.dump(list(unique_trades.values()), f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error storing trades: {str(e)}")
            return False

    def get_last_trade_date(self, file_path: str = "zerodha_trades.json") -> Optional[datetime]:
        """Get the date of the most recent trade from the stored trades"""
        try:
            if not os.path.exists(file_path):
                return None

            with open(file_path, "r") as f:
                try:
                    trades = json.load(f)
                except json.JSONDecodeError:
                    return None

            if not trades:
                return None

            # Find the most recent trade
            latest_date = None
            for trade in trades:
                if trade.get("fill_timestamp"):
                    trade_date = datetime.fromisoformat(trade["fill_timestamp"])
                    if not latest_date or trade_date > latest_date:
                        latest_date = trade_date

            return latest_date
        except Exception as e:
            logger.error(f"Error getting last trade date: {str(e)}")
            return None

    def get_margins(self) -> ZerodhaMargin:
        """Get the user's margin details from Zerodha"""
        try:
            margins = self._get("user/margins")
            return ZerodhaMargin(**margins)
        except Exception as e:
            logger.error(f"Error fetching margins: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch margins: {str(e)}"
            )
