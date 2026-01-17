"""
Yahoo Finance Price Data Provider

Fetches historical OHLCV data from Yahoo Finance via yfinance.
No calculations, no analysis - pure data retrieval.
"""

import pandas as pd
from datetime import datetime
import yfinance as yf
from stock_analysis.data.base_provider import PriceDataProvider


class YahooPriceProvider(PriceDataProvider):
    """
    Fetch price data from Yahoo Finance using yfinance library.
    
    Features:
    - Supports NSE symbols (TCS.NS, INFY.NS, RELIANCE.NS, etc.)
    - Automatically adjusted for stock splits and dividends
    - No forward-filling of missing data (preserves gaps for weekends/holidays)
    - Handles NSE trading calendar correctly
    
    Example:
        provider = YahooPriceProvider()
        df = provider.get_price_history("TCS.NS", 
                                        datetime(2023, 1, 1),
                                        datetime(2024, 1, 1))
        latest = provider.get_latest_price("INFY.NS")
    
    NSE Symbols:
    - TCS.NS, INFY.NS, RELIANCE.NS, HDFC.NS, ITC.NS, etc.
    - Note: Always use .NS suffix for NSE stocks
    """
    
    def get_price_history(self, symbol: str, start_date: datetime, 
                          end_date: datetime) -> pd.DataFrame:
        """
        Fetch historical daily price data from Yahoo Finance.
        
        Data is adjusted for stock splits automatically.
        No forward-fill applied - missing data (weekends/holidays) remains as gaps.
        
        Args:
            symbol: Stock symbol with exchange suffix (e.g., "TCS.NS" for NSE)
            start_date: Start date inclusive (datetime object)
            end_date: End date inclusive (datetime object)
        
        Returns:
            pandas DataFrame with columns:
            - date: Trading date
            - open: Opening price
            - high: Daily high price
            - low: Daily low price
            - close: Closing price (adjusted)
            - volume: Trading volume
            
            Sorted by date in ascending order (oldest first).
            No rows with NaN values.
        
        Raises:
            ValueError: If symbol empty, dates invalid, date range invalid, 
                       or no data found for symbol
            ConnectionError: If Yahoo Finance API unavailable
        
        Example:
            >>> provider = YahooPriceProvider()
            >>> df = provider.get_price_history("TCS.NS", 
            ...                                  datetime(2023, 1, 1),
            ...                                  datetime(2023, 12, 31))
            >>> print(df.shape)
            (246, 6)
            >>> print(df.head())
                      date   open    high     low  close     volume
            0  2023-01-02  3750.0  3768.0  3750.0 3765.0  1234567.0
        """
        try:
            # Validate symbol
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError(f"Symbol must be non-empty string, got: {repr(symbol)}")
            
            # Validate dates are datetime objects
            if not isinstance(start_date, datetime):
                raise ValueError(f"start_date must be datetime object, got {type(start_date).__name__}")
            
            if not isinstance(end_date, datetime):
                raise ValueError(f"end_date must be datetime object, got {type(end_date).__name__}")
            
            # Validate date range
            if start_date > end_date:
                raise ValueError(f"start_date ({start_date.date()}) cannot be after "
                               f"end_date ({end_date.date()})")
            
            # Download data from Yahoo Finance
            # auto_adjust=True handles splits/dividends automatically
            data = yf.download(symbol, start=start_date, end=end_date, 
                              progress=False, auto_adjust=True)
            
            # Check if data is empty
            if data.empty:
                raise ValueError(f"No data found for symbol '{symbol}' in date range "
                               f"{start_date.date()} to {end_date.date()}. "
                               f"Verify symbol is valid (e.g., 'TCS.NS' for NSE stocks)")
            
            # Rename columns to lowercase
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Keep only required columns (drop Adj Close since auto_adjust already applied)
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            data = data[required_cols].copy()
            
            # Reset index to make date a column (not index)
            data = data.reset_index()
            data = data.rename(columns={'Date': 'date'})
            
            # Drop any rows with NaN values (DO NOT forward-fill)
            # This preserves gaps for weekends and NSE holidays
            data = data.dropna()
            
            # Ensure correct data types
            data['date'] = pd.to_datetime(data['date']).dt.date
            data['open'] = data['open'].astype('float64')
            data['high'] = data['high'].astype('float64')
            data['low'] = data['low'].astype('float64')
            data['close'] = data['close'].astype('float64')
            data['volume'] = data['volume'].astype('int64')
            
            # Sort by date ascending (oldest first)
            data = data.sort_values('date').reset_index(drop=True)
            
            return data
            
        except ValueError as e:
            # Re-raise ValueError as-is (our validation errors)
            raise
        except ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Yahoo Finance: {str(e)}")
        except Exception as e:
            # Catch other exceptions
            error_msg = str(e).lower()
            if "connection" in error_msg or "timeout" in error_msg:
                raise ConnectionError(f"Yahoo Finance API connection error: {str(e)}")
            elif "no data" in error_msg:
                raise ValueError(f"No data available for '{symbol}' in specified date range")
            else:
                raise ValueError(f"Error fetching price data for '{symbol}': {str(e)}")
    
    def get_latest_price(self, symbol: str) -> float:
        """
        Get the most recent closing price for a symbol.
        
        Args:
            symbol: Stock symbol with exchange suffix (e.g., "TCS.NS")
        
        Returns:
            Latest closing price as float
        
        Raises:
            ValueError: If symbol empty or no data found
            ConnectionError: If Yahoo Finance API unavailable
        
        Example:
            >>> provider = YahooPriceProvider()
            >>> price = provider.get_latest_price("INFY.NS")
            >>> print(f"INFY latest price: {price}")
            INFY latest price: 1425.50
        """
        try:
            # Validate symbol
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError(f"Symbol must be non-empty string, got: {repr(symbol)}")
            
            # Create ticker object and fetch latest history
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            # Check if data is available
            if hist.empty:
                raise ValueError(f"No data found for symbol '{symbol}'. "
                               f"Verify symbol is valid (e.g., 'TCS.NS' for NSE stocks)")
            
            # Get the latest close price (adjusted for splits)
            latest_price = float(hist['Close'].iloc[-1])
            
            return latest_price
            
        except ValueError as e:
            raise
        except ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Yahoo Finance: {str(e)}")
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "timeout" in error_msg:
                raise ConnectionError(f"Yahoo Finance API connection error: {str(e)}")
            else:
                raise ValueError(f"Error fetching latest price for '{symbol}': {str(e)}")
