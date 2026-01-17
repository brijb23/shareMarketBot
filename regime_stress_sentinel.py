"""
PHASE 19: Regime Stress Sentinel (Indian Market Regimes)

Detect out-of-sample Indian market regimes.
Label trades, increase logging, do NOT change execution logic.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class RegimeStressSentinel:
    """Detect and alert on Indian market regime changes."""
    
    # NSE-calibrated regime thresholds
    ATR_NORMAL_RANGE = (1.5, 3.0)  # ATR% for normal conditions
    GAP_FREQUENCY_THRESHOLD = 0.15  # >15% gaps is unusual
    CORRELATION_SPIKE_THRESHOLD = 0.85  # Cross-stock correlation
    TREND_PERSISTENCE_THRESHOLD = 8  # Max consecutive same-direction moves
    
    def __init__(self, lookback_periods: int = 20):
        self.lookback = lookback_periods
        self.trades = []
        self.ohlc_data = {}  # symbol -> price data
        self.regime_labels = []
        self.stress_events = []
        self.current_regime = 'NORMAL'
        
    def record_trade(self, trade_id: int, symbol: str, entry_price: float,
                    exit_price: float, high_price: float, low_price: float,
                    entry_datetime: str):
        """Record trade with price data for regime analysis."""
        
        self.trades.append({
            'trade_id': trade_id,
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'high_price': high_price,
            'low_price': low_price,
            'entry_datetime': entry_datetime,
            'regime_label': self.current_regime,
        })
        
        # Track OHLC
        if symbol not in self.ohlc_data:
            self.ohlc_data[symbol] = []
        
        self.ohlc_data[symbol].append({
            'datetime': entry_datetime,
            'open': entry_price,
            'high': high_price,
            'low': low_price,
            'close': exit_price,
        })
    
    def analyze_regime(self) -> Dict:
        """Analyze current market regime."""
        
        regime_analysis = {
            'timestamp': datetime.now().isoformat(),
            'current_regime': self.current_regime,
            'metrics': {},
            'triggers': [],
        }
        
        if len(self.trades) < self.lookback:
            regime_analysis['status'] = 'INSUFFICIENT_DATA'
            return regime_analysis
        
        # Get recent trades
        recent = self.trades[-self.lookback:]
        
        # Metric 1: ATR regime (volatility)
        atr_pcts = []
        for trade in recent:
            atr = (trade['high_price'] - trade['low_price']) / trade['entry_price'] * 100
            atr_pcts.append(atr)
        
        avg_atr = np.mean(atr_pcts)
        regime_analysis['metrics']['atr_pct'] = float(avg_atr)
        
        if avg_atr < self.ATR_NORMAL_RANGE[0]:
            regime_analysis['triggers'].append({
                'type': 'LOW_VOLATILITY',
                'atr_pct': float(avg_atr),
                'threshold': self.ATR_NORMAL_RANGE[0],
                'severity': 'LOW',
            })
        elif avg_atr > self.ATR_NORMAL_RANGE[1]:
            regime_analysis['triggers'].append({
                'type': 'HIGH_VOLATILITY',
                'atr_pct': float(avg_atr),
                'threshold': self.ATR_NORMAL_RANGE[1],
                'severity': 'HIGH',
            })
        
        # Metric 2: Gap frequency (India-specific)
        gaps = []
        for i in range(1, len(recent)):
            prev_close = recent[i-1]['exit_price']
            curr_open = recent[i]['entry_price']
            gap_pct = abs(curr_open - prev_close) / prev_close * 100
            if gap_pct > 0.5:  # >0.5% gap
                gaps.append(gap_pct)
        
        gap_frequency = len(gaps) / len(recent)
        regime_analysis['metrics']['gap_frequency'] = float(gap_frequency)
        
        if gap_frequency > self.GAP_FREQUENCY_THRESHOLD:
            regime_analysis['triggers'].append({
                'type': 'HIGH_GAP_FREQUENCY',
                'frequency': float(gap_frequency),
                'threshold': self.GAP_FREQUENCY_THRESHOLD,
                'severity': 'MEDIUM',
            })
        
        # Metric 3: Trend persistence
        returns = []
        for trade in recent:
            ret = (trade['exit_price'] - trade['entry_price']) / trade['entry_price']
            returns.append(ret)
        
        return_signs = np.sign(returns)
        max_streak = self._max_consecutive(return_signs)
        regime_analysis['metrics']['trend_persistence'] = int(max_streak)
        
        if max_streak > self.TREND_PERSISTENCE_THRESHOLD:
            regime_analysis['triggers'].append({
                'type': 'STRONG_TREND',
                'persistence': int(max_streak),
                'threshold': self.TREND_PERSISTENCE_THRESHOLD,
                'severity': 'MEDIUM',
            })
        
        # Metric 4: Cross-stock correlation
        if len(self.ohlc_data) > 1:
            correlations = []
            symbols = list(self.ohlc_data.keys())
            
            for i in range(len(symbols)):
                for j in range(i+1, len(symbols)):
                    sym1_returns = []
                    sym2_returns = []
                    
                    data1 = self.ohlc_data[symbols[i]][-self.lookback:]
                    data2 = self.ohlc_data[symbols[j]][-self.lookback:]
                    
                    min_len = min(len(data1), len(data2))
                    
                    for k in range(min_len):
                        r1 = (data1[k]['close'] - data1[k]['open']) / data1[k]['open']
                        r2 = (data2[k]['close'] - data2[k]['open']) / data2[k]['open']
                        sym1_returns.append(r1)
                        sym2_returns.append(r2)
                    
                    if len(sym1_returns) > 1:
                        corr = np.corrcoef(sym1_returns, sym2_returns)[0, 1]
                        if not np.isnan(corr):
                            correlations.append(corr)
            
            if correlations:
                avg_corr = np.mean(correlations)
                regime_analysis['metrics']['avg_cross_correlation'] = float(avg_corr)
                
                if avg_corr > self.CORRELATION_SPIKE_THRESHOLD:
                    regime_analysis['triggers'].append({
                        'type': 'CORRELATION_SPIKE',
                        'correlation': float(avg_corr),
                        'threshold': self.CORRELATION_SPIKE_THRESHOLD,
                        'severity': 'HIGH',
                    })
        
        # Determine regime label
        high_severity = [t for t in regime_analysis['triggers'] if t['severity'] == 'HIGH']
        
        if high_severity:
            self.current_regime = 'OUT_OF_SAMPLE'
            regime_analysis['regime_determination'] = 'OUT_OF_SAMPLE'
        else:
            self.current_regime = 'NORMAL'
            regime_analysis['regime_determination'] = 'NORMAL'
        
        # Log stress events
        if regime_analysis['triggers']:
            stress_event = {
                'timestamp': datetime.now().isoformat(),
                'regime': self.current_regime,
                'triggers': regime_analysis['triggers'],
                'trade_count': len(self.trades),
            }
            self.stress_events.append(stress_event)
        
        return regime_analysis
    
    def _max_consecutive(self, arr: np.ndarray) -> int:
        """Find max consecutive non-zero elements."""
        if len(arr) == 0:
            return 0
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(arr)):
            if arr[i] == arr[i-1] and arr[i] != 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def get_regime_summary(self) -> Dict:
        """Get regime status summary."""
        
        return {
            'current_regime': self.current_regime,
            'total_trades': len(self.trades),
            'stress_events': len(self.stress_events),
            'recent_stress': self.stress_events[-1] if self.stress_events else None,
        }
    
    def export_regime_log(self, filepath: str):
        """Export regime analysis to JSON."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_trades': len(self.trades),
            'current_regime': self.current_regime,
            'stress_events': self.stress_events,
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)


