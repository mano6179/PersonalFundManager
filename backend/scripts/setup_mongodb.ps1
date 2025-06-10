# Check if MongoDB is installed
$mongodbPath = "C:\Program Files\MongoDB\Server\*\bin\mongod.exe"
$mongodbExists = Test-Path $mongodbPath

if (-not $mongodbExists) {
    Write-Host "MongoDB is not installed. Please install MongoDB first:"
    Write-Host "1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community"
    Write-Host "2. Run the installer and follow the installation wizard"
    Write-Host "3. Make sure to install MongoDB Compass (the GUI tool) when prompted"
    exit 1
}

# Create data directory if it doesn't exist
$dataDir = "C:\data\db"
if (-not (Test-Path $dataDir)) {
    Write-Host "Creating MongoDB data directory at $dataDir"
    New-Item -ItemType Directory -Path $dataDir -Force
}

# Check if MongoDB service is running
$service = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
if ($service -and $service.Status -eq "Running") {
    Write-Host "MongoDB service is already running"
} else {
    Write-Host "Starting MongoDB service..."
    if ($service) {
        Start-Service -Name "MongoDB"
    } else {
        Write-Host "MongoDB service not found. Please ensure MongoDB is properly installed."
        exit 1
    }
}

Write-Host "MongoDB setup complete!"
Write-Host "You can now start your FastAPI application." 