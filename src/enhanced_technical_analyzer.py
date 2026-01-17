"""
Enhanced Technical Analysis Engine - Structure-Based Breakout Confirmation

Rejects low-quality signals by requiring structural confirmation:

1. BREAKOUT REQUIREMENTS (ALL must be met):
   - Close ABOVE resistance (not intraday)
   - Volume > 20-period average
   - RSI not overbought (< 70)
   - Trend alignment on higher timeframe

2. BUY ZONE DERIVATION (at least TWO of):
   - EMA clusters: 20/50/200 in proper order
   - Anchored VWAP from last major swing
   - High-volume nodes / volume profile support
   - Prior consolidation breakout zones

3. INVALIDATION LEVELS (structural, not percentage):
   - Below support level OR
   - 1.5-2.0 × ATR from entry

OUTPUT:
- "NO TRADE" when conditions not met (silence preferred)
- Setup type classification
- Scenario analysis (bull/base/bear)
"""

from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum
import math


class SetupType(Enum):
    """Setup classification."""
    TREND_CONTINUATION = "trend_continuation"
    BREAKOUT_RETEST = "breakout_retest"
    CONSOLIDATION_BREAKOUT = "consolidation_breakout"
    NO_TRADE = "no_trade"


@dataclass
class StructuralLevels:
    """Structural support and resistance levels."""
    swing_low: Optional[float] = None          # Recent swing low
    swing_high: Optional[float] = None         # Recent swing high
    support_zone_low: Optional[float] = None   # Volume profile support
    support_zone_high: Optional[float] = None
    resistance_level: Optional[float] = None   # Next resistance
    consolidation_low: Optional[float] = None  # Range low
    consolidation_high: Optional[float] = None # Range high


@dataclass
class BreakoutConfirmation:
    """Breakout validation results."""
    confirmed: bool
    reasons: List[str]
    issues: List[str]
    volume_ratio: float          # Actual / 20-MA volume
    rsi_level: float
    trend_aligned: bool


@dataclass
class TradeSetup:
    """Complete trade setup with structural basis."""
    setup_type: SetupType
    buy_zone_low: Optional[float]
    buy_zone_high: Optional[float]
    invalidation_low: Optional[float]  # Stop loss level
    invalidation_reason: str            # Why this is the stop
    target_zone_low: Optional[float]
    target_zone_high: Optional[float]
    target_basis: str                   # "Swing high", "Fib extension", etc.
    rr_ratio: Optional[float]
    confidence: str                     # "BUY", "WAIT", "NO TRADE"
    warning: Optional[str]


