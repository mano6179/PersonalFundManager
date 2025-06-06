# Personal Trading Dashboard

A comprehensive web-based dashboard for managing a personal trading fund, featuring trade logging, NAV tracking, technical analysis, and economic calendar integration.

---

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

---

## Project Structure

```
PersonalFundManager/
│
├── main.py                # FastAPI backend entry point
├── run_app.py             # Script to launch backend (Uvicorn)
├── requirements.txt       # Python backend dependencies
├── Procfile, runtime.txt  # Deployment configs (Heroku/Netlify)
├── app/                   # Backend app code (routers, models, services)
│   ├── routers/
│   ├── models/
│   ├── services/
│   └── config/
├── backend/               # Utility scripts (e.g., excel_upload.py)
├── frontend/              # React frontend app
│   ├── public/
│   └── src/
│       ├── components/
│       ├── context/
│       └── pages/
├── static/                # Static files (e.g., zerodha_trades.html)
└── netlify/               # Netlify serverless functions (optional)
```

---

## Tech Stack

- **Frontend**: React, Tailwind CSS, Chart.js
- **Backend**: FastAPI, SQLAlchemy
- **Database**: SQLite
- **Market Data**: yfinance, TA-Lib

---

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```powershell
   python run_app.py
   ```
   Or directly with Uvicorn:
   ```powershell
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```powershell
   cd frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Start the development server:
   ```powershell
   npm start
   ```

---

## Usage

- Access the dashboard at [http://localhost:3000](http://localhost:3000)
- Use the navigation menu to access different modules
- Dark mode toggle is available in the top-right corner

---

## API Endpoints

- `GET /api/trades` - List all trades
- `POST /api/trades` - Create a new trade
- `GET /api/investors` - List all investors
- `POST /api/investors` - Add a new investor
- `GET /api/nav/{investor_id}` - Get NAV history for an investor
- `GET /api/indicators/{symbol}` - Get technical indicators
- `GET /api/events` - List all events
- `POST /api/events` - Add a new event
- `GET /zerodha-trades` - View Zerodha trades loader page

---

## Deployment

- The project includes a `Procfile` and `runtime.txt` for deployment on platforms like Heroku.
- For Netlify serverless functions, see the `netlify/functions/` directory.

---

## License

MIT