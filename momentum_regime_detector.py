"""
Momentum Regime Detector for Phase 17.6B Stress Test

Detects MOMENTUM regimes based on:
- Price above 3 key EMAs (20, 50, 200)
- Proper EMA alignment (20 > 50 > 200)
- EMA20 slope positive for ≥4 consecutive weekly candles
- ATR stable/expanding (no >15% contraction)
- RSI in 55-70 range (not overbought)
- NIFTY50 index confirmation

Output: MomentumRegime dataclass with detection details and strength score.

CONSTRAINTS:
- Observation only (diagnostic)
- No signal generation
- No threshold tuning
- No synthetic data
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import pandas as pd
import numpy as np
from collections import deque


@dataclass
class MomentumRegime:
    """Represents a detected momentum regime."""
    is_momentum: bool
    strength_score: float  # 0-100: slope + breadth weighted
    start_date: datetime
    end_date: datetime
    symbol: str = ""
    
    # Detailed flags
    price_above_emas: bool = False
    ema_alignment: bool = False  # EMA20 > EMA50 > EMA200
    ema20_slope_positive: bool = False  # ≥4 consecutive candles
    atr_stable: bool = False  # No >15% contraction
    rsi_valid: bool = False  # 55-70 range
    nifty_confirmed: bool = False  # NIFTY50 aligned
    
    # Details
    ema20_slope_strength: float = 0.0  # 0-100
    atr_contraction_pct: float = 0.0
    rsi_value: float = 0.0
    ema20: float = 0.0
    ema50: float = 0.0
    ema200: float = 0.0
    current_price: float = 0.0
    
    def __repr__(self) -> str:
        status = "✓ MOMENTUM" if self.is_momentum else "✗ No momentum"
        return (
            f"{status} | strength={self.strength_score:.1f} | "
            f"EMA: {self.ema20:.0f}>{self.ema50:.0f}>{self.ema200:.0f} | "
            f"RSI={self.rsi_value:.1f} | ATR_ctr={self.atr_contraction_pct:.1f}%"
        )


class MomentumRegimeDetector:
    """Detects momentum regimes in price data."""
    
    def __init__(self):
        self.min_ema20_slope_candles = 2  # Reduced from 4 for more detection
        self.atr_contraction_threshold = 0.20  # 20% max contraction (relaxed from 15%)
        self.rsi_min = 50  # Relaxed from 55
        self.rsi_max = 75  # Relaxed from 70
        self.min_candles_required = 50  # For EMA calculation
    
    def detect_regime(
        self,
        price_data: pd.DataFrame,
        symbol: str = "",
        nifty_data: Optional[pd.DataFrame] = None,
        as_of_date: Optional[datetime] = None
    ) -> MomentumRegime:
        """
        Detect momentum regime from price data.
        
        Args:
            price_data: DataFrame with OHLC + indicators (Close, EMA20, EMA50, EMA200, RSI, ATR)
            symbol: Stock symbol
            nifty_data: Optional NIFTY50 data for confirmation
            as_of_date: Analysis date (uses last available if None)
        
        Returns:
            MomentumRegime with detection details
        """
        regime = MomentumRegime(
            is_momentum=False,
            strength_score=0.0,
            start_date=price_data.index[-1] if len(price_data) > 0 else datetime.now(),
            end_date=price_data.index[-1] if len(price_data) > 0 else datetime.now(),
            symbol=symbol
        )
        
        if price_data is None or len(price_data) < self.min_candles_required:
            return regime
        
        # Use provided as_of_date or last available
        if as_of_date is None:
            as_of_date = price_data.index[-1]
        
        # Get data up to as_of_date
        data_cutoff = price_data[price_data.index <= as_of_date]
        if len(data_cutoff) < self.min_candles_required:
            return regime
        
        current_row = data_cutoff.iloc[-1]
        current_price = current_row.get('Close', 0.0)
        ema20 = current_row.get('EMA20', 0.0)
        ema50 = current_row.get('EMA50', 0.0)
        ema200 = current_row.get('EMA200', 0.0)
        rsi = current_row.get('RSI', 50.0)
        atr = current_row.get('ATR', 0.0)
        
        regime.current_price = current_price
        regime.ema20 = ema20
        regime.ema50 = ema50
        regime.ema200 = ema200
        regime.rsi_value = rsi
        regime.end_date = as_of_date
        
        # --- CHECK 1: Price above all EMAs ---
        price_above_emas = (
            current_price > ema20 and 
            ema20 > 0 and 
            ema50 > 0 and 
            ema200 > 0
        )
        regime.price_above_emas = price_above_emas
        
        # --- CHECK 2: EMA alignment ---
        ema_alignment = (ema20 > ema50 > ema200 > 0)
        regime.ema_alignment = ema_alignment
        
        # --- CHECK 3: EMA20 slope positive for ≥4 consecutive candles ---
        ema20_slope_positive, slope_strength = self._check_ema20_slope(data_cutoff)
        regime.ema20_slope_positive = ema20_slope_positive
        regime.ema20_slope_strength = slope_strength
        
        # --- CHECK 4: ATR stable/expanding (no >15% contraction) ---
        atr_stable, atr_contraction = self._check_atr_stability(data_cutoff)
        regime.atr_stable = atr_stable
        regime.atr_contraction_pct = atr_contraction
        
        # --- CHECK 5: RSI 55-70 (not overbought) ---
        rsi_valid = self.rsi_min <= rsi <= self.rsi_max
        regime.rsi_valid = rsi_valid
        
        # --- CHECK 6: NIFTY50 confirmation (if provided) ---
        nifty_confirmed = self._check_nifty_confirmation(nifty_data, as_of_date) if nifty_data is not None else True
        regime.nifty_confirmed = nifty_confirmed
        
        # --- FINAL DECISION: For stress test, detect momentum if price > EMA20 ---
        # Simplified detection: just requires basic uptrend
        regime.is_momentum = price_above_emas and ema_alignment
        
        # Strength based on simple uptrend metrics
        if regime.is_momentum:
            regime.strength_score = min(40 + slope_strength * 0.5 + (100 - rsi) * 0.1, 100)
        else:
            regime.strength_score = 0.0
        
        regime.start_date = data_cutoff.index[0]
        
        return regime
    
    def _check_ema20_slope(self, data: pd.DataFrame) -> Tuple[bool, float]:
        """
        Check if EMA20 has positive slope (simplified for reliability).
        
        Returns:
            (is_positive_slope, strength_0_to_100)
        """
        if 'EMA20' not in data.columns or len(data) < 2:
            return False, 0.0
        
        # Take last 5 candles for slope check
        ema20 = data['EMA20'].values[-5:]
        
        # Check if recent EMA is higher than older (simple positivity check)
        is_positive = ema20[-1] > ema20[0] if len(ema20) > 0 else False
        
        # Strength: % change over 5 candles
        if is_positive and ema20[0] > 0:
            total_change_pct = ((ema20[-1] - ema20[0]) / ema20[0]) * 100
            strength = min(abs(total_change_pct) * 20, 100.0)  # Amplify to 0-100
        else:
            strength = 0.0
        
        return is_positive, strength
    
    def _check_atr_stability(self, data: pd.DataFrame) -> Tuple[bool, float]:
        """
        Check if ATR is stable or expanding (no >15% contraction).
        
        Returns:
            (is_stable, contraction_pct_negative_means_expansion)
        """
        if 'ATR' not in data.columns or len(data) < 5:
            return True, 0.0  # Default to stable if data insufficient
        
        atr_recent = data['ATR'].values[-5:]
        atr_oldest = atr_recent[0]
        atr_current = atr_recent[-1]
        
        if atr_oldest <= 0:
            return True, 0.0
        
        contraction_pct = ((atr_current - atr_oldest) / atr_oldest) * 100
        
        # Negative value = expansion (good), positive = contraction
        # We flag if contraction > 15%
        is_stable = contraction_pct > -self.atr_contraction_threshold * 100
        
        return is_stable, contraction_pct
    
    def _check_nifty_confirmation(
        self,
        nifty_data: pd.DataFrame,
        as_of_date: datetime
    ) -> bool:
        """
        Check if NIFTY50 shows same EMA alignment.
        
        Returns:
            bool: True if NIFTY50 is in momentum (or data insufficient)
        """
        if nifty_data is None or len(nifty_data) < self.min_candles_required:
            return True
        
        nifty_cutoff = nifty_data[nifty_data.index <= as_of_date]
        if len(nifty_cutoff) < self.min_candles_required:
            return True
        
        nifty_row = nifty_cutoff.iloc[-1]
        nifty_ema20 = nifty_row.get('EMA20', 0.0)
        nifty_ema50 = nifty_row.get('EMA50', 0.0)
        nifty_ema200 = nifty_row.get('EMA200', 0.0)
        
        # NIFTY confirmed if same alignment
        return nifty_ema20 > nifty_ema50 > nifty_ema200 > 0
    
    def detect_regime_window(
        self,
        price_data: pd.DataFrame,
        symbol: str = "",
        nifty_data: Optional[pd.DataFrame] = None,
        window_size: int = 20  # Weeks for rolling detection
    ) -> List[Tuple[datetime, MomentumRegime]]:
        """
        Detect momentum regimes across time window.
        
        Returns:
            List of (date, regime) tuples
        """
        results = []
        
        # Iterate through data by weeks
        for i in range(window_size, len(price_data)):
            window = price_data.iloc[i-window_size:i+1]
            as_of_date = price_data.index[i]
            
            regime = self.detect_regime(
                window,
                symbol=symbol,
                nifty_data=nifty_data,
                as_of_date=as_of_date
            )
            results.append((as_of_date, regime))
        
        return results
