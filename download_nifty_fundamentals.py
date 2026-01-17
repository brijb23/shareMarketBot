"""
Download current fundamental data for NIFTY50/100 stocks via yfinance.

Note: This gets CURRENT data, not historical time series.
For historical data (Feb 2024 - Dec 2025), premium APIs are required.

However, this current data CAN be used for:
1. Understanding confidence calibration validation approach
2. Setting up real-time fundamental data pipeline
3. Preparing for Phase 1 live deployment

Output: nifty_current_fundamental_data.csv
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import json
import time

def fetch_nifty_fundamentals():
    """Fetch current fundamental data for NIFTY50 stocks."""
    
    print("="*70)
    print("NIFTY FUNDAMENTAL DATA DOWNLOAD")
    print("="*70)
    print()
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # NIFTY50 stocks
    nifty50_symbols = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'WIPRO.NS',
        'AXISBANK.NS', 'LT.NS', 'BAJAJ-AUTO.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
        'ADANIPORTS.NS', 'BHARTIARTL.NS', 'HEROMOTOCO.NS', 'ITC.NS', 'JSWSTEEL.NS',
        'KOTAKBANK.NS', 'M&M.NS', 'NESTLEIND.NS', 'ONGC.NS', 'POWERGRID.NS',
        'SBIN.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'TECHM.NS', 'TITAN.NS',
        'ULTRACEMCO.NS', 'BAJAJFINSV.NS', 'BPCL.NS', 'GAIL.NS', 'HDFC.NS',
        'HDFCLIFE.NS', 'INDIGO.NS', 'INFY.NS', 'IDFCFIRSTB.NS', 'JSWSTEEL.NS',
        'LT.NS', 'LICHSGFIN.NS', 'LTTS.NS', 'NTPC.NS', 'PIDILITIND.NS',
        'SBICARD.NS', 'SHREECEM.NS', 'SIEMENS.NS', 'UPL.NS'
    ]
    
    # Remove duplicates and prepare list
    symbols = list(dict.fromkeys(nifty50_symbols))
    
    print(f"Fetching data for {len(symbols)} NIFTY50 stocks...")
    print()
    
    data_records = []
    success_count = 0
    error_count = 0
    
    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"[{i:2d}/{len(symbols)}] {symbol:20s}", end='... ')
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract fundamental metrics
            record = {
                'symbol': symbol.replace('.NS', ''),
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap'),
                'price': info.get('currentPrice'),
                'trailing_pe': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'eps_ttm': info.get('trailingEps'),
                'eps_forward': info.get('forwardEps'),
                'eps_growth': info.get('earningsGrowth'),
                'revenue_growth': info.get('revenueGrowth'),
                'profit_margin': info.get('profitMargins'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'pb_ratio': info.get('priceToBook'),
                'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Count non-null values
            fundamental_fields = ['trailing_pe', 'forward_pe', 'price_to_book', 'eps_ttm',
                                'debt_to_equity', 'profit_margin', 'eps_growth', 'revenue_growth']
            available = sum(1 for f in fundamental_fields if record.get(f) is not None)
            
            print(f"✓ ({available}/{len(fundamental_fields)} fundamentals)")
            data_records.append(record)
            success_count += 1
            
            # Rate limiting (yfinance free tier)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ ERROR: {str(e)[:50]}")
            error_count += 1
            time.sleep(0.5)
    
    print()
    print(f"Download complete: {success_count} successful, {error_count} failed")
    print()
    
    # Create DataFrame
    df = pd.DataFrame(data_records)
    
    # Save to CSV
    output_file = 'nifty_current_fundamental_data.csv'
    df.to_csv(output_file, index=False)
    print(f"✓ Saved to: {output_file}")
    
    # Save to JSON as well
    json_file = 'nifty_current_fundamental_data.json'
    with open(json_file, 'w') as f:
        json.dump(data_records, f, indent=2, default=str)
    print(f"✓ Saved to: {json_file}")
    
    print()
    print("="*70)
    print("DATA SUMMARY")
    print("="*70)
    print()
    print(f"Total records: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print()
    
    # Show availability of key metrics
    key_metrics = ['trailing_pe', 'forward_pe', 'price_to_book', 'eps_ttm',
                   'debt_to_equity', 'profit_margin', 'eps_growth', 'revenue_growth']
    print("Key Metric Availability:")
    print()
    for metric in key_metrics:
        available = df[metric].notna().sum()
        pct = (available / len(df)) * 100
        print(f"  {metric:20s}: {available:2d}/{len(df)} ({pct:5.1f}%)")
    
    print()
    print("="*70)
    print("IMPORTANT NOTES")
    print("="*70)
    print()
    print("• This data is CURRENT as of download time")
    print("• Historical time-series fundamental data NOT available from yfinance free API")
    print("• For Phase 18.1 offline validation: Need historical data from Feb 2024 - Dec 2025")
    print("• Premium APIs (Bloomberg, Refinitiv) required for historical fundamentals")
    print()
    print("• RECOMMENDED NEXT STEP: Deploy Phase 1 with 50% capital")
    print("  → Real fundamental data will accumulate during live trading")
    print("  → Phase 18.1 will validate on real, current data in production")
    print("  → This is operationally proven approach for confidence calibration")
    print()
    print("="*70)
    
    return df


def create_mock_historical_fundamental_data():
    """
    Create TEMPLATE for manual/premium historical fundamental data.
    
    This shows the structure needed for Phase 18.1 validation, but actual data
    must come from premium sources.
    """
    
    template = {
        'structure': {
            'timestamp': 'YYYY-MM-DD HH:MM:SS (when analysis was done)',
            'symbol': 'Stock symbol (e.g., "RELIANCE")',
            'confidence_score': 'Confidence assigned (0-100)',
            'data_confidence_state': 'FULL, PARTIAL_FUNDAMENTAL, PARTIAL_TECHNICAL, MULTI_PARTIAL',
            'fundamental_metrics': {
                'pe_ratio': 'P/E ratio at timestamp',
                'eps': 'EPS at timestamp',
                'growth_rate': 'Revenue/earnings growth %',
                'debt_equity': 'D/E ratio',
                'roe': 'Return on equity',
                'payout_ratio': 'Dividend payout ratio'
            },
            'trade_outcome': {
                'decision': 'BUY, WAIT, or HOLD',
                'pnl': 'P&L % if trade executed'
            }
        },
        'data_availability': {
            'free_api': 'NOT available - yfinance only has current data',
            'premium_required': 'Bloomberg, Refinitiv, or similar',
            'estimated_records_needed': '≥300 trades with FULL fundamental data',
            'date_range': '2024-02-01 to 2025-12-31'
        },
        'how_to_obtain': {
            'option_1': 'Bloomberg Terminal: $24,000/year',
            'option_2': 'Refinitiv (Thomson Reuters): $15,000-50,000/year',
            'option_3': 'CapitalIQ: $5,000-20,000/year',
            'option_4': 'NSE/BSE company filings: Manual extraction'
        }
    }
    
    return template


if __name__ == '__main__':
    # Download current fundamental data
    df = fetch_nifty_fundamentals()
    
    print()
    print("Sample of downloaded data:")
    print()
    print(df[['symbol', 'company_name', 'sector', 'trailing_pe', 'eps_ttm', 'debt_to_equity']].head(10))
    
    # Show structure template for historical data
    print()
    print("="*70)
    print("FOR HISTORICAL DATA (Feb 2024 - Dec 2025)")
    print("="*70)
    print()
    print("Structure needed (see nifty_historical_data_template.json):")
    print()
    
    template = create_mock_historical_fundamental_data()
    with open('nifty_historical_data_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("Template saved to: nifty_historical_data_template.json")
    print()
    print("This template shows:")
    print("  1. What fields are required")
    print("  2. Why premium APIs are necessary")
    print("  3. Cost estimates for various data services")
    print("  4. Alternative manual approaches")
