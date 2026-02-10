#!/usr/bin/env python3
"""
Pre-download all required data for backtest.
This script downloads 1 year of historical data for all 50 NIFTY50 stocks
and caches it locally for fast backtest execution.
"""

import os
import json
import pickle
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from pathlib import Path

# Ensure cache directory exists
CACHE_DIR = Path("backtest_data_cache")
CACHE_DIR.mkdir(exist_ok=True)

# NIFTY50 stocks
NIFTY50_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'WIPRO.NS',
    'HDFC.NS', 'LT.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS',
    'KOTAKBANK.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'DMART.NS', 'SBILIFE.NS',
    'HINDUNILVR.NS', 'ICICIBANK.NS', 'ITC.NS', 'JSWSTEEL.NS', 'BAJAJ-AUTO.NS',
    'NTPC.NS', 'TATASTEEL.NS', 'M&MFIN.NS', 'BAJAJHLDNG.NS', 'TITAN.NS',
    'DRREDDY.NS', 'ONGC.NS', 'GRASIM.NS', 'POWERGRID.NS', 'ULTRACEMCO.NS',
    'BHARTIARTL.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS', 'INDIGO.NS', 'SBIN.NS',
    'CIPLA.NS', 'HEROMOTOCORP.NS', 'TECHM.NS', 'EICHERMOT.NS', 'BPCL.NS',
    'DIVISLAB.NS', 'PERSISTENT.NS', 'HCLTECH.NS', 'IDFCBANK.NS', 'GODREJCP.NS',
    'NYKAA.NS', 'APOLLOHOSP.NS', 'BIOCON.NS', 'SHREECEM.NS', 'HINDALCO.NS'
]

def download_stock_data(ticker, end_date=None):
    """Download 1 year of data for a stock."""
    if end_date is None:
        end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    try:
        print(f"  Downloading {ticker}...", end=" ", flush=True)
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, timeout=10)
        
        if data.empty:
            print("FAILED (no data)")
            return None
        
        print(f"OK ({len(data)} bars)")
        return data
    except Exception as e:
        print(f"ERROR: {str(e)[:50]}")
        return None

def main():
    print("=" * 70)
    print("BACKTEST DATA DOWNLOADER - Pre-cache Historical Data")
    print("=" * 70)
    print(f"\nTarget: {len(NIFTY50_STOCKS)} NIFTY50 stocks")
    print(f"Period: 1 year of historical data (up to today: {datetime.now().strftime('%Y-%m-%d')})")
    print(f"Cache directory: {CACHE_DIR.absolute()}")
    print("\n" + "=" * 70)
    print("DOWNLOADING DATA")
    print("=" * 70 + "\n")
    
    success_count = 0
    failed_stocks = []
    downloaded_data = {}
    
    for i, ticker in enumerate(NIFTY50_STOCKS, 1):
        print(f"[{i:2d}/{len(NIFTY50_STOCKS)}]", end=" ")
        data = download_stock_data(ticker)
        
        if data is not None and not data.empty:
            success_count += 1
            downloaded_data[ticker] = data
        else:
            failed_stocks.append(ticker)
    
    print("\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"Successfully downloaded: {success_count}/{len(NIFTY50_STOCKS)}")
    print(f"Failed: {len(failed_stocks)}/{len(NIFTY50_STOCKS)}")
    
    if failed_stocks:
        print(f"Failed stocks: {', '.join(failed_stocks[:5])}" + ("..." if len(failed_stocks) > 5 else ""))
    
    # Save to cache using pickle (preserves DataFrames perfectly)
    cache_file = CACHE_DIR / f"backtest_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
    
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(downloaded_data, f)
        print(f"\n✓ Cached {success_count} stocks to: {cache_file.name}")
        print(f"  Cache file size: {cache_file.stat().st_size / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"\n✗ Failed to save cache: {e}")
        return False
    
    # Also save metadata
    metadata = {
        'downloaded_at': datetime.now().isoformat(),
        'stocks_count': success_count,
        'failed_count': len(failed_stocks),
        'cache_file': str(cache_file),
        'stocks': list(downloaded_data.keys())
    }
    
    metadata_file = CACHE_DIR / f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Metadata saved to: {metadata_file.name}")
    print("\n" + "=" * 70)
    print("DATA READY FOR BACKTEST")
    print("=" * 70)
    print(f"\nRun backtest with: python backtest_enhanced_weekly_with_cache.py")
    print(f"Using cache: {cache_file.name}\n")
    
    return True

if __name__ == "__main__":
    main()
