"""
PHASE 19: Confidence Influence Auditor (India Deployment)

Verify confidence remains non-controlling in live NSE trading.
Diagnostic only — no enforcement.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple


class ConfidenceInfluenceAuditor:
    """Audit confidence independence from trading decisions."""
    
    # Correlation threshold for concern
    CORRELATION_THRESHOLD = 0.30  # Fail if |correlation| >= 0.30
    
    def __init__(self):
        self.trades = []
        self.audit_findings = []
        self.suspicious_patterns = []
        
    def record_trade(self, trade_id: int, symbol: str, confidence: float,
                    position_size_pct: float, entry_time: str, exit_time: str,
                    exit_reason: str, pnl_pct: float, entry_weekday: str):
        """Record trade with confidence and decision metrics."""
        
        self.trades.append({
            'trade_id': trade_id,
            'symbol': symbol,
            'confidence': confidence,
            'position_size_pct': position_size_pct,  # Should be fixed at 2.0%
            'entry_time': entry_time,
            'exit_time': exit_time,
            'exit_reason': exit_reason,  # Should be: STOP_LOSS, TARGET, END_OF_DAY
            'pnl_pct': pnl_pct,
            'entry_weekday': entry_weekday,
            'entry_hour': int(entry_time.split(':')[0]) if ':' in entry_time else 9,
        })
    
    def audit_confidence_independence(self, window_size: int = 50) -> Dict:
        """Audit whether confidence influences trading decisions."""
        
        if len(self.trades) < window_size:
            return {'status': 'INSUFFICIENT_DATA', 'trades': len(self.trades)}
        
        recent = self.trades[-window_size:]
        df = pd.DataFrame(recent)
        
        audit = {
            'timestamp': datetime.now().isoformat(),
            'window': len(df),
            'findings': [],
            'correlations': {},
            'issues': [],
        }
        
        # Finding 1: Position size should be fixed at 2.0%
        pos_sizes = df['position_size_pct'].unique()
        if len(pos_sizes) > 1 or not np.isclose(pos_sizes[0], 2.0, atol=0.01):
            audit['issues'].append({
                'type': 'POSITION_SIZE_VARIANCE',
                'details': f"Position sizes vary: {sorted(pos_sizes)}",
                'severity': 'HIGH',
            })
        
        # Finding 2: Correlation between confidence and position size
        if len(pos_sizes) > 1:
            corr = df['confidence'].corr(df['position_size_pct'])
            audit['correlations']['confidence_vs_position_size'] = float(corr)
            
            if abs(corr) >= self.CORRELATION_THRESHOLD:
                audit['issues'].append({
                    'type': 'CONFIDENCE_POSITION_COUPLING',
                    'correlation': float(corr),
                    'threshold': self.CORRELATION_THRESHOLD,
                    'severity': 'CRITICAL',
                })
        
        # Finding 3: Correlation between confidence and entry timing
        corr = df['confidence'].corr(df['entry_hour'])
        audit['correlations']['confidence_vs_entry_hour'] = float(corr)
        
        if abs(corr) >= self.CORRELATION_THRESHOLD:
            audit['issues'].append({
                'type': 'CONFIDENCE_TIMING_COUPLING',
                'correlation': float(corr),
                'threshold': self.CORRELATION_THRESHOLD,
                'severity': 'MEDIUM',
            })
        
        # Finding 4: Correlation between confidence and exit reason
        exit_reason_coded = df['exit_reason'].map({
            'STOP_LOSS': 1,
            'TARGET': 2,
            'END_OF_DAY': 3,
        })
        if exit_reason_coded.notna().sum() > 0:
            corr = df['confidence'].corr(exit_reason_coded)
            audit['correlations']['confidence_vs_exit_reason'] = float(corr) if not np.isnan(corr) else 0
            
            if abs(corr) >= self.CORRELATION_THRESHOLD:
                audit['issues'].append({
                    'type': 'CONFIDENCE_EXIT_COUPLING',
                    'correlation': float(corr),
                    'threshold': self.CORRELATION_THRESHOLD,
                    'severity': 'MEDIUM',
                })
        
        # Finding 5: Win rate should be independent of confidence
        df['is_winner'] = df['pnl_pct'] > 0
        
        # Split by confidence bins
        confidence_bins = pd.cut(df['confidence'], bins=3, labels=['Low', 'Med', 'High'])
        win_rate_by_conf = df.groupby(confidence_bins)['is_winner'].mean()
        
        audit['win_rate_by_confidence'] = {
            str(k): float(v) for k, v in win_rate_by_conf.items()
        }
        
        # Check if win rates vary significantly
        win_rate_std = win_rate_by_conf.std()
        if win_rate_std > 0.15:  # >15% variance is concerning
            audit['issues'].append({
                'type': 'WIN_RATE_CONFIDENCE_DEPENDENCE',
                'win_rate_std': float(win_rate_std),
                'threshold': 0.15,
                'severity': 'MEDIUM',
            })
        
        # Finding 6: Check for confidence-based branching (e.g., different exit rules)
        high_conf = df[df['confidence'] > 75]
        low_conf = df[df['confidence'] <= 60]
        
        if len(high_conf) > 0 and len(low_conf) > 0:
            high_avg_holding = (df.loc[df['confidence'] > 75, 'position_size_pct']).mean()
            low_avg_holding = (df.loc[df['confidence'] <= 60, 'position_size_pct']).mean()
            
            if high_avg_holding != low_avg_holding:
                audit['issues'].append({
                    'type': 'CONFIDENCE_BRANCHING_DETECTED',
                    'high_confidence_metric': float(high_avg_holding),
                    'low_confidence_metric': float(low_avg_holding),
                    'severity': 'HIGH',
                })
        
        # Summary
        critical_issues = [i for i in audit['issues'] if i['severity'] == 'CRITICAL']
        audit['status'] = 'FAILED' if critical_issues else 'PASSED'
        audit['critical_issue_count'] = len(critical_issues)
        
        self.audit_findings.append(audit)
        return audit
    
    def get_independence_summary(self) -> Dict:
        """Get summary of confidence independence."""
        
        if not self.audit_findings:
            return {'status': 'NO_AUDITS', 'trades': len(self.trades)}
        
        latest = self.audit_findings[-1]
        
        return {
            'status': latest['status'],
            'critical_issues': latest['critical_issue_count'],
            'all_issues': len(latest['issues']),
            'correlations': latest['correlations'],
            'position_size_fixed': 'position_size_pct' not in [i['type'] for i in latest['issues']],
        }
    
    def export_audit_report(self, filepath: str):
        """Export audit findings to JSON."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_trades': len(self.trades),
            'audit_findings': self.audit_findings,
            'summary': {
                'total_audits': len(self.audit_findings),
                'failed_audits': sum(1 for a in self.audit_findings if a['status'] == 'FAILED'),
                'critical_issues_total': sum(a['critical_issue_count'] for a in self.audit_findings),
            },
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)


