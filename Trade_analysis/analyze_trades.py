import pandas as pd

# Load the CSV file into a DataFrame
file_path = 'tradebook-KG2302-FO(last FY).csv'
df = pd.read_csv(file_path)

# Display the first few rows to verify
print(df.head())

# Ensure order_execution_time is datetime
if not pd.api.types.is_datetime64_any_dtype(df['order_execution_time']):
    df['order_execution_time'] = pd.to_datetime(df['order_execution_time'])

# Sort by execution time
trades = df.sort_values('order_execution_time')

from collections import deque, defaultdict

# Position queue per symbol
position_queues = defaultdict(deque)

# Each position: dict with quantity, price, execution_time, trade_type
positions_history = []

for idx, row in trades.iterrows():
    symbol = row['symbol']
    qty = int(row['quantity'])
    trade_type = row['trade_type'].lower()
    exec_time = row['order_execution_time']
    price = row['price']
    # For FIFO, buys add to queue, sells remove from queue
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
    # Save snapshot after each trade
    snapshot = {s: list(q) for s, q in position_queues.items() if q}
    positions_history.append({'time': exec_time, 'positions': snapshot})

def get_active_positions(as_of_date):
    """Return active positions as of a given date (string or datetime)."""
    as_of_date = pd.to_datetime(as_of_date)
    # Find the last snapshot before or at as_of_date
    last = None
    for snap in positions_history:
        if snap['time'] <= as_of_date:
            last = snap['positions']
        else:
            break
    return last if last else {}

# Example usage:
# print(get_active_positions('2024-06-01'))
