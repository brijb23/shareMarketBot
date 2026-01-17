"""
Profit Target Calculation Engine

Calculates risk/reward aligned profit targets.
Only returns targets if risk/reward ratio is favorable.
"""

from stock_analysis.common.models import Targets, BuyZone


class TargetCalculator:
    """
    Calculate profit targets based on entry and risk.
    
    Strategy:
    - Entry price = midpoint of buy zone
    - Base target = entry × 1.25 (25% return)
    - Optimistic target = entry × 1.40 (40% return)
    
    Risk/Reward Filter:
    Returns targets only if risk/reward >= 2.0
    This ensures asymmetric risk (win more than you lose).
    
    Risk/Reward Ratio = (target - entry) / (entry - invalidation)
    
    Example:
    Entry = 100, Invalidation = 95 (risk = 5)
    Base target = 100 × 1.25 = 125 (reward = 25)
    R/R = 25 / 5 = 5.0 ✓ (> 2.0, trade approved)
    
    Returns None if ratio < 2.0 (trade rejected).
    """
    
    @staticmethod
    def calculate_targets(buy_zone: BuyZone, invalidation_price: float,
                         symbol: str = None) -> Targets:
        """
        Calculate profit targets with risk/reward validation.
        
        Args:
            buy_zone: BuyZone with lower_bound and upper_bound
            invalidation_price: Stop loss price (hard limit)
            symbol: Stock symbol (optional, for reference)
        
        Returns:
            Targets object with base and optimistic targets
        
        Returns:
            None if:
            - Risk/reward ratio < 2.0 (asymmetry insufficient)
            - Inputs invalid or insufficient
            - Invalidation price >= entry price (no valid risk)
        
        Raises:
            ValueError: If buy_zone invalid or inputs are wrong type
        
        Example:
            >>> calc = TargetCalculator()
            >>> zone = BuyZone(lower_bound=98, upper_bound=102, ...)
            >>> targets = calc.calculate_targets(zone, invalidation_price=95)
            >>> if targets:
            ...     print(f"Base: {targets.base_target}")
            ...     print(f"Optimistic: {targets.optimistic_target}")
        """
        try:
            # Validate inputs
            if not isinstance(buy_zone, BuyZone):
                raise ValueError(f"buy_zone must be BuyZone, got {type(buy_zone).__name__}")
            
            if buy_zone.lower_bound is None or buy_zone.upper_bound is None:
                return None
            
            if invalidation_price is None:
                return None
            
            if not isinstance(invalidation_price, (int, float)):
                return None
            
            # Calculate entry as midpoint of buy zone
            entry_price = (buy_zone.lower_bound + buy_zone.upper_bound) / 2.0
            
            # Validate entry and invalidation
            if entry_price <= 0 or invalidation_price <= 0:
                return None
            
            # Invalidation must be below entry (stop loss)
            if invalidation_price >= entry_price:
                return None
            
            # Calculate risk
            risk = entry_price - invalidation_price
            
            if risk <= 0:
                return None
            
            # Calculate targets
            base_target = entry_price * 1.25
            optimistic_target = entry_price * 1.40
            
            # Calculate risk/reward ratios
            base_rr = (base_target - entry_price) / risk
            optimistic_rr = (optimistic_target - entry_price) / risk
            
            # Only return targets if minimum risk/reward >= 2.0
            # Use base target for minimum check (more conservative)
            if base_rr < 2.0:
                return None
            
            return Targets(
                entry_price=float(entry_price),
                base_target=float(base_target),
                optimistic_target=float(optimistic_target),
                base_target_rr=round(base_rr, 2),
                optimistic_target_rr=round(optimistic_rr, 2),
                reasoning=f"Entry {entry_price:.2f}, Risk {risk:.2f}, "
                         f"R/R Ratio {base_rr:.2f}x (Base) / {optimistic_rr:.2f}x (Optimistic)"
            )
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error calculating targets: {str(e)}")
