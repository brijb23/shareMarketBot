"""
Buy Zone Calculation Engine

Determines optimal entry price zones based on market structure.
Pure calculation logic - no scoring or decision making.
"""

from enum import Enum
from stock_analysis.common.models import BuyZone


class MarketStructure(Enum):
    """Market structure types determine buy zone calculation logic."""
    TREND_CONTINUATION = "trend_continuation"
    BREAKOUT_RETEST = "breakout_retest"
    CONSOLIDATION = "consolidation"


class BuyZoneCalculator:
    """
    Calculate optimal entry price zones based on market structure.
    
    Three distinct strategies based on price action pattern:
    
    1. TREND_CONTINUATION: Pullback in uptrend
       - Lower = 50 DMA - 1 ATR
       - Upper = 50 DMA + 0.5 ATR
    
    2. BREAKOUT_RETEST: Retest after breakout
       - Lower = Breakout level - 1 ATR
       - Upper = Breakout level
    
    3. CONSOLIDATION: Sideways range breakout
       - Lower = Range low + 25% of range
       - Upper = Range low + 50% of range
    
    Returns None if inputs insufficient for calculation.
    Never returns single price (always has spread).
    
    Example:
        calc = BuyZoneCalculator()
        zone = calc.calculate_buy_zone(
            market_structure=MarketStructure.TREND_CONTINUATION,
            dma_50=100.0,
            atr=2.0
        )
    """
    
    @staticmethod
    def calculate_buy_zone(market_structure: MarketStructure,
                           dma_50: float = None,
                           atr: float = None,
                           breakout_level: float = None,
                           range_low: float = None,
                           range_high: float = None,
                           symbol: str = None) -> BuyZone:
        """
        Calculate buy zone based on market structure.
        
        Args:
            market_structure: MarketStructure enum value
            dma_50: 50-day moving average (required for TREND_CONTINUATION)
            atr: Average True Range (required for all types)
            breakout_level: Price level of breakout (required for BREAKOUT_RETEST)
            range_low: Low of consolidation range (required for CONSOLIDATION)
            range_high: High of consolidation range (required for CONSOLIDATION)
            symbol: Stock symbol (optional, for reference)
        
        Returns:
            BuyZone object with lower_bound and upper_bound
        
        Raises:
            ValueError: If market_structure invalid or wrong type
            ValueError: If calculations fail (negative prices, inverted bounds)
        
        Returns:
            None if insufficient data for the given market structure
        
        Example:
            >>> calc = BuyZoneCalculator()
            >>> zone = calc.calculate_buy_zone(
            ...     MarketStructure.TREND_CONTINUATION,
            ...     dma_50=100.0,
            ...     atr=2.0
            ... )
            >>> print(f"Buy between {zone.lower_bound} and {zone.upper_bound}")
            Buy between 98.0 and 101.0
        """
        try:
            # Validate market_structure
            if not isinstance(market_structure, MarketStructure):
                raise ValueError(f"market_structure must be MarketStructure enum, "
                               f"got {type(market_structure).__name__}")
            
            # Route to appropriate calculation
            if market_structure == MarketStructure.TREND_CONTINUATION:
                return BuyZoneCalculator._calculate_trend_continuation(
                    dma_50, atr, symbol
                )
            elif market_structure == MarketStructure.BREAKOUT_RETEST:
                return BuyZoneCalculator._calculate_breakout_retest(
                    breakout_level, atr, symbol
                )
            elif market_structure == MarketStructure.CONSOLIDATION:
                return BuyZoneCalculator._calculate_consolidation(
                    range_low, range_high, symbol
                )
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error calculating buy zone: {str(e)}")
    
    @staticmethod
    def _calculate_trend_continuation(dma_50: float, atr: float, 
                                     symbol: str = None) -> BuyZone:
        """
        Calculate buy zone for trend continuation (pullback in uptrend).
        
        Strategy: Stock pulls back to 50 DMA and supports there.
        
        lower = 50 DMA − 1 ATR
        upper = 50 DMA + 0.5 ATR
        
        Returns None if dma_50 or atr missing.
        """
        # Validate inputs
        if dma_50 is None or atr is None:
            return None
        
        if not isinstance(dma_50, (int, float)) or not isinstance(atr, (int, float)):
            return None
        
        if dma_50 <= 0 or atr <= 0:
            return None
        
        # Calculate bounds
        lower = dma_50 - (1.0 * atr)
        upper = dma_50 + (0.5 * atr)
        
        # Validate bounds
        if lower >= upper or lower <= 0:
            return None
        
        return BuyZone(
            lower_bound=float(lower),
            upper_bound=float(upper),
            strategy="Trend Continuation",
            reasoning="Pullback to 50 DMA support in uptrend"
        )
    
    @staticmethod
    def _calculate_breakout_retest(breakout_level: float, atr: float,
                                   symbol: str = None) -> BuyZone:
        """
        Calculate buy zone for breakout retest.
        
        Strategy: Stock breaks resistance, pulls back to retest, re-enters above.
        
        lower = breakout_level − 1 ATR
        upper = breakout_level
        
        Returns None if breakout_level or atr missing.
        """
        # Validate inputs
        if breakout_level is None or atr is None:
            return None
        
        if not isinstance(breakout_level, (int, float)) or not isinstance(atr, (int, float)):
            return None
        
        if breakout_level <= 0 or atr <= 0:
            return None
        
        # Calculate bounds
        lower = breakout_level - (1.0 * atr)
        upper = breakout_level
        
        # Validate bounds
        if lower >= upper or lower <= 0:
            return None
        
        return BuyZone(
            lower_bound=float(lower),
            upper_bound=float(upper),
            strategy="Breakout Retest",
            reasoning="Retest of breakout level before next leg up"
        )
    
    @staticmethod
    def _calculate_consolidation(range_low: float, range_high: float,
                                symbol: str = None) -> BuyZone:
        """
        Calculate buy zone for consolidation breakout.
        
        Strategy: Stock consolidates in range, buy zone is upper portion of range.
        
        range = range_high - range_low
        lower = range_low + 25% of range
        upper = range_low + 50% of range
        
        Returns None if range_low or range_high missing.
        """
        # Validate inputs
        if range_low is None or range_high is None:
            return None
        
        if not isinstance(range_low, (int, float)) or not isinstance(range_high, (int, float)):
            return None
        
        if range_low <= 0 or range_high <= 0:
            return None
        
        # Validate range_high > range_low
        if range_high <= range_low:
            return None
        
        # Calculate range and percentages
        range_size = range_high - range_low
        lower = range_low + (0.25 * range_size)
        upper = range_low + (0.50 * range_size)
        
        # Validate bounds
        if lower >= upper or lower <= 0:
            return None
        
        return BuyZone(
            lower_bound=float(lower),
            upper_bound=float(upper),
            strategy="Consolidation Breakout",
            reasoning="Upper half of consolidation range, entry before breakout"
        )

