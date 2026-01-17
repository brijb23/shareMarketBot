"""
Technical Analysis Scoring Engine

Scores technical setup and momentum based on indicators.
No candle pattern prediction, no automatic overbought/oversold signals.
"""

from stock_analysis.common.models import IndicatorData, TechnicalScore


class TechnicalAnalyzer:
    """
    Analyze technical strength and momentum setup.
    
    Scoring system (0-100 total):
    - Trend: 40 points (Price vs 200 DMA + DMA slope)
    - Momentum: 30 points (Relative strength + RSI)
    - Volume: 15 points (Accumulation/Distribution patterns)
    - Volatility: 15 points (ATR%)
    
    Pure rule-based scoring with exact thresholds.
    
    Key principles:
    - Overbought (RSI >75) is not automatic sell
    - Oversold (RSI <35) is not automatic buy
    - Score reflects technical health, not direction prediction
    
    Example:
        analyzer = TechnicalAnalyzer()
        score = analyzer.score_technical(indicator_data)
        print(f"Total Score: {score.total_score}")
    """
    
    @staticmethod
    def score_technical(indicators: IndicatorData) -> TechnicalScore:
        """
        Calculate comprehensive technical score.
        
        Args:
            indicators: IndicatorData object with calculated indicators
        
        Returns:
            TechnicalScore with individual and total scores
        
        Raises:
            ValueError: If indicators invalid or missing required fields
        
        Example:
            >>> analyzer = TechnicalAnalyzer()
            >>> score = analyzer.score_technical(indicators)
            >>> print(f"Trend: {score.trend_score}")
            >>> print(f"Total: {score.total_score}")
        """
        try:
            if not isinstance(indicators, IndicatorData):
                raise ValueError(f"Expected IndicatorData, got {type(indicators).__name__}")
            
            # Calculate individual component scores
            trend_score = TechnicalAnalyzer._score_trend(indicators)
            momentum_score = TechnicalAnalyzer._score_momentum(indicators)
            volume_score = TechnicalAnalyzer._score_volume(indicators)
            volatility_score = TechnicalAnalyzer._score_volatility(indicators)
            
            # Total score: sum of all components (max 100)
            total_score = min(100, trend_score + momentum_score + 
                            volume_score + volatility_score)
            
            return TechnicalScore(
                symbol=indicators.symbol,
                as_of_date=indicators.as_of_date,
                trend_score=trend_score,
                momentum_score=momentum_score,
                volume_score=volume_score,
                volatility_score=volatility_score,
                total_score=int(total_score)
            )
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error scoring technical indicators: {str(e)}")
    
    @staticmethod
    def _score_trend(indicators: IndicatorData) -> int:
        """
        Score trend health (Price vs 200 DMA + DMA slope).
        
        Maximum: 40 points (20 + 20)
        
        Price vs 200 DMA:
        >5% above → 20
        0–5% above → 15
        at DMA → 10
        below → 0
        
        200 DMA slope:
        rising → 20
        flat → 10
        falling → 0
        """
        price_score = TechnicalAnalyzer._score_price_vs_dma(
            indicators.latest_price, indicators.dma_200
        )
        slope_score = TechnicalAnalyzer._score_dma_slope(indicators.dma_200_slope)
        
        return price_score + slope_score
    
    @staticmethod
    def _score_price_vs_dma(price: float, dma_200: float) -> int:
        """
        Score current price relative to 200-day moving average.
        
        >5% above → 20
        0–5% above → 15
        at DMA → 10
        below → 0
        """
        if dma_200 is None or price is None or dma_200 <= 0:
            return 10  # Neutral if data unavailable
        
        pct_above_dma = ((price - dma_200) / dma_200) * 100
        
        if pct_above_dma > 5:
            return 20
        elif pct_above_dma >= 0:
            return 15
        elif pct_above_dma >= -2:  # "at DMA" allows small tolerance
            return 10
        else:
            return 0
    
    @staticmethod
    def _score_dma_slope(slope: float) -> int:
        """
        Score 200 DMA slope direction and strength.
        
        rising → 20
        flat → 10
        falling → 0
        
        Slope is percentage change from 10 days ago.
        rising: > 0.5%
        flat: -0.5% to 0.5%
        falling: < -0.5%
        """
        if slope is None:
            return 10  # Neutral if data unavailable
        
        if slope > 0.5:
            return 20
        elif slope >= -0.5:
            return 10
        else:
            return 0
    
    @staticmethod
    def _score_momentum(indicators: IndicatorData) -> int:
        """
        Score momentum metrics (Relative Strength + RSI).
        
        Maximum: 30 points (15 + 15)
        
        Relative Strength:
        outperform 12M → 15
        outperform 6M → 10
        underperform → 0
        
        RSI:
        45–65 → 15
        35–45 or 65–75 → 8
        <35 or >75 → 0
        
        Note: Extreme RSI (overbought/oversold) doesn't mean exit,
        just reflects extreme conditions in momentum.
        """
        rs_score = TechnicalAnalyzer._score_relative_strength(indicators)
        rsi_score = TechnicalAnalyzer._score_rsi(indicators.rsi_14)
        
        return rs_score + rsi_score
    
    @staticmethod
    def _score_relative_strength(indicators: IndicatorData) -> int:
        """
        Score relative strength vs index.
        
        outperform 12M → 15
        outperform 6M → 10
        underperform → 0
        
        Stock outperforming = positive relative strength
        """
        rs_12m = indicators.relative_strength_12m
        rs_6m = indicators.relative_strength_6m
        
        # If both available, check 12M first (longer trend)
        if rs_12m is not None and rs_12m > 0:
            return 15
        elif rs_6m is not None and rs_6m > 0:
            return 10
        else:
            return 0
    
    @staticmethod
    def _score_rsi(rsi: float) -> int:
        """
        Score RSI momentum indicator.
        
        45–65 → 15 (healthy momentum)
        35–45 or 65–75 → 8 (moderate momentum)
        <35 or >75 → 0 (extreme conditions)
        
        Key: These are conditions, not buy/sell signals.
        Overbought (>75) and oversold (<35) don't automatically mean exit/enter.
        """
        if rsi is None:
            return 8  # Neutral default
        
        if 45 <= rsi <= 65:
            return 15
        elif (35 <= rsi < 45) or (65 < rsi <= 75):
            return 8
        else:
            return 0
    
    @staticmethod
    def _score_volume(indicators: IndicatorData) -> int:
        """
        Score volume pattern.
        
        Maximum: 15 points
        
        accumulation → 15 (buying volume increasing)
        neutral → 8 (no clear pattern)
        distribution → 0 (selling volume increasing)
        
        Note: IndicatorData doesn't directly provide volume state.
        This is a placeholder scoring that returns neutral.
        In a full implementation, would need volume comparison logic.
        """
        # Since IndicatorData doesn't provide volume accumulation/distribution signals,
        # we return neutral score. In production, would analyze:
        # - Volume on up days vs down days
        # - Volume trend vs price trend
        # - On-Balance Volume (OBV)
        
        return 8
    
    @staticmethod
    def _score_volatility(indicators: IndicatorData) -> int:
        """
        Score volatility level via ATR percentage.
        
        Maximum: 15 points
        
        ATR% <2 → 15 (very stable, low volatility)
        2–4 → 8 (moderate volatility)
        >4 → 0 (high volatility, choppy)
        
        ATR% = (ATR / Current Price) * 100
        """
        if indicators.atr_14 is None or indicators.latest_price is None:
            return 8  # Neutral default
        
        if indicators.latest_price <= 0:
            return 8
        
        atr_pct = (indicators.atr_14 / indicators.latest_price) * 100
        
        if atr_pct < 2:
            return 15
        elif atr_pct <= 4:
            return 8
        else:
            return 0
