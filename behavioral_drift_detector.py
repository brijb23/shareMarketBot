"""
PHASE 19: Behavioral Drift Detector (Phase 18.2 Baseline Comparison)

Detect logic drift by comparing live NSE behavior vs Phase 18.2 envelopes.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class BehavioralDriftDetector:
    """Detect behavioral deviations from Phase 18.2 baseline."""
    
    # Phase 18.2 baseline envelope (from backtest)
    BASELINE = {
        'trades_per_week': (10, 30),  # NSE trading week
        'holding_duration_hours': (1, 48),  # Sessions
        'mae_pct': (-2.5, -0.1),  # Max adverse excursion
        'mfe_pct': (0.1, 5.0),  # Max favorable excursion
        'mae_mfe_ratio': (0.2, 0.8),  # Recovery efficiency
        'win_rate': (0.55, 0.65),  # 60% baseline
        'entry_weekday_skew': 0.25,  # Max deviation from uniform
    }
    
    def __init__(self):
        self.trades = []
        self.drift_events = []
        self.metric_history = []
        self.drift_threshold = 2.0  # 2-sigma threshold
        self.persistence_threshold = 10  # Flag after 10 deviations
        self.current_drift_streak = 0
        
    def record_trade(self, trade_id: int, symbol: str, entry_price: float, 
                    exit_price: float, mae_pct: float, mfe_pct: float,
                    pnl_pct: float, entry_weekday: str, entry_datetime: str):
        """Record trade for drift detection."""
        
        holding_duration = self._estimate_holding_duration(entry_datetime)
        
        # Ensure values are scalars, not Series
        mae_val = float(mae_pct) if hasattr(mae_pct, '__float__') else mae_pct
        mfe_val = float(mfe_pct) if hasattr(mfe_pct, '__float__') else mfe_pct
        
        self.trades.append({
            'trade_id': trade_id,
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl_pct': pnl_pct,
            'mae_pct': mae_val,
            'mfe_pct': mfe_val,
            'mae_mfe_ratio': abs(mae_val / mfe_val) if mfe_val != 0 else 0,
            'holding_duration_hours': holding_duration,
            'entry_weekday': entry_weekday,
            'entry_datetime': entry_datetime,
        })
    
    def _estimate_holding_duration(self, entry_time_str: str) -> float:
        """Estimate holding duration in hours (assuming 1-48 hours typical)."""
        # Simplified: assume 4-hour average for demo
        return 4.0
    
    def analyze_drift(self, window_size: int = 20) -> Dict:
        """Analyze behavioral drift vs Phase 18.2 baseline."""
        
        if len(self.trades) < window_size:
            return {'status': 'INSUFFICIENT_DATA', 'trades': len(self.trades)}
        
        # Get recent trades
        recent_trades = self.trades[-window_size:]
        df = pd.DataFrame(recent_trades)
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'window': len(recent_trades),
            'deviations': [],
        }
        
        # Check each metric vs baseline
        deviations = self._check_metric('trades_per_week', self._calc_trades_per_week(), 
                                        self.BASELINE['trades_per_week'])
        if deviations: metrics['deviations'].append(deviations)
        
        deviations = self._check_metric('holding_duration', df['holding_duration_hours'].mean(),
                                        self.BASELINE['holding_duration_hours'])
        if deviations: metrics['deviations'].append(deviations)
        
        deviations = self._check_metric('mae_pct', df['mae_pct'].mean(),
                                        self.BASELINE['mae_pct'])
        if deviations: metrics['deviations'].append(deviations)
        
        deviations = self._check_metric('mfe_pct', df['mfe_pct'].mean(),
                                        self.BASELINE['mfe_pct'])
        if deviations: metrics['deviations'].append(deviations)
        
        deviations = self._check_metric('win_rate', (df['pnl_pct'] > 0).sum() / len(df),
                                        self.BASELINE['win_rate'])
        if deviations: metrics['deviations'].append(deviations)
        
        # Check weekday clustering
        weekday_skew = self._check_weekday_clustering(df)
        if weekday_skew > self.BASELINE['entry_weekday_skew']:
            metrics['deviations'].append({
                'metric': 'entry_weekday_skew',
                'value': weekday_skew,
                'baseline_range': f"<{self.BASELINE['entry_weekday_skew']}",
                'status': 'DEVIATION',
            })
        
        # Update drift streak
        if metrics['deviations']:
            self.current_drift_streak += 1
        else:
            self.current_drift_streak = 0
        
        metrics['drift_streak'] = self.current_drift_streak
        
        # Flag if persistent
        if self.current_drift_streak >= self.persistence_threshold:
            metrics['alert'] = f"DRIFT_ALERT: {self.current_drift_streak} consecutive windows with deviations"
            self.drift_events.append({
                'timestamp': datetime.now().isoformat(),
                'drift_type': 'PERSISTENT_DEVIATION',
                'streak': self.current_drift_streak,
                'deviations': metrics['deviations'],
            })
        
        self.metric_history.append(metrics)
        return metrics
    
    def _check_metric(self, name: str, value: float, baseline_range: Tuple) -> Dict | None:
        """Check if metric deviates from baseline."""
        min_val, max_val = baseline_range
        
        if value < min_val or value > max_val:
            # Calculate deviation in sigmas (estimate 10% as 1 sigma)
            range_size = max_val - min_val
            sigma_estimate = range_size / 4  # Rough estimate
            if sigma_estimate == 0:
                sigma_estimate = 0.01
            
            if value < min_val:
                deviation_sigma = (min_val - value) / sigma_estimate
            else:
                deviation_sigma = (value - max_val) / sigma_estimate
            
            return {
                'metric': name,
                'value': float(value),
                'baseline_range': (min_val, max_val),
                'deviation_sigma': float(deviation_sigma),
                'status': 'DEVIATION' if deviation_sigma > self.drift_threshold else 'WARNING',
            }
        
        return None
    
    def _calc_trades_per_week(self) -> float:
        """Calculate trades per NSE week."""
        if len(self.trades) < 5:
            return len(self.trades)
        
        recent = self.trades[-20:]
        # Assume recent trades span ~2 weeks
        return len(recent) / 2
    
    def _check_weekday_clustering(self, df: pd.DataFrame) -> float:
        """Check if entries cluster on certain weekdays."""
        weekday_counts = df['entry_weekday'].value_counts()
        expected_freq = 1.0 / 5  # Uniform across 5 NSE weekdays
        
        if len(weekday_counts) == 0:
            return 0
        
        # Chi-square style deviation
        max_freq = weekday_counts.max() / len(df)
        skew = max_freq - expected_freq
        return float(skew)
    
    def get_drift_summary(self) -> Dict:
        """Get drift status summary."""
        total_deviations = len(self.drift_events)
        
        return {
            'total_trades': len(self.trades),
            'drift_events': total_deviations,
            'current_drift_streak': self.current_drift_streak,
            'status': 'DRIFTING' if self.current_drift_streak >= self.persistence_threshold else 'NORMAL',
            'last_analysis': self.metric_history[-1] if self.metric_history else None,
        }
    
    def export_drift_log(self, filepath: str):
        """Export drift events to JSON."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_trades': len(self.trades),
            'drift_events': self.drift_events,
            'metric_history': self.metric_history,
            'current_streak': self.current_drift_streak,
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)


