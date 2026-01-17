"""
Event Risk Analyzer
===================
Detects proximity to earnings and major corporate events, downgrades
confidence or suppresses setups when event risk is elevated.

Prevents trading into event risk windows where volatility cannot be
predicted from normal technical/fundamental analysis.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class EventType(Enum):
    """Corporate event classification."""
    EARNINGS = "EARNINGS"
    DIVIDEND = "DIVIDEND"
    STOCK_SPLIT = "STOCK_SPLIT"
    CORPORATE_ACTION = "CORPORATE_ACTION"
    NONE = "NONE"


class RiskLevel(Enum):
    """Event risk severity."""
    HIGH = "HIGH"          # Within 7 days
    MEDIUM = "MEDIUM"      # 7-21 days
    LOW = "LOW"            # 21-60 days
    NONE = "NONE"          # >60 days or no event


class EventRecommendation(Enum):
    """Action recommendation based on event risk."""
    SUPPRESS = "SUPPRESS"   # Do not initiate trade
    WAIT = "WAIT"           # Increase invalidation buffer or skip
    PROCEED_CAUTIOUS = "PROCEED_CAUTIOUS"  # Proceed but flag risk
    PROCEED = "PROCEED"     # No event risk detected


@dataclass
class EventRisk:
    """Output from event risk analysis."""
    event_type: EventType
    days_until_event: Optional[int]     # None if no event
    risk_level: RiskLevel
    recommendation: EventRecommendation
    
    # Details
    event_date: Optional[str]           # ISO format date
    action_buffer: Optional[int]        # Days to add to invalidation or skip trading
    explanation: str                    # Clear reason for recommendation


class EventRiskAnalyzer:
    """Detects event proximity and recommends actions."""
    
    # Configurable windows (in days)
    EARNINGS_SUPPRESS_WINDOW = 7        # Suppress trades within 7 days of earnings
    EARNINGS_CAUTION_WINDOW = 21        # Flag as risky within 21 days
    DIVIDEND_SUPPRESS_WINDOW = 5        # Ex-dividend date volatility
    SPLIT_SUPPRESS_WINDOW = 7           # Stock split volatility
    
    # Known earnings dates (can be loaded from external data source)
    # Format: {"SYMBOL.NS": "2026-01-20", "RELIANCE.NS": "2026-01-28", ...}
    EARNINGS_CALENDAR = {}
    
    @staticmethod
    def check_event_proximity(
        symbol: str,
        current_date: datetime,
        earnings_date: Optional[str] = None,
        dividend_date: Optional[str] = None,
        other_events: Optional[list] = None,
    ) -> EventRisk:
        """
        Check proximity to earnings, dividends, or corporate events.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE.NS")
            current_date: Current analysis date
            earnings_date: Expected earnings date (ISO format, optional)
            dividend_date: Dividend ex-date (ISO format, optional)
            other_events: List of other event dicts: [{"type": "SPLIT", "date": "2026-02-01"}]
        
        Returns:
            EventRisk object with recommendation
        """
        
        # Parse current date
        if isinstance(current_date, str):
            current_date = datetime.fromisoformat(current_date)
        
        # Priority order: Earnings > Dividend > Other
        
        # 1. Check Earnings
        if earnings_date:
            earnings_dt = datetime.fromisoformat(earnings_date)
            days_until = (earnings_dt - current_date).days
            
            if 0 <= days_until <= EventRiskAnalyzer.EARNINGS_SUPPRESS_WINDOW:
                return EventRisk(
                    event_type=EventType.EARNINGS,
                    days_until_event=days_until,
                    risk_level=RiskLevel.HIGH,
                    recommendation=EventRecommendation.SUPPRESS,
                    event_date=earnings_date,
                    action_buffer=7,
                    explanation=f"Earnings in {days_until} days: Suppress new positions to avoid event volatility.",
                )
            elif days_until <= EventRiskAnalyzer.EARNINGS_CAUTION_WINDOW:
                return EventRisk(
                    event_type=EventType.EARNINGS,
                    days_until_event=days_until,
                    risk_level=RiskLevel.MEDIUM,
                    recommendation=EventRecommendation.PROCEED_CAUTIOUS,
                    event_date=earnings_date,
                    action_buffer=3,
                    explanation=f"Earnings in {days_until} days: Increase invalidation buffer by 3 points due to event risk.",
                )
        
        # 2. Check Dividend
        if dividend_date:
            div_dt = datetime.fromisoformat(dividend_date)
            days_until = (div_dt - current_date).days
            
            if 0 <= days_until <= EventRiskAnalyzer.DIVIDEND_SUPPRESS_WINDOW:
                return EventRisk(
                    event_type=EventType.DIVIDEND,
                    days_until_event=days_until,
                    risk_level=RiskLevel.HIGH,
                    recommendation=EventRecommendation.WAIT,
                    event_date=dividend_date,
                    action_buffer=5,
                    explanation=f"Ex-dividend date in {days_until} days: Gap risk on dividend day. Wait for confirmation post-event.",
                )
        
        # 3. Check Other Events
        if other_events:
            for event in other_events:
                event_dt = datetime.fromisoformat(event.get("date", "2099-01-01"))
                days_until = (event_dt - current_date).days
                event_type_str = event.get("type", "CORPORATE_ACTION").upper()
                
                if event_type_str == "STOCK_SPLIT" and 0 <= days_until <= EventRiskAnalyzer.SPLIT_SUPPRESS_WINDOW:
                    return EventRisk(
                        event_type=EventType.STOCK_SPLIT,
                        days_until_event=days_until,
                        risk_level=RiskLevel.HIGH,
                        recommendation=EventRecommendation.SUPPRESS,
                        event_date=event.get("date"),
                        action_buffer=7,
                        explanation=f"Stock split in {days_until} days: Suppress position to avoid adjustment risks.",
                    )
                elif event_type_str == "CORPORATE_ACTION" and 0 <= days_until <= 14:
                    return EventRisk(
                        event_type=EventType.CORPORATE_ACTION,
                        days_until_event=days_until,
                        risk_level=RiskLevel.HIGH,
                        recommendation=EventRecommendation.SUPPRESS,
                        event_date=event.get("date"),
                        action_buffer=7,
                        explanation=f"Corporate action in {days_until} days: Suppress position due to outcome uncertainty.",
                    )
        
        # No event risk detected
        return EventRisk(
            event_type=EventType.NONE,
            days_until_event=None,
            risk_level=RiskLevel.NONE,
            recommendation=EventRecommendation.PROCEED,
            event_date=None,
            action_buffer=None,
            explanation="No significant event risk detected.",
        )
    
    @staticmethod
    def apply_event_downgrade(
        base_confidence: float,
        event_risk: EventRisk,
    ) -> tuple:
        """
        Apply event risk downgrade to confidence score.
        
        Args:
            base_confidence: 0-100 confidence before event adjustment
            event_risk: EventRisk object
        
        Returns:
            (adjusted_confidence, adjusted_recommendation, explanation)
        """
        
        if event_risk.recommendation == EventRecommendation.SUPPRESS:
            # Suppress: Very high downgrade or block
            adjusted = base_confidence * 0.4  # 60% reduction
            recommendation = "SUPPRESS_TRADE"
            explanation = f"Event risk too high: {event_risk.explanation}"
            return adjusted, recommendation, explanation
        
        elif event_risk.recommendation == EventRecommendation.WAIT:
            # Wait: Moderate downgrade
            adjusted = base_confidence * 0.5  # 50% reduction
            recommendation = "WAIT_FOR_CONFIRMATION"
            explanation = f"Event risk moderate: {event_risk.explanation}"
            return adjusted, recommendation, explanation
        
        elif event_risk.recommendation == EventRecommendation.PROCEED_CAUTIOUS:
            # Proceed but flag: Mild downgrade
            adjusted = base_confidence * 0.8  # 20% reduction
            recommendation = "PROCEED_WITH_CAUTION"
            explanation = f"Event risk present but acceptable: {event_risk.explanation}"
            return adjusted, recommendation, explanation
        
        else:
            # No event risk
            return base_confidence, "PROCEED", "No event risk detected."
    
    @staticmethod
    def get_invalidation_buffer(event_risk: EventRisk) -> int:
        """
        Return additional buffer (in points or %) to add to invalidation level.
        
        In high-event-risk scenarios, widen the stop to avoid whipsaws
        from event volatility.
        
        Returns:
            Buffer in percentage points (0, 3, or 5)
        """
        if event_risk.action_buffer is not None:
            return event_risk.action_buffer
        return 0
    
    @staticmethod
    def configure_earnings_calendar(earnings_dict: dict):
        """
        Load external earnings calendar.
        
        Args:
            earnings_dict: {"SYMBOL.NS": "2026-01-20", "RELIANCE.NS": "2026-01-28", ...}
        """
        EventRiskAnalyzer.EARNINGS_CALENDAR = earnings_dict
    
    @staticmethod
    def get_earnings_date(symbol: str) -> Optional[str]:
        """Retrieve earnings date from calendar if available."""
        return EventRiskAnalyzer.EARNINGS_CALENDAR.get(symbol)
