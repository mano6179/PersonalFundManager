import pandas as pd
import re
import numpy as np
from datetime import datetime

def parse_symbol(symbol):
    """
    Parse NSE option symbols for both monthly and weekly expiries.
    Returns: underlying, expiry_year, expiry_month, expiry_day, strike, option_type, expiry_date
    """
    # Monthly: NIFTY24APR22300CE
    m_monthly = re.match(r'^([A-Z]+)(\d{2})(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(\d+)(CE|PE)$', symbol)
    # Weekly: NIFTY2450522650PE or NIFTY24O312650PE
    m_weekly = re.match(r'^([A-Z]+)(\d{2})(\d|O|N|D)(\d{2})(\d+)(CE|PE)$', symbol)

    month_map = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6,
                 'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12,
                 'O':10, 'N':11, 'D':12}

    if m_monthly:
        underlying = m_monthly.group(1)
        year = 2000 + int(m_monthly.group(2))
        month = month_map[m_monthly.group(3)]
        strike = int(m_monthly.group(4))
        option_type = m_monthly.group(5)
        expiry_date = None  # Use expiry_date from CSV for monthly, or infer last Thursday if needed
        return underlying, year, month, np.nan, strike, option_type, expiry_date

    elif m_weekly:
        underlying = m_weekly.group(1)
        year = 2000 + int(m_weekly.group(2))
        month_code = m_weekly.group(3)
        day = int(m_weekly.group(4))
        month = month_map[month_code] if month_code in month_map else int(month_code)
        strike = int(m_weekly.group(5))
        option_type = m_weekly.group(6)
        try:
            expiry_date = datetime(year, month, day)
        except:
            expiry_date = None
        return underlying, year, month, day, strike, option_type, expiry_date

    return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, None

# Load and clean data
file_path = 'tradebook-KG2302-FO-last-FY.csv'
trades = pd.read_csv(file_path)

# Standardize columns
trades.columns = [col.strip().lower() for col in trades.columns]

# Parse dates with error handling
date_cols = ['trade_date', 'expiry_date']
for col in date_cols:
    trades[col] = pd.to_datetime(trades[col], format='%d-%m-%Y', errors='coerce')

# Parse symbols
parsed = trades['symbol'].apply(parse_symbol)
trades[['underlying', 'expiry_year', 'expiry_month', 'expiry_day', 'strike', 'option_type','parsed_expiry_date']] = \
    pd.DataFrame(parsed.tolist(), index=trades.index)

# Use parsed expiry date where CSV date is missing
trades['expiry_date'] = trades['expiry_date'].combine_first(trades['parsed_expiry_date'])
trades.drop(columns=['parsed_expiry_date'], inplace=True)

# Add unique trade ID
trades['trade_id'] = pd.util.hash_pandas_object(trades[['symbol', 'trade_date', 'quantity', 'price']])

# Validate critical columns
critical_cols = ['symbol', 'trade_type', 'quantity', 'price', 'expiry_date']
print("Missing values before cleaning:")
print(trades[critical_cols].isnull().sum())

# Drop rows with missing critical data
trades_clean = trades.dropna(subset=critical_cols).copy()

# Add expiry date from symbol (more accurate than CSV date)
def calculate_expiry(row):
    try:
        return datetime(row['expiry_year'], row['expiry_month'], 1) + pd.offsets.MonthEnd(0)
    except:
        return row['expiry_date']

trades_clean['expiry_date'] = trades_clean.apply(calculate_expiry, axis=1)

# Save cleaned data
output_path = 'tradebook_phase1_cleaned.csv'
trades_clean.to_csv(output_path, index=False)

print(f"\nCleaning complete. Saved {len(trades_clean)} trades to {output_path}")
print("Sample parsed data:")
print(trades_clean[['symbol', 'underlying', 'expiry_year', 'expiry_month', 
                   'strike', 'option_type', 'trade_date', 'expiry_date']].head())
