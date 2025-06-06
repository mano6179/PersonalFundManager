import pandas as pd
import numpy as np
from collections import defaultdict

# Load cleaned trade data
trades = pd.read_csv('tradebook_phase1_cleaned.csv', parse_dates=['trade_date', 'expiry_date', 'order_execution_time'])

# Sort trades for FIFO matching
trades = trades.sort_values(['order_execution_time', 'trade_id'])

# Composite key for each contract
trades['position_key'] = trades.apply(
    lambda x: f"{x['underlying']}|{x['expiry_date']}|{x['strike']}|{x['option_type']}",
    axis=1
)

# Financial year business days
all_dates = pd.date_range(start='2024-04-01', end='2025-03-31', freq='B')

# Ledger: {position_key: list of open/closed lots with their lifecycle}
position_ledger = defaultdict(list)

for _, row in trades.iterrows():
    key = row['position_key']
    qty = row['quantity'] * (1 if row['trade_type'].lower() == 'buy' else -1)
    price = row['price']
    trade_id = row['trade_id']
    trade_date = row['trade_date']
    expiry_date = row['expiry_date']

    # If same direction or no open lot, it's a new entry
    if (qty > 0 and (not position_ledger[key] or position_ledger[key][-1]['direction'] == 'Long')) or \
        (qty < 0 and (not position_ledger[key] or position_ledger[key][-1]['direction'] == 'Short')):
        position_ledger[key].append({
        'open_qty': abs(qty),
        'direction': 'Long' if qty > 0 else 'Short',
        'open_date': trade_date,
        'open_price': price,
        'expiry': expiry_date,
        'close_qty': 0,
        'close_date': None,
        'close_price': None
    })

    else:
        # Closing existing lots FIFO
        remaining = abs(qty)
        for lot in position_ledger[key]:
            if lot['close_qty'] < lot['open_qty'] and lot['direction'] != ('Long' if qty > 0 else 'Short'):
                open_remain = lot['open_qty'] - lot['close_qty']
                close_now = min(open_remain, remaining)
                lot['close_qty'] += close_now
                lot['close_date'] = trade_date
                lot['close_price'] = price  # Last close price for this lot
                remaining -= close_now
                if remaining == 0:
                    break
        # If more closing than open, treat as new entry in opposite direction
        if remaining > 0:
            position_ledger[key].append({
                'open_qty': remaining,
                'direction': 'Long' if qty > 0 else 'Short',
                'open_date': trade_date,
                'open_price': price,
                'expiry': expiry_date,
                'close_qty': 0,
                'close_date': None,
                'close_price': None
            })

# Build daily active position book
daily_position_book = []
def safe_strike_to_int(strike):
    if pd.isna(strike):
        return None
    try:
        return int(float(strike))
    except Exception:
        return None
for key, lots in position_ledger.items():
    underlying, expiry_str, strike, opt_type = key.split('|')
    expiry = pd.to_datetime(expiry_str)
    for lot in lots:
        # The position is active from open_date to the earlier of close_date or expiry
        start_date = lot['open_date']
        end_date = lot['close_date'] if lot['close_date'] is not None else expiry
        active_dates = pd.date_range(start=max(start_date, all_dates[0]), end=min(end_date, expiry), freq='B')
        for date in active_dates:
            daily_position_book.append({
                'date': date,
                'underlying': underlying,
                'expiry': expiry_str,
                'strike': safe_strike_to_int(strike),
                'option_type': opt_type,
                'quantity': lot['open_qty'] if lot['direction'] == 'Long' else -lot['open_qty'],
                'position_type': lot['direction'],
                'avg_entry_price': lot['open_price'],
                'status': (
                    'Expired' if date == expiry and (lot['close_date'] is None or lot['close_date'] > expiry)
                    else 'Closed' if lot['close_date'] is not None and date == lot['close_date']
                    else 'Active'
                )
            })

# Output as DataFrame
daily_positions_df = pd.DataFrame(daily_position_book)
daily_positions_df = daily_positions_df.sort_values(['date', 'underlying', 'expiry', 'strike', 'option_type'])

# Save to CSV
daily_positions_df.to_csv('phase3_daily_active_positions.csv', index=False)

print("Phase 3 complete. Sample output:")
print(daily_positions_df.head(10))