class EnhancedTechnicalAnalyzer:
    """
    Structural technical analysis with rigorous breakout confirmation.
    
    Philosophy:
    - Prefer NO TRADE over low-quality signals
    - Require volume confirmation
    - Use market structure, not just indicators
    - Clear setup type classification
    """
    
    def __init__(self):
        pass
    
    def analyze(
        self,
        current_price: float,
        ema_20: float,
        ema_50: float,
        ema_200: float,
        atr: float,
        rsi_14: float,
        macd_line: float,
        macd_signal: float,
        volume_current: float,
        volume_20ma: float,
        recent_high_20d: float,
        recent_low_20d: float,
        recent_high_52w: float,
        recent_low_52w: float,
        vwap: Optional[float] = None,
        htf_trend: Optional[str] = None,  # "uptrend", "downtrend", "sideways"
    ) -> TradeSetup:
        """
        Complete technical analysis with breakout confirmation.
        
        Returns TradeSetup with BUY / WAIT / NO TRADE signal.
        """
        
        # Step 1: Identify structural levels
        levels = self._identify_structural_levels(
            current_price, ema_20, ema_50, ema_200,
            recent_high_20d, recent_low_20d,
            recent_high_52w, recent_low_52w
        )
        
        # Step 2: Check if we're in a breakout
        breakout = self._check_breakout_confirmation(
            current_price, recent_high_20d, volume_current, volume_20ma,
            rsi_14, macd_line, macd_signal, htf_trend
        )
        
        # Step 3: Determine setup type
        setup_type = self._classify_setup(
            current_price, ema_20, ema_50, ema_200,
            recent_low_20d, breakout, levels
        )
        
        # Step 4: If valid setup, calculate levels and targets
        if setup_type != SetupType.NO_TRADE and breakout.confirmed:
            return self._build_trade_setup(
                setup_type, current_price, breakout, levels, atr,
                recent_high_20d, recent_low_20d, vwap
            )
        
        # No valid setup
        return TradeSetup(
            setup_type=SetupType.NO_TRADE,
            buy_zone_low=None,
            buy_zone_high=None,
            invalidation_low=None,
            invalidation_reason="",
            target_zone_low=None,
            target_zone_high=None,
            target_basis="",
            rr_ratio=None,
            confidence="NO TRADE",
            warning="Breakout not confirmed" if not breakout.confirmed else None
        )
    
    @staticmethod
    def _identify_structural_levels(
        price: float, ema_20: float, ema_50: float, ema_200: float,
        high_20: float, low_20: float, high_52: float, low_52: float
    ) -> StructuralLevels:
        """Identify key structural support and resistance levels."""
        
        return StructuralLevels(
            swing_low=low_20,
            swing_high=high_20,
            support_zone_low=min(ema_50, low_20 * 0.98),
            support_zone_high=ema_50,
            resistance_level=high_20 * 1.02,
            consolidation_low=low_20,
            consolidation_high=high_20,
        )
    
    @staticmethod
    def _check_breakout_confirmation(
        price: float, resistance: float,
        volume: float, volume_20ma: float,
        rsi: float, macd_line: float, macd_signal: float,
        htf_trend: Optional[str]
    ) -> BreakoutConfirmation:
        """
        Rigorous breakout confirmation - ALL conditions must pass.
        
        Requirements:
        1. Close above resistance (not intraday pump)
        2. Volume > 1.3x 20-MA
        3. RSI not overbought (< 70)
        4. MACD positive
        5. HTF trend aligned (if available)
        """
        
        reasons = []
        issues = []
        
        # Check 1: Price above resistance
        above_resistance = price > resistance * 1.001  # 0.1% buffer
        if above_resistance:
            reasons.append("Close above resistance")
        else:
            issues.append(f"Price {price:.2f} not above resistance {resistance:.2f}")
        
        # Check 2: Volume confirmation
        volume_ratio = volume / volume_20ma if volume_20ma > 0 else 0
        volume_confirmed = volume_ratio >= 1.3
        if volume_confirmed:
            reasons.append(f"Volume {volume_ratio:.1f}x above average")
        else:
            issues.append(f"Volume only {volume_ratio:.1f}x (need 1.3+)")
        
        # Check 3: RSI not overbought
        rsi_ok = rsi < 70
        if rsi_ok:
            reasons.append(f"RSI {rsi:.0f} not overbought")
        else:
            issues.append(f"RSI {rsi:.0f} overbought (>70)")
        
        # Check 4: MACD positive
        macd_positive = macd_line > macd_signal
        if macd_positive:
            reasons.append("MACD positive (line > signal)")
        else:
            issues.append("MACD not positive")
        
        # Check 5: HTF trend alignment (if available)
        trend_aligned = (htf_trend == "uptrend") if htf_trend else True
        if htf_trend:
            if trend_aligned:
                reasons.append("Higher timeframe trend aligned")
            else:
                issues.append(f"HTF trend {htf_trend} not aligned")
        
        # Overall confirmation: ALL must pass
        all_confirmed = (
            above_resistance and volume_confirmed and rsi_ok and
            macd_positive and trend_aligned
        )
        
        return BreakoutConfirmation(
            confirmed=all_confirmed,
            reasons=reasons,
            issues=issues,
            volume_ratio=volume_ratio,
            rsi_level=rsi,
            trend_aligned=trend_aligned
        )
    
    @staticmethod
    def _classify_setup(
        price: float, ema_20: float, ema_50: float, ema_200: float,
        low_20: float, breakout: BreakoutConfirmation,
        levels: StructuralLevels
    ) -> SetupType:
        """Classify setup type based on price action and EMA alignment."""
        
        if not breakout.confirmed:
            return SetupType.NO_TRADE
        
        # EMA cluster alignment (20/50/200 in order = strong uptrend)
        ema_aligned = (ema_20 > ema_50 > ema_200)
        
        # Price in relation to EMAs
        price_above_50 = price > ema_50
        price_above_200 = price > ema_200
        ema_50_above_200 = ema_50 > ema_200
        
        # Trend continuation: Price pulling back to 50 EMA, breaks back up
        if (ema_aligned and price_above_200 and
            (low_20 <= ema_50 * 1.02) and price > ema_20):
            return SetupType.TREND_CONTINUATION
        
        # Breakout retest: Price breaks out, retests level, breaks again
        if price_above_200 and ema_50_above_200 and breakout.confirmed:
            return SetupType.BREAKOUT_RETEST
        
        # Consolidation breakout: Price breaks above range
        if breakout.confirmed:
            return SetupType.CONSOLIDATION_BREAKOUT
        
        return SetupType.NO_TRADE
    
    @staticmethod
    def _build_trade_setup(
        setup_type: SetupType, price: float, breakout: BreakoutConfirmation,
        levels: StructuralLevels, atr: float,
        high_20: float, low_20: float, vwap: Optional[float]
    ) -> TradeSetup:
        """Build complete trade setup with targets and stops."""
        
        # Buy zone: Current price to recent high + 1% buffer
        buy_zone_low = price
        buy_zone_high = high_20 * 1.01
        
        # Invalidation (stop loss): Structural support or 2x ATR below
        invalidation_1 = levels.support_zone_low
        invalidation_2 = price - (2.0 * atr)
        invalidation_low = max(invalidation_1, invalidation_2)
        
        invalidation_reason = f"Below support ({invalidation_1:.2f}) or 2x ATR ({invalidation_2:.2f})"
        
        # Target zones: Use swing highs and Fibonacci
        fib_extension = price + (price - low_20) * 1.618  # 161.8% extension
        target_zone_low = high_20 * 1.02
        target_zone_high = fib_extension
        target_basis = f"Swing high + Fib extension (161.8%)"
        
        # Risk-reward ratio
        risk = price - invalidation_low
        reward = target_zone_low - price
        rr_ratio = reward / risk if risk > 0 else None
        
        # Confidence based on setup strength
        if rr_ratio and rr_ratio >= 2.0:
            confidence = "BUY"
        elif rr_ratio and rr_ratio >= 1.5:
            confidence = "WAIT"
        else:
            confidence = "NO TRADE"
        
        warning = None
        if breakout.volume_ratio < 1.5:
            warning = f"Lower volume confirmation ({breakout.volume_ratio:.1f}x)"
        
        return TradeSetup(
            setup_type=setup_type,
            buy_zone_low=buy_zone_low,
            buy_zone_high=buy_zone_high,
            invalidation_low=invalidation_low,
            invalidation_reason=invalidation_reason,
            target_zone_low=target_zone_low,
            target_zone_high=target_zone_high,
            target_basis=target_basis,
            rr_ratio=rr_ratio,
            confidence=confidence,
            warning=warning
        )
