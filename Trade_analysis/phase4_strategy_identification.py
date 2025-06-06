import pandas as pd
import numpy as np
from collections import defaultdict

# Load the daily active positions from Phase 3
positions = pd.read_csv('phase3_daily_active_positions.csv', parse_dates=['date', 'expiry'])

def make_strategy_id(date, underlying, expiry, strategy_type, legs):
    legs_str = '|'.join([f"{s}_{t}_{np.sign(q)}" for s, t, q in legs])
    return f"{date.strftime('%Y%m%d')}_{underlying}_{expiry}_{strategy_type}_{legs_str}"

def detect_strategies(df):
    strategies = []
    # Group by expiry, underlying
    for (expiry, underlying), group in df.groupby(['expiry', 'underlying']):
        group = group.sort_values(['option_type', 'strike'])
        legs = group.to_dict('records')
        leg_used = [False] * len(legs)

        # 1. Iron Condor (4 legs: 2P+2C, all same expiry, proper strikes/directions)
        for i in range(len(legs)):
            for j in range(i+1, len(legs)):
                for k in range(j+1, len(legs)):
                    for l in range(k+1, len(legs)):
                        idxs = [i, j, k, l]
                        if any(leg_used[x] for x in idxs):
                            continue
                        subset = [legs[x] for x in idxs]
                        types = [x['option_type'] for x in subset]
                        qtys = [x['quantity'] for x in subset]
                        strikes = [x['strike'] for x in subset]
                        if types.count('CE') == 2 and types.count('PE') == 2 and len(set(strikes)) == 4:
                            ce_legs = [x for x in subset if x['option_type'] == 'CE']
                            pe_legs = [x for x in subset if x['option_type'] == 'PE']
                            ce_legs = sorted(ce_legs, key=lambda x: x['strike'])
                            pe_legs = sorted(pe_legs, key=lambda x: x['strike'], reverse=True)
                            # Check for correct vertical spread structure
                            if (ce_legs[0]['quantity'] == -ce_legs[1]['quantity'] and
                                pe_legs[0]['quantity'] == -pe_legs[1]['quantity']):
                                strat_legs = [(x['strike'], x['option_type'], x['quantity']) for x in subset]
                                sid = make_strategy_id(subset[0]['date'], underlying, expiry, 'Iron Condor', strat_legs)
                                for x in idxs: leg_used[x] = True
                                strategies.append({
                                    'date': subset[0]['date'],
                                    'underlying': underlying,
                                    'expiry': expiry,
                                    'strategy_type': 'Iron Condor',
                                    'legs': strat_legs,
                                    'strategy_id': sid
                                })

        # 2. Vertical Spreads (Bull/Bear Call/Put) for unused legs
        for i in range(len(legs)):
            for j in range(i+1, len(legs)):
                if leg_used[i] or leg_used[j]:
                    continue
                l1, l2 = legs[i], legs[j]
                if (l1['option_type'] == l2['option_type'] and
                    l1['strike'] != l2['strike'] and
                    l1['quantity'] == -l2['quantity']):
                    # Classify spread
                    if l1['option_type'] == 'CE':
                        # Bull Call: Long lower strike, Short higher strike
                        if l1['strike'] < l2['strike'] and l1['quantity'] > 0:
                            spread_type = 'Bull Call Spread'
                        elif l1['strike'] > l2['strike'] and l1['quantity'] < 0:
                            spread_type = 'Bull Call Spread'
                        else:
                            spread_type = 'Bear Call Spread'
                    else:
                        # Bull Put: Long higher strike, Short lower strike
                        if l1['strike'] > l2['strike'] and l1['quantity'] > 0:
                            spread_type = 'Bull Put Spread'
                        elif l1['strike'] < l2['strike'] and l1['quantity'] < 0:
                            spread_type = 'Bull Put Spread'
                        else:
                            spread_type = 'Bear Put Spread'
                    strat_legs = [(l1['strike'], l1['option_type'], l1['quantity']),
                                  (l2['strike'], l2['option_type'], l2['quantity'])]
                    sid = make_strategy_id(l1['date'], underlying, expiry, spread_type, strat_legs)
                    leg_used[i] = leg_used[j] = True
                    strategies.append({
                        'date': l1['date'],
                        'underlying': underlying,
                        'expiry': expiry,
                        'strategy_type': spread_type,
                        'legs': strat_legs,
                        'strategy_id': sid
                    })

        # 3. Straddle (2 legs, same expiry, same strike, CE+PE, same direction)
        for i in range(len(legs)):
            for j in range(i+1, len(legs)):
                if leg_used[i] or leg_used[j]:
                    continue
                l1, l2 = legs[i], legs[j]
                if (l1['strike'] == l2['strike'] and
                    l1['option_type'] != l2['option_type'] and
                    l1['quantity'] == l2['quantity']):
                    strat_legs = [(l1['strike'], l1['option_type'], l1['quantity']),
                                  (l2['strike'], l2['option_type'], l2['quantity'])]
                    sid = make_strategy_id(l1['date'], underlying, expiry, 'Straddle', strat_legs)
                    leg_used[i] = leg_used[j] = True
                    strategies.append({
                        'date': l1['date'],
                        'underlying': underlying,
                        'expiry': expiry,
                        'strategy_type': 'Straddle',
                        'legs': strat_legs,
                        'strategy_id': sid
                    })
        # 4. Strangle (2 legs, same expiry, CE+PE, diff strikes, same direction)
        for i in range(len(legs)):
            for j in range(i+1, len(legs)):
                if leg_used[i] or leg_used[j]:
                    continue
                l1, l2 = legs[i], legs[j]
                if (l1['option_type'] != l2['option_type'] and
                    l1['strike'] != l2['strike'] and
                    l1['quantity'] == l2['quantity']):
                    strat_legs = [(l1['strike'], l1['option_type'], l1['quantity']),
                                  (l2['strike'], l2['option_type'], l2['quantity'])]
                    sid = make_strategy_id(l1['date'], underlying, expiry, 'Strangle', strat_legs)
                    leg_used[i] = leg_used[j] = True
                    strategies.append({
                        'date': l1['date'],
                        'underlying': underlying,
                        'expiry': expiry,
                        'strategy_type': 'Strangle',
                        'legs': strat_legs,
                        'strategy_id': sid
                    })

        # 5. Single legs (unmatched) - classify as Naked Call/Put Buy/Sell
        for ix, leg in enumerate(legs):
            if not leg_used[ix]:
                strat_legs = [(leg['strike'], leg['option_type'], leg['quantity'])]
                # Classification:
                if leg['option_type'] == 'CE':
                    if leg['quantity'] > 0:
                        single_type = 'Naked Call Buy'
                    else:
                        single_type = 'Naked Call Sell'
                elif leg['option_type'] == 'PE':
                    if leg['quantity'] > 0:
                        single_type = 'Naked Put Buy'
                    else:
                        single_type = 'Naked Put Sell'
                else:
                    single_type = 'Single Leg'
                sid = make_strategy_id(leg['date'], underlying, expiry, single_type, strat_legs)
                strategies.append({
                    'date': leg['date'],
                    'underlying': underlying,
                    'expiry': expiry,
                    'strategy_type': single_type,
                    'legs': strat_legs,
                    'strategy_id': sid
                })

    # Calendar spreads: group by underlying, strike, option_type, and direction, but different expiry
    cal_group = df.groupby(['underlying', 'strike', 'option_type', 'quantity'])
    for (underlying, strike, option_type, quantity), group in cal_group:
        if group['expiry'].nunique() > 1:
            exp_list = group['expiry'].unique()
            strat_legs = [(strike, option_type, quantity, e) for e in exp_list]
            sid = f"CAL_{underlying}_{strike}_{option_type}_{quantity}_" + "_".join([str(e) for e in exp_list])
            date = group['date'].min()
            strategies.append({
                'date': date,
                'underlying': underlying,
                'expiry': '|'.join([str(e) for e in exp_list]),
                'strategy_type': 'Calendar Spread',
                'legs': strat_legs,
                'strategy_id': sid
            })
    return strategies

# Process all days
all_strategies = []
for date, day_df in positions.groupby('date'):
    day_strats = detect_strategies(day_df)
    all_strategies.extend(day_strats)

# Convert to DataFrame for output
strat_df = pd.DataFrame(all_strategies)
strat_df['legs'] = strat_df['legs'].apply(lambda x: ";".join([f"{s}-{t}-{q}" if len(l)==3 else f"{s}-{t}-{q}-{e}" for l in x for s,t,q,*e in [l]]))

# Save to CSV
strat_df.to_csv('phase4_daily_strategies.csv', index=False)
print("Phase 4 complete: Daily strategies saved to 'phase4_daily_strategies.csv'.")
print(strat_df.head())
