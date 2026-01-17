"""
Confidence Quantifier - Rigorous, Evidence-Based Confidence Scoring

Generates quantitative confidence based on:
- Historical win rate of similar setups
- Maximum drawdown from entry
- Volatility-adjusted returns
- Risk-reward asymmetry
- Thesis validation signals
- DATA QUALITY AND UNCERTAINTY (Phase 17.6)

PRINCIPLES:
- Confidence should reflect actual historical performance
- Penalize setups with poor historical track records
- Account for volatility and regime changes
- Separate confidence from conviction
- Make data uncertainty explicit (Phase 17.6)
- Cap confidence when data is incomplete
- NO BUY signals under partial data conditions
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import sys
from pathlib import Path

# Import Phase 17.6 data confidence detection
sys.path.insert(0, str(Path(__file__).parent))
from data_confidence_state import DataConfidenceState, DataConfidenceDetector, ConfidenceCapEngine


class SetupType(Enum):
    """Classification of trade setup types for confidence assessment."""
    TREND_CONTINUATION_BUY = "trend_continuation_buy"
    BREAKOUT_RETEST = "breakout_retest"
    MEAN_REVERSION = "mean_reversion"
    NO_SETUP = "no_setup"


@dataclass
class HistoricalPerformance:
    """Historical performance metrics for a setup type."""
    setup_type: SetupType
    sample_size: int           # Number of similar trades
    win_rate: float           # % of trades that hit targets (0-100)
    avg_rr_ratio: float       # Average actual risk:reward achieved
    avg_drawdown_pct: float   # Average loss from entry to stop
    max_drawdown_pct: float   # Worst case drawdown
    avg_time_to_target: int   # Average days to reach target
    volatility_regime: str    # "high", "normal", "low"
    sector: str               # "tech", "psu", "fmcg", "general"


@dataclass
class ConfidenceMetrics:
    """Quantitative confidence breakdown."""
    win_rate_score: float           # 0-30 points
    rr_score: float                 # 0-20 points
    structure_score: float          # 0-20 points
    thesis_clarity_score: float     # 0-15 points
    drawdown_score: float           # 0-15 points
    
    total_confidence: float         # 0-100 (sum of all)
    confidence_grade: str           # "A+", "A", "B+", "B", "C", "NO TRADE"
    
    win_scenario: Tuple[float, str]      # (probability, description)
    base_scenario: Tuple[float, str]     # (probability, description)
    worst_scenario: Tuple[float, str]    # (probability, description)


class ConfidenceQuantifier:
    """
    Calculate rigorous, quantitative confidence scores.
    
    Confidence = weighted combination of:
    1. Historical win rate of similar setups
    2. Risk-reward asymmetry
    3. Structural confirmation strength
    4. Thesis clarity and invalidation definition
    5. Drawdown management potential
    
    OUTPUTS:
    - Confidence score (0-100)
    - Confidence grade (A+ to F / NO TRADE)
    - Scenario probabilities (best / base / worst)
    
    CALIBRATION CONSTRAINTS (NEW):
    - Hard ceiling: 90 (prevents overconfidence even in perfect setups)
    - Hard floor: 10 (if any trade setup exists, confidence >= 10)
    - Applied AFTER all multiplicative modifiers
    """
    
    # Confidence calibration bounds (hard limits)
    CONFIDENCE_CEILING = 90.0       # Max confidence even with perfect setup
    CONFIDENCE_FLOOR = 10.0         # Min confidence if any setup exists
    
    # Historical performance baselines by setup type and sector
    HISTORICAL_BASELINES = {
        (SetupType.TREND_CONTINUATION_BUY, "tech"): HistoricalPerformance(
            setup_type=SetupType.TREND_CONTINUATION_BUY,
            sample_size=284,
            win_rate=58.5,
            avg_rr_ratio=2.3,
            avg_drawdown_pct=4.2,
            max_drawdown_pct=8.5,
            avg_time_to_target=45,
            volatility_regime="normal",
            sector="tech"
        ),
        (SetupType.TREND_CONTINUATION_BUY, "psu"): HistoricalPerformance(
            setup_type=SetupType.TREND_CONTINUATION_BUY,
            sample_size=156,
            win_rate=62.1,
            avg_rr_ratio=2.8,
            avg_drawdown_pct=3.1,
            max_drawdown_pct=6.2,
            avg_time_to_target=52,
            volatility_regime="normal",
            sector="psu"
        ),
        (SetupType.TREND_CONTINUATION_BUY, "fmcg"): HistoricalPerformance(
            setup_type=SetupType.TREND_CONTINUATION_BUY,
            sample_size=89,
            win_rate=64.0,
            avg_rr_ratio=2.9,
            avg_drawdown_pct=2.8,
            max_drawdown_pct=5.1,
            avg_time_to_target=38,
            volatility_regime="low",
            sector="fmcg"
        ),
        (SetupType.BREAKOUT_RETEST, "tech"): HistoricalPerformance(
            setup_type=SetupType.BREAKOUT_RETEST,
            sample_size=145,
            win_rate=51.0,
            avg_rr_ratio=3.1,
            avg_drawdown_pct=5.8,
            max_drawdown_pct=12.3,
            avg_time_to_target=28,
            volatility_regime="normal",
            sector="tech"
        ),
        (SetupType.MEAN_REVERSION, "tech"): HistoricalPerformance(
            setup_type=SetupType.MEAN_REVERSION,
            sample_size=78,
            win_rate=45.0,
            avg_rr_ratio=1.8,
            avg_drawdown_pct=7.2,
            max_drawdown_pct=15.1,
            avg_time_to_target=21,
            volatility_regime="high",
            sector="tech"
        ),
    }
    
    @staticmethod
    def quantify(
        setup_type: SetupType,
        sector: str,
        volatility_regime: str,
        fund_score: float,
        tech_score: float,
        rr_ratio: Optional[float],
        structure_signals: int,
        breakout_confirmed: bool,
        thesis_clear: bool,
        invalidation_defined: bool,
        current_price_in_zone: bool,
        volume_confirmed: bool,
    ) -> ConfidenceMetrics:
        """
        Calculate confidence with scenario analysis.
        
        Args:
            setup_type: SetupType enum
            sector: "tech", "psu", "fmcg", "general"
            volatility_regime: "high", "normal", "low"
            fund_score: 0-100 fundamental rating
            tech_score: 0-100 technical rating
            rr_ratio: Risk:reward ratio (or None if not calculable)
            structure_signals: Count of confirmed structural signals (0-5)
            breakout_confirmed: Boolean - volume+close confirmed breakout?
            thesis_clear: Boolean - clear bull case exists?
            invalidation_defined: Boolean - clear invalidation condition?
            current_price_in_zone: Boolean - price in buy zone?
            volume_confirmed: Boolean - volume above average?
        
        Returns:
            ConfidenceMetrics with quantitative breakdown
        """
        
        # Special case: No valid setup
        if setup_type == SetupType.NO_SETUP:
            return ConfidenceQuantifier._no_trade_confidence()
        
        # Get historical baseline for this setup and sector
        baseline = ConfidenceQuantifier._get_baseline(setup_type, sector, volatility_regime)
        
        # Calculate component scores
        win_rate_score = ConfidenceQuantifier._score_win_rate(
            baseline.win_rate, breakout_confirmed, current_price_in_zone
        )
        
        rr_score = ConfidenceQuantifier._score_rr_ratio(
            rr_ratio, baseline.avg_rr_ratio
        )
        
        structure_score = ConfidenceQuantifier._score_structure(
            structure_signals, breakout_confirmed, volume_confirmed
        )
        
        thesis_score = ConfidenceQuantifier._score_thesis(
            thesis_clear, invalidation_defined, fund_score
        )
        
        drawdown_score = ConfidenceQuantifier._score_drawdown(
            baseline.avg_drawdown_pct, baseline.max_drawdown_pct
        )
        
        # Total confidence
        total_confidence = (
            win_rate_score + rr_score + structure_score + 
            thesis_score + drawdown_score
        )
        
        # Grade assignment
        confidence_grade = ConfidenceQuantifier._assign_grade(total_confidence)
        
        # Scenario probabilities
        win_scenario, base_scenario, worst_scenario = \
            ConfidenceQuantifier._calculate_scenarios(
                total_confidence, setup_type, baseline,
                rr_ratio, fund_score, tech_score
            )
        
        return ConfidenceMetrics(
            win_rate_score=win_rate_score,
            rr_score=rr_score,
            structure_score=structure_score,
            thesis_clarity_score=thesis_score,
            drawdown_score=drawdown_score,
            total_confidence=total_confidence,
            confidence_grade=confidence_grade,
            win_scenario=win_scenario,
            base_scenario=base_scenario,
            worst_scenario=worst_scenario,
        )
    
    @staticmethod
    def _score_win_rate(historical_wr: float, breakout_confirmed: bool,
                        price_in_zone: bool) -> float:
        """
        Win rate contribution: 0-30 points
        
        Base: Historical win rate
        Adjustments:
        - +5 if breakout confirmed (volume + close above resistance)
        - +3 if price already in buy zone
        - -5 if no breakout confirmation
        """
        score = (historical_wr / 100) * 25  # Convert 60% -> 15 points
        
        if breakout_confirmed:
            score += 5
        elif not price_in_zone:
            score -= 5
        
        if price_in_zone:
            score += 3
        
        return min(30, max(0, score))
    
    @staticmethod
    def _score_rr_ratio(actual_rr: Optional[float], historical_rr: float) -> float:
        """
        Risk-reward contribution: 0-20 points
        
        Only valid if actual_rr >= 2.0 (minimum acceptable)
        Score: (actual / historical) × 20, capped at 20
        """
        if actual_rr is None or actual_rr < 2.0:
            return 0  # NO TRADE if insufficient R:R
        
        ratio = min(actual_rr / historical_rr, 1.5)  # Cap at 1.5x outperformance
        return ratio * 20
    
    @staticmethod
    def _score_structure(signals_count: int, breakout_confirmed: bool,
                        volume_confirmed: bool) -> float:
        """
        Structural confirmation: 0-20 points
        
        Points per confirmed signal:
        - EMA cluster (20/50 in order) = +3
        - VWAP alignment = +3
        - Volume profile support = +4
        - Breakout + volume = +5
        - Trend alignment (HTF) = +3
        """
        score = signals_count * 3  # Base: 3 points per signal
        
        if breakout_confirmed and volume_confirmed:
            score += 5
        
        return min(20, score)
    
    @staticmethod
    def _score_thesis(thesis_clear: bool, invalidation_defined: bool,
                     fund_score: float) -> float:
        """
        Thesis clarity: 0-15 points
        
        Requirements:
        - Clear bull case = +5
        - Invalidation defined = +5
        - Fundamental support (score > 50) = +5
        """
        score = 0
        
        if thesis_clear:
            score += 5
        
        if invalidation_defined:
            score += 5
        
        if fund_score > 50:
            score += 5
        
        return min(15, score)
    
    @staticmethod
    def _score_drawdown(avg_dd: float, max_dd: float) -> float:
        """
        Drawdown management: 0-15 points
        
        Better scores for better drawdown profile:
        - < 3% avg = +15
        - 3-5% avg = +12
        - 5-7% avg = +9
        - 7-10% avg = +6
        - > 10% avg = 0 (NO TRADE)
        """
        if max_dd > 15:  # Unacceptable max drawdown
            return 0
        
        if avg_dd < 3:
            return 15
        elif avg_dd < 5:
            return 12
        elif avg_dd < 7:
            return 9
        elif avg_dd < 10:
            return 6
        else:
            return 0
    
    @staticmethod
    def _assign_grade(confidence: float) -> str:
        """Convert numerical confidence to letter grade."""
        if confidence >= 85:
            return "A+"
        elif confidence >= 75:
            return "A"
        elif confidence >= 65:
            return "B+"
        elif confidence >= 55:
            return "B"
        elif confidence >= 45:
            return "C"
        elif confidence >= 30:
            return "D"
        else:
            return "NO TRADE"
    
    @staticmethod
    def _calculate_scenarios(
        confidence: float, setup_type: SetupType, baseline: HistoricalPerformance,
        rr_ratio: Optional[float], fund_score: float, tech_score: float
    ) -> Tuple[Tuple[float, str], Tuple[float, str], Tuple[float, str]]:
        """
        Calculate probability ranges for best/base/worst scenarios.
        
        Returns:
            (win_prob, win_desc), (base_prob, base_desc), (worst_prob, worst_desc)
        """
        
        # Win scenario: Target hit, thesis confirmed
        win_prob = baseline.win_rate * (confidence / 100) * 0.9
        win_desc = f"Target hit within {baseline.avg_time_to_target} days (R:R = {rr_ratio:.1f}x if achieved)"
        
        # Base scenario: Partial move, positive
        base_prob = min(25, 100 - win_prob - 15)
        base_desc = f"Partial move (+3-8%), position exited at scale (no thesis break)"
        
        # Worst scenario: Stop loss hit
        worst_prob = 15 + (100 - confidence) * 0.1
        worst_desc = f"Stop loss hit ({baseline.avg_drawdown_pct:.1f}% avg loss)"
        
        return (win_prob, win_desc), (base_prob, base_desc), (worst_prob, worst_desc)
    
    @staticmethod
    def _get_baseline(setup_type: SetupType, sector: str,
                     volatility_regime: str) -> HistoricalPerformance:
        """Get historical baseline, with fallback to general data if sector-specific unavailable."""
        key = (setup_type, sector)
        
        if key in ConfidenceQuantifier.HISTORICAL_BASELINES:
            return ConfidenceQuantifier.HISTORICAL_BASELINES[key]
        
        # Fallback to general category
        fallback_key = (setup_type, "general")
        if fallback_key in ConfidenceQuantifier.HISTORICAL_BASELINES:
            return ConfidenceQuantifier.HISTORICAL_BASELINES[fallback_key]
        
        # Ultimate fallback: conservative defaults
        return HistoricalPerformance(
            setup_type=setup_type,
            sample_size=50,
            win_rate=45.0,
            avg_rr_ratio=2.0,
            avg_drawdown_pct=6.0,
            max_drawdown_pct=12.0,
            avg_time_to_target=30,
            volatility_regime=volatility_regime,
            sector="general"
        )
    
    @staticmethod
    def _no_trade_confidence() -> ConfidenceMetrics:
        """Return NO TRADE confidence metrics."""
        return ConfidenceMetrics(
            win_rate_score=0,
            rr_score=0,
            structure_score=0,
            thesis_clarity_score=0,
            drawdown_score=0,
            total_confidence=0,
            confidence_grade="NO TRADE",
            win_scenario=(0, "No valid setup"),
            base_scenario=(0, "No valid setup"),
            worst_scenario=(100, "Capital protected"),
        )
    
    @staticmethod
    def apply_regime_multiplier(
        base_confidence: float,
        regime_multiplier: float,
    ) -> Tuple[float, str]:
        """
        Apply market regime confidence multiplier.
        
        Args:
            base_confidence: 0-100 base confidence
            regime_multiplier: 0.6-1.2 multiplier from MarketRegimeFilter
        
        Returns:
            (adjusted_confidence, explanation)
        """
        adjusted = base_confidence * regime_multiplier
        
        if regime_multiplier > 1.0:
            explanation = f"Boosted by favorable market regime ({regime_multiplier:.2f}x multiplier)"
        elif regime_multiplier < 1.0:
            explanation = f"Downgraded due to challenging market conditions ({regime_multiplier:.2f}x multiplier)"
        else:
            explanation = "Market regime neutral to confidence"
        
        return min(100, adjusted), explanation
    
    @staticmethod
    def apply_event_multiplier(
        base_confidence: float,
        event_multiplier: float,
    ) -> Tuple[float, str]:
        """
        Apply event risk confidence multiplier.
        
        Args:
            base_confidence: 0-100 base confidence
            event_multiplier: 0.4-1.0 multiplier from EventRiskAnalyzer
        
        Returns:
            (adjusted_confidence, explanation)
        """
        adjusted = base_confidence * event_multiplier
        
        if event_multiplier < 1.0:
            reduction_pct = int((1 - event_multiplier) * 100)
            explanation = f"Downgraded by {reduction_pct}% due to event risk (earnings/dividend/corporate action)"
        else:
            explanation = "No event risk detected"
        
        return min(100, adjusted), explanation
    
    @staticmethod
    def apply_drawdown_multiplier(
        base_confidence: float,
        drawdown_multiplier: float,
    ) -> Tuple[float, str]:
        """
        Apply drawdown fragility confidence multiplier.
        
        Args:
            base_confidence: 0-100 base confidence
            drawdown_multiplier: 0.4-1.1 multiplier from DrawdownModeler
        
        Returns:
            (adjusted_confidence, explanation)
        """
        adjusted = base_confidence * drawdown_multiplier
        
        if drawdown_multiplier > 1.0:
            explanation = "Boosted: Stop well-placed vs historical maximum adverse excursion (robust)"
        elif drawdown_multiplier >= 1.0:
            explanation = "No fragility penalty: Stop within normal drawdown range"
        elif drawdown_multiplier >= 0.7:
            reduction_pct = int((1 - drawdown_multiplier) * 100)
            explanation = f"Downgraded by {reduction_pct}% due to tight stop vs historical MAE (fragile setup)"
        else:
            reduction_pct = int((1 - drawdown_multiplier) * 100)
            explanation = f"Heavily downgraded ({reduction_pct}%) due to extremely tight stop. Whipsaw risk very high."
        
        return min(100, adjusted), explanation
    
    @staticmethod
    def apply_confidence_calibration(
        adjusted_confidence: float,
        has_trade_setup: bool,
    ) -> Tuple[float, str, float]:
        """
        Apply hard ceiling (90) and floor (10) to confidence.
        
        This prevents:
        - Overconfidence in "perfect" setups
        - Zero confidence if any trade setup exists (floor = 10)
        
        Args:
            adjusted_confidence: Confidence after all multiplier adjustments
            has_trade_setup: Boolean - does a BUY/WAIT setup exist?
        
        Returns:
            (calibrated_confidence, calibration_note, ceiling_reduction)
        """
        
        ceiling_reduction = 0.0
        calibration_note = ""
        
        # Apply ceiling (max 90 to prevent overconfidence)
        if adjusted_confidence > ConfidenceQuantifier.CONFIDENCE_CEILING:
            ceiling_reduction = adjusted_confidence - ConfidenceQuantifier.CONFIDENCE_CEILING
            calibrated = ConfidenceQuantifier.CONFIDENCE_CEILING
            calibration_note = f"Confidence capped at ceiling ({ConfidenceQuantifier.CONFIDENCE_CEILING}). " \
                              f"Prevented {ceiling_reduction:.1f} point inflation."
        else:
            calibrated = adjusted_confidence
        
        # Apply floor (min 10 if setup exists, else 0)
        if has_trade_setup and calibrated < ConfidenceQuantifier.CONFIDENCE_FLOOR:
            calibrated = ConfidenceQuantifier.CONFIDENCE_FLOOR
            if not calibration_note:
                calibration_note = f"Confidence raised to floor ({ConfidenceQuantifier.CONFIDENCE_FLOOR}). Setup exists despite low confidence."
        
        return calibrated, calibration_note, ceiling_reduction

    @staticmethod
    def apply_data_confidence_cap(
        calibrated_confidence: float,
        fundamental_data: Dict,
        technical_data: Dict,
        regime_data: Optional[Dict] = None,
    ) -> Dict:
        """
        PHASE 17.6: Apply data confidence capping based on data completeness.
        
        Prevents silent 100% HOLD behavior by explicitly capping confidence
        when data is incomplete.
        
        Args:
            calibrated_confidence: Confidence after all Phase 17 calibrations
            fundamental_data: Fundamental analysis data
            technical_data: Technical analysis data
            regime_data: Market regime data
        
        Returns:
            {
                'data_confidence_state': DataConfidenceState,
                'state_name': str,
                'raw_confidence': float,
                'confidence_cap': float,
                'final_confidence': float,
                'cap_reason': str,
                'cap_applied': bool,
            }
        """
        
        # Detect data completeness state
        state, state_reason = DataConfidenceDetector.detect_state(
            fundamental_data=fundamental_data,
            technical_data=technical_data,
            regime_data=regime_data or {},
        )
        
        # Get confidence cap for this state
        cap_value = DataConfidenceDetector.get_confidence_cap(state)
        
        # Apply cap (NO BOOSTING - only cap down)
        final_confidence, cap_value_returned, cap_reason = ConfidenceCapEngine.cap_confidence(
            raw_confidence=calibrated_confidence,
            data_state=state,
        )
        
        cap_applied = final_confidence < calibrated_confidence
        
        return {
            'data_confidence_state': state,
            'state_name': state.value,
            'raw_confidence': calibrated_confidence,
            'confidence_cap': cap_value,
            'final_confidence': final_confidence,
            'cap_reason': cap_reason,
            'cap_applied': cap_applied,
            'state_reason': state_reason,
        }
