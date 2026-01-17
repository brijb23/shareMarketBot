"""
Indicator Calculation Engine

Computes technical indicators from price data.
No scoring, no decisions - pure calculations only.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from decimal import Decimal
from stock_analysis.common.models import IndicatorData


class IndicatorEngine:
    """
    Calculate technical indicators from historical price data.
    
    All calculations use data strictly up to the snapshot date.
    No future data leakage.
    
    Indicators computed:
    - 50 DMA (50-day moving average)
    - 200 DMA (200-day moving average)
    - 200 DMA slope (trend direction)
    - RSI(14) (Relative Strength Index)
    - ATR(14) (Average True Range - volatility)
    - Relative Strength vs Index (6M and 12M)
    
    Example:
        engine = IndicatorEngine()
        indicators = engine.calculate_indicators(
            price_df=df,
            index_df=index_df,
            as_of_date=datetime(2024, 1, 15)
        )
    """
    
    @staticmethod
    def calculate_indicators(price_df: pd.DataFrame, 
                           index_df: pd.DataFrame,
                           as_of_date: datetime,
                           symbol: str = None) -> IndicatorData:
        """
        Calculate all technical indicators.
        
        Args:
            price_df: DataFrame with columns [date, open, high, low, close, volume]
                     Sorted by date ascending (oldest first)
            index_df: DataFrame with index prices [date, close]
                     For calculating relative strength
            as_of_date: Reference date (datetime). Only use data <= this date.
            symbol: Stock symbol (optional, for error messages)
        
        Returns:
            IndicatorData object with all calculated indicators
        
        Raises:
            ValueError: If insufficient data for calculations
            KeyError: If required columns missing
        
        Example:
            >>> engine = IndicatorEngine()
            >>> ind = engine.calculate_indicators(df, index_df, datetime(2024, 1, 15))
            >>> print(f"RSI: {ind.rsi_14}")
            >>> print(f"50 DMA: {ind.dma_50}")
        """
        try:
            # Validate inputs
            if not isinstance(price_df, pd.DataFrame) or price_df.empty:
                raise ValueError("price_df must be non-empty DataFrame")
            
            if not isinstance(index_df, pd.DataFrame) or index_df.empty:
                raise ValueError("index_df must be non-empty DataFrame")
            
            if not isinstance(as_of_date, datetime):
                raise ValueError(f"as_of_date must be datetime, got {type(as_of_date).__name__}")
            
            # Validate required columns
            price_cols = {'date', 'open', 'high', 'low', 'close', 'volume'}
            if not price_cols.issubset(price_df.columns):
                raise KeyError(f"price_df missing columns: {price_cols - set(price_df.columns)}")
            
            index_cols = {'date', 'close'}
            if not index_cols.issubset(index_df.columns):
                raise KeyError(f"index_df missing columns: {index_cols - set(index_df.columns)}")
            
            # Ensure date columns are datetime
            price_df = price_df.copy()
            index_df = index_df.copy()
            price_df['date'] = pd.to_datetime(price_df['date'])
            index_df['date'] = pd.to_datetime(index_df['date'])
            as_of_date_ts = pd.Timestamp(as_of_date)
            
            # Filter to data up to as_of_date (no future leakage)
            price_data = price_df[price_df['date'] <= as_of_date_ts].copy()
            index_data = index_df[index_df['date'] <= as_of_date_ts].copy()
            
            if price_data.empty:
                raise ValueError(f"No price data found on or before {as_of_date.date()}")
            
            if index_data.empty:
                raise ValueError(f"No index data found on or before {as_of_date.date()}")
            
            # Sort by date ascending
            price_data = price_data.sort_values('date').reset_index(drop=True)
            index_data = index_data.sort_values('date').reset_index(drop=True)
            
            # Extract prices
            closes = price_data['close'].values
            highs = price_data['high'].values
            lows = price_data['low'].values
            volumes = price_data['volume'].values
            latest_date = price_data['date'].iloc[-1]
            
            # Calculate indicators
            dma_50 = IndicatorEngine._calculate_dma(closes, 50)
            dma_200 = IndicatorEngine._calculate_dma(closes, 200)
            dma_200_slope = IndicatorEngine._calculate_dma_slope(closes, 200)
            rsi_14 = IndicatorEngine._calculate_rsi(closes, 14)
            atr_14 = IndicatorEngine._calculate_atr(highs, lows, closes, 14)
            
            # Calculate relative strength vs index
            rs_6m = IndicatorEngine._calculate_relative_strength(
                price_data, index_data, months=6
            )
            rs_12m = IndicatorEngine._calculate_relative_strength(
                price_data, index_data, months=12
            )
            
            # Get latest price for reference
            latest_price = closes[-1]
            
            # Create IndicatorData object
            indicators = IndicatorData(
                symbol=symbol or "UNKNOWN",
                as_of_date=latest_date.to_pydatetime(),
                current_price=Decimal(str(latest_price)),
                latest_price=Decimal(str(latest_price)),
                price_52w_high=Decimal(str(np.max(closes[-252:]) if len(closes) >= 252 else np.max(closes))),
                price_52w_low=Decimal(str(np.min(closes[-252:]) if len(closes) >= 252 else np.min(closes))),
                sma_20=Decimal(str(dma_50)) if dma_50 is not None else None,
                sma_50=Decimal(str(dma_50)) if dma_50 is not None else None,
                sma_200=Decimal(str(dma_200)) if dma_200 is not None else None,
                dma_50=Decimal(str(dma_50)) if dma_50 is not None else None,
                dma_200=Decimal(str(dma_200)) if dma_200 is not None else None,
                dma_200_slope=Decimal(str(dma_200_slope)) if dma_200_slope is not None else None,
                rsi_14=float(rsi_14) if rsi_14 is not None else None,
                macd_line=Decimal("0"),
                macd_signal=Decimal("0"),
                macd_histogram=Decimal("0"),
                atr_14=Decimal(str(atr_14)) if atr_14 is not None else None,
                atr_percent=float(atr_14) / float(latest_price) * 100 if atr_14 is not None else None,
                volatility_level="normal",
                volume_current=int(volumes[-1]) if len(volumes) > 0 else 0,
                volume_20d_avg=int(np.mean(volumes[-20:])) if len(volumes) >= 20 else 0,
                volume_trend="stable",
                rsi_above_50=float(rsi_14) > 50 if rsi_14 is not None else False,
                relative_strength_6m=float(rs_6m) if rs_6m is not None else None,
                relative_strength_12m=float(rs_12m) if rs_12m is not None else None
            )
            
            return indicators
            
        except (ValueError, KeyError) as e:
            raise
        except Exception as e:
            raise ValueError(f"Error calculating indicators: {str(e)}")
    
    @staticmethod
    def _calculate_dma(prices: np.ndarray, period: int) -> float:
        """
        Calculate simple moving average (DMA).
        
        Args:
            prices: Array of closing prices
            period: Number of periods for moving average
        
        Returns:
            DMA value or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        return float(np.mean(prices[-period:]))
    
    @staticmethod
    def _calculate_dma_slope(prices: np.ndarray, period: int) -> float:
        """
        Calculate slope of DMA line.
        
        Compares recent DMA to DMA from 10 days ago.
        Positive = uptrend, Negative = downtrend
        
        Args:
            prices: Array of closing prices
            period: Period for moving average
        
        Returns:
            Slope as percentage or None if insufficient data
        """
        if len(prices) < max(period + 10, 250):
            return None
        
        # Current DMA
        dma_current = np.mean(prices[-period:])
        
        # DMA from 10 days ago
        dma_past = np.mean(prices[-period-10:-10])
        
        if dma_past == 0:
            return 0.0
        
        # Calculate slope as percentage change
        slope = ((dma_current - dma_past) / dma_past) * 100
        
        return float(slope)
    
    @staticmethod
    def _calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).
        
        RSI measures momentum. Range: 0-100
        - > 70: Overbought (potential reversal)
        - < 30: Oversold (potential bounce)
        - 50: Neutral
        
        Args:
            prices: Array of closing prices
            period: RSI period (default 14)
        
        Returns:
            RSI value (0-100) or None if insufficient data
        """
        if len(prices) < period + 1:
            return None
        
        # Calculate price changes
        deltas = np.diff(prices[-period-1:])
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gain and loss
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        # Avoid division by zero
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        # Calculate RS (Relative Strength)
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    @staticmethod
    def _calculate_atr(highs: np.ndarray, lows: np.ndarray, 
                       closes: np.ndarray, period: int = 14) -> float:
        """
        Calculate Average True Range (ATR).
        
        Measures volatility. Higher ATR = higher volatility.
        
        Args:
            highs: Array of high prices
            lows: Array of low prices
            closes: Array of closing prices
            period: ATR period (default 14)
        
        Returns:
            ATR value or None if insufficient data
        """
        if len(highs) < period + 1:
            return None
        
        # Calculate True Range for each period
        tr1 = highs[-period-1:] - lows[-period-1:]  # High - Low
        tr2 = np.abs(highs[-period-1:] - closes[-period-2:-1])  # High - Prev Close
        tr3 = np.abs(lows[-period-1:] - closes[-period-2:-1])   # Low - Prev Close
        
        # True Range is maximum of these three
        tr = np.maximum(np.maximum(tr1, tr2), tr3)
        
        # ATR is average of True Range
        atr = np.mean(tr[-period:])
        
        return float(atr)
    
    @staticmethod
    def _calculate_relative_strength(price_df: pd.DataFrame, 
                                    index_df: pd.DataFrame,
                                    months: int = 6) -> float:
        """
        Calculate relative strength vs index over N months.
        
        Compares stock return to index return.
        Positive = stock outperforming index
        Negative = stock underperforming index
        
        Args:
            price_df: Sorted DataFrame with price data
            index_df: Sorted DataFrame with index data
            months: Number of months lookback (6 or 12)
        
        Returns:
            Relative strength as percentage or None if insufficient data
        """
        if len(price_df) < 30 or len(index_df) < 30:
            return None
        
        # Get data from N months ago
        # Approximate: 30 days per month
        lookback_days = months * 30
        
        if len(price_df) < lookback_days or len(index_df) < lookback_days:
            return None
        
        # Stock returns
        stock_start = price_df['close'].iloc[-lookback_days]
        stock_end = price_df['close'].iloc[-1]
        stock_return = ((stock_end - stock_start) / stock_start) * 100
        
        # Index returns
        index_start = index_df['close'].iloc[-lookback_days]
        index_end = index_df['close'].iloc[-1]
        index_return = ((index_end - index_start) / index_start) * 100
        
        # Relative strength
        relative_strength = stock_return - index_return
        
        return float(relative_strength)
