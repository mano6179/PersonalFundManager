import requests
import hashlib
import json
from datetime import datetime, timedelta

class SimpleZerodha:
    """A simplified version of the Zerodha API client"""
    
    def __init__(self, api_key, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = None
        self.root_url = "https://api.kite.trade"
        self.login_url = "https://kite.zerodha.com/connect/login"
        
    def get_login_url(self):
        """Get the login URL for Zerodha"""
        return f"{self.login_url}?api_key={self.api_key}&v=3"
    
    def generate_session(self, request_token):
        """Generate a session with the request token"""
        if not self.api_secret:
            raise ValueError("API secret is required to generate a session")
        
        # Create checksum
        data = f"{self.api_key}{request_token}{self.api_secret}"
        h = hashlib.sha256(data.encode('utf-8'))
        checksum = h.hexdigest()
        
        # Make the request
        url = f"{self.root_url}/session/token"
        headers = {
            "X-Kite-Version": "3"
        }
        data = {
            "api_key": self.api_key,
            "request_token": request_token,
            "checksum": checksum
        }
        
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()["data"]
            self.access_token = data["access_token"]
            return data
        else:
            raise Exception(f"Failed to generate session: {response.text}")
    
    def set_access_token(self, access_token):
        """Set the access token for API calls"""
        self.access_token = access_token
    
    def _get(self, endpoint, params=None):
        """Make a GET request to the Zerodha API"""
        if not self.access_token:
            raise ValueError("Access token is required for API calls")
        
        url = f"{self.root_url}/{endpoint}"
        headers = {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}"
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"API request failed: {response.text}")
    
    def profile(self):
        """Get user profile"""
        return self._get("user/profile")
    
    def holdings(self):
        """Get user holdings"""
        return self._get("portfolio/holdings")
    
    def positions(self):
        """Get user positions"""
        return self._get("portfolio/positions")
    
    def orders(self):
        """Get user orders"""
        return self._get("orders")
    
    def trades(self):
        """Get user trades"""
        return self._get("trades")
    
    def margins(self):
        """Get user margins"""
        return self._get("user/margins")

# Example usage
if __name__ == "__main__":
    # Initialize the client
    zerodha = SimpleZerodha(api_key="2o2hlqr9zojrs4uo")
    
    # Get the login URL
    login_url = zerodha.get_login_url()
    
    print(f"Login URL: {login_url}")
    print("To use the API, you need to:")
    print("1. Open the login URL in your browser")
    print("2. Log in to your Zerodha account")
    print("3. Get the request token from the redirect URL")
    print("4. Use the request token to generate a session")
    
    # The following code would be used after getting the request token
    # request_token = "your_request_token"
    # session_data = zerodha.generate_session(request_token)
    # print(f"Access token: {session_data['access_token']}")
    
    # After setting the access token, you can make API calls
    # zerodha.set_access_token("your_access_token")
    # profile = zerodha.profile()
    # print(f"User profile: {profile}")
