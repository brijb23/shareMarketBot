"""
Invalidation Level Calculation Engine

Determines stop loss and thesis break conditions.
Invalidation is mandatory - no trade without clear stops.
"""

from stock_analysis.common.models import Invalidation


class InvalidationCalculator:
    """
    Calculate stop loss and thesis invalidation levels.
    
    Strategy:
    Stop loss = Minimum of:
    1. 200 DMA − 1 ATR (technical support)
    2. Recent structural swing low (price pattern support)
    
    Key principle: Thesis invalidation is mandatory.
    If invalidation is unclear → no trade (returns None).
    
    Stop loss represents the point where the investment thesis breaks.
    Example thesis: "Stock will pull back to 50 DMA and bounce"
    If stock falls through 200 DMA support → thesis invalid → exit
    
    Example:
    200 DMA = 100, ATR = 2 → technical stop = 98
    Recent swing low = 97
    → Invalidation = min(98, 97) = 97
    """
    
    @staticmethod
    def calculate_invalidation(dma_200: float, atr: float, 
                              swing_low: float = None,
                              symbol: str = None) -> Invalidation:
        """
        Calculate stop loss and invalidation level.
        
        Args:
            dma_200: 200-day moving average
            atr: Average True Range (volatility)
            swing_low: Recent structural swing low price (optional)
            symbol: Stock symbol (optional, for reference)
        
        Returns:
            Invalidation object with stop loss level and reasoning
        
        Returns:
            None if:
            - Stop loss cannot be determined (missing data)
            - Inputs invalid or insufficient
            - Invalidation is unclear
        
        Raises:
            ValueError: If inputs wrong type
        
        Example:
            >>> calc = InvalidationCalculator()
            >>> inv = calc.calculate_invalidation(
            ...     dma_200=100.0,
            ...     atr=2.0,
            ...     swing_low=97.0
            ... )
            >>> if inv:
            ...     print(f"Stop loss: {inv.hard_stop}")
        """
        try:
            # Validate inputs
            if dma_200 is None or atr is None:
                return None
            
            if not isinstance(dma_200, (int, float)) or not isinstance(atr, (int, float)):
                return None
            
            if dma_200 <= 0 or atr <= 0:
                return None
            
            # Calculate technical stop: 200 DMA − 1 ATR
            technical_stop = dma_200 - (1.0 * atr)
            
            if technical_stop <= 0:
                return None
            
            # Determine invalidation level
            # If swing_low available, use minimum of both
            if swing_low is not None and isinstance(swing_low, (int, float)):
                if swing_low > 0:
                    # Use lower of the two stops (more conservative)
                    hard_stop = min(technical_stop, swing_low)
                    source = f"Structural swing low (${swing_low:.2f})"
                else:
                    hard_stop = technical_stop
                    source = f"200 DMA - 1 ATR"
            else:
                hard_stop = technical_stop
                source = f"200 DMA - 1 ATR"
            
            # Validate stop
            if hard_stop <= 0:
                return None
            
            return Invalidation(
                hard_stop_price=float(hard_stop),
                thesis_break_condition="Closing below hard stop level",
                thesis_break_price=float(hard_stop),
                stop_source=source,
                reasoning=f"Stop at {hard_stop:.2f} ({source}). "
                         f"Thesis invalid if price closes below stop."
            )
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error calculating invalidation: {str(e)}")
    
    @staticmethod
    def is_invalidation_triggered(invalidation: Invalidation, 
                                 current_price: float) -> bool:
        """
        Check if current price has triggered the invalidation (stop loss).
        
        Args:
            invalidation: Invalidation object with stop levels
            current_price: Current stock price
        
        Returns:
            True if price has broken through hard stop (thesis broken)
            False if price is still above stop (thesis intact)
            None if inputs invalid
        
        Example:
            >>> triggered = InvalidationCalculator.is_invalidation_triggered(
            ...     invalidation, current_price=96.5
            ... )
            >>> if triggered:
            ...     print("STOP LOSS HIT - EXIT POSITION")
        """
        try:
            if invalidation is None or current_price is None:
                return None
            
            if not isinstance(current_price, (int, float)):
                return None
            
            if invalidation.hard_stop_price is None:
                return None
            
            # Thesis broken if price closes below hard stop
            return current_price < invalidation.hard_stop_price
            
        except Exception as e:
            return None
