from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn

from simple_zerodha import SimpleZerodha

app = FastAPI(
    title="Simple Zerodha API",
    description="A simple API for interacting with Zerodha"
)

# Initialize the Zerodha client
zerodha = SimpleZerodha(api_key="2o2hlqr9zojrs4uo")

# Models
class TokenRequest(BaseModel):
    api_key: str
    api_secret: str
    access_token: str

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to Simple Zerodha API"}

@app.get("/login", response_class=RedirectResponse)
def login_to_zerodha():
    """Redirect to Zerodha login page"""
    login_url = zerodha.get_login_url()
    return RedirectResponse(url=login_url)

@app.get("/callback")
def zerodha_callback(request_token: str = Query(..., description="Request token from Zerodha")):
    """Handle callback from Zerodha after login"""
    try:
        # In a real application, you would use the API secret here
        # For now, we'll just return the request token
        return {
            "success": True,
            "message": "Received request token",
            "data": {
                "request_token": request_token
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process request token: {str(e)}"
        )

@app.post("/set-token")
def set_access_token(token_request: TokenRequest):
    """Set access token for Zerodha API"""
    try:
        # Set the API secret
        zerodha.api_secret = token_request.api_secret
        
        # Set the access token
        zerodha.set_access_token(token_request.access_token)
        
        return {
            "success": True,
            "message": "Access token set successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set access token: {str(e)}"
        )

@app.get("/profile")
def get_profile():
    """Get user profile from Zerodha"""
    try:
        if not zerodha.access_token:
            raise HTTPException(
                status_code=401,
                detail="Access token not set. Please set the access token first."
            )
        
        profile = zerodha.profile()
        return {
            "success": True,
            "message": "Profile fetched successfully",
            "data": profile
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch profile: {str(e)}"
        )

@app.get("/holdings")
def get_holdings():
    """Get user holdings from Zerodha"""
    try:
        if not zerodha.access_token:
            raise HTTPException(
                status_code=401,
                detail="Access token not set. Please set the access token first."
            )
        
        holdings = zerodha.holdings()
        return {
            "success": True,
            "message": "Holdings fetched successfully",
            "data": holdings
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch holdings: {str(e)}"
        )

@app.get("/positions")
def get_positions():
    """Get user positions from Zerodha"""
    try:
        if not zerodha.access_token:
            raise HTTPException(
                status_code=401,
                detail="Access token not set. Please set the access token first."
            )
        
        positions = zerodha.positions()
        return {
            "success": True,
            "message": "Positions fetched successfully",
            "data": positions
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch positions: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("simple_zerodha_app:app", host="127.0.0.1", port=8000, reload=True)
