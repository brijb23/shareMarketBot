"""
Common utilities and helpers (no business logic).
"""

from decimal import Decimal
from typing import List, Optional


def round_price(price: Decimal, decimals: int = 2) -> Decimal:
    """
    Round a price to standard decimal places.
    
    Args:
        price: Price value
        decimals: Number of decimal places (default 2 for INR)
    
    Returns:
        Rounded Decimal
    """
    pass


def percentage_change(start: Decimal, end: Decimal) -> float:
    """
    Calculate percentage change from start to end.
    
    Args:
        start: Starting price
        end: Ending price
    
    Returns:
        Percentage change as float (e.g., 5.5 for 5.5%)
    """
    pass


def calculate_target_price(entry: Decimal, risk_pct: float, reward_multiplier: float) -> Decimal:
    """
    Calculate target price based on entry and risk parameters.
    
    Args:
        entry: Entry price
        risk_pct: Risk percentage (e.g., 10.0 for 10%)
        reward_multiplier: Reward multiplier (e.g., 2.5 for 2.5:1 ratio)
    
    Returns:
        Target price
    """
    pass


def format_currency(value: Decimal, currency: str = "₹") -> str:
    """
    Format value as currency string.
    
    Args:
        value: Numeric value
        currency: Currency symbol
    
    Returns:
        Formatted string (e.g., "₹1,234.56")
    """
    pass


def validate_price(price: Decimal, min_price: Decimal = Decimal("1"), 
                   max_price: Decimal = Decimal("999999")) -> bool:
    """
    Validate that price is within reasonable bounds.
    
    Args:
        price: Price to validate
        min_price: Minimum valid price
        max_price: Maximum valid price
    
    Returns:
        True if valid, False otherwise
    """
    pass


def validate_percentage(value: float, min_val: float = 0, max_val: float = 100) -> bool:
    """
    Validate that value is a valid percentage.
    
    Args:
        value: Percentage value
        min_val: Minimum (default 0)
        max_val: Maximum (default 100)
    
    Returns:
        True if valid, False otherwise
    """
    pass


def moving_average(values: List[float], period: int) -> Optional[float]:
    """
    Calculate simple moving average.
    
    Args:
        values: List of values in chronological order
        period: Period for averaging
    
    Returns:
        Average or None if insufficient data
    """
    pass


class ReportPrinter:
    """
    Utility for printing human-readable analysis reports.
    """
    
    @staticmethod
    def print_snapshot(snapshot):
        """
        Print a snapshot analysis report.
        
        Args:
            snapshot: Snapshot object to print
        """
        print(f"Ticker: {snapshot.ticker}")
        print(f"Snapshot Date: {snapshot.snapshot_date}")
        print(f"Price at Date: Rs {snapshot.price_at_date}")
        
        # Fundamental Score
        fund_score = snapshot.fundamental_score
        if fund_score and fund_score.overall_score is not None:
            print(f"\nFundamental Score: {fund_score.overall_score:.1f}/100")
        elif fund_score and fund_score.total_score is not None:
            print(f"\nFundamental Score: {fund_score.total_score}/100")
        else:
            print(f"\nFundamental Score: N/A")
        
        # Technical Score
        tech_score = snapshot.technical_score
        if tech_score and tech_score.overall_score is not None:
            print(f"Technical Score: {tech_score.overall_score:.1f}/100")
        elif tech_score and tech_score.total_score is not None:
            print(f"Technical Score: {tech_score.total_score}/100")
        else:
            print(f"Technical Score: N/A")
        
        # Decision
        if snapshot.decision:
            print(f"\nDecision: {snapshot.decision}")
            print(f"Confidence: N/A")
            print(f"Rationale: {snapshot.decision}")
        else:
            print(f"\nDecision: Not yet determined")


