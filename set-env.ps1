# Set environment variables for Personal Fund Manager
$env:MONGODB_URL = "mongodb://localhost:27017"
$env:DATABASE_NAME = "personal_fund_manager"
$env:JWT_SECRET = "8201b6ab6998a8d800afb10005e1325536c6046cd20fafebc30d461ed0c425a5"
$env:ACCESS_TOKEN_EXPIRE_MINUTES = "30"
$env:REFRESH_TOKEN_EXPIRE_DAYS = "7"

Write-Host "Environment variables set successfully!" 