# Fund Manager

A comprehensive web-based dashboard for managing a personal trading fund, featuring trade logging, NAV tracking, technical analysis, and economic calendar integration.

## Features

- **Trade Log Tracker**
  - Input form for logging new trades
  - PnL calculation (realized and unrealized)
  - Strategy tagging and categorization
  - CSV import/export functionality

- **NAV & Fund Tracker**
  - Daily NAV calculation
  - Tiered profit-sharing model
  - Investor capital management
  - Tax consideration toggle

- **Technical Analysis**
  - RSI, MACD, Bollinger Bands
  - IV percentile tracking
  - Volume analysis
  - Exhaustion alerts

- **Economic Calendar**
  - Macroeconomic event tracking
  - Custom event creation
  - Impact assessment
  - Calendar view

## Tech Stack

- **Frontend**: React, Tailwind CSS, Chart.js
- **Backend**: FastAPI, SQLAlchemy
- **Database**: SQLite
- **Market Data**: yfinance, TA-Lib

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Usage

1. Access the dashboard at `http://localhost:3000`
2. Use the navigation menu to access different modules
3. Dark mode toggle is available in the top-right corner

## API Endpoints

- `GET /api/trades` - List all trades
- `POST /api/trades` - Create a new trade
- `GET /api/investors` - List all investors
- `POST /api/investors` - Add a new investor
- `GET /api/nav/{investor_id}` - Get NAV history for an investor
- `GET /api/indicators/{symbol}` - Get technical indicators
- `GET /api/events` - List all events
- `POST /api/events` - Add a new event

## License

MIT 
