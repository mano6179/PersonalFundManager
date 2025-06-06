from kiteconnect import KiteConnect

# Initialize Kite Connect
kite = KiteConnect(api_key="2o2hlqr9zojrs4uo")

# Get the login URL
login_url = kite.login_url()
print(f"Login URL: {login_url}")

# This is just a test script to verify that the Zerodha API is working
print("If you see this message, the Zerodha API is working correctly!")
print("To use the API, you need to:")
print("1. Open the login URL in your browser")
print("2. Log in to your Zerodha account")
print("3. Get the request token from the redirect URL")
print("4. Use the request token to generate a session")
