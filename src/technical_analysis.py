"""
Technical Analysis Engine
Analyzes price trends, momentum, and timing for entry/exit
"""

from typing import Dict, Tuple
from .data_models import TechnicalMetrics
from .constants import TECHNICAL_THRESHOLDS as THRESHOLDS


class TechnicalAnalyzer:
    """
    Deterministic technical analysis based on price action.
    Decision: IF timing is favorable for entry/exit.
    """
    
    def __init__(self):
        self.thresholds = THRESHOLDS
        self.rules_passed = []
        self.rules_failed = []
    
    def analyze(self, metrics: TechnicalMetrics) -> Tuple[str, Dict]:
        """
        Comprehensive technical analysis.
        
        Args:
            metrics: TechnicalMetrics object
            
        Returns:
            (trend_assessment, analysis_details_dict)
            trend_assessment: "uptrend", "weak_trend", "downtrend"
        """
        self.rules_passed = []
        self.rules_failed = []
        
        # Rule 1: Price positioning vs moving averages
        price_trend = self._analyze_moving_averages(metrics)
        
        # Rule 2: Momentum confirmation
        momentum_state = self._analyze_momentum(metrics)
        
        # Rule 3: Volume confirmation
        volume_confirmed = self._check_volume_confirmation(metrics)
        
        # Determine overall trend
        trend_assessment = self._determine_trend(
            price_trend, momentum_state, volume_confirmed
        )
        
        return trend_assessment, {
            "price_trend": price_trend,
            "momentum_state": momentum_state,
            "volume_confirmed": volume_confirmed,
            "trend_assessment": trend_assessment,
            "rules_passed": self.rules_passed,
            "rules_failed": self.rules_failed,
            "metrics": {
                "current_price": metrics.current_price,
                "sma_20": metrics.sma_20,
                "sma_200": metrics.sma_200,
                "rsi_14": metrics.rsi_14,
                "macd_histogram": metrics.macd_histogram,
                "volume_trend": metrics.volume_trend,
            }
        }
    
    def _analyze_moving_averages(self, metrics: TechnicalMetrics) -> str:
        """
        Rule: Trend defined by price position relative to moving averages.
        - Above 200 SMA: Long-term uptrend
        - Between 20 & 200 SMA: Weak/mixed trend
        - Below 20 SMA: Downtrend
        """
        if metrics.current_price > metrics.sma_200:
            if metrics.current_price > metrics.sma_20:
                self.rules_passed.append("Price > SMA-200 & SMA-20: Strong uptrend")
                return "above_200sma_and_20sma"
            else:
                self.rules_failed.append("Price < SMA-20 despite > SMA-200: Pullback/weakness")
                return "between_20_200sma"
        else:
            self.rules_failed.append("Price < SMA-200: Below long-term trend")
            return "below_200sma"
    
    def _analyze_momentum(self, metrics: TechnicalMetrics) -> str:
        """
        Rule: Momentum indicators confirm trend direction.
        - Positive: MACD > signal line, RSI 40-70
        - Neutral: MACD = signal, RSI 40-60
        - Negative: MACD < signal, RSI < 40
        """
        macd_positive = metrics.macd_line > metrics.macd_signal
        macd_negative = metrics.macd_line < metrics.macd_signal
        
        rsi_strong = metrics.rsi_14 > 50
        rsi_weak = metrics.rsi_14 < 50
        rsi_oversold = metrics.rsi_14 < 30
        rsi_overbought = metrics.rsi_14 > 70
        
        if macd_positive and rsi_strong and not rsi_overbought:
            self.rules_passed.append("MACD positive, RSI strong: Positive momentum")
            return "positive"
        elif macd_positive and rsi_oversold:
            self.rules_passed.append("MACD positive but RSI oversold: Weak positive")
            return "weak_positive"
        elif macd_negative and rsi_weak:
            self.rules_failed.append("MACD negative, RSI weak: Negative momentum")
            return "negative"
        else:
            self.rules_failed.append("MACD/RSI mixed signals: Indecisive")
            return "neutral"
    
    def _check_volume_confirmation(self, metrics: TechnicalMetrics) -> bool:
        """
        Rule: Volume must support the move.
        - Rising price + increasing volume = Genuine strength
        - Rising price + decreasing volume = Weak rally (warning)
        """
        if metrics.volume_trend == "increasing":
            self.rules_passed.append("Volume increasing: Move is confirmed")
            return True
        elif metrics.volume_trend == "stable":
            if metrics.current_volume > metrics.avg_volume_20d * 1.2:
                self.rules_passed.append("Volume above average: Reasonable confirmation")
                return True
            else:
                self.rules_failed.append("Volume below average: Weak confirmation")
                return False
        else:  # decreasing
            self.rules_failed.append("Volume decreasing: Move lacks confirmation")
            return False
    
    def _determine_trend(self, price_trend: str, momentum: str, volume_ok: bool) -> str:
        """
        Consolidate all technical signals into a trend assessment.
        Conservative rule: ALL must align for strong signals.
        """
        
        # Strong uptrend: above both SMAs, positive momentum, volume confirmed
        if (price_trend in ["above_200sma_and_20sma"] and 
            momentum in ["positive", "weak_positive"] and 
            volume_ok):
            return "uptrend"
        
        # Weak/mixed trend: ambiguous signals
        if price_trend == "between_20_200sma" or momentum == "neutral":
            return "weak_trend"
        
        # Downtrend: below trend lines or negative momentum
        if price_trend == "below_200sma" or momentum == "negative":
            return "downtrend"
        
        return "weak_trend"
    
    def get_timing_score(self, metrics: TechnicalMetrics) -> float:
        """
        Score from 0-100 for timing favorability.
        100 = Perfect entry setup, 0 = Avoid entry at all cost
        """
        trend, details = self.analyze(metrics)
        
        score = 50.0  # Base neutral score
        
        # Trend component: +/-25 points
        if trend == "uptrend":
            score += 25.0
        elif trend == "downtrend":
            score -= 25.0
        # weak_trend keeps score at 50
        
        # Price positioning: +/-10 points
        price_from_52w_high = ((metrics.price_52w_high - metrics.current_price) / 
                                metrics.price_52w_high) * 100
        if price_from_52w_high > 20:  # 20%+ below high = better entry
            score += 10.0
        elif price_from_52w_high < 5:  # Near 52w high = worse entry
            score -= 5.0
        
        # RSI extremes: volatility
        if metrics.rsi_14 > 70:
            score -= 10.0  # Overbought
        elif metrics.rsi_14 < 30:
            score += 5.0  # Oversold = potential bounce (but risky)
        
        return max(0.0, min(100.0, score))
    
    def get_entry_timing(self, metrics: TechnicalMetrics) -> str:
        """
        Specific timing recommendation.
        """
        trend, _ = self.analyze(metrics)
        
        if trend == "uptrend":
            if metrics.rsi_14 < 50:
                return "Good entry: Uptrend with pullback (RSI < 50)"
            else:
                return "Entry possible: Confirmed uptrend (wait for pullback)"
        elif trend == "downtrend":
            return "Avoid entry: Downtrend in progress"
        else:
            return "Wait: Trend unclear, no clear entry signal"