if __name__ == '__main__':
    auditor = ConfidenceInfluenceAuditor()
    
    print("Confidence Influence Auditor (India Deployment)")
    print("="*60)
    print(f"Correlation threshold for coupling: {auditor.CORRELATION_THRESHOLD}")
    print()
    
    # Simulate trades (properly independent)
    for i in range(1, 26):
        confidence = 40 + (i % 50)  # Varies 40-90
        pnl = 0.5 if i % 2 == 0 else -0.3
        
        auditor.record_trade(
            i,
            f'STOCK{i}.NS',
            confidence,
            2.0,  # Fixed position size
            f"09:{i*2:02d}",
            f"15:{i*2:02d}",
            ['STOP_LOSS', 'TARGET', 'END_OF_DAY'][i % 3],
            pnl,
            ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][(i-1) % 5]
        )
    
    # Run audit
    audit_result = auditor.audit_confidence_independence(window_size=20)
    
    print(f"Audit status: {audit_result['status']}")
    print(f"Issues found: {audit_result['critical_issue_count']} critical")
    print()
    print("Correlations:")
    for metric, corr in audit_result['correlations'].items():
        print(f"  {metric}: {corr:.3f}")
    
    print()
    summary = auditor.get_independence_summary()
    print(f"Position size fixed: {summary['position_size_fixed']}")
    
    # Export
    auditor.export_audit_report('confidence_influence_audit_demo.json')
    print("\n✓ Demo audit exported to confidence_influence_audit_demo.json")
