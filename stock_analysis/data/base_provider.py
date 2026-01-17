"""
Abstract Data Provider Interfaces

Base classes defining contracts for external data sources.
No API logic, no calculations - only method signatures.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
from stock_analysis.common.models import FundamentalData


class PriceDataProvider(ABC):
    """
    Abstract base class for price data providers.
    
    Implementations must provide methods to:
    - Fetch historical price data
    - Get latest price quote
    
    Different source implementations:
    - YahooPriceProvider (Yahoo Finance via yfinance)
    - NSEPriceProvider (NSE direct API)
    - CSVPriceProvider (Local CSV files)
    """
    
    @abstractmethod
    def get_price_history(self, symbol: str, start_date: datetime, 
                          end_date: datetime) -> pd.DataFrame:
        """
        Fetch historical daily price data for a symbol.
        
        Args:
            symbol: Stock symbol/ticker (e.g., "TCS", "INFY", "RELIANCE")
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
        
        Returns:
            pandas DataFrame with columns:
            - Date (index)
            - Open: Opening price
            - High: Daily high
            - Low: Daily low
            - Close: Closing price
            - Volume: Trading volume
            - Adjusted Close: Price adjusted for splits/dividends
            
            Sorted by date in ascending order (oldest first).
        
        Raises:
            ValueError: If symbol invalid or date range invalid
            ConnectionError: If data source unavailable
            KeyError: If symbol not found in data source
        """
        pass
    
    @abstractmethod
    def get_latest_price(self, symbol: str) -> float:
        """
        Get the most recent closing price for a symbol.
        
        Args:
            symbol: Stock symbol/ticker
        
        Returns:
            Latest closing price as float
        
        Raises:
            ValueError: If symbol invalid
            ConnectionError: If data source unavailable
            KeyError: If symbol not found
        """
        pass


class FundamentalDataProvider(ABC):
    """
    Abstract base class for fundamental data providers.
    
    Implementations must provide methods to:
    - Fetch fundamental metrics
    - Store fundamental data
    
    Different source implementations:
    - CSVFundamentalProvider (CSV files with manual data)
    - ScreenerFundamentalProvider (Screener.in CSV export)
    - APIFundamentalProvider (Paid financial data APIs)
    """
    
    @abstractmethod
    def get_fundamentals(self, symbol: str, as_of_date: datetime) -> FundamentalData:
        """
        Get fundamental data for a symbol as of specific date.
        
        Args:
            symbol: Stock symbol/ticker
            as_of_date: Date for which to retrieve data
                       (typically most recent quarter <= this date)
        
        Returns:
            FundamentalData object with financial metrics:
            - Profitability: Net Profit Margin, ROE, ROCE
            - Growth: Revenue CAGR, EPS CAGR
            - Valuation: P/E ratio, Price/Book ratio
            - Balance sheet: Debt-to-Equity, Current Ratio
            - Other: Book value, Dividend yield
        
        Raises:
            ValueError: If symbol invalid or date invalid
            KeyError: If symbol not found in data source
            FileNotFoundError: If data file missing
        """
        pass
    
    @abstractmethod
    def save_fundamentals(self, symbol: str, data: FundamentalData) -> None:
        """
        Store/update fundamental data for a symbol.
        
        Args:
            symbol: Stock symbol/ticker
            data: FundamentalData object to store
        
        Returns:
            None
        
        Raises:
            ValueError: If data invalid or incomplete
            IOError: If cannot write to storage
        """
        pass
