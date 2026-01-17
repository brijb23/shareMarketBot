"""
PHASE 17.6: UNCERTAINTY-AWARE DECISION ENGINE
Enforces strict capital discipline: BUY signals ONLY under FULL data confidence
"""

from typing import Dict, Optional
from enum import Enum

from data_confidence_state import DataConfidenceState


class UncertaintyAwareDecisionEngine:
    """
    Wraps Phase 17 decision logic with data confidence constraints.
    
    CORE RULE:
    - BUY is allowed ONLY if DataConfidenceState == FULL
    - PARTIAL states output: WAIT, HOLD, or SELL
    - NEVER generate BUY under partial data
    """
    
    @staticmethod
    def make_uncertainty_aware_decision(
        raw_decision: str,  # "BUY", "HOLD", "SELL", "WAIT"
        raw_confidence: float,
        data_confidence_state: DataConfidenceState,
        final_confidence: float,
        cap_details: Dict,
    ) -> Dict:
        """
        Apply uncertainty constraints to raw decision.
        
        Args:
            raw_decision: Decision before uncertainty constraints
            raw_confidence: Confidence before data cap
            data_confidence_state: DataConfidenceState enum
            final_confidence: Confidence after data cap
            cap_details: Output from ConfidenceCapEngine
        
        Returns:
            {
                'decision': str,  # Final decision after uncertainty constraints
                'is_buy_allowed': bool,
                'raw_decision': str,
                'decision_modified': bool,
                'modification_reason': str,
                'data_confidence_state': DataConfidenceState,
                'final_confidence': float,
                'cap_applied': bool,
            }
        """
        
        # Rule 1: BUY ONLY allowed under FULL data confidence
        buy_allowed = (data_confidence_state == DataConfidenceState.FULL)
        
        final_decision = raw_decision
        decision_modified = False
        modification_reason = ""
        
        # Apply uncertainty constraints
        if raw_decision == "BUY":
            if not buy_allowed:
                # Convert BUY to WAIT under partial data
                final_decision = "WAIT"
                decision_modified = True
                modification_reason = (
                    f"BUY signal suppressed due to {data_confidence_state.value} data state. "
                    f"Downgraded to WAIT. "
                    f"(Raw confidence: {raw_confidence:.1f}, Capped to: {final_confidence:.1f})"
                )
        
        elif raw_decision == "HOLD":
            # HOLD is safe under any data state
            # But if confidence got capped significantly, note it
            if cap_details.get('cap_applied', False):
                pass  # HOLD remains, but cap is recorded
        
        elif raw_decision == "SELL":
            # SELL logic unchanged (conservative capital preservation)
            pass
        
        elif raw_decision == "WAIT":
            # WAIT already assumes caution
            pass
        
        return {
            'decision': final_decision,
            'is_buy_allowed': buy_allowed,
            'raw_decision': raw_decision,
            'decision_modified': decision_modified,
            'modification_reason': modification_reason,
            'data_confidence_state': data_confidence_state,
            'data_confidence_state_name': data_confidence_state.value,
            'final_confidence': final_confidence,
            'cap_applied': cap_details.get('cap_applied', False),
        }


class UncertaintyAwareMetrics:
    """Tracks uncertainty-related metrics for backtest instrumentation"""
    
    def __init__(self):
        self.total_analyses = 0
        self.analyses_by_state = {}
        self.buy_signals_total = 0
        self.buy_signals_under_full = 0
        self.buy_signals_suppressed = 0
        self.confidence_caps_applied = 0
        self.average_cap_reduction = 0.0
        self.cap_reductions = []
        self.modifications_by_reason = {}
    
    def record_analysis(
        self,
        symbol: str,
        data_state: DataConfidenceState,
        raw_decision: str,
        final_decision: str,
        raw_confidence: float,
        final_confidence: float,
        cap_applied: bool,
        cap_reduction: float = 0.0,
        modification_reason: Optional[str] = None,
    ):
        """Record metrics for single analysis"""
        
        self.total_analyses += 1
        
        # Track by state
        state_name = data_state.value
        if state_name not in self.analyses_by_state:
            self.analyses_by_state[state_name] = 0
        self.analyses_by_state[state_name] += 1
        
        # Track BUY signals
        if raw_decision == "BUY":
            self.buy_signals_total += 1
            if data_state == DataConfidenceState.FULL:
                self.buy_signals_under_full += 1
            else:
                self.buy_signals_suppressed += 1
        
        # Track confidence caps
        if cap_applied:
            self.confidence_caps_applied += 1
            if cap_reduction > 0:
                self.cap_reductions.append(cap_reduction)
        
        # Track modifications
        if final_decision != raw_decision:
            if modification_reason not in self.modifications_by_reason:
                self.modifications_by_reason[modification_reason or "Unknown"] = 0
            self.modifications_by_reason[modification_reason or "Unknown"] += 1
    
    def calculate_average_cap(self):
        """Calculate average confidence cap reduction"""
        if self.cap_reductions:
            self.average_cap_reduction = sum(self.cap_reductions) / len(self.cap_reductions)
        return self.average_cap_reduction
    
    def get_summary_report(self) -> str:
        """Generate text report of uncertainty metrics"""
        
        report = []
        report.append("\n" + "=" * 80)
        report.append("PHASE 17.6: UNCERTAINTY-AWARE DECISION METRICS")
        report.append("=" * 80)
        
        # Overall statistics
        report.append("\n[OVERALL STATISTICS]")
        report.append(f"Total analyses: {self.total_analyses}")
        report.append(f"BUY signals (total): {self.buy_signals_total} ({self.buy_signals_total/max(1, self.total_analyses)*100:.1f}%)")
        report.append(f"  - Under FULL data: {self.buy_signals_under_full}")
        report.append(f"  - Suppressed (partial data): {self.buy_signals_suppressed}")
        
        # Analysis by state
        report.append(f"\n[ANALYSES BY DATA CONFIDENCE STATE]")
        for state_name in sorted(self.analyses_by_state.keys()):
            count = self.analyses_by_state[state_name]
            pct = count / max(1, self.total_analyses) * 100
            report.append(f"  {state_name}: {count} ({pct:.1f}%)")
        
        # Confidence caps
        report.append(f"\n[CONFIDENCE CAPPING]")
        report.append(f"Caps applied: {self.confidence_caps_applied} ({self.confidence_caps_applied/max(1, self.total_analyses)*100:.1f}%)")
        
        if self.cap_reductions:
            avg_reduction = self.calculate_average_cap()
            min_reduction = min(self.cap_reductions)
            max_reduction = max(self.cap_reductions)
            report.append(f"Average cap reduction: {avg_reduction:.1f} points")
            report.append(f"Min reduction: {min_reduction:.1f} points")
            report.append(f"Max reduction: {max_reduction:.1f} points")
        
        # Modifications
        if self.modifications_by_reason:
            report.append(f"\n[DECISION MODIFICATIONS]")
            for reason, count in sorted(self.modifications_by_reason.items(), key=lambda x: -x[1]):
                pct = count / max(1, self.total_analyses) * 100
                report.append(f"  {reason}: {count} ({pct:.1f}%)")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
