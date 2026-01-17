"""
Volatility-Adjusted Technical Scoring
For volatile stocks (mining, construction, cyclicals), adjust scoring
to recognize pullbacks as opportunities, not weaknesses
"""

from typing import Dict


class VolatilityAdjustedScoring:
    """
    Adjust technical scores for volatile stock types.
    Volatile doesn't mean bad - it means opportunities!
    """
    
    @staticmethod
    def adjust_tech_score(
        base_tech_score: float,
        stock_type: str,
        rsi: float,
        atr_percent: float,  # ATR as % of price
        price_vs_ma20: float,  # % above/below MA20
        volume_trend: str
    ) -> Dict:
        """
        Adjust technical score for stock type.
        
        Args:
            base_tech_score: Original tech score (0-100)
            stock_type: 'blue_chip', 'psu_government', 'recovery_turnaround', 'cyclical_volatile'
            rsi: RSI value (0-100)
            atr_percent: ATR as percentage of price
            price_vs_ma20: % distance from MA20 (negative = below, positive = above)
            volume_trend: 'increasing', 'stable', 'decreasing'
        
        Returns:
            {
                'adjusted_score': float,
                'adjustments': list of (adjustment, reason),
                'interpretation': str
            }
        """
        
        adjusted_score = base_tech_score
        adjustments = []
        
        # Different rules per stock type
        if stock_type == 'blue_chip':
            # Blue chips: standard scoring, no major adjustments
            # Only reward low volatility
            if atr_percent < 1.5:
                adjusted_score += 5
                adjustments.append((+5, "Low volatility - stable blue chip"))
        
        elif stock_type == 'psu_government':
            # PSU stocks: adjust for government intervention/policy effects
            # Don't penalize for moving on policy news
            
            # Oversold = opportunity to buy (RSI < 30 gets bonus)
            if rsi < 30:
                adjusted_score += 15
                adjustments.append((+15, "Oversold PSU - good entry opportunity"))
            
            # Volume spike matters more for PSUs (institution buying)
            if volume_trend == 'increasing':
                adjusted_score += 10
                adjustments.append((+10, "Increasing volume - institutional buying"))
            
            # Pullback in uptrend is opportunity
            if price_vs_ma20 < -5 and base_tech_score > 50:
                adjusted_score += 10
                adjustments.append((+10, "Pullback to MA20 - good entry in uptrend"))
        
        elif stock_type == 'recovery_turnaround':
            # Recovery stocks: volatility is normal, reward momentum
            
            # Oversold bounce is EXACTLY what we want
            if rsi < 25:
                adjusted_score += 20
                adjustments.append((+20, "Capitulation oversold - bounce opportunity"))
            elif rsi < 30:
                adjusted_score += 15
                adjustments.append((+15, "Oversold recovery - entry signal"))
            
            # RSI rising from oversold is bullish
            if 30 <= rsi <= 50:
                adjusted_score += 10
                adjustments.append((+10, "RSI rising from oversold - recovery forming"))
            
            # Volume must confirm recovery
            if volume_trend == 'increasing':
                adjusted_score += 15
                adjustments.append((+15, "Volume confirming recovery"))
            elif volume_trend == 'decreasing':
                adjusted_score -= 10
                adjustments.append((-10, "Decreasing volume - recovery weak"))
            
            # High volatility in recovery = normal, don't penalize
            if atr_percent > 3.0:
                # Don't penalize - volatility expected in recovery
                pass
        
        elif stock_type == 'cyclical_volatile':
            # Cyclical stocks: high standards, but reward breakouts
            
            # Breakout above key level with volume = strong signal
            if price_vs_ma20 > 5 and volume_trend == 'increasing':
                adjusted_score += 20
                adjustments.append((+20, "Breakout above MA20 on volume"))
            
            # Pullback to support = opportunity (if in uptrend)
            if price_vs_ma20 < -3 and base_tech_score >= 50:
                adjusted_score += 15
                adjustments.append((+15, "Pullback to support in uptrend"))
            
            # Overbought is NOT automatic sell for cyclicals
            if rsi > 70 and volume_trend == 'increasing':
                # Don't penalize - continuation pattern
                adjustments.append((0, "Overbought but volume increasing - continuation likely"))
            
            # Oversold is BIG opportunity for cyclicals
            if rsi < 25:
                adjusted_score += 25
                adjustments.append((+25, "Severe oversold - major reversal opportunity"))
        
        # Cap score at 100
        adjusted_score = min(100, max(0, adjusted_score))
        
        # Generate interpretation
        if adjusted_score >= 75:
            interpretation = "STRONG technical setup"
        elif adjusted_score >= 65:
            interpretation = "GOOD technical setup"
        elif adjusted_score >= 50:
            interpretation = "NEUTRAL technical setup"
        elif adjusted_score >= 35:
            interpretation = "WEAK technical setup"
        else:
            interpretation = "POOR technical setup"
        
        return {
            'adjusted_score': adjusted_score,
            'adjustments': adjustments,
            'interpretation': interpretation,
            'notes': f'Adjusted {base_tech_score:.0f} → {adjusted_score:.0f} for {stock_type}'
        }
    
    @staticmethod
    def interpret_volatility(
        stock_type: str,
        rsi: float,
        atr_percent: float
    ) -> str:
        """Interpret volatility for the stock type."""
        
        if stock_type == 'blue_chip':
            if atr_percent > 2.5:
                return "Unusual volatility - investigate news"
            else:
                return "Normal, stable volatility"
        
        elif stock_type == 'psu_government':
            if atr_percent > 3.0:
                return "Higher volatility - likely policy-driven"
            else:
                return "Stable volatility typical for PSU"
        
        elif stock_type == 'recovery_turnaround':
            if atr_percent > 4.0:
                return "High volatility - expected in recovery phase"
            else:
                return "Stabilizing volatility - recovery maturing"
        
        elif stock_type == 'cyclical_volatile':
            if atr_percent > 3.5:
                return "Normal high volatility for cyclical"
            else:
                return "Lower volatility - consolidating"
        
        return "Standard volatility"
