"""
Stock Classification Engine
Categorizes stocks into types (blue_chip, psu_government, recovery, cyclical)
Each type has different thresholds and rules
"""

from typing import Dict, List, Optional


class StockClassifier:
    """
    Classify stocks into categories for dynamic threshold application.
    
    Categories:
    - blue_chip: Stable, high-quality (TCS, HDFC, INFY)
    - psu_government: Government-backed infrastructure (HUDCO, NTPC, POWERGRID)
    - recovery_turnaround: Improving from weak state (HCC, recently weak stocks)
    - cyclical_volatile: Mining, construction, high volatility (VEDL, JSPL, HCC when falling)
    """
    
    # Government/PSU stocks
    PSU_STOCKS = {
        'HUDCO.NS', 'NTPC.NS', 'POWERGRID.NS', 'COALINDIA.NS', 'ONGC.NS',
        'SBIN.NS', 'BANKBARODA.NS', 'BPCL.NS', 'IOC.NS', 'BHEL.NS'
    }
    
    # Blue chip / Large cap stable
    BLUE_CHIP_STOCKS = {
        'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HDFC.NS', 'HDFCBANK.NS',
        'ICICIBANK.NS', 'KOTAKBANK.NS', 'NESTLEIND.NS', 'HINDUNILVR.NS',
        'ASIANPAINT.NS', 'MARUTI.NS', 'BAJAJFINSV.NS'
    }
    
    # Cyclical / Mining / High volatility
    CYCLICAL_VOLATILE_STOCKS = {
        'VEDL.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS',
        'HCC.NS', 'EICHERMOT.NS', 'ADANIPORTS.NS'
    }
    
    # Can be classified as recovery if fundamental trend is improving
    RECOVERY_CANDIDATES = {
        'HCC.NS', 'VEDL.NS', 'HUDCO.NS', 'NTPC.NS', 'COALINDIA.NS',
        'TATASTEEL.NS', 'JSWSTEEL.NS'
    }
    
    @staticmethod
    def classify(symbol: str, 
                 fundamental_trend: Optional[str] = None,
                 fund_score: Optional[float] = None) -> str:
        """
        Classify a stock into a category.
        
        Args:
            symbol: Stock symbol (e.g., 'HUDCO.NS')
            fundamental_trend: 'improving', 'stable', 'deteriorating' (optional, for recovery detection)
            fund_score: Fundamental score (optional, helps with recovery detection)
        
        Returns:
            Stock type: 'blue_chip', 'psu_government', 'recovery_turnaround', 'cyclical_volatile'
        """
        
        # Check for recovery classification first (most specific)
        if (symbol in StockClassifier.RECOVERY_CANDIDATES and 
            fundamental_trend == 'improving' and 
            fund_score is not None and fund_score >= 50):
            return 'recovery_turnaround'
        
        # Check blue chips
        if symbol in StockClassifier.BLUE_CHIP_STOCKS:
            return 'blue_chip'
        
        # Check PSU
        if symbol in StockClassifier.PSU_STOCKS:
            return 'psu_government'
        
        # Check cyclical
        if symbol in StockClassifier.CYCLICAL_VOLATILE_STOCKS:
            return 'cyclical_volatile'
        
        # Default: treat as blue chip (conservative)
        return 'blue_chip'
    
    @staticmethod
    def get_thresholds(stock_type: str) -> Dict:
        """
        Get decision thresholds for a stock type.
        
        Args:
            stock_type: Type from classify()
        
        Returns:
            Dict with fund_min, tech_min, and other rules
        """
        
        thresholds = {
            'blue_chip': {
                'fund_min': 65,
                'tech_min': 65,
                'allow_convergence': False,
                'position_size': 1.0,  # 100% of normal
                'review_frequency': 'monthly',
                'description': 'Strict filters: Both fund & tech must be strong'
            },
            
            'psu_government': {
                'fund_min': 55,  # Lowered - PSUs have leverage but stable cash flows
                'tech_min': 60,  # Lowered - respond to policy more than technicals
                'allow_convergence': True,  # Can enter early if momentum builds
                'position_size': 1.0,  # Full position (PSUs are stable)
                'review_frequency': 'bi_weekly',  # Check for policy changes
                'description': 'Relaxed: PSUs allowed at lower thresholds due to leverage & policy tailwinds'
            },
            
            'recovery_turnaround': {
                'fund_min': 50,  # Low - improving trend matters more than absolute score
                'tech_min': 65,  # HIGH - need clear technical confirmation
                'momentum_min': 65,  # NEW: Momentum is critical for recovery plays
                'allow_convergence': True,  # Convergence is the main entry signal
                'position_size': 0.5,  # 50% of normal (higher risk)
                'review_frequency': 'weekly',  # Watch closely - volatile
                'description': 'Recovery: Lower fund threshold but needs improving trend + tech + momentum'
            },
            
            'cyclical_volatile': {
                'fund_min': 60,  # Moderate - higher quality needed for risky cyclicals
                'tech_min': 70,  # HIGH - need crystal clear entry
                'volume_required': True,  # Volume confirmation essential
                'support_level_required': True,  # Must bounce off support
                'position_size': 0.5,  # 50% of normal (very volatile)
                'review_frequency': 'weekly',  # Daily in volatile periods
                'description': 'Cyclical: High thresholds due to volatility risk'
            }
        }
        
        return thresholds.get(stock_type, thresholds['blue_chip'])


