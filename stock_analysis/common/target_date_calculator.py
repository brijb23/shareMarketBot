"""
Target Date Calculator

Calculates realistic target achievement dates based on:
- Distance to target (% gain needed)
- Technical score (momentum/strength)
- Fundamental score (stability)
- Historical patterns
"""

from datetime import datetime, timedelta
import math


class TargetDateCalculator:
    """Calculate when price targets will be achieved based on analysis scores"""
    
    @staticmethod
    def calculate_target_date(current_price: float,
                             target_price: float,
                             technical_score: float,
                             fundamental_score: float,
                             momentum_score: float = 50) -> dict:
        """
        Calculate realistic target achievement date based on analysis scores.
        
        Methodology:
        - % Gain Required determines base timeframe
        - Technical Score (0-100) accelerates achievement (stronger technicals = faster)
        - Fundamental Score (0-100) indicates stability (higher = can hold position longer)
        - Momentum Score (0-100) shows institutional interest
        
        Base Timeframes:
        - 5-10% gain: 1-2 months (short-term weakness correction)
        - 10-20% gain: 2-4 months (normal rally)
        - 20-35% gain: 4-6 months (strong rally)
        - 35-50% gain: 6-9 months (recovery move)
        - 50%+ gain: 9-12 months (major trend shift)
        
        Args:
            current_price: Current stock price
            target_price: Target stock price
            technical_score: Technical score (0-100)
            fundamental_score: Fundamental score (0-100)
            momentum_score: Momentum score (0-100), default 50 (neutral)
        
        Returns:
            dict with:
                - target_date: Expected achievement date
                - months_to_target: Number of months
                - confidence: 'High', 'Medium', 'Low'
                - reasoning: Explanation
                - upside_pct: % gain to target
        """
        
        if current_price <= 0 or target_price <= current_price:
            return {
                'target_date': None,
                'months_to_target': 0,
                'confidence': 'N/A',
                'reasoning': 'Invalid price inputs',
                'upside_pct': 0
            }
        
        # Calculate % upside
        target_price = float(target_price)
        current_price = float(current_price)
        upside_pct = ((target_price - current_price) / current_price) * 100
        
        # Base timeframe in months based on % gain
        if upside_pct <= 5:
            base_months = 1.0
        elif upside_pct <= 10:
            base_months = 1.5
        elif upside_pct <= 20:
            base_months = 3.0
        elif upside_pct <= 35:
            base_months = 5.0
        elif upside_pct <= 50:
            base_months = 7.5
        else:
            base_months = 10.0
        
        # Technical Score Adjustment (0-100)
        # High technical score (80+) accelerates achievement by 25%
        # Low technical score (30-) delays achievement by 25%
        tech_multiplier = 1.0 + ((technical_score - 50) / 200)  # Range: 0.75 to 1.25
        
        # Momentum Score Adjustment (0-100)
        # High momentum (70+) accelerates by 15%
        # Institutional buying reduces time to target
        momentum_multiplier = 1.0 + ((momentum_score - 50) / 333)  # Range: 0.85 to 1.15
        
        # Fundamental Score Impact (0-100)
        # High fundamental score (75+) = more stable, longer holding period acceptable
        # Low fundamental score (40-) = need quick exit on weakness
        # This affects confidence, not speed
        
        # Calculate adjusted months to target
        adjusted_months = base_months * tech_multiplier * momentum_multiplier
        
        # Cap at reasonable bounds
        adjusted_months = max(0.5, min(12, adjusted_months))
        
        # Determine confidence level based on fundamental + technical alignment
        combined_score = (fundamental_score + technical_score) / 2
        
        if combined_score >= 70 and momentum_score >= 60:
            confidence = 'High'
            confidence_reason = 'Strong fundamentals, technicals, and institutional interest'
        elif combined_score >= 60 and momentum_score >= 50:
            confidence = 'Medium'
            confidence_reason = 'Good alignment of fundamentals and technicals'
        else:
            confidence = 'Low'
            confidence_reason = 'Mixed signals, more patience required'
        
        # Calculate target date
        today = datetime.now()
        target_date = today + timedelta(days=int(adjusted_months * 30.44))  # 30.44 days/month
        
        return {
            'target_date': target_date,
            'target_date_str': target_date.strftime('%b %Y'),  # e.g., "Apr 2026"
            'months_to_target': round(adjusted_months, 1),
            'confidence': confidence,
            'confidence_reason': confidence_reason,
            'reasoning': (
                f"{upside_pct:.1f}% upside | "
                f"Tech Score: {technical_score}/100 | "
                f"Fund Score: {fundamental_score}/100 | "
                f"Momentum: {momentum_score}/100"
            ),
            'upside_pct': round(upside_pct, 1)
        }
    
    @staticmethod
    def get_quarterly_target(target_date: datetime) -> str:
        """
        Convert target date to quarter format.
        
        Args:
            target_date: Target achievement date
        
        Returns:
            String like "Q1 2026", "Q2 2026", etc.
        """
        if not target_date:
            return "N/A"
        
        month = target_date.month
        year = target_date.year
        
        if month <= 3:
            quarter = "Q1"
        elif month <= 6:
            quarter = "Q2"
        elif month <= 9:
            quarter = "Q3"
        else:
            quarter = "Q4"
        
        return f"{quarter} {year}"
    
    @staticmethod
    def format_target_entry(current_price: float,
                           target_price: float,
                           technical_score: float,
                           fundamental_score: float,
                           momentum_score: float = 50) -> str:
        """
        Format complete target information for reports.
        
        Returns formatted string with date, timeframe, and confidence.
        """
        result = TargetDateCalculator.calculate_target_date(
            current_price, target_price, technical_score, fundamental_score, momentum_score
        )
        
        if result['target_date'] is None:
            return "N/A"
        
        return (
            f"Target: {result['upside_pct']:.1f}% | "
            f"By: {result['target_date_str']} ({result['months_to_target']} mo) | "
            f"Confidence: {result['confidence']}"
        )
