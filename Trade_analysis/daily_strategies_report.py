import pandas as pd
from collections import deque, defaultdict

# Load the CSV file into a DataFrame
file_path = 'tradebook-KG2302-FO(last FY).csv'
df = pd.read_csv(file_path)

# Ensure order_execution_time is datetime
if not pd.api.types.is_datetime64_any_dtype(df['order_execution_time']):
    df['order_execution_time'] = pd.to_datetime(df['order_execution_time'])

# Sort by execution time
trades = df.sort_values('order_execution_time')

# Position queue per symbol
position_queues = defaultdict(deque)
# Track daily snapshots
end_of_day_positions = {}

# Get all unique trade dates (as date, not datetime)
trades['trade_date_only'] = trades['order_execution_time'].dt.date
unique_dates = sorted(trades['trade_date_only'].unique())

# Process trades FIFO and take snapshot at end of each day
day_idx = 0
for idx, row in trades.iterrows():
    symbol = row['symbol']
    qty = int(row['quantity'])
    trade_type = row['trade_type'].lower()
    exec_time = row['order_execution_time']
    price = row['price']
    # FIFO logic
    if trade_type == 'buy':
        position_queues[symbol].append({'quantity': qty, 'price': price, 'execution_time': exec_time})
    elif trade_type == 'sell':
        qty_to_close = qty
        while qty_to_close > 0 and position_queues[symbol]:
            pos = position_queues[symbol][0]
            if pos['quantity'] > qty_to_close:
                pos['quantity'] -= qty_to_close
                qty_to_close = 0
            else:
                qty_to_close -= pos['quantity']
                position_queues[symbol].popleft()
    # If this is the last trade of the day, save snapshot
    next_idx = idx + 1
    is_last_trade_today = (next_idx == len(trades)) or (trades.iloc[next_idx]['trade_date_only'] != row['trade_date_only'])
    if is_last_trade_today:
        # Save a copy of all open positions at end of this day
        snapshot = {s: list(q) for s, q in position_queues.items() if q}
        end_of_day_positions[row['trade_date_only']] = snapshot

# Print active strategies at end of each day
def describe_strategy(positions):
    """Describe the options strategy based on open positions."""
    if not positions:
        return 'No open positions'
    legs = []
    for symbol, pos_list in positions.items():
        for pos in pos_list:
            legs.append(f"{symbol}: {pos['quantity']} @ {pos['price']} (opened {pos['execution_time'].date()})")
    return '\n'.join(legs)

print("Active option strategies at end of each day in last financial year:")
for day, positions in end_of_day_positions.items():
    print(f"\nDate: {day}")
    print(describe_strategy(positions))
