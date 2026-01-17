"""
Two-Layer Output Formatter

Separates Investment View (long-term thesis) from Trade Setup (tactical confirmation).

LAYER 1: INVESTMENT VIEW
- Long-term thesis summary
- Accumulate / Hold / Avoid decision
- Fundamental strengths and risks
- Invalidation conditions

LAYER 2: TRADE SETUP (OPTIONAL)
- Only shown if technical confirmation exists
- Buy zone with structural basis
- Invalidation level (stop loss)
- Target zones with scenario analysis
- Risk-reward ratio
- Status: BUY / WAIT / NO TRADE

CONFIDENCE:
- Quantitative score (0-100) with breakdown
- Historical performance of similar setups
- Scenario probabilities (best/base/worst)
- Clear statement of uncertainty
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from enum import Enum


class InvestmentDecision(Enum):
    """Long-term investment thesis."""
    ACCUMULATE = "Accumulate"      # Strong long-term thesis
    HOLD = "Hold"                   # Acceptable but wait for better timing
    AVOID = "Avoid"                 # Weak thesis, wait for improvement


@dataclass
class InvestmentView:
    """Long-term investment thesis layer."""
    symbol: str
    decision: InvestmentDecision
    thesis_summary: str              # One-sentence bull case
    
    fundamental_strengths: List[str] # 2-3 key strengths
    fundamental_risks: List[str]     # 2-3 key risks
    
    invalidation_condition: str       # When thesis breaks
    
    fund_score: float                # 0-100
    sector: str
    analysis_date: str


@dataclass
class TradeSetup:
    """Tactical trade setup (conditional on technical confirmation)."""
    status: str                       # "BUY", "WAIT", "NO TRADE"
    
    buy_zone_low: float
    buy_zone_high: float
    buy_zone_basis: str              # "EMA cluster + volume support"
    
    invalidation_level: float
    invalidation_reason: str         # "2x ATR below support"
    
    target_zone_low: float
    target_zone_high: float
    target_basis: str                # "Swing high + 161.8% extension"
    
    rr_ratio: Optional[float]        # Risk:Reward
    volume_confirmation: bool
    breakout_confirmed: bool
    warning: Optional[str]


@dataclass
class ConfidenceReport:
    """Quantitative confidence breakdown with risk adjustments."""
    total_score: float               # 0-100 (after all multipliers applied)
    grade: str                       # "A+", "A", "B+", etc.
    
    win_rate_component: float        # 0-30
    rr_component: float              # 0-20
    structure_component: float       # 0-20
    thesis_component: float          # 0-15
    drawdown_component: float        # 0-15
    
    # Scenarios
    win_scenario: Tuple[float, str]      # (probability %, description)
    base_scenario: Tuple[float, str]
    worst_scenario: Tuple[float, str]
    
    # Historical context
    setup_type: str
    historical_win_rate: float
    sample_size: int
    uncertainty_statement: str
    
    # Risk adjustments
    regime_adjustment: float = 0.0           # Points added/subtracted by regime filter
    regime_explanation: str = ""             # Explanation of regime impact
    event_adjustment: float = 0.0            # Points added/subtracted by event risk
    event_explanation: str = ""              # Explanation of event risk impact
    drawdown_adjustment: float = 0.0         # Points added/subtracted by drawdown fragility
    drawdown_explanation: str = ""           # Explanation of drawdown impact
    
    # Risk objects (for detailed analysis)
    market_regime: Optional[object] = None   # MarketRegime object
    event_risk: Optional[object] = None      # EventRisk object
    drawdown_analysis: Optional[object] = None  # DrawdownAnalysis object
    
    # Phase 17: Confidence calibration and instability suppression
    base_confidence: float = 0.0             # Score before any multipliers
    confidence_before_calibration: float = 0.0  # Score after multipliers, before ceiling/floor
    calibration_adjustment: float = 0.0     # Points added/subtracted by ceiling/floor calibration
    calibration_note: str = ""               # Explanation of calibration applied
    ceiling_reduction: float = 0.0           # Points prevented from inflation (if ceiling applied)
    regime_instability_active: bool = False  # Whether regime instability suppression is active
    instability_suppression_note: str = ""  # Reason for instability suppression
    suppressed_investment_decision: str = ""  # What decision was suppressed (e.g., "WAIT" instead of "BUY")


class TwoLayerOutputFormatter:
    """
    Format stock analysis into clear, two-layer output:
    1. Investment View (long-term thesis)
    2. Trade Setup (tactical entry, if confirmed)
    3. Confidence (quantitative backing)
    """
    
    @staticmethod
    def format_report(
        symbol: str,
        investment_view: InvestmentView,
        trade_setup: Optional[TradeSetup],
        confidence: ConfidenceReport,
    ) -> str:
        """Generate formatted analysis report."""
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"STOCK ANALYSIS: {symbol}")
        lines.append("=" * 80)
        lines.append("")
        
        # LAYER 1: INVESTMENT VIEW
        lines.extend(TwoLayerOutputFormatter._format_investment_view(investment_view))
        lines.append("")
        lines.append("-" * 80)
        lines.append("")
        
        # LAYER 2: TRADE SETUP (if available)
        if trade_setup and trade_setup.status != "NO TRADE":
            lines.extend(TwoLayerOutputFormatter._format_trade_setup(trade_setup))
            lines.append("")
            lines.append("-" * 80)
            lines.append("")
        else:
            lines.append("TRADE SETUP: NO CONFIRMED ENTRY")
            lines.append("")
            lines.append("Reasons:")
            if trade_setup:
                if trade_setup.warning:
                    lines.append(f"  • {trade_setup.warning}")
                if trade_setup.rr_ratio and trade_setup.rr_ratio < 2.0:
                    lines.append(f"  • Insufficient risk-reward ({trade_setup.rr_ratio:.1f}:1 < 2.0:1)")
            else:
                lines.append("  • Technical confirmation not met")
            lines.append("")
            lines.append("-" * 80)
            lines.append("")
        
        # LAYER 3: CONFIDENCE & SCENARIOS
        lines.extend(TwoLayerOutputFormatter._format_confidence(confidence))
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_investment_view(view: InvestmentView) -> List[str]:
        """Format investment thesis layer."""
        lines = []
        
        lines.append("INVESTMENT VIEW (Long-Term Thesis)")
        lines.append(f"Decision: {view.decision.value}")
        lines.append(f"Thesis: {view.thesis_summary}")
        lines.append("")
        
        lines.append(f"Fundamental Score: {view.fund_score:.0f}/100")
        lines.append(f"Sector: {view.sector}")
        lines.append("")
        
        lines.append("Bull Case:")
        for i, strength in enumerate(view.fundamental_strengths, 1):
            lines.append(f"  {i}. {strength}")
        lines.append("")
        
        lines.append("Bear Case:")
        for i, risk in enumerate(view.fundamental_risks, 1):
            lines.append(f"  {i}. {risk}")
        lines.append("")
        
        lines.append(f"Thesis Invalidation: {view.invalidation_condition}")
        
        return lines
    
    @staticmethod
    def _format_trade_setup(setup: TradeSetup) -> List[str]:
        """Format tactical trade setup layer."""
        lines = []
        
        lines.append("TRADE SETUP (Tactical Entry)")
        lines.append(f"Status: {setup.status}")
        lines.append("")
        
        lines.append(f"Buy Zone: Rs {setup.buy_zone_low:.2f} - Rs {setup.buy_zone_high:.2f}")
        lines.append(f"  Basis: {setup.buy_zone_basis}")
        lines.append("")
        
        lines.append(f"Invalidation Level: Rs {setup.invalidation_level:.2f}")
        lines.append(f"  Reason: {setup.invalidation_reason}")
        lines.append("")
        
        lines.append(f"Target Zone: Rs {setup.target_zone_low:.2f} - Rs {setup.target_zone_high:.2f}")
        lines.append(f"  Basis: {setup.target_basis}")
        lines.append("")
        
        if setup.rr_ratio:
            lines.append(f"Risk-Reward Ratio: 1:{setup.rr_ratio:.1f}")
        lines.append("")
        
        lines.append("Confirmations:")
        lines.append(f"  • Volume Confirmed: {'Yes' if setup.volume_confirmation else 'No'}")
        lines.append(f"  • Breakout Confirmed: {'Yes' if setup.breakout_confirmed else 'No'}")
        
        if setup.warning:
            lines.append(f"  ⚠ {setup.warning}")
        
        return lines
    
    @staticmethod
    def _format_confidence(conf: ConfidenceReport) -> List[str]:
        """Format quantitative confidence section with risk adjustments and calibration."""
        lines = []
        
        lines.append("CONFIDENCE & SCENARIOS")
        
        # CONFIDENCE TRANSFORMATION PIPELINE
        lines.append("Confidence Calculation Pipeline:")
        lines.append(f"  1. Base Score (5 components):        {conf.base_confidence:>6.1f}/100")
        lines.append("")
        
        # Show multipliers applied
        if conf.regime_adjustment != 0 or conf.regime_explanation:
            direction = "+" if conf.regime_adjustment >= 0 else ""
            lines.append(f"  2. Market Regime Adjustment:         {direction}{conf.regime_adjustment:>5.1f}")
            lines.append(f"     ({conf.regime_explanation})")
        if conf.event_adjustment != 0 or conf.event_explanation:
            direction = "+" if conf.event_adjustment >= 0 else ""
            lines.append(f"  3. Event Risk Adjustment:            {direction}{conf.event_adjustment:>5.1f}")
            lines.append(f"     ({conf.event_explanation})")
        if conf.drawdown_adjustment != 0 or conf.drawdown_explanation:
            direction = "+" if conf.drawdown_adjustment >= 0 else ""
            lines.append(f"  4. Drawdown Fragility Adjustment:    {direction}{conf.drawdown_adjustment:>5.1f}")
            lines.append(f"     ({conf.drawdown_explanation})")
        
        lines.append("")
        lines.append(f"  Score After Modifiers:               {conf.confidence_before_calibration:>6.1f}/100")
        lines.append("")
        
        # CALIBRATION SECTION
        if conf.calibration_adjustment != 0 or conf.ceiling_reduction > 0:
            lines.append("  5. Confidence Calibration:")
            if conf.ceiling_reduction > 0:
                lines.append(f"     • Ceiling Applied: Max 90/100 (prevented {conf.ceiling_reduction:.1f} points of inflation)")
            if conf.calibration_adjustment > 0:
                lines.append(f"     • Floor Applied: Min 10/100 (ensured {conf.calibration_adjustment:.1f} points minimum)")
            if conf.calibration_note:
                lines.append(f"     • {conf.calibration_note}")
            lines.append("")
        
        lines.append(f"  ► FINAL CONFIDENCE:                  {conf.total_score:>6.1f}/100 [{conf.grade}]")
        lines.append("")
        
        # REGIME INSTABILITY WARNING
        if conf.regime_instability_active:
            lines.append("  ⚠ REGIME INSTABILITY SUPPRESSION ACTIVE")
            lines.append(f"     {conf.instability_suppression_note}")
            if conf.suppressed_investment_decision:
                lines.append(f"     Investment Decision Suppressed: OVERRIDDEN TO '{conf.suppressed_investment_decision}'")
            lines.append("")
        
        lines.append("Confidence Components:")
        lines.append(f"  • Win Rate:      {conf.win_rate_component:>2.0f}/30  (historical validation)")
        lines.append(f"  • R:R Ratio:     {conf.rr_component:>2.0f}/20  (risk-reward balance)")
        lines.append(f"  • Structure:     {conf.structure_component:>2.0f}/20  (chart confirmation)")
        lines.append(f"  • Thesis:        {conf.thesis_component:>2.0f}/15  (fundamental basis)")
        lines.append(f"  • Drawdown:      {conf.drawdown_component:>2.0f}/15  (exit robustness)")
        lines.append("")
        
        lines.append("Setup Type: " + conf.setup_type)
        lines.append(f"Historical Performance: {conf.historical_win_rate:.1f}% win rate ({conf.sample_size} similar trades)")
        lines.append("")
        
        # RISK ADJUSTMENTS SECTION - COMPACT
        if conf.regime_explanation or conf.event_explanation or conf.drawdown_explanation:
            lines.append("Market Conditions Applied:")
            if conf.regime_explanation:
                lines.append(f"  • Market Regime: {conf.regime_explanation}")
            if conf.event_explanation:
                lines.append(f"  • Event Risk: {conf.event_explanation}")
            if conf.drawdown_explanation:
                lines.append(f"  • Drawdown Risk: {conf.drawdown_explanation}")
            lines.append("")
        
        # RISK DETAILS (if present)
        if conf.market_regime:
            lines.append("Market Regime Details:")
            lines.append(f"  • Regime Type: {conf.market_regime.regime_type.value}")
            lines.append(f"  • Trend Alignment: {conf.market_regime.index_trend}")
            lines.append(f"  • Volatility Percentile: {conf.market_regime.volatility_percentile:.0f}th")
            lines.append(f"  • Breadth Ratio: {conf.market_regime.breadth_ratio:.2f}")
            if conf.market_regime.regime_instability:
                lines.append(f"  • ⚠ Instability Detected: {conf.market_regime.instability_reason}")
            if conf.market_regime.risk_warning:
                lines.append(f"  • ⚠ {conf.market_regime.risk_warning}")
            lines.append("")
        
        if conf.event_risk and conf.event_risk.event_type.value != "NONE":
            lines.append("Event Risk Details:")
            lines.append(f"  • Event Type: {conf.event_risk.event_type.value}")
            if conf.event_risk.days_until_event is not None:
                lines.append(f"  • Days Until: {conf.event_risk.days_until_event}")
            lines.append(f"  • Risk Level: {conf.event_risk.risk_level.value}")
            lines.append(f"  • Recommendation: {conf.event_risk.recommendation.value}")
            lines.append(f"  • {conf.event_risk.explanation}")
            lines.append("")
        
        if conf.drawdown_analysis:
            lines.append("Drawdown Profile:")
            lines.append(f"  • Setup Type: {conf.drawdown_analysis.setup_type}")
            if conf.drawdown_analysis.volatility_normalized and conf.drawdown_analysis.atr_ratio > 1.0:
                lines.append(f"  • Typical MAE (volatility-adjusted): {conf.drawdown_analysis.normalized_mae_typical:.2f}%")
                lines.append(f"    - Baseline MAE: {conf.drawdown_analysis.mae_typical:.2f}% | ATR Ratio: {conf.drawdown_analysis.atr_ratio:.2f}x")
            else:
                lines.append(f"  • Typical MAE: {conf.drawdown_analysis.mae_typical:.2f}%")
            lines.append(f"  • Worst-Case MAE (p95): {conf.drawdown_analysis.mae_worst_case:.2f}%")
            lines.append(f"  • Recommended Stop: {conf.drawdown_analysis.stop_below_entry_pct:.2f}% below entry")
            if conf.drawdown_analysis.volatility_normalized and conf.drawdown_analysis.atr_ratio > 1.0:
                lines.append(f"    - Volatility-adjusted from {conf.drawdown_analysis.mae_typical * (conf.drawdown_analysis.atr_ratio - 1):.2f}% baseline")
            lines.append(f"  • Fragility Level: {conf.drawdown_analysis.fragility_level.value}")
            lines.append(f"  • {conf.drawdown_analysis.recommendation}")
            lines.append("")
        
        lines.append("Scenario Analysis:")
        win_prob, win_desc = conf.win_scenario
        base_prob, base_desc = conf.base_scenario
        worst_prob, worst_desc = conf.worst_scenario
        
        lines.append(f"  WIN ({win_prob:.0f}%):    {win_desc}")
        lines.append(f"  BASE ({base_prob:.0f}%):   {base_desc}")
        lines.append(f"  WORST ({worst_prob:.0f}%): {worst_desc}")
        lines.append("")
        
        lines.append("Uncertainty Statement:")
        lines.append(f"  {conf.uncertainty_statement}")
        
        return lines


# ============================================================================
# EXAMPLE OUTPUT (for testing)
# ============================================================================

EXAMPLE_OUTPUT = """
================================================================================
STOCK ANALYSIS: RELIANCE.NS
================================================================================

