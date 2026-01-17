"""
CSV-based Fundamentals Data Provider

Loads fundamental data from CSV snapshot files.
No calculations, no scoring - pure data retrieval and filtering.
"""

import pandas as pd
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict
from stock_analysis.data.base_provider import FundamentalDataProvider
from stock_analysis.common.models import FundamentalData


class CSVFundamentalsProvider(FundamentalDataProvider):
    """
    Load fundamental data from CSV files.
    
    CSV Storage:
    - Location: data/fundamentals/ directory
    - Files: One CSV per symbol (e.g., TCS.csv, INFY.csv)
    - Format: Semicolon or comma-delimited
    
    CSV Columns:
    - symbol: Stock ticker (e.g., "TCS")
    - date: Data date (YYYY-MM-DD format)
    - revenue_cagr: Revenue CAGR (%)
    - profit_cagr: Profit CAGR (%)
    - roce: Return on Capital Employed (%)
    - roe: Return on Equity (%)
    - margin_trend: "expanding", "flat", or "shrinking"
    - debt_to_equity: D/E ratio
    - interest_coverage: Interest coverage ratio
    - operating_cash_flow: OCF in millions
    - net_profit: Net profit in millions
    - pe_ratio: Current P/E ratio
    - historical_pe_median: Median P/E (historical)
    - peg_ratio: PEG ratio
    
    Behavior:
    - Given symbol and as_of_date: returns latest record where date <= as_of_date
    - Never returns future data
    - Raises error if no valid record exists
    
    Example CSV (TCS.csv):
        symbol,date,revenue_cagr,profit_cagr,roce,roe,margin_trend,debt_to_equity,interest_coverage,operating_cash_flow,net_profit,pe_ratio,historical_pe_median,peg_ratio
        TCS,2023-01-01,12.5,15.3,25.5,28.0,expanding,0.15,45.2,5000,2500,18.5,17.0,1.2
        TCS,2023-03-31,13.0,16.1,26.0,28.5,expanding,0.14,46.0,5200,2600,18.0,17.0,1.1
    
    Usage:
        provider = CSVFundamentalsProvider(data_dir="data/fundamentals")
        fund_data = provider.get_fundamentals("TCS", datetime(2023, 6, 15))
    """
    
    def __init__(self, data_dir: str = "data/fundamentals"):
        """
        Initialize CSV fundamentals provider.
        
        Args:
            data_dir: Directory containing CSV files (default: data/fundamentals)
        
        Raises:
            FileNotFoundError: If data_dir does not exist
        """
        self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Fundamentals data directory not found: {self.data_dir}")
    
    def get_fundamentals(self, symbol: str, as_of_date: datetime) -> FundamentalData:
        """
        Get fundamental data for symbol as of a specific date.
        
        Returns the latest record where date <= as_of_date.
        Never returns future data.
        
        Args:
            symbol: Stock symbol (e.g., "TCS", "INFY")
            as_of_date: Reference date (datetime object)
        
        Returns:
            FundamentalData object with fields populated from CSV row
        
        Raises:
            ValueError: If symbol empty or as_of_date is not datetime
            FileNotFoundError: If CSV file for symbol doesn't exist
            ValueError: If CSV file corrupted or has wrong format
            ValueError: If no records found with date <= as_of_date
            (This ensures no future data is returned)
        
        Example:
            >>> provider = CSVFundamentalsProvider()
            >>> data = provider.get_fundamentals("TCS", datetime(2023, 6, 15))
            >>> print(data.roe)
            28.5
        """
        try:
            # Validate symbol
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError(f"Symbol must be non-empty string, got: {repr(symbol)}")
            
            symbol = symbol.strip().upper()
            
            # Validate as_of_date
            if not isinstance(as_of_date, datetime):
                raise ValueError(f"as_of_date must be datetime object, got {type(as_of_date).__name__}")
            
            # Construct CSV file path
            csv_path = self.data_dir / f"{symbol}.csv"
            
            # Check if file exists
            if not csv_path.exists():
                raise FileNotFoundError(f"No CSV file found for symbol '{symbol}' at {csv_path}")
            
            # Read CSV file
            try:
                df = pd.read_csv(csv_path)
            except Exception as e:
                raise ValueError(f"Error reading CSV file for '{symbol}': {str(e)}")
            
            # Validate CSV has required columns
            required_cols = {
                'symbol', 'date', 'revenue_cagr', 'profit_cagr', 'roce', 'roe',
                'margin_trend', 'debt_to_equity', 'interest_coverage',
                'operating_cash_flow', 'net_profit', 'pe_ratio',
                'historical_pe_median', 'peg_ratio'
            }
            
            csv_cols = set(df.columns)
            missing_cols = required_cols - csv_cols
            
            if missing_cols:
                raise ValueError(f"CSV file for '{symbol}' missing columns: {missing_cols}")
            
            # Convert date column to datetime
            try:
                df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            except Exception as e:
                raise ValueError(f"Error parsing date column in CSV for '{symbol}': {str(e)}")
            
            # Filter for matching symbol
            df = df[df['symbol'].str.strip().str.upper() == symbol]
            
            if df.empty:
                raise ValueError(f"No records found in CSV for symbol '{symbol}'")
            
            # Filter for dates <= as_of_date (never return future data)
            as_of_date_converted = pd.Timestamp(as_of_date)
            if as_of_date_converted.tzinfo is not None:
                as_of_date_converted = as_of_date_converted.tz_localize(None)
            df = df[df['date'] <= as_of_date_converted]
            
            if df.empty:
                raise ValueError(f"No records found for symbol '{symbol}' with date <= {as_of_date.date()}. "
                               f"All available records are in the future.")
            
            # Get the latest (most recent) record
            latest_record = df.loc[df['date'].idxmax()]
            
            # Convert to FundamentalData object
            fund_data = FundamentalData(
                ticker=str(latest_record['symbol']),
                as_of_date=latest_record['date'].to_pydatetime(),
                revenue_cagr=Decimal(str(latest_record['revenue_cagr'])),
                profit_cagr=Decimal(str(latest_record['profit_cagr'])),
                roce=Decimal(str(latest_record['roce'])),
                roe=Decimal(str(latest_record['roe'])),
                margin_trend=str(latest_record['margin_trend']),
                debt_to_equity=Decimal(str(latest_record['debt_to_equity'])),
                interest_coverage=float(latest_record['interest_coverage']),
                operating_cash_flow=float(latest_record['operating_cash_flow']),
                net_profit=float(latest_record['net_profit']),
                pe_ratio=Decimal(str(latest_record['pe_ratio'])),
                historical_pe_median=float(latest_record['historical_pe_median']),
                peg_ratio=float(latest_record['peg_ratio'])
            )
            
            return fund_data
            
        except ValueError as e:
            raise
        except FileNotFoundError as e:
            raise
        except Exception as e:
            raise ValueError(f"Unexpected error retrieving fundamentals for '{symbol}': {str(e)}")
    
    def calculate_fundamental_trend(self, symbol: str, as_of_date: datetime, lookback_months: int = 12) -> Dict:
        """
        Calculate fundamental improvement trend over a period.
        
        Args:
            symbol: Stock symbol
            as_of_date: Reference date
            lookback_months: How many months to look back (default 12)
        
        Returns:
            Dict with keys:
            - trend: 'improving', 'stable', 'declining'
            - roe_change: Change in ROE over period
            - revenue_cagr_change: Change in revenue CAGR
            - margin_trend: Current margin trend
            - improvement_velocity: Months to see improvement
        """
        try:
            symbol = symbol.strip().upper()
            csv_path = self.data_dir / f"{symbol}.csv"
            
            if not csv_path.exists():
                return {
                    'trend': 'unknown',
                    'roe_change': 0,
                    'revenue_cagr_change': 0,
                    'margin_trend': 'unknown',
                    'improvement_velocity': 0
                }
            
            df = pd.read_csv(csv_path)
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            df = df[df['symbol'].str.strip().str.upper() == symbol]
            
            # Filter for dates <= as_of_date
            as_of_date_converted = pd.Timestamp(as_of_date)
            if as_of_date_converted.tzinfo is not None:
                as_of_date_converted = as_of_date_converted.tz_localize(None)
            df = df[df['date'] <= as_of_date_converted].sort_values('date')
            
            if len(df) < 2:
                return {
                    'trend': 'insufficient_data',
                    'roe_change': 0,
                    'revenue_cagr_change': 0,
                    'margin_trend': df.iloc[-1]['margin_trend'] if len(df) > 0 else 'unknown',
                    'improvement_velocity': 0
                }
            
            # Get current and historical values
            current = df.iloc[-1]
            oldest = df.iloc[0]
            
            roe_change = float(current['roe']) - float(oldest['roe'])
            rev_cagr_change = float(current['revenue_cagr']) - float(oldest['revenue_cagr'])
            profit_cagr_change = float(current['profit_cagr']) - float(oldest['profit_cagr'])
            
            # Determine trend
            if roe_change > 2 or profit_cagr_change > 1:
                trend = 'improving'
            elif roe_change < -2 or profit_cagr_change < -1:
                trend = 'declining'
            else:
                trend = 'stable'
            
            # Calculate improvement velocity (months since last improvement)
            improvement_velocity = len(df) * 3  # Assuming quarterly data
            if trend == 'improving':
                # Find when improvement started
                for i in range(len(df) - 1, 0, -1):
                    if float(df.iloc[i]['roe']) > float(df.iloc[i-1]['roe']):
                        improvement_velocity = (len(df) - i) * 3
                        break
            
            return {
                'trend': trend,
                'roe_change': roe_change,
                'revenue_cagr_change': rev_cagr_change,
                'profit_cagr_change': profit_cagr_change,
                'margin_trend': str(current['margin_trend']),
                'improvement_velocity': improvement_velocity,
                'lookback_period_months': lookback_months
            }
        
        except Exception:
            return {
                'trend': 'unknown',
                'roe_change': 0,
                'revenue_cagr_change': 0,
                'margin_trend': 'unknown',
                'improvement_velocity': 0
            }
    
    def save_fundamentals(self, symbol: str, data: FundamentalData) -> None:
        """
        Append fundamental data to CSV file.
        
        Args:
            symbol: Stock symbol
            data: FundamentalData object to save
        
        Returns:
            None
        
        Raises:
            ValueError: If symbol empty or data invalid
            IOError: If cannot write to CSV file
        
        Note:
            - Creates CSV file if it doesn't exist
            - Appends row to existing CSV
            - No duplicate checking (can append same date multiple times)
        """
        try:
            # Validate symbol
            if not isinstance(symbol, str) or not symbol.strip():
                raise ValueError(f"Symbol must be non-empty string, got: {repr(symbol)}")
            
            symbol = symbol.strip().upper()
            
            # Validate FundamentalData
            if not isinstance(data, FundamentalData):
                raise ValueError(f"data must be FundamentalData object, got {type(data).__name__}")
            
            # Construct CSV file path
            csv_path = self.data_dir / f"{symbol}.csv"
            
            # Create directory if it doesn't exist
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare data row
            new_row = pd.DataFrame([{
                'symbol': symbol,
                'date': data.as_of_date,
                'revenue_cagr': data.revenue_cagr,
                'profit_cagr': data.profit_cagr,
                'roce': data.roce,
                'roe': data.roe,
                'margin_trend': data.margin_trend,
                'debt_to_equity': data.debt_to_equity,
                'interest_coverage': data.interest_coverage,
                'operating_cash_flow': data.operating_cash_flow,
                'net_profit': data.net_profit,
                'pe_ratio': data.pe_ratio,
                'historical_pe_median': data.historical_pe_median,
                'peg_ratio': data.peg_ratio
            }])
            
            # Check if file exists and has data
            if csv_path.exists():
                # Append to existing CSV
                existing_df = pd.read_csv(csv_path)
                updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                updated_df.to_csv(csv_path, index=False)
            else:
                # Create new CSV file
                new_row.to_csv(csv_path, index=False)
            
        except ValueError as e:
            raise
        except Exception as e:
            raise IOError(f"Error saving fundamentals for '{symbol}' to CSV: {str(e)}")
