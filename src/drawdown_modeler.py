"""
Drawdown Modeler
================
Tracks Maximum Adverse Excursion (MAE) by setup type and sector.
Flags setups as "fragile" if proposed stops are tighter than typical MAE.

Prevents false breakouts and whipsaws by validating stop placement
against historical drawdown profiles.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Tuple


class SetupType(Enum):
    """Trade setup classification."""
    TREND_CONTINUATION = "TREND_CONTINUATION"
    BREAKOUT_RETEST = "BREAKOUT_RETEST"
    CONSOLIDATION_BREAKOUT = "CONSOLIDATION_BREAKOUT"
    NO_TRADE = "NO_TRADE"


class FragilityLevel(Enum):
    """Setup fragility assessment."""
    ROBUST = "ROBUST"              # Stop > 1.5x MAE, can withstand normal noise
    NORMAL = "NORMAL"              # Stop within MAE range, typical risk/reward
    FRAGILE = "FRAGILE"            # Stop < MAE, likely to be hit prematurely
    EXTREMELY_FRAGILE = "EXTREMELY_FRAGILE"  # Stop << MAE, high whipsaw risk


@dataclass
class SetupDrawdownProfile:
    """Historical drawdown metrics for a setup type + sector combination."""
    setup_type: str                 # "TREND_CONTINUATION", "BREAKOUT_RETEST", etc.
    sector: str                     # "IT", "PSU", "FMCG", "FINANCIALS", "ENERGY", "OTHER"
    
    mae_pct_mean: float             # Average MAE (%)
    mae_pct_p95: float              # 95th percentile MAE (worst case)
    mae_pct_p75: float              # 75th percentile MAE
    mae_pct_p50: float              # Median MAE
    
    sample_count: int               # Number of trades in baseline
    win_rate_pct: float             # % of trades that recovered from MAE


@dataclass
class DrawdownAnalysis:
    """Output from drawdown modeling."""
    setup_type: str
    sector: str
    entry_price: float
    proposed_stop: float
    
    # Historical baseline
    mae_typical: float              # Typical (median) MAE for this setup/sector
    mae_worst_case: float           # 95th percentile MAE
    mae_mean: float                 # Average MAE
    
    # Comparison
    stop_below_entry_pct: float     # How far below entry (%)
    fragility_level: FragilityLevel
    is_fragile: bool                # True if stop < typical MAE
    
    # Recommendation
    minimum_recommended_stop: float  # Stop should be at least this level
    gap_to_mae: float               # How much tighter stop is vs median MAE (%)
    recommendation: str             # "ROBUST", "ACCEPTABLE", "FRAGILE_SUPPRESS", etc.
    
    # NEW: Volatility normalization
    volatility_normalized: bool = False      # Was MAE scaled by volatility?
    atr_ratio: float = 1.0                   # Current ATR / baseline ATR
    normalized_mae_typical: float = 0.0      # MAE after volatility scaling
    normalized_stop_threshold: float = 0.0   # Recommended stop after scaling


class DrawdownModeler:
    """Historical drawdown profiling by setup + sector."""
    
    # Historical MAE baselines (from analysis of past setups)
    # Format: (setup_type, sector) -> SetupDrawdownProfile
    DRAWDOWN_PROFILES: Dict[Tuple[str, str], SetupDrawdownProfile] = {
        
        # TREND CONTINUATION SETUPS
        ("TREND_CONTINUATION", "IT"): SetupDrawdownProfile(
            setup_type="TREND_CONTINUATION",
            sector="IT",
            mae_pct_mean=2.8,
            mae_pct_p95=4.5,
            mae_pct_p75=3.8,
            mae_pct_p50=2.6,
            sample_count=128,
            win_rate_pct=68.0,
        ),
        ("TREND_CONTINUATION", "PSU"): SetupDrawdownProfile(
            setup_type="TREND_CONTINUATION",
            sector="PSU",
            mae_pct_mean=3.2,
            mae_pct_p95=5.1,
            mae_pct_p75=4.2,
            mae_pct_p50=3.0,
            sample_count=94,
            win_rate_pct=65.0,
        ),
        ("TREND_CONTINUATION", "FMCG"): SetupDrawdownProfile(
            setup_type="TREND_CONTINUATION",
            sector="FMCG",
            mae_pct_mean=2.3,
            mae_pct_p95=3.6,
            mae_pct_p75=3.0,
            mae_pct_p50=2.1,
            sample_count=72,
            win_rate_pct=72.0,
        ),
        ("TREND_CONTINUATION", "FINANCIALS"): SetupDrawdownProfile(
            setup_type="TREND_CONTINUATION",
            sector="FINANCIALS",
            mae_pct_mean=3.1,
            mae_pct_p95=4.9,
            mae_pct_p75=4.0,
            mae_pct_p50=2.9,
            sample_count=156,
            win_rate_pct=67.0,
        ),
        ("TREND_CONTINUATION", "ENERGY"): SetupDrawdownProfile(
            setup_type="TREND_CONTINUATION",
            sector="ENERGY",
            mae_pct_mean=3.5,
            mae_pct_p95=5.8,
            mae_pct_p75=4.6,
            mae_pct_p50=3.2,
            sample_count=61,
            win_rate_pct=62.0,
        ),
        
        # BREAKOUT RETEST SETUPS
        ("BREAKOUT_RETEST", "IT"): SetupDrawdownProfile(
            setup_type="BREAKOUT_RETEST",
            sector="IT",
            mae_pct_mean=3.4,
            mae_pct_p95=5.2,
            mae_pct_p75=4.4,
            mae_pct_p50=3.1,
            sample_count=83,
            win_rate_pct=64.0,
        ),
        ("BREAKOUT_RETEST", "PSU"): SetupDrawdownProfile(
            setup_type="BREAKOUT_RETEST",
            sector="PSU",
            mae_pct_mean=4.1,
            mae_pct_p95=6.3,
            mae_pct_p75=5.2,
            mae_pct_p50=3.8,
            sample_count=57,
            win_rate_pct=61.0,
        ),
        ("BREAKOUT_RETEST", "FMCG"): SetupDrawdownProfile(
            setup_type="BREAKOUT_RETEST",
            sector="FMCG",
            mae_pct_mean=2.9,
            mae_pct_p95=4.5,
            mae_pct_p75=3.7,
            mae_pct_p50=2.7,
            sample_count=44,
            win_rate_pct=68.0,
        ),
        ("BREAKOUT_RETEST", "FINANCIALS"): SetupDrawdownProfile(
            setup_type="BREAKOUT_RETEST",
            sector="FINANCIALS",
            mae_pct_mean=3.8,
            mae_pct_p95=5.9,
            mae_pct_p75=4.8,
            mae_pct_p50=3.5,
            sample_count=102,
            win_rate_pct=63.0,
        ),
        ("BREAKOUT_RETEST", "ENERGY"): SetupDrawdownProfile(
            setup_type="BREAKOUT_RETEST",
            sector="ENERGY",
            mae_pct_mean=4.4,
            mae_pct_p95=6.8,
            mae_pct_p75=5.5,
            mae_pct_p50=4.0,
            sample_count=35,
            win_rate_pct=59.0,
        ),
        
        # CONSOLIDATION BREAKOUT SETUPS
        ("CONSOLIDATION_BREAKOUT", "IT"): SetupDrawdownProfile(
            setup_type="CONSOLIDATION_BREAKOUT",
            sector="IT",
            mae_pct_mean=3.9,
            mae_pct_p95=6.1,
            mae_pct_p75=5.0,
            mae_pct_p50=3.6,
            sample_count=67,
            win_rate_pct=62.0,
        ),
        ("CONSOLIDATION_BREAKOUT", "PSU"): SetupDrawdownProfile(
            setup_type="CONSOLIDATION_BREAKOUT",
            sector="PSU",
            mae_pct_mean=4.6,
            mae_pct_p95=7.2,
            mae_pct_p75=5.8,
            mae_pct_p50=4.2,
            sample_count=41,
            win_rate_pct=59.0,
        ),
        ("CONSOLIDATION_BREAKOUT", "FMCG"): SetupDrawdownProfile(
            setup_type="CONSOLIDATION_BREAKOUT",
            sector="FMCG",
            mae_pct_mean=3.4,
            mae_pct_p95=5.2,
            mae_pct_p75=4.3,
            mae_pct_p50=3.1,
            sample_count=38,
            win_rate_pct=66.0,
        ),
        ("CONSOLIDATION_BREAKOUT", "FINANCIALS"): SetupDrawdownProfile(
            setup_type="CONSOLIDATION_BREAKOUT",
            sector="FINANCIALS",
            mae_pct_mean=4.2,
            mae_pct_p95=6.5,
            mae_pct_p75=5.3,
            mae_pct_p50=3.9,
            sample_count=88,
            win_rate_pct=61.0,
        ),
        ("CONSOLIDATION_BREAKOUT", "ENERGY"): SetupDrawdownProfile(
            setup_type="CONSOLIDATION_BREAKOUT",
            sector="ENERGY",
            mae_pct_mean=4.9,
            mae_pct_p95=7.6,
            mae_pct_p75=6.2,
            mae_pct_p50=4.5,
            sample_count=29,
            win_rate_pct=55.0,
        ),
    }
    
    @staticmethod
    def analyze_setup_fragility(
        setup_type: str,
        sector: str,
        entry_price: float,
        proposed_stop: float,
        current_atr: Optional[float] = None,
        baseline_atr: Optional[float] = None,
    ) -> DrawdownAnalysis:
        """
        Analyze if proposed stop is robust vs historical MAE.
        Optionally scales MAE by volatility ratio for high-vol regimes.
        
        Args:
            setup_type: "TREND_CONTINUATION", "BREAKOUT_RETEST", "CONSOLIDATION_BREAKOUT"
            sector: "IT", "PSU", "FMCG", "FINANCIALS", "ENERGY", "OTHER"
            entry_price: Entry price
            proposed_stop: Proposed stop loss price
            current_atr: Current ATR (optional, for volatility normalization)
            baseline_atr: Baseline ATR (optional, for volatility normalization)
        
        Returns:
            DrawdownAnalysis with fragility assessment (MAE may be volatility-scaled)
        """
        
        # Get or estimate profile
        profile = DrawdownModeler.DRAWDOWN_PROFILES.get(
            (setup_type, sector)
        )
        
        if profile is None:
            # Fallback: use sector average or conservative estimate
            profile = DrawdownModeler._get_fallback_profile(setup_type, sector)
        
        # Calculate stop vs entry
        stop_distance = entry_price - proposed_stop
        stop_pct_below_entry = (stop_distance / entry_price) * 100 if entry_price > 0 else 0
        
        # NEW: Volatility normalization
        atr_ratio = 1.0
        mae_to_use = profile.mae_pct_p50  # Start with baseline
        normalized_mae = profile.mae_pct_p50
        normalized_stop_threshold = entry_price * (1 - (profile.mae_pct_p50 / 100))
        volatility_normalized = False
        
        if current_atr and baseline_atr and baseline_atr > 0:
            atr_ratio = current_atr / baseline_atr
            # Scale MAE by volatility ratio (high vol = wider stops needed)
            if atr_ratio > 1.1:  # Only scale if volatility is elevated
                normalized_mae = profile.mae_pct_p50 * atr_ratio
                normalized_stop_threshold = entry_price * (1 - (normalized_mae / 100))
                volatility_normalized = True
                mae_to_use = normalized_mae
        
        # Compare to MAE (using original or normalized)
        gap_to_median_mae = stop_pct_below_entry - mae_to_use
        gap_to_mean_mae = stop_pct_below_entry - profile.mae_pct_mean
        
        # Assess fragility (using volatility-normalized or baseline MAE)
        mae_p95_threshold = profile.mae_pct_p95 * atr_ratio if volatility_normalized else profile.mae_pct_p95
        mae_p75_threshold = profile.mae_pct_p75 * atr_ratio if volatility_normalized else profile.mae_pct_p75
        
        if stop_pct_below_entry >= mae_p95_threshold:
            # Stop well beyond worst-case MAE: Very robust
            fragility = FragilityLevel.ROBUST
            recommendation = f"ROBUST: Stop well beyond {'volatility-adjusted ' if volatility_normalized else ''}worst-case drawdown."
        elif stop_pct_below_entry >= mae_p75_threshold:
            # Stop in upper-middle of historical MAE range: Good
            fragility = FragilityLevel.NORMAL
            recommendation = f"ACCEPTABLE: Stop within normal {'volatility-adjusted ' if volatility_normalized else ''}drawdown range."
        elif stop_pct_below_entry >= mae_to_use:
            # Stop at median: Typical risk
            fragility = FragilityLevel.NORMAL
            recommendation = f"NORMAL: Stop at {'volatility-adjusted ' if volatility_normalized else ''}median MAE. Whipsaw risk present."
        elif stop_pct_below_entry >= mae_to_use - 0.5:
            # Stop just below mean: Concerning
            fragility = FragilityLevel.FRAGILE
            recommendation = f"FRAGILE: Stop tighter than {'volatility-adjusted ' if volatility_normalized else ''}MAE. High whipsaw risk."
        else:
            # Stop << MAE: Very risky
            fragility = FragilityLevel.EXTREMELY_FRAGILE
            recommendation = f"EXTREMELY_FRAGILE: Stop far tighter than {'volatility-adjusted ' if volatility_normalized else ''}MAE. Suppress trade."
        
        # Recommended minimum stop (at median MAE or volatility-adjusted)
        minimum_stop = normalized_stop_threshold
        
        return DrawdownAnalysis(
            setup_type=setup_type,
            sector=sector,
            entry_price=entry_price,
            proposed_stop=proposed_stop,
            mae_typical=profile.mae_pct_p50,
            mae_worst_case=profile.mae_pct_p95,
            mae_mean=profile.mae_pct_mean,
            stop_below_entry_pct=stop_pct_below_entry,
            fragility_level=fragility,
            is_fragile=fragility in [FragilityLevel.FRAGILE, FragilityLevel.EXTREMELY_FRAGILE],
            minimum_recommended_stop=minimum_stop,
            gap_to_mae=gap_to_median_mae,
            recommendation=recommendation,
            volatility_normalized=volatility_normalized,
            atr_ratio=atr_ratio,
            normalized_mae_typical=normalized_mae,
            normalized_stop_threshold=normalized_stop_threshold,
        )
    
    @staticmethod
    def _get_fallback_profile(setup_type: str, sector: str) -> SetupDrawdownProfile:
        """Return conservative fallback if specific profile not found."""
        # Average across sectors for this setup type
        matching = [
            v for (k, v) in DrawdownModeler.DRAWDOWN_PROFILES.items()
            if k[0] == setup_type
        ]
        
        if matching:
            avg_mae_mean = sum(p.mae_pct_mean for p in matching) / len(matching)
            avg_mae_p95 = sum(p.mae_pct_p95 for p in matching) / len(matching)
            avg_mae_p75 = sum(p.mae_pct_p75 for p in matching) / len(matching)
            avg_mae_p50 = sum(p.mae_pct_p50 for p in matching) / len(matching)
        else:
            # Generic conservative estimate
            avg_mae_mean = 3.5
            avg_mae_p95 = 6.0
            avg_mae_p75 = 4.8
            avg_mae_p50 = 3.2
        
        return SetupDrawdownProfile(
            setup_type=setup_type,
            sector=sector,
            mae_pct_mean=avg_mae_mean,
            mae_pct_p95=avg_mae_p95,
            mae_pct_p75=avg_mae_p75,
            mae_pct_p50=avg_mae_p50,
            sample_count=100,  # Synthetic
            win_rate_pct=63.0,  # Conservative estimate
        )
    
    @staticmethod
    def apply_fragility_downgrade(
        base_confidence: float,
        drawdown_analysis: DrawdownAnalysis,
    ) -> Tuple[float, str]:
        """
        Downgrade confidence if setup is fragile.
        
        Args:
            base_confidence: 0-100 confidence before fragility adjustment
            drawdown_analysis: DrawdownAnalysis object
        
        Returns:
            (adjusted_confidence, explanation)
        """
        
        if drawdown_analysis.fragility_level == FragilityLevel.ROBUST:
            # Boost by 10% for very robust stops
            adjusted = base_confidence * 1.1
            explanation = "Stop well-placed vs historical MAE (robust)."
        
        elif drawdown_analysis.fragility_level == FragilityLevel.NORMAL:
            # No adjustment
            adjusted = base_confidence
            explanation = "Stop within normal drawdown range."
        
        elif drawdown_analysis.fragility_level == FragilityLevel.FRAGILE:
            # Reduce by 30%
            adjusted = base_confidence * 0.7
            explanation = "Stop tighter than typical MAE (fragile). Whipsaw risk elevated."
        
        else:  # EXTREMELY_FRAGILE
            # Reduce by 60%, nearly block the trade
            adjusted = base_confidence * 0.4
            explanation = "Stop far tighter than historical MAE (extremely fragile). Strongly recommend suppression."
        
        return min(100, adjusted), explanation