if __name__ == '__main__':
    sentinel = RegimeStressSentinel(lookback_periods=20)
    
    print("Regime Stress Sentinel (Indian Market Regimes)")
    print("="*60)
    print(f"ATR normal range: {sentinel.ATR_NORMAL_RANGE}%")
    print(f"Gap frequency threshold: {sentinel.GAP_FREQUENCY_THRESHOLD*100:.1f}%")
    print(f"Trend persistence threshold: {sentinel.TREND_PERSISTENCE_THRESHOLD}")
    print()
    
    # Simulate trades (mostly normal with some stress)
    for i in range(1, 26):
        entry = 100 + np.random.randn() * 2
        high = entry + abs(np.random.randn() * 2)
        low = entry - abs(np.random.randn() * 2)
        exit_p = entry + np.random.randn() * 1.5
        
        # Introduce stress after trade 20
        if i > 20:
            high = entry + abs(np.random.randn() * 5)  # Higher ATR
            low = entry - abs(np.random.randn() * 5)
        
        sentinel.record_trade(i, f'STOCK{i}.NS', entry, exit_p, high, low,
                            f"2025-01-09 09:{i*2:02d}:00")
    
    # Run analysis
    result = sentinel.analyze_regime()
    
    print(f"Regime: {result['current_regime']}")
    print(f"Metrics:")
    for metric, value in result['metrics'].items():
        print(f"  {metric}: {value:.3f}")
    
    print(f"\nTriggers: {len(result['triggers'])}")
    for trigger in result['triggers']:
        print(f"  - {trigger['type']}: {trigger['severity']}")
    
    print()
    summary = sentinel.get_regime_summary()
    print(f"Stress events: {summary['stress_events']}")
    
    # Export
    sentinel.export_regime_log('regime_stress_sentinel_demo.json')
    print("\n✓ Demo log exported to regime_stress_sentinel_demo.json")
