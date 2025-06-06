from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from typing import List, Dict, Any
import json
import asyncio
import logging
from app.services.websocket_service import KiteTickerService
from app.services.zerodha_service_modified import ZerodhaService
from app.config.zerodha_config import ZERODHA_CONFIG

# Create logger
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/api/market",
    tags=["market"],
    responses={404: {"description": "Not found"}},
)

# Store WebSocket connections
active_connections: Dict[str, WebSocket] = {}
ticker_service: KiteTickerService = None

def get_ticker_service(zerodha_service: ZerodhaService = Depends(ZerodhaService)) -> KiteTickerService:
    """Get or create ticker service"""
    global ticker_service
    if not ticker_service or not ticker_service.connected:
        if not zerodha_service.access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated with Zerodha"
            )
        ticker_service = KiteTickerService(
            api_key=ZERODHA_CONFIG["api_key"],
            access_token=zerodha_service.access_token
        )
    return ticker_service

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time market data"""
    await websocket.accept()
    active_connections[client_id] = websocket

    try:
        # Start Zerodha WebSocket connection if not already connected
        ticker_service = get_ticker_service()
        if not ticker_service.connected:
            await ticker_service.connect()
            
        # Register callback for market data
        async def send_to_client(data: Dict[str, Any]):
            if client_id in active_connections:
                await active_connections[client_id].send_json(data)
        
        ticker_service.callbacks['ticks'].append(send_to_client)
        
        # Keep connection alive and handle client messages
        while True:
            try:
                data = await websocket.receive_json()
                if data.get('type') == 'subscribe':
                    # Handle subscription requests
                    tokens = data.get('tokens', [])
                    await ticker_service.subscribe(tokens)
            except Exception as e:
                logger.error(f"Error handling client message: {str(e)}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        # Cleanup
        if client_id in active_connections:
            del active_connections[client_id]
        if ticker_service and ticker_service.callbacks.get('ticks'):
            ticker_service.callbacks['ticks'].remove(send_to_client)

@router.post("/subscribe")
async def subscribe_instruments(
    instrument_tokens: List[int],
    ticker: KiteTickerService = Depends(get_ticker_service)
):
    """Subscribe to market data for given instruments"""
    try:
        await ticker.subscribe(instrument_tokens)
        return {"message": "Subscribed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/unsubscribe")
async def unsubscribe_instruments(
    instrument_tokens: List[int],
    ticker: KiteTickerService = Depends(get_ticker_service)
):
    """Unsubscribe from market data for given instruments"""
    try:
        await ticker.unsubscribe(instrument_tokens)
        return {"message": "Unsubscribed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
