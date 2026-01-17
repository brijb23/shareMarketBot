"""
Stock Classification System - Enhanced
Categorizes stocks into types (blue_chip, psu_government, recovery_turnaround, cyclical_volatile)
Each type has different thresholds and rules for improved decision-making
"""

from typing import Dict, Optional


class StockClassifier:
    """Classify stocks into categories for tailored analysis and decision thresholds"""
    
    # Government/PSU stocks - benefit from leverage and policy support
    PSU_STOCKS = {
        'HUDCO.NS', 'NTPC.NS', 'POWERGRID.NS', 'COALINDIA.NS', 'ONGC.NS',
        'SBIN.NS', 'BANKBARODA.NS', 'BPCL.NS', 'IOC.NS', 'BHEL.NS',
        'HCC.NS'  # HCC is cyclical BUT also PSU, classify as PSU
    }
    
    # Blue chip / Large cap stable - high quality
    BLUE_CHIP_STOCKS = {
        'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HDFC.NS', 'HDFCBANK.NS',
        'ICICIBANK.NS', 'KOTAKBANK.NS', 'NESTLEIND.NS', 'HINDUNILVR.NS',
        'ASIANPAINT.NS', 'MARUTI.NS', 'BAJAJFINSV.NS', 'MRF.NS'
    }
    
    # Cyclical / Mining / High volatility - need extra care
    CYCLICAL_VOLATILE_STOCKS = {
        'VEDL.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS',
        'EICHERMOT.NS', 'ADANIPORTS.NS'
    }
    
    @staticmethod
    def classify_stock(symbol: str, 
                      fundamental_trend: Optional[str] = None,
                      fund_score: Optional[float] = None) -> str:
        """
        Classify stock into category for threshold adjustment.
        
        Args:
            symbol: Stock symbol (e.g., 'HUDCO.NS')
            fundamental_trend: 'improving', 'stable', 'deteriorating' (optional)
            fund_score: Fundamental score (optional)
        
        Returns:
            Stock type: 'blue_chip', 'psu_government', 'recovery_turnaround', 'cyclical_volatile'
        """
        
        # Check for recovery classification (improving trend + decent fundamentals)
        if (symbol in StockClassifier.PSU_STOCKS or symbol in StockClassifier.CYCLICAL_VOLATILE_STOCKS):
            if (fundamental_trend == 'improving' and 
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
    def classify_stock_legacy(symbol: str) -> str:
        """
        Legacy method for backward compatibility.
        Returns: 'government', 'highly_volatile', 'stable_quality', or 'normal'
        """
        # Map new classification to old for backward compatibility
        new_class = StockClassifier.classify_stock(symbol)
        
        if new_class == 'psu_government':
            return 'government'
        elif new_class == 'cyclical_volatile':
            return 'highly_volatile'
        elif new_class == 'blue_chip':
            return 'stable_quality'
        else:
            return 'normal'
    
    @staticmethod
    def get_adjusted_thresholds(stock_type: str) -> Dict:
        """
        Get adjusted thresholds based on stock type (OLD NAMING for backward compatibility)
        Uses new STOCK_TYPE_THRESHOLDS internally.
        """
        # Map old names to new thresholds
        type_mapping = {
            'government': 'psu_government',
            'highly_volatile': 'cyclical_volatile',
            'stable_quality': 'blue_chip',
            'normal': 'blue_chip'
        }
        
        new_type = type_mapping.get(stock_type, 'blue_chip')
        return StockClassifier.get_thresholds(new_type)
    
    @staticmethod
    def get_thresholds(stock_type: str) -> Dict:
        """
        Get decision thresholds for a stock type (NEW naming).
        
        Args:
            stock_type: Type from classify_stock()
        
        Returns:
            Dict with fund_min, tech_min, and other rules
        """
        
        thresholds = {
            'blue_chip': {
                'fund': 65,
                'tech': 65,
                'momentum': 60,
                'fund_weight': 0.40,
                'tech_weight': 0.30,
                'momentum_weight': 0.15,
                'fundamental_lag_months': 6,
                'allow_convergence': False,
                'position_size': 1.0,
                'review_frequency': 'monthly',
                'description': 'Strict: Both fund & tech must be strong'
            },
            
            'psu_government': {
                'fund': 55,  # Lowered - PSUs have leverage & policy support
                'tech': 60,  # Respond to policy more than technicals
                'momentum': 60,
                'fund_weight': 0.35,
                'tech_weight': 0.30,
                'momentum_weight': 0.20,
                'fundamental_lag_months': 24,
                'allow_convergence': True,  # Can enter early if momentum builds
                'position_size': 1.0,
                'review_frequency': 'bi_weekly',
                'description': 'Relaxed: PSUs allowed at lower thresholds due to leverage & policy'
            },
            
            'recovery_turnaround': {
                'fund': 50,  # Low - improving trend matters more
                'tech': 65,  # HIGH - need clear technical confirmation
                'momentum': 65,  # Momentum critical for recovery plays
                'fund_weight': 0.30,
                'tech_weight': 0.35,
                'momentum_weight': 0.25,
                'fundamental_lag_months': 12,
                'allow_convergence': True,  # Convergence is main entry signal
                'position_size': 0.5,  # 50% - higher risk
                'review_frequency': 'weekly',
                'description': 'Recovery: Lower fund but needs improving trend + strong tech + momentum'
            },
            
            'cyclical_volatile': {
                'fund': 60,  # Moderate - higher quality for risky cyclicals
                'tech': 70,  # HIGH - crystal clear entry needed
                'momentum': 65,
                'fund_weight': 0.30,
                'tech_weight': 0.40,
                'momentum_weight': 0.20,
                'fundamental_lag_months': 18,
                'allow_convergence': False,  # Too risky for convergence
                'position_size': 0.5,  # 50% - very volatile
                'review_frequency': 'weekly',
                'description': 'Cyclical: High thresholds due to volatility risk'
            }
        }
        
        return thresholds.get(stock_type, thresholds['blue_chip'])
    
    @staticmethod
    def is_government_stock(symbol: str) -> bool:
        """Quick check if stock is government enterprise"""
        return symbol in StockClassifier.PSU_STOCKS
