"""
PHASE 17.5: LOGIC ACTIVATION DIAGNOSTICS
Instrumentation to identify blocking gates and dead logic paths
"""

from dataclasses import dataclass, field
from typing import Dict, List, DefaultDict
from collections import defaultdict
from datetime import datetime
import statistics


@dataclass
class DiagnosticsCollector:
    """Collects diagnostic data throughout backtest without changing logic"""
    
    # Fundamental Score Distribution
    fundamental_scores: List[float] = field(default_factory=list)
    fundamental_validity: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))  # VALID/WEAK/INVALID
    sector_fundamental_scores: DefaultDict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    
    # Technical Setup Classification
    technical_setups: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    breakout_failures: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Confidence Computation Path
    raw_confidence_scores: List[float] = field(default_factory=list)
    final_confidence_scores: List[float] = field(default_factory=list)
    confidence_exactly_50: int = 0
    confidence_components_zero: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Decision Gate Blockages
    gate_blocks: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    reached_buy_eligibility: int = 0
    actual_buy_decisions: int = 0
    actual_hold_decisions: int = 0
    actual_sell_decisions: int = 0
    
    # Signal counts
    buy_signals: int = 0
    hold_signals: int = 0
    sell_signals: int = 0
    wait_signals: int = 0
    
    def record_fundamental_score(self, score: float, sector: str = "unknown", validity: str = "VALID"):
        """Record fundamental score without changing logic"""
        self.fundamental_scores.append(score)
        self.fundamental_validity[validity] += 1
        self.sector_fundamental_scores[sector].append(score)
    
    def record_technical_setup(self, setup_type: str):
        """Record technical setup type"""
        self.technical_setups[setup_type] += 1
    
    def record_breakout_failure(self, reason: str):
        """Record why breakout condition failed"""
        self.breakout_failures[reason] += 1
    
    def record_confidence(self, raw: float, final: float):
        """Record confidence before and after adjustments"""
        self.raw_confidence_scores.append(raw)
        self.final_confidence_scores.append(final)
        if abs(final - 50.0) < 0.001:
            self.confidence_exactly_50 += 1
    
    def record_component_zero(self, component_name: str):
        """Record when a confidence component is zero"""
        self.confidence_components_zero[component_name] += 1
    
    def record_gate_block(self, gate_name: str):
        """Record which gate blocked a decision"""
        self.gate_blocks[gate_name] += 1
    
    def record_buy_eligible(self):
        """Record when all conditions for BUY were met"""
        self.reached_buy_eligibility += 1
    
    def record_signal(self, decision: str):
        """Record final signal decision"""
        if decision == "BUY":
            self.buy_signals += 1
            self.actual_buy_decisions += 1
        elif decision == "HOLD":
            self.hold_signals += 1
            self.actual_hold_decisions += 1
        elif decision == "SELL":
            self.sell_signals += 1
            self.actual_sell_decisions += 1
        elif decision == "WAIT":
            self.wait_signals += 1
    
    def generate_report(self) -> str:
        """Generate diagnostic summary report"""
        report = []
        report.append("\n" + "=" * 80)
        report.append("PHASE 17.5: LOGIC ACTIVATION DIAGNOSTICS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. FUNDAMENTAL SCORE DISTRIBUTION
        report.append("\n" + "-" * 80)
        report.append("1. FUNDAMENTAL SCORE DISTRIBUTION")
        report.append("-" * 80)
        
        if self.fundamental_scores:
            min_fund = min(self.fundamental_scores)
            max_fund = max(self.fundamental_scores)
            mean_fund = statistics.mean(self.fundamental_scores)
            
            count_60 = len([s for s in self.fundamental_scores if s > 60])
            count_65 = len([s for s in self.fundamental_scores if s > 65])
            count_70 = len([s for s in self.fundamental_scores if s > 70])
            count_75 = len([s for s in self.fundamental_scores if s > 75])
            
            report.append(f"Total fundamental scores recorded: {len(self.fundamental_scores)}")
            report.append(f"Min: {min_fund:.1f}")
            report.append(f"Max: {max_fund:.1f}")
            report.append(f"Mean: {mean_fund:.1f}")
            report.append(f"Stdev: {statistics.stdev(self.fundamental_scores) if len(self.fundamental_scores) > 1 else 0:.1f}")
            report.append(f"\nCounts:")
            report.append(f"  > 60: {count_60}")
            report.append(f"  > 65: {count_65}")
            report.append(f"  > 70: {count_70}")
            report.append(f"  > 75: {count_75}")
            
            report.append(f"\nValidity Distribution:")
            for validity, count in sorted(self.fundamental_validity.items()):
                report.append(f"  {validity}: {count}")
            
            if self.sector_fundamental_scores:
                report.append(f"\nSector-wise Average Fundamental Scores:")
                for sector in sorted(self.sector_fundamental_scores.keys()):
                    scores = self.sector_fundamental_scores[sector]
                    if scores:
                        avg = statistics.mean(scores)
                        report.append(f"  {sector}: {avg:.1f} (n={len(scores)})")
        else:
            report.append("WARNING: No fundamental scores recorded!")
        
        # 2. TECHNICAL SETUP CLASSIFICATION
        report.append("\n" + "-" * 80)
        report.append("2. TECHNICAL SETUP CLASSIFICATION")
        report.append("-" * 80)
        
        if self.technical_setups:
            total_setups = sum(self.technical_setups.values())
            for setup_type in sorted(self.technical_setups.keys()):
                count = self.technical_setups[setup_type]
                pct = count / total_setups * 100 if total_setups > 0 else 0
                report.append(f"  {setup_type}: {count} ({pct:.1f}%)")
            
            if self.breakout_failures:
                report.append(f"\nBreakout Failure Reasons:")
                for reason in sorted(self.breakout_failures.keys()):
                    count = self.breakout_failures[reason]
                    report.append(f"  {reason}: {count}")
        else:
            report.append("WARNING: No technical setups recorded!")
        
        # 3. CONFIDENCE COMPUTATION PATH
        report.append("\n" + "-" * 80)
        report.append("3. CONFIDENCE COMPUTATION PATH")
        report.append("-" * 80)
        
        if self.raw_confidence_scores:
            min_raw = min(self.raw_confidence_scores)
            max_raw = max(self.raw_confidence_scores)
            mean_raw = statistics.mean(self.raw_confidence_scores)
            
            min_final = min(self.final_confidence_scores)
            max_final = max(self.final_confidence_scores)
            mean_final = statistics.mean(self.final_confidence_scores)
            
            report.append(f"Raw Confidence Scores:")
            report.append(f"  Min: {min_raw:.1f}")
            report.append(f"  Max: {max_raw:.1f}")
            report.append(f"  Mean: {mean_raw:.1f}")
            report.append(f"  Stdev: {statistics.stdev(self.raw_confidence_scores) if len(self.raw_confidence_scores) > 1 else 0:.1f}")
            
            report.append(f"\nFinal Confidence Scores (after adjustments):")
            report.append(f"  Min: {min_final:.1f}")
            report.append(f"  Max: {max_final:.1f}")
            report.append(f"  Mean: {mean_final:.1f}")
            report.append(f"  Stdev: {statistics.stdev(self.final_confidence_scores) if len(self.final_confidence_scores) > 1 else 0:.1f}")
            
            report.append(f"\n*** CRITICAL: Exactly 50.0 occurrences: {self.confidence_exactly_50} / {len(self.final_confidence_scores)} ***")
            if self.confidence_exactly_50 > len(self.final_confidence_scores) * 0.9:
                report.append("    ^^^ ALERT: >90% of confidence scores are EXACTLY 50.0 ^^^")
                report.append("    This indicates dead logic paths or constant-output computation.")
            
            if self.confidence_components_zero:
                report.append(f"\nComponents Recording Zero:")
                for component, count in sorted(self.confidence_components_zero.items()):
                    report.append(f"  {component}: {count} times")
        else:
            report.append("WARNING: No confidence scores recorded!")
        
        # 4. DECISION GATE BLOCKAGES
        report.append("\n" + "-" * 80)
        report.append("4. FINAL DECISION GATE ANALYSIS")
        report.append("-" * 80)
        
        report.append(f"Decision Gate Blockage Counts:")
        total_blocks = 0
        for gate in sorted(self.gate_blocks.keys()):
            count = self.gate_blocks[gate]
            total_blocks += count
            report.append(f"  {gate}: {count}")
        
        report.append(f"\nDecision Progression:")
        report.append(f"  Reached BUY eligibility: {self.reached_buy_eligibility}")
        report.append(f"  Actual BUY decisions: {self.actual_buy_decisions}")
        report.append(f"  Actual HOLD decisions: {self.actual_hold_decisions}")
        report.append(f"  Actual SELL decisions: {self.actual_sell_decisions}")
        report.append(f"  WAIT signals (suppressed): {self.wait_signals}")
        
        # 5. SIGNAL SUMMARY
        report.append("\n" + "-" * 80)
        report.append("5. FINAL SIGNAL SUMMARY")
        report.append("-" * 80)
        
        total_decisions = self.buy_signals + self.hold_signals + self.sell_signals + self.wait_signals
        if total_decisions > 0:
            report.append(f"  BUY:  {self.buy_signals:5d} ({self.buy_signals/total_decisions*100:5.1f}%)")
            report.append(f"  HOLD: {self.hold_signals:5d} ({self.hold_signals/total_decisions*100:5.1f}%)")
            report.append(f"  SELL: {self.sell_signals:5d} ({self.sell_signals/total_decisions*100:5.1f}%)")
            report.append(f"  WAIT: {self.wait_signals:5d} ({self.wait_signals/total_decisions*100:5.1f}%) [SUPPRESSED]")
        
        # CRITICAL FINDINGS
        report.append("\n" + "=" * 80)
        report.append("CRITICAL FINDINGS")
        report.append("=" * 80)
        
        findings = []
        
        if self.buy_signals == 0:
            findings.append("[CRITICAL] Zero BUY signals generated in entire backtest")
            if self.reached_buy_eligibility == 0:
                findings.append("  -> Root cause: No signals reached BUY eligibility")
                findings.append("  -> Check: Decision gates blocking earlier in pipeline")
            else:
                findings.append("  -> BUY eligibility was reached but final gate(s) blocked execution")
        
        if self.confidence_exactly_50 > len(self.final_confidence_scores) * 0.9:
            findings.append("[CRITICAL] >90% confidence scores are EXACTLY 50.0")
            findings.append("  -> Indicates: Confidence computation always returns constant value")
            findings.append("  -> Check: ConfidenceQuantifier returning hardcoded/default values")
        
        if not self.fundamental_scores or max(self.fundamental_scores) < 65:
            findings.append("[CRITICAL] Fundamental scores never exceed 65")
            findings.append("  -> Blocks: Any threshold checking for >65")
            findings.append("  -> Check: Fundamental analyzer returning consistently low scores")
        
        if "NO_TRADE" in self.technical_setups and self.technical_setups.get("NO_TRADE", 0) > sum(self.technical_setups.values()) * 0.9:
            findings.append("[CRITICAL] >90% technical setups classified as NO_TRADE")
            findings.append("  -> Blocks: Technical confirmation at signal gate")
            findings.append("  -> Check: Technical setup classification logic")
        
        for finding in findings:
            report.append(finding)
        
        if not findings:
            report.append("No critical findings detected.")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "PHASE_17_5_DIAGNOSTIC_REPORT.md"):
        """Save report to file"""
        report = self.generate_report()
        with open(filename, "w") as f:
            f.write(report)
        return filename


# Global instance for collecting diagnostics
_diagnostics = DiagnosticsCollector()


def get_diagnostics_collector() -> DiagnosticsCollector:
    """Get global diagnostics collector"""
    return _diagnostics


def reset_diagnostics():
    """Reset diagnostics for new run"""
    global _diagnostics
    _diagnostics = DiagnosticsCollector()
