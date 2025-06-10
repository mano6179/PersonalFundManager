import json
import logging
import asyncio
import websockets
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._closed = False

    async def connect(self, websocket: WebSocket):
        if self._closed:
            return
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")

    async def close_all(self):
        self._closed = True
        for connection in self.active_connections[:]:
            try:
                await connection.close()
                await self.disconnect(connection)
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {str(e)}")

    async def broadcast_json(self, message: dict):
        if self._closed:
            return
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                await self.disconnect(connection)

manager = ConnectionManager()

class KiteTickerService:
    """Service for handling real-time market data through Zerodha's WebSocket"""
    
    def __init__(self, api_key: str, access_token: str):
        self.api_key = api_key
        self.access_token = access_token
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.callbacks: Dict[str, List[Callable]] = {
            'ticks': [],
            'order_update': [],
            'message': []
        }
        self.subscribed_tokens: List[int] = []
        self.ws_url = "wss://ws.kite.trade"

    async def connect(self):
        """Establish WebSocket connection"""
        try:
            # Create connection with authentication
            auth_header = f"{self.api_key}:{self.access_token}"
            self.ws = await websockets.connect(
                self.ws_url,
                extra_headers={"X-Kite-Version": "3", "Authorization": auth_header}
            )
            self.connected = True
            logger.info("WebSocket connection established")
            asyncio.create_task(self._message_handler())
        except Exception as e:
            logger.error(f"WebSocket connection failed: {str(e)}")
            self.connected = False
            raise

    async def _message_handler(self):
        """Handle incoming WebSocket messages"""
        try:
            while self.connected and self.ws:
                message = await self.ws.recv()
                
                try:
                    # Zerodha sends binary data for ticks
                    if isinstance(message, bytes):
                        ticks = self._parse_binary_message(message)
                        for callback in self.callbacks['ticks']:
                            await callback(ticks)
                    else:
                        # Handle other message types (order updates, etc.)
                        data = json.loads(message)
                        msg_type = data.get('type', 'message')
                        for callback in self.callbacks.get(msg_type, []):
                            await callback(data)
                            
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Message handler error: {str(e)}")
            self.connected = False
            
    def _parse_binary_message(self, data: bytes) -> Dict[str, Any]:
        """Parse binary tick data from Zerodha"""
        # Implement according to Kite Connect WebSocket binary message format
        # This is a simplified version - you'll need to implement the full binary parsing
        import struct
        
        # Parse header
        packet_length = len(data)
        header_size = 2  # First 2 bytes contain count
        (count,) = struct.unpack('>H', data[0:header_size])
        
        ticks = []
        pos = header_size
        
        for _ in range(count):
            if packet_length < pos + 44:  # Minimum tick size
                break
                
            instrument_token = struct.unpack('>I', data[pos:pos+4])[0]
            pos += 4
            
            # Parse LTP (Last Traded Price)
            ltp = struct.unpack('>I', data[pos:pos+4])[0] / 100.0
            pos += 4
            
            # Add more fields as needed according to your subscription mode
            tick = {
                'instrument_token': instrument_token,
                'last_price': ltp,
                'timestamp': datetime.now().isoformat()
            }
            ticks.append(tick)
            
        return {'type': 'ticks', 'data': ticks}

    async def _reconnect(self, max_retries: int = 5, delay: int = 5):
        """Attempt to reconnect to WebSocket"""
        retries = 0
        while retries < max_retries and not self.connected:
            try:
                logger.info(f"Attempting to reconnect... (Attempt {retries + 1}/{max_retries})")
                await self.connect()
                if self.connected:
                    # Resubscribe to previous tokens
                    if self.subscribed_tokens:
                        await self.subscribe(self.subscribed_tokens)
                    return
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {str(e)}")
                retries += 1
                await asyncio.sleep(delay)

    async def subscribe(self, instrument_tokens: List[int], mode: str = 'full'):
        """Subscribe to given instrument tokens"""
        if not self.connected:
            raise Exception("WebSocket not connected")

        try:
            message = {
                "a": "subscribe",  # action
                "v": instrument_tokens,  # values
                "m": mode  # mode: 'full', 'quote', or 'ltp'
            }
            await self.ws.send(json.dumps(message))
            self.subscribed_tokens.extend(instrument_tokens)
            logger.info(f"Subscribed to instruments: {instrument_tokens}")
        except Exception as e:
            logger.error(f"Subscription failed: {str(e)}")
            raise

    async def unsubscribe(self, instrument_tokens: List[int]):
        """Unsubscribe from given instrument tokens"""
        if not self.connected:
            raise Exception("WebSocket not connected")

        try:
            message = {
                "a": "unsubscribe",
                "v": instrument_tokens
            }
            await self.ws.send(json.dumps(message))
            self.subscribed_tokens = [t for t in self.subscribed_tokens if t not in instrument_tokens]
            logger.info(f"Unsubscribed from instruments: {instrument_tokens}")
        except Exception as e:
            logger.error(f"Unsubscribe failed: {str(e)}")
            raise

    def on_ticks(self, callback: Callable[[List[Dict]], None]):
        """Register callback for tick data"""
        self.callbacks['ticks'].append(callback)

    def on_order_update(self, callback: Callable[[Dict], None]):
        """Register callback for order updates"""
        self.callbacks['order_update'].append(callback)

    def on_message(self, callback: Callable[[Dict], None]):
        """Register callback for other messages"""
        self.callbacks['message'].append(callback)

    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            self.connected = False
            await self.ws.close()
            logger.info("WebSocket connection closed")

    async def broadcast_nav_update(nav_data: dict):
        """Broadcast NAV updates to all connected clients"""
        try:
            message = {
                "type": "nav_update",
                "data": {
                    "date": nav_data["date"].isoformat() if isinstance(nav_data["date"], datetime) else nav_data["date"],
                    "nav_value": float(nav_data["nav_value"]),
                    "investor_id": nav_data["investor_id"]
                }
            }
            logger.info(f"Broadcasting NAV update: {message}")
            await manager.broadcast_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting NAV update: {str(e)}")