INVESTMENT VIEW (Long-Term Thesis)
Decision: Accumulate
Thesis: Strong cash generation with energy transition exposure; valued at 14x FY26E EPS

Fundamental Score: 72/100
Sector: Energy

Bull Case:
  1. Consolidated refinery margins remain healthy (Rs 1,500-2,000/bbl structural)
  2. Jio capex cycle cooling; FCF inflection near (2.5x EBITDA by FY26)
  3. Low carbon dividend yield (~3.2%) with 12% capex reduction path

Bear Case:
  1. Crude oil dependency (40% EBITDA); geopolitical tail risk
  2. Energy transition capex ($5B+) creates execution risk
  3. Valuation at 13-14x leaves little margin for miss

Thesis Invalidation: Oil prices <$40/bbl sustained + FCF guidance cut >15%

--------------------------------------------------------------------------------

TRADE SETUP (Tactical Entry)
Status: BUY

Buy Zone: Rs 1,245.00 - Rs 1,265.00
  Basis: EMA cluster (20/50 aligned) + volume profile support at 200 DMA

Invalidation Level: Rs 1,225.00
  Reason: 2x ATR (16.5) below current support level

Target Zone: Rs 1,310.00 - Rs 1,405.00
  Basis: Swing high (Apr) + 161.8% Fib extension

Risk-Reward Ratio: 1:3.2

Confirmations:
  • Volume Confirmed: Yes
  • Breakout Confirmed: Yes

--------------------------------------------------------------------------------

CONFIDENCE & SCENARIOS
Overall Confidence: 74/100 [A]

Confidence Breakdown:
  • Win Rate Component:    18/30
  • R:R Ratio Component:   18/20
  • Structure Component:   16/20
  • Thesis Component:      12/15
  • Drawdown Component:    10/15

Setup Type: Trend Continuation
Historical Win Rate: 62.1% (156 similar trades)

Scenario Analysis:
  WIN (48%):    Target hit within 45 days (R:R = 3.2x if achieved)
  BASE (35%):   Partial move (+5-8%), position scaled out
  WORST (17%):  Stop loss hit (3.1% average loss in similar setups)

Uncertainty Statement:
  This is a high-conviction trade setup with strong structural confirmation.
  However, oil price moves remain a significant tail risk. Position sizing
  should account for sector exposure. Invalidation at Rs 1,225 is firm.

================================================================================
"""
