from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from app.routers import nav_router, auth_router, zerodha_router, market_router, logs_router
from app.config.database import init_db, close_db, get_database
from app.services.websocket_service import manager
import os
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify environment variables
if not os.getenv("MONGODB_URL"):
    raise ValueError("MONGODB_URL environment variable is not set")

app = FastAPI(
    title="Steady Gains 2025 - Trading Dashboard",
    description="A comprehensive web-based dashboard for managing a personal trading fund"
)

@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup"""
    try:
        async with asyncio.timeout(60.0):  # Increased timeout to 60 seconds
            await init_db()
            logger.info("Database connection initialized successfully")
    except asyncio.TimeoutError:
        logger.error("Database initialization timed out")
        raise Exception("Database initialization timed out. Please ensure your MongoDB Atlas connection string is correct and the IP address is whitelisted.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during database shutdown: {str(e)}")

# Get frontend URL from environment variable or use localhost for development
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nav_router)
app.include_router(auth_router)
app.include_router(zerodha_router)
app.include_router(market_router)
app.include_router(logs_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Steady Gains API"}

@app.get("/kite/callback")
async def kite_callback(request_token: str, action: str = None, status: str = None):
    """
    Handle Kite callback and redirect to our API endpoint
    """
    if status == "success" and request_token:
        return RedirectResponse(url=f"/api/zerodha/callback?request_token={request_token}")
    return {"error": "Login failed"}

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/zerodha-trades")
def zerodha_trades_page():
    """Serve the Zerodha trades HTML page"""
    return FileResponse("static/zerodha_trades.html")

@app.websocket("/ws/nav")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to ping the database
        db = await get_database()
        await db.command("ping")
        return {
            "status": "healthy",
            "database": {
                "type": "MongoDB Atlas",
                "status": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service unhealthy: MongoDB Atlas connection failed. Please check your connection string and IP whitelist settings."
        )
