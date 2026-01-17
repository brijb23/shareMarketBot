"""
CSV Price Data Provider

Loads historical price data from local CSV files.
Useful for testing and offline analysis.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from stock_analysis.data.base_provider import PriceDataProvider


class CSVPriceProvider(PriceDataProvider):
    """
    Load price data from CSV files in data/prices/ directory.
    
    File Format:
    - Filename: {symbol}.csv (e.g., TCS.NS.csv)
    - Columns: date, open, high, low, close, volume
    - Date format: YYYY-MM-DD
    
    Example:
        provider = CSVPriceProvider()
        df = provider.get_price_history("TCS.NS",
                                        datetime(2023, 1, 1),
                                        datetime(2024, 1, 1))
    """
    
    def __init__(self, data_dir: str = "data/prices"):
        """
        Initialize CSV price provider.
        
        Args:
            data_dir: Directory containing price CSV files (default: data/prices)
        
        Raises:
            FileNotFoundError: If data directory doesn't exist
        """
        self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Price data directory not found: {self.data_dir}")
    
    def get_price_history(self, symbol: str, start_date: datetime,
                          end_date: datetime) -> pd.DataFrame:
        """
        Load historical price data from CSV file.
        
        Args:
            symbol: Stock symbol (e.g., "TCS.NS")
            start_date: Start date inclusive
            end_date: End date inclusive
        
        Returns:
            pandas DataFrame with columns: date, open, high, low, close, volume
            (date column contains the dates)
        
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If data is malformed
        """
        csv_file = self.data_dir / f"{symbol}.csv"
        
        if not csv_file.exists():
            raise FileNotFoundError(f"Price data file not found: {csv_file}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Normalize column names to lowercase
            df.columns = df.columns.str.lower()
            
            # Convert date column to datetime and remove timezone info
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            
            # Ensure start_date and end_date are timezone-naive
            if start_date.tzinfo is not None:
                start_date = start_date.replace(tzinfo=None)
            if end_date.tzinfo is not None:
                end_date = end_date.replace(tzinfo=None)
            
            # Filter by date range
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            df_filtered = df.loc[mask].copy()
            
            # Ensure correct column types
            for col in ['open', 'high', 'low', 'close']:
                df_filtered.loc[:, col] = pd.to_numeric(df_filtered[col])
            
            df_filtered.loc[:, 'volume'] = pd.to_numeric(df_filtered['volume'])
            
            return df_filtered
        
        except Exception as e:
            raise ValueError(f"Error reading price data for {symbol}: {str(e)}")
    
    def get_latest_price(self, symbol: str) -> float:
        """
        Get latest closing price from CSV file.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Latest closing price
        
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If data is malformed
        """
        csv_file = self.data_dir / f"{symbol}.csv"
        
        if not csv_file.exists():
            raise FileNotFoundError(f"Price data file not found: {csv_file}")
        
        try:
            df = pd.read_csv(csv_file)
            latest_close = float(df.iloc[-1]['close'])
            return latest_close
        except Exception as e:
            raise ValueError(f"Error reading latest price for {symbol}: {str(e)}")
