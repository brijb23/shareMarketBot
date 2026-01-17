"""
Market Regime Filter
====================
Classifies market conditions (TRENDING, RANGING, RISK_OFF) and applies
confidence multiplier to trade setups based on regime alignment.

Lightweight implementation using:
- Index trend via EMA structure
- Volatility percentile (ATR-based)
- Market breadth (advance/decline ratio)

NO NEW INDICATORS: Uses only price + volume data already collected.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
import statistics


class MarketRegimeType(Enum):
    """Market condition classification."""
    TRENDING = "TRENDING"      # Strong directional bias, low dispersion
    RANGING = "RANGING"        # No clear direction, elevated but managed dispersion
    RISK_OFF = "RISK_OFF"       # Elevated volatility, flight to safety, panic selling


@dataclass
class MarketRegime:
    """Output from regime analysis."""
    regime_type: MarketRegimeType
    regime_strength: float          # 0-100: how confident in this regime classification
    confidence_multiplier: float    # 0.6-1.2: multiplier for trade confidence
    
    # Supporting metrics (for transparency)
    index_trend: str               # "UPTREND" / "DOWNTREND" / "SIDEWAYS"
    ema_alignment: float           # 0-100: how aligned EMA structure is
    volatility_percentile: float   # 0-100: historical volatility context
    breadth_ratio: float           # Advances / Declines: >1.2 = bullish, <0.8 = bearish
    
    # Explicit guidance
    regime_alignment: str          # "ALIGNED" / "MIXED" / "MISALIGNED"
    risk_warning: Optional[str]    # e.g., "Elevated volatility in ranging market"
    
    # NEW: Regime Instability Detection
    regime_instability: bool       # TRUE when volatility expanding or breadth collapsing
    instability_reason: Optional[str]  # Reason for instability flag (if TRUE)
    atr_expansion_rate: float      # Rate of ATR change over last N periods (%)
    breadth_deterioration: float   # Rate of breadth weakening (%)
    suppression_active: bool       # TRUE = suppress BUY/ACCUMULATE for 1-3 periods


class MarketRegimeFilter:
    """Lightweight market regime detection."""
    
    @staticmethod
    def analyze(
        index_prices: list,           # NIFTY50 or market index close prices (last 100+ bars)
        index_atr_values: list,       # ATR for same bars
        market_breadth: dict,         # {"advances": N, "declines": N}
        current_price: float,
        current_atr: float,
    ) -> MarketRegime:
        """
        Classify market regime and return confidence multiplier.
        
        Args:
            index_prices: Last 100+ closes of market index
            index_atr_values: ATR for same period
            market_breadth: dict with advances/declines counts
            current_price: Latest index close
            current_atr: Current ATR value
        
        Returns:
            MarketRegime with type, multiplier, and supporting metrics
        """
        
        # 1. INDEX TREND via EMA structure
        ema20, ema50, ema200 = MarketRegimeFilter._calculate_emas(index_prices)
        index_trend, ema_alignment = MarketRegimeFilter._assess_ema_structure(
            current_price, ema20, ema50, ema200
        )
        
        # 2. VOLATILITY PERCENTILE
        volatility_percentile = MarketRegimeFilter._calculate_volatility_percentile(
            index_atr_values
        )
        
        # 3. MARKET BREADTH
        breadth_ratio = MarketRegimeFilter._calculate_breadth_ratio(market_breadth)
        
        # 4. REGIME CLASSIFICATION
        regime_type, regime_strength, risk_warning = MarketRegimeFilter._classify_regime(
            index_trend, volatility_percentile, breadth_ratio
        )
        
        # 5. CONFIDENCE MULTIPLIER
        confidence_multiplier, regime_alignment = MarketRegimeFilter._assign_multiplier(
            regime_type, ema_alignment, breadth_ratio
        )
        
        # 6. NEW: REGIME INSTABILITY DETECTION
        atr_expansion = MarketRegimeFilter._calculate_atr_expansion_rate(index_atr_values)
        breadth_deterioration = MarketRegimeFilter._estimate_breadth_deterioration(market_breadth)
        regime_instability, instability_reason = MarketRegimeFilter._detect_instability(
            atr_expansion, breadth_deterioration, volatility_percentile
        )
        
        # If instability detected, set suppression flag
        suppression_active = regime_instability
        
        return MarketRegime(
            regime_type=regime_type,
            regime_strength=regime_strength,
            confidence_multiplier=confidence_multiplier,
            index_trend=index_trend,
            ema_alignment=ema_alignment,
            volatility_percentile=volatility_percentile,
            breadth_ratio=breadth_ratio,
            regime_alignment=regime_alignment,
            risk_warning=risk_warning,
            regime_instability=regime_instability,
            instability_reason=instability_reason,
            atr_expansion_rate=atr_expansion,
            breadth_deterioration=breadth_deterioration,
            suppression_active=suppression_active,
        )
    
    @staticmethod
    def _calculate_emas(prices: list) -> Tuple[float, float, float]:
        """Calculate 20, 50, 200-period EMAs."""
        if len(prices) < 200:
            # Fallback: use simple average if insufficient data
            return (
                statistics.mean(prices[-20:]) if len(prices) >= 20 else prices[-1],
                statistics.mean(prices[-50:]) if len(prices) >= 50 else prices[-1],
                statistics.mean(prices[-200:]) if len(prices) >= 200 else prices[-1],
            )
        
        def ema(data, period):
            multiplier = 2.0 / (period + 1)
            ema_val = data[0]
            for price in data[1:]:
                ema_val = price * multiplier + ema_val * (1 - multiplier)
            return ema_val
        
        return (
            ema(prices[-20:], 20),
            ema(prices[-50:], 50),
            ema(prices[-200:], 200),
        )
    
    @staticmethod
    def _assess_ema_structure(price: float, ema20: float, ema50: float, ema200: float) -> Tuple[str, float]:
        """
        Assess EMA alignment.
        
        Returns:
            (trend_direction, alignment_score)
        """
        # Perfect uptrend: price > EMA20 > EMA50 > EMA200
        # Perfect downtrend: price < EMA20 < EMA50 < EMA200
        # Perfect sideways: all EMAs within ~2% of each other
        
        ema_range = max(ema20, ema50, ema200) - min(ema20, ema50, ema200)
        ema_avg = (ema20 + ema50 + ema200) / 3
        ema_dispersion = ema_range / ema_avg if ema_avg > 0 else 0  # % spread
        
        uptrend_score = 0
        downtrend_score = 0
        
        # Uptrend checks
        if price > ema20:
            uptrend_score += 25
        if ema20 > ema50:
            uptrend_score += 25
        if ema50 > ema200:
            uptrend_score += 25
        if price > ema50:
            uptrend_score += 15
        
        # Downtrend checks
        if price < ema20:
            downtrend_score += 25
        if ema20 < ema50:
            downtrend_score += 25
        if ema50 < ema200:
            downtrend_score += 25
        if price < ema50:
            downtrend_score += 15
        
        # Determine trend
        if uptrend_score > downtrend_score and uptrend_score > 50:
            trend = "UPTREND"
            alignment = uptrend_score
        elif downtrend_score > uptrend_score and downtrend_score > 50:
            trend = "DOWNTREND"
            alignment = downtrend_score
        else:
            trend = "SIDEWAYS"
            # Sideways alignment: EMAs clustered (low dispersion)
            alignment = 100 - (ema_dispersion * 100) if ema_dispersion < 1 else 50
        
        return trend, min(100, alignment)
    
    @staticmethod
    def _calculate_volatility_percentile(atr_values: list) -> float:
        """
        Calculate current volatility as percentile of recent history.
        
        Returns:
            0-100: 0 = lowest volatility in period, 100 = highest
        """
        if len(atr_values) < 2:
            return 50.0  # Neutral default
        
        current_atr = atr_values[-1]
        recent_atr = atr_values[-50:] if len(atr_values) >= 50 else atr_values
        
        atr_min = min(recent_atr)
        atr_max = max(recent_atr)
        atr_range = atr_max - atr_min
        
        if atr_range == 0:
            return 50.0
        
        percentile = ((current_atr - atr_min) / atr_range) * 100
        return min(100, max(0, percentile))
    
    @staticmethod
    def _calculate_breadth_ratio(breadth: dict) -> float:
        """
        Calculate advances / declines ratio.
        
        >1.2: bullish breadth
        0.8-1.2: neutral breadth
        <0.8: bearish breadth
        """
        advances = breadth.get("advances", 0)
        declines = breadth.get("declines", 0)
        
        if declines == 0:
            return 1.0 if advances == 0 else 2.0  # Default neutral or strong bullish
        
        ratio = advances / declines
        return min(2.0, max(0.5, ratio))  # Cap at extremes
    
    @staticmethod
    def _classify_regime(
        trend: str,
        volatility_percentile: float,
        breadth_ratio: float,
    ) -> Tuple[MarketRegimeType, float, Optional[str]]:
        """
        Classify market regime based on trend, volatility, and breadth.
        
        Returns:
            (regime_type, regime_strength, risk_warning)
        """
        risk_warning = None
        
        # RISK_OFF: High volatility OR strong bearish breadth with downtrend
        if volatility_percentile > 75 or (breadth_ratio < 0.8 and trend == "DOWNTREND"):
            return MarketRegimeType.RISK_OFF, 85.0, "Elevated volatility and/or bearish breadth"
        
        # TRENDING: Clear trend + aligned breadth + moderate-to-high volatility
        if trend in ["UPTREND", "DOWNTREND"]:
            bullish_alignment = breadth_ratio > 1.2
            bearish_alignment = breadth_ratio < 0.8
            
            if (trend == "UPTREND" and bullish_alignment) or (trend == "DOWNTREND" and bearish_alignment):
                # Well-aligned trending
                strength = 85.0
                if volatility_percentile > 60:
                    risk_warning = "Trending but elevated volatility"
                return MarketRegimeType.TRENDING, strength, risk_warning
            else:
                # Trend but breadth misaligned (weakening trend)
                strength = 65.0
                risk_warning = f"{trend} but breadth not confirming (ratio: {breadth_ratio:.2f})"
                return MarketRegimeType.TRENDING, strength, risk_warning
        
        # RANGING: No clear trend, moderate volatility
        return MarketRegimeType.RANGING, 70.0, "No clear directional bias" if volatility_percentile > 50 else None
    
    @staticmethod
    def _assign_multiplier(
        regime: MarketRegimeType,
        ema_alignment: float,
        breadth_ratio: float,
    ) -> Tuple[float, str]:
        """
        Assign confidence multiplier based on regime alignment.
        
        TRENDING market:
          - BUY signals in direction of trend: 1.1-1.2x multiplier
          - BUY signals against trend: 0.6-0.75x multiplier
        
        RANGING market:
          - All signals: 0.8-0.9x multiplier (less reliable)
        
        RISK_OFF market:
          - All signals: 0.6-0.75x multiplier (high risk environment)
        
        Returns:
            (multiplier, alignment_description)
        """
        
        if regime == MarketRegimeType.TRENDING:
            if ema_alignment > 70:
                # Strong trend alignment
                multiplier = 1.15
                alignment = "ALIGNED"
            elif ema_alignment > 50:
                # Moderate trend alignment
                multiplier = 1.0
                alignment = "ALIGNED"
            else:
                # Weak alignment (trend weakening)
                multiplier = 0.75
                alignment = "MISALIGNED"
        
        elif regime == MarketRegimeType.RANGING:
            if breadth_ratio > 1.0 and breadth_ratio < 1.2:
                # Balanced breadth in ranging = neutral
                multiplier = 0.85
                alignment = "MIXED"
            elif breadth_ratio > 1.2:
                # Slightly bullish in range
                multiplier = 0.9
                alignment = "MIXED"
            elif breadth_ratio < 0.8:
                # Slightly bearish in range
                multiplier = 0.8
                alignment = "MIXED"
            else:
                multiplier = 0.85
                alignment = "MIXED"
        
        else:  # RISK_OFF
            if breadth_ratio < 0.7:
                # Panic selling
                multiplier = 0.6
                alignment = "MISALIGNED"
            else:
                # Moderate stress
                multiplier = 0.7
                alignment = "MISALIGNED"
        
        return multiplier, alignment
    
    @staticmethod
    def apply_regime_confidence(
        base_confidence: float,
        regime: MarketRegime,
    ) -> Tuple[float, str]:
        """
        Apply regime multiplier to base confidence score.
        
        Args:
            base_confidence: 0-100 confidence before regime adjustment
            regime: MarketRegime object
        
        Returns:
            (adjusted_confidence, explanation)
        """
        adjusted = base_confidence * regime.confidence_multiplier
        
        if regime.confidence_multiplier > 1.0:
            explanation = f"Boosted by favorable market regime ({regime.regime_type.value})"
        elif regime.confidence_multiplier < 1.0:
            explanation = f"Downgraded due to {regime.regime_type.value} conditions"
        else:
            explanation = "Market regime neutral"
        
        return min(100, adjusted), explanation
    
    @staticmethod
    def _calculate_atr_expansion_rate(atr_values: list) -> float:
        """
        Calculate ATR rate of change over last 10-20 periods.
        
        Returns:
            % change from 20-period baseline to current
        """
        if len(atr_values) < 20:
            return 0.0
        
        baseline_atr = statistics.mean(atr_values[-20:-10])
        current_atr = statistics.mean(atr_values[-5:])
        
        if baseline_atr == 0:
            return 0.0
        
        expansion_rate = ((current_atr - baseline_atr) / baseline_atr) * 100
        return expansion_rate
    
    @staticmethod
    def _estimate_breadth_deterioration(breadth: dict) -> float:
        """
        Estimate breadth deterioration from breadth ratio.
        
        Returns:
            % deterioration estimate (0-100)
        """
        ratio = breadth.get("breadth_ratio", 1.0)
        
        # breadth_ratio = advances / declines
        # 1.0 = neutral, >1.2 = bullish, <0.8 = bearish
        if ratio >= 1.2:
            return 0.0  # No deterioration
        elif ratio >= 1.0:
            return 10.0  # Slight deterioration
        elif ratio >= 0.8:
            return 30.0  # Moderate deterioration
        elif ratio >= 0.6:
            return 60.0  # Significant deterioration
        else:
            return 85.0  # Severe deterioration
    
    @staticmethod
    def _detect_instability(
        atr_expansion: float,
        breadth_deterioration: float,
        volatility_percentile: float,
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect regime instability (transition warning).
        
        TRUE when:
        - ATR expanding >25% from baseline AND volatility >70th percentile, OR
        - Breadth deteriorating >50% AND volatility >75th percentile
        
        Returns:
            (is_unstable, reason)
        """
        reasons = []
        
        # Check volatility expansion
        if atr_expansion > 25.0 and volatility_percentile > 70.0:
            reasons.append(f"Volatility expanding rapidly (ATR +{atr_expansion:.1f}%, vol {volatility_percentile:.0f}th percentile)")
        
        # Check breadth deterioration
        if breadth_deterioration > 50.0 and volatility_percentile > 75.0:
            reasons.append(f"Breadth deteriorating severely ({breadth_deterioration:.0f}%) with elevated volatility")
        
        # Combined condition: both metrics showing stress
        if atr_expansion > 20.0 and breadth_deterioration > 40.0:
            reasons.append("Multiple instability signals detected (ATR + breadth stress)")
        
        if reasons:
            return True, " | ".join(reasons)
        else:
            return False, None
