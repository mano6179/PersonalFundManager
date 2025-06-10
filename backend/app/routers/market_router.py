from fastapi import APIRouter, WebSocket, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging
from app.services.websocket_service import KiteTickerService
from app.services.zerodha_service_modified import ZerodhaService
from app.config.zerodha_config import ZERODHA_CONFIG
from ..services.market_update_service import MarketUpdateService
from ..models.market_update import MarketUpdate
from ..services.auth_service import AuthService
from fastapi.security import OAuth2PasswordBearer

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
market_service = MarketUpdateService()
auth_service = AuthService()

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

@router.post("/market-updates", response_model=MarketUpdate)
async def create_market_update(
    update: MarketUpdate,
    token: str = Depends(oauth2_scheme)
):
    """Create a new market update"""
    # Verify user is authenticated
    await auth_service.get_current_user(token)
    return await market_service.create_update(update)

@router.get("/market-updates", response_model=List[MarketUpdate])
async def get_market_updates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    token: str = Depends(oauth2_scheme)
):
    """Get market updates with optional filtering"""
    # Verify user is authenticated
    await auth_service.get_current_user(token)
    return await market_service.get_updates(skip, limit, category, is_public)

@router.get("/market-updates/public", response_model=List[MarketUpdate])
async def get_public_updates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None
):
    """Get public market updates"""
    return await market_service.get_public_updates(skip, limit, category)

@router.get("/market-updates/{update_id}", response_model=MarketUpdate)
async def get_market_update(
    update_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get a specific market update"""
    # Verify user is authenticated
    await auth_service.get_current_user(token)
    return await market_service.get_update(update_id)

@router.put("/market-updates/{update_id}", response_model=MarketUpdate)
async def update_market_update(
    update_id: str,
    update: MarketUpdate,
    token: str = Depends(oauth2_scheme)
):
    """Update a market update"""
    # Verify user is authenticated
    await auth_service.get_current_user(token)
    return await market_service.update_update(update_id, update)

@router.delete("/market-updates/{update_id}")
async def delete_market_update(
    update_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Delete a market update"""
    # Verify user is authenticated
    await auth_service.get_current_user(token)
    return await market_service.delete_update(update_id)

@router.get("/market-updates/search", response_model=List[MarketUpdate])
async def search_market_updates(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    token: str = Depends(oauth2_scheme)
):
    """Search market updates"""
    # Verify user is authenticated
    await auth_service.get_current_user(token)
    return await market_service.search_updates(query, skip, limit)
