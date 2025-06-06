from typing import Dict, List, Optional, Any
import logging
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.services.zerodha_service_modified import ZerodhaService

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self, zerodha_service: ZerodhaService):
        self.zerodha = zerodha_service
        
    async def get_quote(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get market quotes for given symbols
        Example: ["NSE:INFY", "BSE:SBIN"]
        """
        try:
            # First get instrument tokens
            instruments = await self._get_instrument_tokens(symbols)
            
            # Get quotes using instrument tokens
            quotes = self.zerodha._get(
                "quote", 
                params={"i": ",".join(instruments)}
            )
            
            return self._format_quotes(quotes)
            
        except Exception as e:
            logger.error(f"Error fetching quotes: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch quotes: {str(e)}"
            )
    
    async def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Get historical data for a symbol
        interval can be: minute, day, 3minute, 5minute, 10minute, 15minute, 30minute, 60minute
        """
        try:
            instrument_token = (await self._get_instrument_tokens([symbol]))[0]
            
            data = self.zerodha._get(
                f"instruments/historical/{instrument_token}/{interval}",
                params={
                    "from": from_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "to": to_date.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            
            return self._format_historical_data(data)
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch historical data: {str(e)}"
            )
    
    async def _get_instrument_tokens(self, symbols: List[str]) -> List[str]:
        """Convert trading symbols to instrument tokens"""
        # This needs to be implemented using Zerodha's instrument dump
        # For now, return dummy data
        return ["408065", "779521"]  # Example instrument tokens
        
    def _format_quotes(self, quotes: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw quote data into a more usable structure"""
        formatted = {}
        for token, quote in quotes.items():
            formatted[token] = {
                "last_price": quote.get("last_price"),
                "ohlc": quote.get("ohlc"),
                "volume": quote.get("volume"),
                "buy_quantity": quote.get("buy_quantity"),
                "sell_quantity": quote.get("sell_quantity"),
                "average_price": quote.get("average_price"),
                "depth": quote.get("depth", {})
            }
        return formatted
        
    def _format_historical_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format historical data into OHLCV format"""
        return [{
            "timestamp": candle[0],
            "open": candle[1],
            "high": candle[2],
            "low": candle[3],
            "close": candle[4],
            "volume": candle[5]
        } for candle in data]
