from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import nav_router, auth_router, zerodha_router
import os

app = FastAPI(
    title="Steady Gains 2025 - Trading Dashboard",
    description="A comprehensive web-based dashboard for managing a personal trading fund"
)

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
app.include_router(nav_router.router)
app.include_router(auth_router.router)
app.include_router(zerodha_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Steady Gains API"}

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/zerodha-trades")
def zerodha_trades_page():
    """Serve the Zerodha trades HTML page"""
    return FileResponse("static/zerodha_trades.html")
