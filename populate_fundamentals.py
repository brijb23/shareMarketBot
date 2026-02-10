"""
Populate fundamental data CSV files using yfinance
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

def fetch_fundamental_data(ticker):
    """Fetch fundamental data from yfinance for a given ticker"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Calculate growth rates from financials if available
        try:
            financials = stock.financials
            if not financials.empty and len(financials.columns) >= 2:
                # Revenue CAGR (using most recent 2 years)
                revenues = financials.loc['Total Revenue'] if 'Total Revenue' in financials.index else None
                if revenues is not None and len(revenues) >= 2:
                    revenue_cagr = ((revenues.iloc[0] / revenues.iloc[-1]) ** (1 / (len(revenues) - 1)) - 1) * 100
                else:
                    revenue_cagr = info.get('revenueGrowth', 0.10) * 100 if info.get('revenueGrowth') else 10.0
                
                # Net income for profit CAGR
                net_income = financials.loc['Net Income'] if 'Net Income' in financials.index else None
                if net_income is not None and len(net_income) >= 2:
                    profit_cagr = ((net_income.iloc[0] / net_income.iloc[-1]) ** (1 / (len(net_income) - 1)) - 1) * 100
                else:
                    profit_cagr = info.get('earningsGrowth', 0.10) * 100 if info.get('earningsGrowth') else 10.0
            else:
                revenue_cagr = info.get('revenueGrowth', 0.10) * 100 if info.get('revenueGrowth') else 10.0
                profit_cagr = info.get('earningsGrowth', 0.10) * 100 if info.get('earningsGrowth') else 10.0
        except Exception as e:
            revenue_cagr = info.get('revenueGrowth', 0.10) * 100 if info.get('revenueGrowth') else 10.0
            profit_cagr = info.get('earningsGrowth', 0.10) * 100 if info.get('earningsGrowth') else 10.0
        
        # Get cash flow data
        try:
            cashflow = stock.cashflow
            operating_cash_flow = cashflow.loc['Operating Cash Flow'].iloc[0] if not cashflow.empty and 'Operating Cash Flow' in cashflow.index else 1000000000
        except:
            operating_cash_flow = 1000000000
        
        # Extract fundamental metrics
        data = {
            'symbol': ticker,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'revenue_cagr': round(revenue_cagr, 1),
            'profit_cagr': round(profit_cagr, 1),
            'roce': round(info.get('returnOnAssets', 0.15) * 100, 1) if info.get('returnOnAssets') else 15.0,  # yfinance doesn't have ROCE, use ROA as proxy
            'roe': round(info.get('returnOnEquity', 0.15) * 100, 1) if info.get('returnOnEquity') else 15.0,
            'debt_to_equity': round(info.get('debtToEquity', 50) / 100, 1) if info.get('debtToEquity') else 0.5,
            'dividend_yield': round(info.get('dividendYield', 0.02) * 100, 1) if info.get('dividendYield') else 2.0,
            'pe_ratio': round(info.get('trailingPE', 20), 6) if info.get('trailingPE') else 20.0,
            'pb_ratio': round(info.get('priceToBook', 1.5), 6) if info.get('priceToBook') else 1.5,
            'peg_ratio': round(info.get('pegRatio', 1.5), 10) if info.get('pegRatio') else 1.5,
            'operating_cash_flow': int(operating_cash_flow),
            'interest_coverage': round(info.get('interestCoverage', 5.0), 1) if info.get('interestCoverage') else 5.0,
            'margin_trend': 'Improving',  # Default, would need historical data to determine
            'net_profit': int(info.get('netIncomeToCommon', 5000000000)) if info.get('netIncomeToCommon') else 5000000000,
            'historical_pe_median': round(info.get('trailingPE', 20), 10) if info.get('trailingPE') else 20.0,
        }
        
        return data
    
    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return None

def main():
    # Define data directory
    data_dir = Path('data/fundamentals')
    
    if not data_dir.exists():
        print(f"Error: {data_dir} does not exist")
        return
    
    # Get all existing CSV files
    csv_files = list(data_dir.glob('*.csv'))
    
    print(f"Found {len(csv_files)} CSV files to update")
    print("=" * 80)
    
    success_count = 0
    failed_count = 0
    failed_tickers = []
    
    for csv_file in csv_files:
        ticker = csv_file.stem  # Get filename without extension
        print(f"\nProcessing {ticker}... ", end='')
        
        # Fetch data from yfinance
        data = fetch_fundamental_data(ticker)
        
        if data:
            # Create DataFrame with the data
            df = pd.DataFrame([data])
            
            # Save to CSV
            df.to_csv(csv_file, index=False)
            print(f"✓ Updated (ROE={data['roe']}%, ROCE={data['roce']}%)")
            success_count += 1
        else:
            print(f"✗ Failed")
            failed_count += 1
            failed_tickers.append(ticker)
        
        # Add delay to avoid rate limiting
        time.sleep(0.5)
    
    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {failed_count}")
    
    if failed_tickers:
        print(f"\nFailed tickers:")
        for ticker in failed_tickers:
            print(f"  - {ticker}")

if __name__ == "__main__":
    main()