class FundamentalTrendDetector:
    """
    Track fundamental score changes over time to detect improvements/deterioration.
    """
    
    # Store historical scores (in production, this would be a database)
    _history = {}
    
    @staticmethod
    def record_score(symbol: str, quarter: str, score: float):
        """Record fundamental score for a symbol in a quarter."""
        if symbol not in FundamentalTrendDetector._history:
            FundamentalTrendDetector._history[symbol] = {}
        FundamentalTrendDetector._history[symbol][quarter] = score
    
    @staticmethod
    def detect_trend(symbol: str, current_score: float) -> Dict:
        """
        Detect if fundamentals are improving, stable, or deteriorating.
        
        Returns:
            {
                'direction': 'improving' | 'stable' | 'deteriorating',
                'change': float (points),
                'velocity': 'accelerating' | 'constant' | 'decelerating',
                'quarters_improving': int,
                'confidence': float (0-100)
            }
        """
        
        history = FundamentalTrendDetector._history.get(symbol, {})
        
        if len(history) < 2:
            # Not enough data
            return {
                'direction': 'unknown',
                'change': 0,
                'velocity': 'unknown',
                'quarters_improving': 0,
                'confidence': 0
            }
        
        # Get last 4 quarters
        sorted_quarters = sorted(history.items())
        recent_scores = [score for _, score in sorted_quarters[-4:]]
        
        if len(recent_scores) < 2:
            return {
                'direction': 'unknown',
                'change': 0,
                'velocity': 'unknown',
                'quarters_improving': 0,
                'confidence': 0
            }
        
        # Calculate trend metrics
        previous_score = recent_scores[-2]
        change = current_score - previous_score
        
        # Detect direction
        if change > 2:  # At least 2 points improvement
            direction = 'improving'
            quarters_improving = sum(1 for i in range(1, len(recent_scores)) 
                                    if recent_scores[i] > recent_scores[i-1])
        elif change < -2:  # More than 2 points deterioration
            direction = 'deteriorating'
            quarters_improving = 0
        else:
            direction = 'stable'
            quarters_improving = sum(1 for i in range(1, len(recent_scores)) 
                                    if recent_scores[i] >= recent_scores[i-1] - 1)
        
        # Detect velocity (rate of change)
        if len(recent_scores) >= 3:
            prev_change = recent_scores[-2] - recent_scores[-3]
            if abs(change) > abs(prev_change):
                velocity = 'accelerating'
            elif abs(change) < abs(prev_change) and abs(change) > 0:
                velocity = 'decelerating'
            else:
                velocity = 'constant'
        else:
            velocity = 'constant'
        
        # Confidence: higher if consistent trend
        confidence = min(100, 50 + (quarters_improving * 10) + (abs(change) * 2))
        
        return {
            'direction': direction,
            'change': change,
            'velocity': velocity,
            'quarters_improving': quarters_improving,
            'confidence': confidence
        }
