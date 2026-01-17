"""
Generate Phase 17.6 backtest trades by applying uncertainty-aware suppression
to Phase 17 trade decisions.

This creates synthetic Phase 17.6 trades for Phase 18 validation by:
1. Loading Phase 17 trades
2. Applying Phase 17.6 BUY-only-under-FULL-data logic
3. Converting BUYs with partial data to WAITs
4. Exporting Phase 17.6 version

CONSTRAINT: No logic changes, just application of Phase 17.6 decision rules
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import random

def generate_phase176_trades(input_path: Path, output_path: Path):
    """Generate Phase 17.6 trades from Phase 17."""
    
    # Load Phase 17 trades
    with open(input_path, 'r') as f:
        phase17_trades = json.load(f)
    
    print(f"Loaded {len(phase17_trades)} Phase 17 trades")
    
    # Apply Phase 17.6 suppression logic
    phase176_trades = []
    suppression_count = 0
    
    for trade in phase17_trades:
        # Create copy for Phase 17.6
        phase176_trade = trade.copy()
        
        # Apply Phase 17.6: BUY only if FULL data
        # For test: Simulate 30% of analyses have PARTIAL_FUNDAMENTAL data
        if trade.get('phase17_decision') == 'BUY':
            # Random assignment: 70% FULL, 30% PARTIAL_FUNDAMENTAL
            has_full_data = random.random() < 0.70
            
            if has_full_data:
                phase176_trade['phase176_decision'] = 'BUY'
                phase176_trade['data_confidence_state'] = 'FULL'
            else:
                phase176_trade['data_confidence_state'] = 'PARTIAL_FUNDAMENTAL'
                # Suppress: BUY -> WAIT
                phase176_trade['phase176_decision'] = 'WAIT'
                phase176_trade['phase176_was_suppressed'] = True
                phase176_trade['phase176_suppression_reason'] = 'PARTIAL_FUNDAMENTAL_DATA'
                # Clear trade details (entry not executed)
                phase176_trade['entry_price'] = None
                phase176_trade['stop_loss'] = None
                phase176_trade['target_price'] = None
                phase176_trade['exit_price'] = None
                phase176_trade['exit_date'] = None
                phase176_trade['exit_reason'] = 'SUPPRESSED_PARTIAL_DATA'
                phase176_trade['final_pnl_pct'] = None
                phase176_trade['holding_period_days'] = None
                phase176_trade['max_adverse_excursion'] = None
                phase176_trade['max_favorable_excursion'] = None
                suppression_count += 1
                
                # Apply confidence cap (Phase 17.6)
                raw_conf = trade.get('phase17_confidence_after_cal', 50.0)
                if raw_conf > 62.0:
                    # Cap at PARTIAL_FUNDAMENTAL ceiling
                    phase176_trade['phase176_confidence_after_cap'] = 62.0
        else:
            # Not a BUY - mark as FULL (no suppression applies to HOLD/WAIT/SELL)
            phase176_trade['phase176_decision'] = trade.get('phase17_decision')
            phase176_trade['phase176_was_suppressed'] = False
            phase176_trade['phase176_suppression_reason'] = None
            phase176_trade['data_confidence_state'] = 'FULL'
            phase176_trade['phase176_confidence_after_cap'] = trade.get('phase17_confidence_after_cal', 50.0)
        
        phase176_trades.append(phase176_trade)
    
    # Export Phase 17.6 trades
    with open(output_path, 'w') as f:
        json.dump(phase176_trades, f, indent=2)
    
    print(f"Generated {len(phase176_trades)} Phase 17.6 trades")
    print(f"  - BUYs suppressed to WAIT: {suppression_count}")
    print(f"  Saved to: {output_path.name}")

if __name__ == '__main__':
    base_path = Path(__file__).parent
    
    # Generate from Phase 17
    generate_phase176_trades(
        base_path / "phase17_backtest_trades.json",
        base_path / "phase17_6_backtest_trades.json"
    )
    
    print("\nPhase 17.6 trades ready for Phase 18 validation")
