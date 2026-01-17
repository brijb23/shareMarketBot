"""
Convergence Signal Detector
Detects when Tech + Momentum align with improving Fundamentals
This catches institutional accumulation in recovery/PSU stocks
"""

from typing import Dict, Optional


class ConvergenceDetector:
    """
    Detect convergence signals for recovery and PSU stocks.
    
    Convergence occurs when:
    - Fundamentals are improving (trend = improving)
    - Technical breaks above key levels (Tech >= 65)
    - Momentum builds (RSI > 50, MACD positive, Volume increasing)
    
    This is the signal that institutional money is entering
    BEFORE quarterly financials improve (solving the lag problem)
    """
    
    @staticmethod
    def detect_convergence(
        symbol: str,
        stock_type: str,
        fund_score: float,
        fundamental_trend: Optional[Dict] = None,
        tech_score: float = 0,
        momentum_score: float = 0,
        rsi: float = 50,
        macd_histogram: float = 0,
        volume_trend: str = 'stable'
    ) -> Dict:
        """
        Detect convergence signal for entry.
        
        Args:
            symbol: Stock symbol
            stock_type: 'psu_government' or 'recovery_turnaround'
            fund_score: Fundamental score (0-100)
            fundamental_trend: Dict with 'direction' key
            tech_score: Technical score (0-100)
            momentum_score: Momentum score (0-100)
            rsi: RSI value (0-100)
            macd_histogram: MACD histogram (positive = bullish)
            volume_trend: 'increasing', 'stable', 'decreasing'
        
        Returns:
            {
                'has_convergence': bool,
                'signal_strength': float (0-100),
                'position_size': float (0.0-1.0),
                'reason': str,
                'components': dict
            }
        """
        
        # Convergence only for PSU/recovery stocks
        if stock_type not in ['psu_government', 'recovery_turnaround']:
            return {
                'has_convergence': False,
                'signal_strength': 0,
                'position_size': 0,
                'reason': f'Convergence only for PSU/recovery stocks, not {stock_type}',
                'components': {}
            }
        
        # Initialize convergence components
        components = {
            'fundamental_ok': False,
            'trend_improving': False,
            'technical_strong': False,
            'momentum_building': False,
            'volume_confirmed': False
        }
        
        # Check component 1: Fundamental quality (not too weak)
        if fund_score >= 50:  # Low but acceptable for recovery
            components['fundamental_ok'] = True
        
        # Check component 2: Trend is improving
        if fundamental_trend and fundamental_trend.get('direction') == 'improving':
            components['trend_improving'] = True
        
        # Check component 3: Technical is strong
        if tech_score >= 65:
            components['technical_strong'] = True
        
        # Check component 4: Momentum is building
        momentum_conditions = (
            rsi > 50 and  # RSI above neutral
            macd_histogram > 0 and  # MACD positive
            momentum_score >= 65  # Momentum score confirms
        )
        if momentum_conditions:
            components['momentum_building'] = True
        
        # Check component 5: Volume confirmed
        if volume_trend in ['increasing', 'stable']:  # Not decreasing
            components['volume_confirmed'] = True
        
        # Convergence requires AT LEAST 4 of 5 components
        components_passed = sum(1 for v in components.values() if v)
        has_convergence = components_passed >= 4
        
        # Calculate signal strength (0-100)
        signal_strength = (components_passed / 5) * 100
        
        # Position sizing based on signal strength
        # Convergence trades are smaller (higher risk)
        if has_convergence:
            if signal_strength >= 90:
                position_size = 0.75  # 75% of normal
                reason = 'STRONG CONVERGENCE: All signals aligned'
            elif signal_strength >= 80:
                position_size = 0.5  # 50% of normal
                reason = 'CONVERGENCE: Tech + Momentum + Improving Fundamentals'
            else:
                position_size = 0.33  # 33% of normal
                reason = 'WEAK CONVERGENCE: Some alignment, use caution'
        else:
            position_size = 0
            if fund_score < 50:
                reason = 'No convergence: Fundamental score too weak'
            elif components_passed < 3:
                reason = f'No convergence: Only {components_passed}/5 conditions met'
            else:
                reason = 'No convergence: Missing key signals'
        
        return {
            'has_convergence': has_convergence,
            'signal_strength': signal_strength,
            'position_size': position_size,
            'reason': reason,
            'components': components
        }
    
    @staticmethod
    def get_convergence_entry_signal(
        symbol: str,
        stock_type: str,
        convergence_data: Dict
    ) -> str:
        """
        Generate trading signal based on convergence.
        
        Returns: 'CONVERGENCE_BUY', 'HOLD', 'AVOID'
        """
        
        if not convergence_data.get('has_convergence'):
            return 'HOLD'
        
        if convergence_data['signal_strength'] >= 80:
            return 'CONVERGENCE_BUY'
        else:
            return 'HOLD'
