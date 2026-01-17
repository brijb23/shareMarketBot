"""
PHASE 19: Capital Invariant Monitor (NSE Calibrated)

Continuously monitor live capital risk using Indian equity behavior.
Hard kill-switches for capital protection.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple


class CapitalInvariantMonitor:
    """Monitor capital safety with NSE-calibrated kill-switches."""
    
    # NSE-CALIBRATED HARD KILL-SWITCHES (Non-negotiable)
    MAX_DRAWDOWN_LIMIT = -3.0  # Halt if DD >= -3.0%
    ROLLING_LOSS_LIMIT = 5     # Halt if 5 consecutive losses
    SINGLE_TRADE_LOSS_LIMIT = 2.0  # Halt if any loss > 2.0%
    
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.trades = []
        self.capital_history = [initial_capital]
        self.killswitch_events = []
        self.invariant_violations = []
        self.is_halted = False
        self.halt_reason = None
        
    def record_trade(self, trade_id: int, symbol: str, entry_price: float, 
                    exit_price: float, qty: int, pnl_pct: float, 
                    confidence: float, entry_time: str):
        """Record a live trade."""
        if self.is_halted:
            self.log_halt_violation(trade_id, "System halted")
            return False
        
        # Calculate P&L
        capital_before = self.capital_history[-1]
        pnl_dollars = capital_before * 2.0 / 100 * pnl_pct / 100  # 2% fixed sizing
        capital_after = capital_before + pnl_dollars
        
        # Check kill-switches BEFORE recording trade
        violations = self._check_kill_switches(pnl_pct, capital_before, capital_after)
        
        # Record trade
        self.trades.append({
            'trade_id': trade_id,
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'qty': qty,
            'pnl_pct': pnl_pct,
            'pnl_dollars': pnl_dollars,
            'capital_before': capital_before,
            'capital_after': capital_after,
            'confidence': confidence,
            'entry_time': entry_time,
            'exit_time': datetime.now().isoformat(),
            'violations': violations,
        })
        
        self.capital_history.append(capital_after)
        
        # If violations exist, halt
        if violations:
            self._trigger_halt(violations)
            return False
        
        return True
    
    def _check_kill_switches(self, pnl_pct: float, capital_before: float, 
                            capital_after: float) -> List[str]:
        """Check all kill-switch conditions."""
        violations = []
        
        # Kill-switch 1: Single trade loss > 2.0%
        if pnl_pct < -self.SINGLE_TRADE_LOSS_LIMIT:
            violations.append(f"SINGLE_TRADE_LOSS: {pnl_pct:.3f}% exceeds {self.SINGLE_TRADE_LOSS_LIMIT}% limit")
        
        # Kill-switch 2: Maximum drawdown
        equity = np.array(self.capital_history + [capital_after])
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity[-1] - running_max[-1]) / running_max[-1] * 100
        if drawdown <= self.MAX_DRAWDOWN_LIMIT:
            violations.append(f"MAX_DRAWDOWN: {drawdown:.3f}% exceeds {self.MAX_DRAWDOWN_LIMIT}% limit")
        
        # Kill-switch 3: Rolling 5-trade loss streak
        if len(self.trades) >= self.ROLLING_LOSS_LIMIT:
            recent_pnls = [t['pnl_pct'] for t in self.trades[-self.ROLLING_LOSS_LIMIT:]]
            if all(p < 0 for p in recent_pnls):
                violations.append(f"ROLLING_LOSS_STREAK: {self.ROLLING_LOSS_LIMIT} consecutive losses detected")
        
        return violations
    
    def _trigger_halt(self, violations: List[str]):
        """Trigger system halt."""
        self.is_halted = True
        self.halt_reason = " | ".join(violations)
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'trigger': self.halt_reason,
            'capital': self.capital_history[-1],
            'trades_executed': len(self.trades),
        }
        self.killswitch_events.append(event)
    
    def log_halt_violation(self, trade_id: int, reason: str):
        """Log attempt to execute while halted."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'trade_id': trade_id,
            'reason': reason,
            'status': 'REJECTED',
        }
        self.invariant_violations.append(event)
    
    def get_capital_curve(self) -> pd.DataFrame:
        """Return capital curve."""
        return pd.DataFrame({
            'trade_num': range(len(self.capital_history)),
            'capital': self.capital_history,
        })
    
    def get_drawdown_stats(self) -> Dict:
        """Calculate drawdown statistics."""
        equity = np.array(self.capital_history)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max * 100
        
        return {
            'current_drawdown': float(drawdown[-1]),
            'max_drawdown': float(np.min(drawdown)),
            'drawdown_limit': self.MAX_DRAWDOWN_LIMIT,
            'status': 'SAFE' if np.min(drawdown) > self.MAX_DRAWDOWN_LIMIT else 'VIOLATED',
        }
    
    def export_state(self, filepath: str):
        """Export monitor state to JSON."""
        state = {
            'timestamp': datetime.now().isoformat(),
            'is_halted': self.is_halted,
            'halt_reason': self.halt_reason,
            'trades': self.trades,
            'capital_history': self.capital_history,
            'killswitch_events': self.killswitch_events,
            'invariant_violations': self.invariant_violations,
            'drawdown_stats': self.get_drawdown_stats(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def get_status_summary(self) -> Dict:
        """Get brief status summary."""
        if len(self.capital_history) < 2:
            return {'status': 'INITIALIZING', 'trades': 0}
        
        equity = np.array(self.capital_history)
        current_capital = equity[-1]
        max_capital = np.max(equity)
        drawdown = (current_capital - max_capital) / max_capital * 100
        total_return = (current_capital - self.initial_capital) / self.initial_capital * 100
        
        return {
            'status': 'HALTED' if self.is_halted else 'ACTIVE',
            'trades_count': len(self.trades),
            'current_capital': float(current_capital),
            'total_return': float(total_return),
            'current_drawdown': float(drawdown),
            'max_drawdown_threshold': self.MAX_DRAWDOWN_LIMIT,
            'halt_reason': self.halt_reason,
        }


if __name__ == '__main__':
    # Demo
    monitor = CapitalInvariantMonitor()
    
    print("Capital Invariant Monitor (NSE Calibrated)")
    print("="*60)
    print(f"Kill-switch 1: Single trade loss > {monitor.SINGLE_TRADE_LOSS_LIMIT}%")
    print(f"Kill-switch 2: Max drawdown >= {monitor.MAX_DRAWDOWN_LIMIT}%")
    print(f"Kill-switch 3: Rolling {monitor.ROLLING_LOSS_LIMIT}-trade loss streak")
    print()
    
    # Simulate trades
    trades = [
        (+0.5, 'INFY.NS', 1700, 1708, 100, 80),
        (+0.3, 'TCS.NS', 4000, 4012, 50, 75),
        (-1.2, 'BAJAJ.NS', 8500, 8398, 10, 45),
        (+0.8, 'HDFCBANK.NS', 1600, 1613, 100, 70),
        (-0.6, 'RELIANCE.NS', 2100, 2087, 50, 50),
    ]
    
    for i, (pnl_pct, symbol, entry, exit, qty, conf) in enumerate(trades, 1):
        success = monitor.record_trade(i, symbol, entry, exit, qty, pnl_pct, conf, 
                                      f"2025-01-09 09:{i*5:02d}:00")
        status = monitor.get_status_summary()
        print(f"Trade {i}: {symbol} | P&L: {pnl_pct:+.2f}% | Status: {status['status']}")
    
    print()
    print(monitor.get_drawdown_stats())
    
    # Export
    monitor.export_state('capital_invariant_monitor_demo.json')
    print("\n✓ Demo state exported to capital_invariant_monitor_demo.json")
