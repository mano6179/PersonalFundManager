import pandas as pd

# --- Load data ---
trades = pd.read_csv('tradebook_phase2_annotated.csv', parse_dates=['trade_date', 'expiry_date'])
strategies = pd.read_csv('phase4_daily_strategies.csv', parse_dates=['date', 'expiry'])

# --- Normalize columns ---
trades['entry_exit'] = trades['entry_exit'].astype(str).str.strip().str.lower()
trades['option_type'] = trades['option_type'].astype(str).str.strip().str.upper()
trades['strike'] = trades['strike'].apply(lambda x: int(float(x)) if pd.notna(x) and str(x).strip() != '' else pd.NA).astype('Int64')
trades['symbol'] = trades['symbol'].astype(str).str.strip()

# --- Robust leg parser ---
def parse_leg(leg_str):
    parts = leg_str.split('-', 2)
    strike = None
    option_type = None
    quantity = 0
    if len(parts) >= 1 and parts[0].strip() != '':
        try:
            strike = int(float(parts[0]))
        except Exception:
            pass
    if len(parts) >= 2 and parts[1].strip() != '':
        option_type = parts[1].upper()
    if len(parts) >= 3 and parts[2].strip() != '':
        try:
            quantity = int(parts[2])
        except Exception:
            quantity = 0
    return {'strike': strike, 'option_type': option_type, 'quantity': quantity}

# --- Prepare for PnL calculation ---
entry_trades = trades[trades['entry_exit'] == 'entry'].copy()
exit_trades = trades[trades['entry_exit'].isin(['exit', 'partial exit'])].copy()

# --- FIFO PnL calculation for each leg ---
def fifo_pnl_for_leg(symbol, strike, option_type):
    entries = entry_trades[
        (entry_trades['symbol'] == symbol) &
        (entry_trades['strike'] == strike) &
        (entry_trades['option_type'] == option_type)
    ].sort_values('trade_date')
    exits = exit_trades[
        (exit_trades['symbol'] == symbol) &
        (exit_trades['strike'] == strike) &
        (exit_trades['option_type'] == option_type)
    ].sort_values('trade_date')

    entry_queue = []
    pnl_records = []

    # Build entry queue: each lot is [qty_remaining, entry_price, trade_type, trade_date]
    for _, row in entries.iterrows():
        entry_queue.append([row['matched_qty'], row['price'], row['trade_type'], row['trade_date']])

    for _, exit_row in exits.iterrows():
        qty_to_match = exit_row['matched_qty']
        exit_price = exit_row['price']
        exit_type = exit_row['trade_type']
        exit_date = exit_row['trade_date']
        while qty_to_match > 0 and entry_queue:
            entry_qty, entry_price, entry_type, entry_date = entry_queue[0]
            matched = min(qty_to_match, entry_qty)
            # Long: buy entry, sell exit; Short: sell entry, buy exit
            if entry_type == 'buy' and exit_type == 'sell':
                pnl = (exit_price - entry_price) * matched
            elif entry_type == 'sell' and exit_type == 'buy':
                pnl = (entry_price - exit_price) * matched
            else:
                pnl = 0  # Should not happen in correct data
            pnl_records.append({'date': exit_date, 'symbol': symbol, 'strike': strike,
                               'option_type': option_type, 'pnl': pnl})
            qty_to_match -= matched
            entry_qty -= matched
            if entry_qty == 0:
                entry_queue.pop(0)
            else:
                entry_queue[0][0] = entry_qty
    # Handle expired options (remaining in queue)
    for entry_qty, entry_price, entry_type, entry_date in entry_queue:
        # Find expiry from strategies
        expiry = strategies[
            (strategies['legs'].str.contains(f"{strike}-{option_type}")) &
            (strategies['date'] >= entry_date)
        ]['expiry'].max()
        if pd.isna(expiry):
            continue
        expiry = pd.to_datetime(expiry)
        if entry_type == 'buy':
            pnl = (0 - entry_price) * entry_qty  # Option expires worthless
        else:
            pnl = (entry_price - 0) * entry_qty  # Short premium kept
        pnl_records.append({'date': expiry, 'symbol': symbol, 'strike': strike,
                            'option_type': option_type, 'pnl': pnl})
    return pnl_records

# --- Aggregate PnL for all legs ---
all_leg_keys = trades[['symbol', 'strike', 'option_type']].drop_duplicates()
all_pnl_records = []
for _, leg in all_leg_keys.iterrows():
    recs = fifo_pnl_for_leg(leg['symbol'], leg['strike'], leg['option_type'])
    all_pnl_records.extend(recs)

# --- Map PnL to strategies ---
pnl_df = pd.DataFrame(all_pnl_records)
results = []
for _, strat in strategies.iterrows():
    legs = [parse_leg(l) for l in str(strat['legs']).split(';')]
    # For each leg, sum PnL for this strategy's date and leg
    pnl_booked = 0.0
    for leg in legs:
        if leg['strike'] is None or leg['option_type'] is None:
            continue
        leg_pnl = pnl_df[
            (pnl_df['date'] == strat['date']) &
            (pnl_df['strike'] == leg['strike']) &
            (pnl_df['option_type'] == leg['option_type'])
        ]['pnl'].sum()
        pnl_booked += leg_pnl
    results.append({
        'date': strat['date'],
        'strategy_id': strat['strategy_id'],
        'strategy_type': strat['strategy_type'],
        'active_legs': strat['legs'],
        'pnl_booked': round(pnl_booked, 2)
    })

final_df = pd.DataFrame(results)
final_df.to_csv('strategy_pnl_booked.csv', index=False)
print("PnL booked only for exited/expired strategies. Sample:")
print(final_df[final_df['pnl_booked'] != 0].head(10))
