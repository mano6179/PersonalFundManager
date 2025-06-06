import pandas as pd
import numpy as np
from collections import defaultdict

# Load the cleaned and parsed tradebook from Phase 1
file_path = 'tradebook_phase1_cleaned.csv'
trades = pd.read_csv(file_path, parse_dates=['trade_date', 'expiry_date', 'order_execution_time'])

# Sort trades by execution time for correct sequencing
trades = trades.sort_values('order_execution_time').reset_index(drop=True)

# Create a composite key for each position (underlying, expiry, strike, option_type)
trades['position_key'] = trades.apply(
    lambda row: f"{row['underlying']}_{row['expiry_date'].strftime('%Y-%m-%d')}_{row['strike']}_{row['option_type']}", 
    axis=1
)

# Map trade_type to quantity direction
trades['net_qty'] = trades.apply(
    lambda row: row['quantity'] * (1 if row['trade_type'].lower() == 'buy' else -1), 
    axis=1
)

# Initialize columns for annotation
trades['entry_exit'] = np.nan
trades['matched_qty'] = 0
trades['matched_trade_ids'] = None

# Dictionary to track open positions using FIFO
open_positions = defaultdict(list)

for idx, row in trades.iterrows():
    key = row['position_key']
    trade_qty = row['net_qty']
    price = row['price']
    trade_id = row['trade_id']
    
    current_position = sum(lot['qty'] for lot in open_positions[key])
    
    # Determine if this trade is entry or exit
    if (current_position == 0) or (current_position * trade_qty > 0):
        # Entry (same direction or new position)
        open_positions[key].append({'qty': trade_qty, 'price': price, 'trade_id': trade_id})
        trades.at[idx, 'entry_exit'] = 'Entry'
        trades.at[idx, 'matched_qty'] = abs(trade_qty)
    else:
        # Exit (opposite direction)
        remaining_qty = abs(trade_qty)
        matched = 0
        matched_ids = []
        
        while remaining_qty > 0 and open_positions[key]:
            current_lot = open_positions[key][0]
            
            # Calculate possible match
            close_qty = min(remaining_qty, abs(current_lot['qty']))
            
            # Reduce both the lot and the exit trade
            if current_lot['qty'] > 0:
                # Closing long position with sell
                current_lot['qty'] -= close_qty
                matched += close_qty
            else:
                # Closing short position with buy
                current_lot['qty'] += close_qty
                matched += close_qty
                
            remaining_qty -= close_qty
            matched_ids.append(str(current_lot['trade_id']))
            
            # Remove fully closed lots
            if current_lot['qty'] == 0:
                open_positions[key].pop(0)
                
        # Update trade status
        if matched == 0:
            trades.at[idx, 'entry_exit'] = 'Unmatched Exit'
        elif matched == abs(trade_qty):
            trades.at[idx, 'entry_exit'] = 'Exit'
        else:
            trades.at[idx, 'entry_exit'] = 'Partial Exit'
            
        trades.at[idx, 'matched_qty'] = matched
        trades.at[idx, 'matched_trade_ids'] = ';'.join(matched_ids)

# Summary counts for audit
entry_count = (trades['entry_exit'] == 'Entry').sum()
exit_count = (trades['entry_exit'] == 'Exit').sum()
partial_exit_count = (trades['entry_exit'] == 'Partial Exit').sum()
unmatched_exit_count = (trades['entry_exit'] == 'Unmatched Exit').sum()

print(f'''Matching Summary:
Entries: {entry_count}
Full Exits: {exit_count}
Partial Exits: {partial_exit_count}
Unmatched Exits: {unmatched_exit_count}''')

# Save annotated trades
trades.to_csv('tradebook_phase2_annotated.csv', index=False)
print("\nSample trades:")
print(trades[['trade_date', 'symbol', 'trade_type', 'quantity', 
             'entry_exit', 'matched_qty', 'matched_trade_ids']].head(10))
