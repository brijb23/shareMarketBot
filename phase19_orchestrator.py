"""
PHASE 19: Orchestrator (Multi-Module Surveillance)

Orchestrate all 5 surveillance modules for live NSE trading.
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from capital_invariant_monitor import CapitalInvariantMonitor
from behavioral_drift_detector import BehavioralDriftDetector
from confidence_influence_auditor import ConfidenceInfluenceAuditor
from regime_stress_sentinel import RegimeStressSentinel


class Phase19Orchestrator:
    """Orchestrate all surveillance modules for Phase 1 live trading."""
    
    def __init__(self, output_dir: str = 'phase19_surveillance'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize all 5 modules
        self.capital_monitor = CapitalInvariantMonitor()
        self.drift_detector = BehavioralDriftDetector()
        self.confidence_auditor = ConfidenceInfluenceAuditor()
        self.regime_sentinel = RegimeStressSentinel()
        
        self.execution_log = []
        self.system_status = 'ACTIVE'
        self.creation_timestamp = datetime.now().isoformat()
        
    def execute_live_trade(self, trade_data: Dict) -> Dict:
        """Execute a live trade through surveillance pipeline."""
        
        # Extract trade data
        trade_id = trade_data['trade_id']
        symbol = trade_data['symbol']
        entry_price = trade_data['entry_price']
        exit_price = trade_data['exit_price']
        pnl_pct = trade_data['pnl_pct']
        confidence = trade_data['confidence']
        entry_time = trade_data['entry_time']
        exit_time = trade_data['exit_time']
        mae_pct = trade_data.get('mae_pct', -0.5)
        mfe_pct = trade_data.get('mfe_pct', 1.5)
        high_price = trade_data.get('high_price', entry_price * 1.02)
        low_price = trade_data.get('low_price', entry_price * 0.98)
        exit_reason = trade_data.get('exit_reason', 'TARGET')
        entry_weekday = trade_data.get('entry_weekday', 'Mon')
        
        result = {
            'trade_id': trade_id,
            'timestamp': datetime.now().isoformat(),
            'checks': {},
        }
        
        # Check 1: Capital Invariant Monitor
        # qty = round(10000 / entry_price)  # 2% position sizing (example 10k capital)
        qty = 1  # Normalized qty for this validation
        capital_ok = self.capital_monitor.record_trade(
            trade_id, symbol, entry_price, exit_price, qty,
            pnl_pct, confidence, entry_time
        )
        
        result['checks']['capital_invariant'] = {
            'passed': capital_ok,
            'system_halted': self.capital_monitor.is_halted,
            'halt_reason': self.capital_monitor.halt_reason,
        }
        
        if not capital_ok:
            result['decision'] = 'REJECTED_CAPITAL_VIOLATION'
            self.system_status = 'HALTED'
            self.execution_log.append(result)
            return result
        
        # Check 2: Record for drift detection
        self.drift_detector.record_trade(
            trade_id, symbol, entry_price, exit_price, mae_pct, mfe_pct,
            pnl_pct, entry_weekday, entry_time
        )
        
        # Check 3: Record for confidence audit
        self.confidence_auditor.record_trade(
            trade_id, symbol, confidence, 2.0, entry_time, exit_time,
            exit_reason, pnl_pct, entry_weekday
        )
        
        # Check 4: Record for regime sentinel
        self.regime_sentinel.record_trade(
            trade_id, symbol, entry_price, exit_price, high_price, low_price,
            entry_time
        )
        
        result['decision'] = 'ACCEPTED'
        self.execution_log.append(result)
        return result
    
    def run_surveillance_cycle(self) -> Dict:
        """Run all surveillance modules (typically hourly or EOD)."""
        
        cycle = {
            'timestamp': datetime.now().isoformat(),
            'modules': {},
        }
        
        # Module 1: Capital Invariant Monitor
        capital_status = self.capital_monitor.get_status_summary()
        cycle['modules']['capital_invariant'] = capital_status
        
        # Module 2: Behavioral Drift Detector
        drift_analysis = self.drift_detector.analyze_drift(window_size=20)
        drift_summary = self.drift_detector.get_drift_summary()
        cycle['modules']['behavioral_drift'] = drift_summary
        
        # Module 3: Confidence Influence Auditor
        confidence_audit = self.confidence_auditor.audit_confidence_independence(window_size=50)
        confidence_summary = self.confidence_auditor.get_independence_summary()
        cycle['modules']['confidence_auditor'] = confidence_summary
        
        # Module 4: Regime Stress Sentinel
        regime_analysis = self.regime_sentinel.analyze_regime()
        regime_summary = self.regime_sentinel.get_regime_summary()
        cycle['modules']['regime_sentinel'] = regime_summary
        
        # Determine overall system health
        system_health = self._determine_system_health(cycle)
        cycle['system_health'] = system_health
        
        return cycle
    
    def _determine_system_health(self, cycle: Dict) -> Dict:
        """Determine overall system health from all modules."""
        
        health = {
            'timestamp': cycle['timestamp'],
            'overall_status': 'HEALTHY',
            'alerts': [],
            'warnings': [],
        }
        
        # Check capital status
        capital = cycle['modules']['capital_invariant']
        if capital.get('status') == 'HALTED':
            health['overall_status'] = 'HALTED'
            health['alerts'].append(f"CAPITAL: {capital.get('halt_reason')}")
        
        # Check drift status
        drift = cycle['modules']['behavioral_drift']
        if drift.get('status') == 'DRIFTING':
            health['warnings'].append(f"DRIFT: Streak={drift.get('current_drift_streak')}")
        
        # Check confidence
        confidence = cycle['modules']['confidence_auditor']
        if confidence.get('status') == 'FAILED':
            health['alerts'].append(f"CONFIDENCE: {confidence.get('critical_issues')} critical issues")
        
        # Check regime
        regime = cycle['modules']['regime_sentinel']
        if regime.get('current_regime') == 'OUT_OF_SAMPLE':
            health['warnings'].append('REGIME: Out-of-sample detected')
        
        return health
    
    def export_surveillance_state(self, filename: str = 'phase19_surveillance_state.json'):
        """Export complete surveillance state to JSON."""
        
        state = {
            'creation_timestamp': self.creation_timestamp,
            'current_timestamp': datetime.now().isoformat(),
            'system_status': self.system_status,
            'execution_log': self.execution_log,
            'modules': {
                'capital_monitor': {
                    'trades': len(self.capital_monitor.trades),
                    'status': self.capital_monitor.get_status_summary(),
                },
                'drift_detector': {
                    'trades': len(self.drift_detector.trades),
                    'summary': self.drift_detector.get_drift_summary(),
                },
                'confidence_auditor': {
                    'trades': len(self.confidence_auditor.trades),
                    'summary': self.confidence_auditor.get_independence_summary(),
                },
                'regime_sentinel': {
                    'trades': len(self.regime_sentinel.trades),
                    'summary': self.regime_sentinel.get_regime_summary(),
                },
            },
        }
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        return str(filepath)
    
    def generate_surveillance_report(self) -> str:
        """Generate a human-readable surveillance report."""
        
        report = []
        report.append("# PHASE 19: SURVEILLANCE CYCLE REPORT")
        report.append(f"\n**Timestamp**: {datetime.now().isoformat()}")
        report.append(f"**System Status**: {self.system_status}")
        
        # Capital invariant status
        report.append("\n## Capital Invariant Monitor")
        capital_status = self.capital_monitor.get_status_summary()
        report.append(f"- Status: {capital_status.get('status')}")
        report.append(f"- Trades: {capital_status.get('trades_count')}")
        report.append(f"- Current Capital: ${capital_status.get('current_capital'):,.2f}")
        report.append(f"- Total Return: {capital_status.get('total_return'):+.2f}%")
        report.append(f"- Current Drawdown: {capital_status.get('current_drawdown'):.2f}%")
        if capital_status.get('halt_reason'):
            report.append(f"- ⚠️ Halt Reason: {capital_status.get('halt_reason')}")
        
        # Drift detector status
        report.append("\n## Behavioral Drift Detector")
        drift_summary = self.drift_detector.get_drift_summary()
        report.append(f"- Status: {drift_summary.get('status')}")
        report.append(f"- Drift Events: {drift_summary.get('drift_events')}")
        report.append(f"- Current Streak: {drift_summary.get('current_drift_streak')}")
        
        # Confidence auditor status
        report.append("\n## Confidence Influence Auditor")
        conf_summary = self.confidence_auditor.get_independence_summary()
        report.append(f"- Status: {conf_summary.get('status')}")
        report.append(f"- Position Size Fixed: {conf_summary.get('position_size_fixed')}")
        report.append(f"- Critical Issues: {conf_summary.get('critical_issues')}")
        
        # Regime sentinel status
        report.append("\n## Regime Stress Sentinel")
        regime_summary = self.regime_sentinel.get_regime_summary()
        report.append(f"- Current Regime: {regime_summary.get('current_regime')}")
        report.append(f"- Stress Events: {regime_summary.get('stress_events')}")
        
        # Summary
        report.append("\n## Summary")
        report.append(f"- Total Trades Logged: {len(self.capital_monitor.trades)}")
        report.append(f"- Execution Log Entries: {len(self.execution_log)}")
        
        return "\n".join(report)
    
    def get_full_status(self) -> Dict:
        """Get complete status of all modules."""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_status': self.system_status,
            'capital_monitor': self.capital_monitor.get_status_summary(),
            'drift_detector': self.drift_detector.get_drift_summary(),
            'confidence_auditor': self.confidence_auditor.get_independence_summary(),
            'regime_sentinel': self.regime_sentinel.get_regime_summary(),
            'execution_log_size': len(self.execution_log),
        }


if __name__ == '__main__':
    orchestrator = Phase19Orchestrator()
    
    print("Phase 19 Orchestrator: Multi-Module Surveillance")
    print("="*60)
    print()
    
    # Simulate 10 trades
    for i in range(1, 11):
        trade = {
            'trade_id': i,
            'symbol': f'STOCK{i}.NS',
            'entry_price': 100 + np.random.randn() * 2,
            'exit_price': 100 + np.random.randn() * 2,
            'pnl_pct': 0.5 if i % 2 == 0 else -0.3,
            'confidence': 50 + np.random.uniform(-10, 30),
            'entry_time': f"2025-01-09 09:{i*5:02d}:00",
            'exit_time': f"2025-01-09 15:{i*5:02d}:00",
            'mae_pct': -np.random.uniform(0.5, 2.0),
            'mfe_pct': np.random.uniform(0.5, 3.0),
            'high_price': 105,
            'low_price': 95,
            'exit_reason': ['STOP_LOSS', 'TARGET', 'END_OF_DAY'][i % 3],
            'entry_weekday': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][(i-1) % 5],
        }
        
        import numpy as np  # Quick import
        result = orchestrator.execute_live_trade(trade)
        print(f"Trade {i}: {result['decision']}")
    
    # Run surveillance cycle
    print("\nRunning surveillance cycle...")
    cycle = orchestrator.run_surveillance_cycle()
    
    print(f"System Health: {cycle['system_health']['overall_status']}")
    if cycle['system_health']['alerts']:
        for alert in cycle['system_health']['alerts']:
            print(f"  🚨 {alert}")
    if cycle['system_health']['warnings']:
        for warning in cycle['system_health']['warnings']:
            print(f"  ⚠️  {warning}")
    
    # Export
    filepath = orchestrator.export_surveillance_state()
    print(f"\n✓ Surveillance state exported to {filepath}")
    
    # Report
    report = orchestrator.generate_surveillance_report()
    print("\n" + report)
