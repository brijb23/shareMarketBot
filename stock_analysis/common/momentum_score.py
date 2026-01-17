"""
Price Momentum Scorer
Detects institutional accumulation and trending strength
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MomentumScorer:
    """Calculate price momentum using multiple indicators"""
    
    @staticmethod
    def calculate_momentum_score(price_data, current_date):
        """
        Calculate momentum score (0-100) for a given date
        
        price_data: DataFrame with OHLCV data (columns: Close, Volume)
        current_date: reference date for calculation
        
        Returns: momentum_score (0-100)
        """
        try:
            # Filter data up to current_date
            filtered_data = price_data[price_data.index <= current_date].copy()
            
            if len(filtered_data) < 30:
                return 50  # Default middle score if insufficient data
            
            # Get recent 60 days of data
            recent_data = filtered_data.tail(60).copy()
            
            scores = []
            
            # 1. Price Rate of Change (ROC) - 20%
            roc_score = MomentumScorer._calculate_roc(recent_data)
            scores.append(('roc', roc_score, 0.20))
            
            # 2. Volume Trend - 20%
            volume_score = MomentumScorer._calculate_volume_trend(recent_data)
            scores.append(('volume', volume_score, 0.20))
            
            # 3. Moving Average Alignment - 25%
            ma_score = MomentumScorer._calculate_ma_alignment(recent_data)
            scores.append(('ma', ma_score, 0.25))
            
            # 4. RSI-based momentum - 20%
            rsi_score = MomentumScorer._calculate_rsi(recent_data)
            scores.append(('rsi', rsi_score, 0.20))
            
            # 5. Price above support/resistance - 15%
            level_score = MomentumScorer._calculate_price_levels(recent_data)
            scores.append(('levels', level_score, 0.15))
            
            # Calculate weighted score
            weighted_score = sum(score * weight for name, score, weight in scores)
            
            return max(0, min(100, int(weighted_score)))
        
        except Exception as e:
            # Fallback on error
            return 50
    
    @staticmethod
    def _calculate_roc(data):
        """Rate of Change - measures price momentum (0-100)"""
        if len(data) < 2:
            return 50
        
        close_prices = data['Close'].values
        current_price = close_prices[-1]
        price_20_days_ago = close_prices[max(0, len(close_prices) - 20)]
        price_60_days_ago = close_prices[0]
        
        roc_20 = ((current_price - price_20_days_ago) / price_20_days_ago * 100) if price_20_days_ago > 0 else 0
        roc_60 = ((current_price - price_60_days_ago) / price_60_days_ago * 100) if price_60_days_ago > 0 else 0
        
        # Strong uptrend: roc_20 > 5%, roc_60 > 10% = 100
        # Weak uptrend: roc_20 > 0%, roc_60 > 0% = 70
        # Neutral: both trending flat = 50
        # Downtrend: both negative = 30
        
        if roc_20 > 5 and roc_60 > 10:
            return 95
        elif roc_20 > 3 and roc_60 > 5:
            return 80
        elif roc_20 > 0 and roc_60 > 0:
            return 70
        elif roc_20 < 0 and roc_60 < 0:
            return 30
        else:
            return 50
    
    @staticmethod
    def _calculate_volume_trend(data):
        """Volume accumulation trend (0-100)"""
        if len(data) < 20:
            return 50
        
        recent_volume = data['Volume'].values[-20:]
        earlier_volume = data['Volume'].values[:20]
        
        avg_recent = np.mean(recent_volume)
        avg_earlier = np.mean(earlier_volume)
        
        if avg_earlier == 0:
            return 50
        
        volume_increase = (avg_recent - avg_earlier) / avg_earlier * 100
        
        # Volume surge indicates institutional accumulation
        if volume_increase > 50:
            return 95
        elif volume_increase > 20:
            return 80
        elif volume_increase > 0:
            return 65
        elif volume_increase > -20:
            return 50
        else:
            return 35
    
    @staticmethod
    def _calculate_ma_alignment(data):
        """Moving average alignment - 20, 50, 200 day MAs (0-100)"""
        if len(data) < 200:
            return 50
        
        close = data['Close'].values
        
        # Calculate moving averages
        ma20 = np.mean(close[-20:])
        ma50 = np.mean(close[-50:])
        ma200 = np.mean(close[-200:]) if len(close) >= 200 else np.mean(close)
        
        current = close[-1]
        
        # Perfect alignment: 20 > 50 > 200 = 100
        # Good uptrend: Price > 20 > 50 = 80
        # Weak uptrend: Price > 50 but 20 < 50 = 60
        # Neutral = 50
        # Weak downtrend = 40
        # Strong downtrend = 20
        
        score = 50
        
        if ma20 > ma50 > ma200:
            score = 85
            if current > ma20:
                score = 100
        elif current > ma20 and ma20 > ma50:
            score = 75
        elif current > ma50 > ma200:
            score = 65
        elif ma50 > ma200 > current:
            score = 45
        elif ma200 > ma50 > ma20:
            score = 25
        
        return score
    
    @staticmethod
    def _calculate_rsi(data):
        """Relative Strength Index momentum (0-100)"""
        if len(data) < 14:
            return 50
        
        close = data['Close'].values
        
        # Calculate RSI
        deltas = np.diff(close)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        
        if avg_loss == 0:
            rsi = 100 if avg_gain > 0 else 50
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # RSI 70-100: Overbought (momentum exhaustion) = 60
        # RSI 50-70: Strong uptrend = 80
        # RSI 50: Neutral = 50
        # RSI 30-50: Weak downtrend = 40
        # RSI 0-30: Oversold (potential reversal) = 70
        
        if rsi > 70:
            return 60
        elif rsi > 50:
            return 80
        elif rsi > 30:
            return 50
        else:
            return 70  # Oversold is a bullish signal
    
    @staticmethod
    def _calculate_price_levels(data):
        """Price position relative to support/resistance (0-100)"""
        if len(data) < 60:
            return 50
        
        close = data['Close'].values
        
        # 60-day high and low
        high_60 = np.max(close[-60:])
        low_60 = np.min(close[-60:])
        current = close[-1]
        
        if high_60 == low_60:
            return 50
        
        # Position in range: 0 = at low, 1 = at high
        position = (current - low_60) / (high_60 - low_60)
        
        # Price near 52-week high = 90 (momentum signal)
        # Price in upper half = 70
        # Price in middle = 50
        # Price in lower half = 30
        # Price near 52-week low = 70 (reversal signal)
        
        if position > 0.75:
            return 90
        elif position > 0.5:
            return 70
        elif position > 0.25:
            return 50
        elif position > 0.1:
            return 30
        else:
            return 70  # Near lows (potential reversal)
    
    @staticmethod
    def get_momentum_interpretation(score):
        """Convert momentum score to interpretation"""
        if score >= 75:
            return "Strong Momentum"
        elif score >= 65:
            return "Moderate Momentum"
        elif score >= 50:
            return "Neutral Momentum"
        elif score >= 35:
            return "Weak Momentum"
        else:
            return "Negative Momentum"
