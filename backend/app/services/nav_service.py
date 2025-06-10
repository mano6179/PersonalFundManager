from typing import List
from backend.app.models.nav import FundEntry

def calculate_fund_state(entries: List[FundEntry]) -> List[FundEntry]:
    nav_peak = 0.0
    for i, entry in enumerate(entries):
        if i == 0:
            # First entry - initialize with starting values
            entry.fund_value = entry.funds_in_out
            entry.outstanding_units = 1000 if entry.outstanding_units is None else entry.outstanding_units
            entry.nav = entry.fund_value / entry.outstanding_units
        else:
            prev = entries[i-1]
            entry.previous_nav = prev.nav
            
            # Calculate fund value based on previous state plus P&L
            net_pl = entry.realised_pnl - entry.charges
            entry.fund_value = prev.nav * prev.outstanding_units + net_pl
            
            # Handle funds in/out
            if entry.funds_in_out != 0:
                if entry.funds_in_out > 0:
                    # Issue new units when funds are added
                    new_units = entry.funds_in_out / prev.nav
                    entry.outstanding_units = prev.outstanding_units + new_units
                    entry.fund_value += entry.funds_in_out
                else:
                    # Handle redemptions
                    units_redeemed = abs(entry.funds_in_out) / prev.nav
                    entry.outstanding_units = prev.outstanding_units - units_redeemed
                    entry.fund_value += entry.funds_in_out
            else:
                entry.outstanding_units = prev.outstanding_units
            
            # Calculate new NAV
            entry.nav = entry.fund_value / entry.outstanding_units
        
        # Track NAV peak and drawdown
        nav_peak = max(nav_peak, entry.nav)
        entry.nav_peak = nav_peak
        entry.nav_drawdown = round(((nav_peak - entry.nav) / nav_peak) * 100, 2) if nav_peak > 0 else 0.0
    
    return entries