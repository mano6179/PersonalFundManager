from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routers import nav_router, auth_router, zerodha_router, market_router
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
app.include_router(market_router.router)

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
