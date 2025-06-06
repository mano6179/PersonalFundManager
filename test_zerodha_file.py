from kiteconnect import KiteConnect

# Initialize Kite Connect
kite = KiteConnect(api_key="2o2hlqr9zojrs4uo")

# Get the login URL
login_url = kite.login_url()

# Write output to a file
with open("zerodha_test_output.txt", "w") as f:
    f.write(f"Login URL: {login_url}\n")
    f.write("If you see this message, the Zerodha API is working correctly!\n")
    f.write("To use the API, you need to:\n")
    f.write("1. Open the login URL in your browser\n")
    f.write("2. Log in to your Zerodha account\n")
    f.write("3. Get the request token from the redirect URL\n")
    f.write("4. Use the request token to generate a session\n")
