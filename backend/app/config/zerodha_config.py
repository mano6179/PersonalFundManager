import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Zerodha API configuration
ZERODHA_CONFIG: Dict[str, Any] = {
    "api_key": os.getenv("ZERODHA_API_KEY", "2o2hlqr9zojrs4uo"),
    "api_secret": os.getenv("ZERODHA_API_SECRET", "1q2b87k3dafygrgn3k8j3cmtkmwnmi6q"),
    "redirect_url": os.getenv("ZERODHA_REDIRECT_URL", "http://localhost:8000/api/zerodha/callback"),
    "login_url": "https://kite.zerodha.com/connect/login",
    "api_url": "https://api.kite.trade"
}
