"""
PHASE 17.6: DATA CONFIDENCE STATE DETECTION
Classifies data completeness and applies appropriate confidence ceilings
"""

from enum import Enum
from typing import Dict, Tuple, Optional


class DataConfidenceState(Enum):
    """Data completeness classification"""
    FULL = "FULL"
    PARTIAL_FUNDAMENTAL = "PARTIAL_FUNDAMENTAL"
    PARTIAL_TECHNICAL = "PARTIAL_TECHNICAL"
    MULTI_PARTIAL = "MULTI_PARTIAL"


class DataConfidenceDetector:
    """Detects data completeness and assigns confidence state"""
    
    # Confidence ceilings by state
    CONFIDENCE_CAPS = {
        DataConfidenceState.FULL: 90.0,
        DataConfidenceState.PARTIAL_FUNDAMENTAL: 62.0,
        DataConfidenceState.PARTIAL_TECHNICAL: 60.0,
        DataConfidenceState.MULTI_PARTIAL: 55.0,
    }
    
    @staticmethod
    def detect_state(
        fundamental_data: Dict,
        technical_data: Dict,
        regime_data: Optional[Dict] = None,
    ) -> Tuple[DataConfidenceState, str]:
        """
        Detect data completeness state and cap reason
        
        Returns:
            (DataConfidenceState, reason_string)
        """
        
        fundamental_partial = DataConfidenceDetector._is_fundamental_partial(fundamental_data)
        technical_partial = DataConfidenceDetector._is_technical_partial(technical_data)
        regime_partial = DataConfidenceDetector._is_regime_partial(regime_data or {})
        
        # Determine state
        partial_count = sum([fundamental_partial, technical_partial, regime_partial])
        
        if partial_count == 0:
            # All pillars complete
            return DataConfidenceState.FULL, "All data available"
        elif partial_count >= 2:
            # Multiple pillars incomplete
            return DataConfidenceState.MULTI_PARTIAL, DataConfidenceDetector._build_partial_reason(
                fundamental_partial, technical_partial, regime_partial
            )
        elif fundamental_partial:
            return DataConfidenceState.PARTIAL_FUNDAMENTAL, DataConfidenceDetector._build_fundamental_reason(
                fundamental_data
            )
        else:
            # technical_partial or regime_partial
            return DataConfidenceState.PARTIAL_TECHNICAL, "Technical or regime data incomplete"
    
    @staticmethod
    def _is_fundamental_partial(fundamental_data: Dict) -> bool:
        """Check if fundamental data is incomplete"""
        
        # Check for missing score key (critical indicator)
        if 'score' not in fundamental_data:
            return True
        
        score = fundamental_data.get('score')
        
        # Check if score is at default (no calculation)
        if score == 50.0:
            return True
        
        # Check for unknown sector (no fundamental context)
        if fundamental_data.get('sector') == 'unknown':
            return True
        
        # Check for zero variance across population (synthetic)
        # This would be detected at population level, return False here
        
        return False
    
    @staticmethod
    def _is_technical_partial(technical_data: Dict) -> bool:
        """Check if technical data is incomplete"""
        
        # Check for minimum candle count
        candle_count = technical_data.get('candle_count', 0)
        if candle_count < 50:  # Insufficient history
            return True
        
        # Check for missing critical indicators
        required_indicators = [
            'rsi_14', 'atr', 'ema_20', 'ema_50', 'ema_200',
            'macd_line', 'macd_signal', 'current_price'
        ]
        
        for indicator in required_indicators:
            if indicator not in technical_data:
                return True
            # Allow 0.0 for indicators (valid), but not None
            if technical_data[indicator] is None:
                return True
        
        # Check for invalid values
        price = technical_data.get('current_price', 0)
        if price <= 0:
            return True
        
        atr = technical_data.get('atr', 0)
        if atr <= 0:
            return True
        
        # If we got here, technical data is complete
        return False
    
    @staticmethod
    def _is_regime_partial(regime_data: Dict) -> bool:
        """Check if regime/market data is incomplete"""
        
        # Regime is partial if critical components missing
        required = ['regime', 'volatility_regime']
        for field in required:
            if field not in regime_data:
                return True
            if regime_data[field] is None:
                return True
        
        return False
    
    @staticmethod
    def _build_fundamental_reason(fundamental_data: Dict) -> str:
        """Build detailed reason for fundamental partiality"""
        
        reasons = []
        
        if 'score' not in fundamental_data:
            reasons.append("score key missing")
        elif fundamental_data.get('score') == 50.0:
            reasons.append("score is default (50.0)")
        
        if fundamental_data.get('sector') == 'unknown':
            reasons.append("sector unknown")
        
        if reasons:
            return f"Fundamental data incomplete: {', '.join(reasons)}"
        return "Fundamental data incomplete"
    
    @staticmethod
    def _build_partial_reason(
        fundamental_partial: bool,
        technical_partial: bool,
        regime_partial: bool,
    ) -> str:
        """Build detailed reason for multi-partial state"""
        
        reasons = []
        
        if fundamental_partial:
            reasons.append("fundamentals")
        if technical_partial:
            reasons.append("technical")
        if regime_partial:
            reasons.append("regime")
        
        return f"Multiple data pillars incomplete: {', '.join(reasons)}"
    
    @staticmethod
    def get_confidence_cap(state: DataConfidenceState) -> float:
        """Get confidence ceiling for state"""
        return DataConfidenceDetector.CONFIDENCE_CAPS.get(state, 50.0)


class ConfidenceCapEngine:
    """Applies confidence caps based on data state"""
    
    @staticmethod
    def cap_confidence(
        raw_confidence: float,
        data_state: DataConfidenceState,
    ) -> Tuple[float, float, str]:
        """
        Apply confidence cap
        
        Returns:
            (final_confidence, cap_value, cap_reason)
        """
        
        cap = DataConfidenceDetector.get_confidence_cap(data_state)
        
        # NO BOOSTING: only cap down, never boost up
        final_confidence = min(raw_confidence, cap)
        
        # Determine if cap was applied
        cap_reason = ""
        if final_confidence < raw_confidence:
            cap_reason = f"Capped by {data_state.value} state ({cap})"
        else:
            cap_reason = f"No cap applied ({data_state.value} allows up to {cap})"
        
        return final_confidence, cap, cap_reason