if __name__ == '__main__':
    detector = BehavioralDriftDetector()
    
    print("Behavioral Drift Detector (Phase 18.2 Baseline)")
    print("="*60)
    print(f"Win rate baseline: {detector.BASELINE['win_rate']}")
    print(f"Holding duration baseline: {detector.BASELINE['holding_duration_hours']} hours")
    print(f"Drift threshold: {detector.drift_threshold} sigma")
    print(f"Persistence threshold: {detector.persistence_threshold} trades")
    print()
    
    # Simulate trades (normal baseline)
    for i in range(1, 26):
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
        weekday = weekdays[(i-1) % 5]
        
        mae = -np.random.uniform(0.5, 2.0)
        mfe = np.random.uniform(0.5, 4.0)
        pnl = 0.5 if i % 2 == 0 else -0.3  # 50% win rate drift toward 60%
        
        detector.record_trade(i, f'STOCK{i}.NS', 100, 101, mae, mfe, pnl, 
                            weekday, f"2025-01-09 09:{i*2:02d}:00")
    
    # Run analysis
    result = detector.analyze_drift(window_size=20)
    
    print(f"Deviations found: {len(result['deviations'])}")
    for dev in result['deviations'][:3]:
        print(f"  - {dev['metric']}: {dev['value']:.3f} ({dev['status']})")
    
    print()
    summary = detector.get_drift_summary()
    print(f"Status: {summary['status']}")
    print(f"Drift streak: {summary['current_drift_streak']}")
    
    # Export
    detector.export_drift_log('behavioral_drift_detector_demo.json')
    print("\n✓ Demo log exported to behavioral_drift_detector_demo.json")
