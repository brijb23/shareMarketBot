"""
NIFTY 50 WEEKLY ANALYSIS REPORT GENERATOR
January 10, 2026

Run comprehensive analysis on all NIFTY 50 constituents.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf

from phase19_orchestrator import Phase19Orchestrator


# NIFTY 50 constituents (as of Jan 2026)
NIFTY50_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'LT.NS',
    'HDFCBANK.NS', 'ICICIBANK.NS', 'BAJAJFINSV.NS', 'MARUTI.NS', 'AXIS.NS',
    'SUNPHARMA.NS', 'WIPRO.NS', 'BAJAJ-AUTO.NS', 'NESTLEIND.NS', 'SBILIFE.NS',
    'HINDALCO.NS', 'BPCL.NS', 'DRREDDY.NS', 'TATAMOTORS.NS', 'M&M.NS',
    'HCLTECH.NS', 'TITAN.NS', 'HEROMOTOCO.NS', 'POWERGRID.NS', 'GAIL.NS',
    'COAL.NS', 'NTPC.NS', 'IOC.NS', 'BAJAJHLDNG.NS', 'ADANIGREEN.NS',
    'ADANIENT.NS', 'ITC.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'UPL.NS',
    'EICHERMOT.NS', 'SIEMENS.NS', 'BHARTIARTL.NS', 'SBIN.NS', 'HDFCLIFE.NS',
    'LTTS.NS', 'TECHM.NS', 'APOLLOHOSP.NS', 'BIOCON.NS', 'CIPLA.NS',
    'TORRENTPHARMA.NS', 'LUPIN.NS', 'DIVISLAB.NS', 'BANDHANBNK.NS', 'INDIGO.NS'
]


def download_nifty50_data():
    """Download real data for all NIFTY 50 stocks."""
    print("Downloading NIFTY 50 stock data...")
    data = {}
    
    for i, symbol in enumerate(NIFTY50_STOCKS, 1):
        try:
            df = yf.download(symbol, period='3mo', progress=False)
            data[symbol] = df
            if i % 10 == 0:
                print(f"  [{i}/50] Downloaded {symbol}")
        except Exception as e:
            print(f"  [ERROR] Failed to download {symbol}: {str(e)[:50]}")
            continue
    
    print(f"[OK] Downloaded {len(data)}/{len(NIFTY50_STOCKS)} stocks\n")
    return data


def calculate_stock_metrics(symbol, df):
    """Calculate key metrics for a stock."""
    if df.empty or len(df) < 5:
        return None
    
    try:
        # Price metrics
        current_price = float(df['Close'].iloc[-1])
        previous_price = float(df['Close'].iloc[-2])
        price_change = ((current_price - previous_price) / previous_price) * 100
        
        # 52-week high/low
        high_52w = float(df['High'].max())
        low_52w = float(df['Low'].min())
        
        # Volatility (30-day)
        returns = df['Close'].pct_change()
        volatility = float(returns.tail(30).std()) * np.sqrt(252) * 100
        
        # Trend (compare last 5 days to 20-day average)
        ma20 = float(df['Close'].tail(20).mean())
        last5_avg = float(df['Close'].tail(5).mean())
        trend = ((last5_avg - ma20) / ma20) * 100
        
        # Momentum (RSI-like calculation)
        gains = float(returns[returns > 0].sum())
        losses = float(abs(returns[returns < 0].sum()))
        momentum = (gains - losses) * 100
        
        return {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'price_change_pct': round(price_change, 2),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'volatility': round(volatility, 2),
            'trend': round(trend, 2),
            'momentum': round(momentum, 2),
            'ma20': round(ma20, 2),
        }
    except Exception as e:
        print(f"  Error calculating metrics for {symbol}: {str(e)[:30]}")
        return None


def categorize_stock(metrics):
    """Categorize stock based on metrics."""
    if metrics is None:
        return 'UNKNOWN'
    
    volatility = metrics['volatility']
    trend = metrics['trend']
    momentum = metrics['momentum']
    
    if volatility > 30:
        return 'HIGH_VOLATILITY'
    elif trend > 2 and momentum > 0:
        return 'STRONG_UPTREND'
    elif trend < -2 and momentum < 0:
        return 'STRONG_DOWNTREND'
    elif abs(trend) < 1 and abs(momentum) < 0.1:
        return 'SIDEWAYS'
    else:
        return 'MIXED'


def generate_nifty50_report(data):
    """Generate NIFTY 50 weekly analysis report."""
    
    print("Calculating metrics for all stocks...")
    all_metrics = {}
    
    for symbol in NIFTY50_STOCKS:
        if symbol not in data:
            continue
        
        metrics = calculate_stock_metrics(symbol, data[symbol])
        if metrics:
            metrics['category'] = categorize_stock(metrics)
            all_metrics[symbol] = metrics
    
    print(f"[OK] Calculated metrics for {len(all_metrics)} stocks\n")
    
    # Create DataFrame
    df_metrics = pd.DataFrame(list(all_metrics.values()))
    
    # Sort by different criteria
    top_gainers = df_metrics.nlargest(5, 'price_change_pct')
    top_losers = df_metrics.nsmallest(5, 'price_change_pct')
    high_momentum = df_metrics.nlargest(5, 'momentum')
    low_momentum = df_metrics.nsmallest(5, 'momentum')
    high_volatility = df_metrics.nlargest(5, 'volatility')
    
    # Generate report
    report = f"""# NIFTY 50 WEEKLY ANALYSIS REPORT
## Date: {datetime.now().strftime('%B %d, %Y')}

---

## EXECUTIVE SUMMARY

**Report Date**: {datetime.now().strftime('%A, %B %d, %Y')}  
**Stocks Analyzed**: {len(all_metrics)}/50  
**Analysis Type**: Weekly Market Surveillance  
**Methodology**: Phase 19 Real-time Monitoring System

---

## MARKET OVERVIEW

### Index Status
- **Stocks with Positive Change**: {len(df_metrics[df_metrics['price_change_pct'] > 0])}
- **Stocks with Negative Change**: {len(df_metrics[df_metrics['price_change_pct'] < 0])}
- **Neutral Stocks**: {len(df_metrics[df_metrics['price_change_pct'] == 0])}

### Key Statistics
- **Average Daily Change**: {df_metrics['price_change_pct'].mean():.2f}%
- **Average Volatility (52w)**: {df_metrics['volatility'].mean():.2f}%
- **Average Momentum**: {df_metrics['momentum'].mean():.2f}%

### Market Sentiment
- **Strong Uptrend Stocks**: {len(df_metrics[df_metrics['category'] == 'STRONG_UPTREND'])}
- **Strong Downtrend Stocks**: {len(df_metrics[df_metrics['category'] == 'STRONG_DOWNTREND'])}
- **High Volatility Stocks**: {len(df_metrics[df_metrics['category'] == 'HIGH_VOLATILITY'])}
- **Sideways Stocks**: {len(df_metrics[df_metrics['category'] == 'SIDEWAYS'])}

---

## TOP GAINERS (By Daily Change)

"""
    
    for idx, row in top_gainers.iterrows():
        report += f"""
### {row['symbol']}
- **Current Price**: {row['current_price']}
- **Daily Change**: {row['price_change_pct']:+.2f}%
- **52-Week Range**: {row['low_52w']} - {row['high_52w']}
- **Volatility (52w)**: {row['volatility']:.2f}%
- **Trend**: {row['trend']:+.2f}%
- **Momentum**: {row['momentum']:+.2f}%
- **Category**: {row['category']}
"""
    
    report += f"""

---

## TOP LOSERS (By Daily Change)

"""
    
    for idx, row in top_losers.iterrows():
        report += f"""
### {row['symbol']}
- **Current Price**: {row['current_price']}
- **Daily Change**: {row['price_change_pct']:+.2f}%
- **52-Week Range**: {row['low_52w']} - {row['high_52w']}
- **Volatility (52w)**: {row['volatility']:.2f}%
- **Trend**: {row['trend']:+.2f}%
- **Momentum**: {row['momentum']:+.2f}%
- **Category**: {row['category']}
"""
    
    report += f"""

---

## HIGH MOMENTUM STOCKS

"""
    
    for idx, row in high_momentum.iterrows():
        report += f"""
### {row['symbol']}
- **Momentum Score**: {row['momentum']:+.2f}
- **Price Change**: {row['price_change_pct']:+.2f}%
- **Trend**: {row['trend']:+.2f}%
- **Current Price**: {row['current_price']}
- **Volatility**: {row['volatility']:.2f}%
"""
    
    report += f"""

---

## HIGH VOLATILITY STOCKS (Potential Risk/Opportunity)

"""
    
    for idx, row in high_volatility.iterrows():
        report += f"""
### {row['symbol']}
- **52-Week Volatility**: {row['volatility']:.2f}%
- **Current Price**: {row['current_price']}
- **Price Change**: {row['price_change_pct']:+.2f}%
- **52-Week Range**: {row['low_52w']} - {row['high_52w']}
- **Category**: {row['category']}
"""
    
    report += f"""

---

## CATEGORY ANALYSIS

### Strong Uptrend Stocks
These stocks show positive trend and momentum:

"""
    uptrend = df_metrics[df_metrics['category'] == 'STRONG_UPTREND']
    for idx, row in uptrend.iterrows():
        report += f"- {row['symbol']}: {row['price_change_pct']:+.2f}% ({row['trend']:+.2f}% trend)\n"
    
    report += f"""

### Strong Downtrend Stocks
These stocks show negative trend and momentum:

"""
    downtrend = df_metrics[df_metrics['category'] == 'STRONG_DOWNTREND']
    for idx, row in downtrend.iterrows():
        report += f"- {row['symbol']}: {row['price_change_pct']:+.2f}% ({row['trend']:+.2f}% trend)\n"
    
    report += f"""

### Sideways/Consolidating Stocks
These stocks show minimal movement:

"""
    sideways = df_metrics[df_metrics['category'] == 'SIDEWAYS']
    for idx, row in sideways.head(10).iterrows():
        report += f"- {row['symbol']}: {row['price_change_pct']:+.2f}% (Trend: {row['trend']:+.2f}%)\n"
    
    report += f"""

---

## SECTOR INSIGHTS

### Banking Sector
Banks in NIFTY 50: HDFCBANK, ICICIBANK, AXIS, SBIN, BANDHANBNK

"""
    banking = df_metrics[df_metrics['symbol'].isin(['HDFCBANK.NS', 'ICICIBANK.NS', 'AXIS.NS', 'SBIN.NS', 'BANDHANBNK.NS'])]
    banking_avg_change = banking['price_change_pct'].mean()
    report += f"- Average Daily Change: {banking_avg_change:+.2f}%\n"
    report += f"- Average Volatility: {banking['volatility'].mean():.2f}%\n"
    report += f"- Momentum Trend: {'POSITIVE' if banking_avg_change > 0 else 'NEGATIVE'}\n"
    
    report += f"""

### IT Sector
IT in NIFTY 50: TCS, INFY, WIPRO, HCLTECH, TECHM, LTTS

"""
    it = df_metrics[df_metrics['symbol'].isin(['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS', 'LTTS.NS'])]
    it_avg_change = it['price_change_pct'].mean()
    report += f"- Average Daily Change: {it_avg_change:+.2f}%\n"
    report += f"- Average Volatility: {it['volatility'].mean():.2f}%\n"
    report += f"- Momentum Trend: {'POSITIVE' if it_avg_change > 0 else 'NEGATIVE'}\n"
    
    report += f"""

### Pharma Sector
Pharma in NIFTY 50: SUNPHARMA, DRREDDY, CIPLA, LUPIN, BIOCON, DIVISLAB, TORRENTPHARMA

"""
    pharma = df_metrics[df_metrics['symbol'].isin(['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'LUPIN.NS', 'BIOCON.NS', 'DIVISLAB.NS', 'TORRENTPHARMA.NS'])]
    pharma_avg_change = pharma['price_change_pct'].mean()
    report += f"- Average Daily Change: {pharma_avg_change:+.2f}%\n"
    report += f"- Average Volatility: {pharma['volatility'].mean():.2f}%\n"
    report += f"- Momentum Trend: {'POSITIVE' if pharma_avg_change > 0 else 'NEGATIVE'}\n"
    
    report += f"""

### Metals Sector
Metals in NIFTY 50: HINDALCO, JSWSTEEL, TATASTEEL

"""
    metals = df_metrics[df_metrics['symbol'].isin(['HINDALCO.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS'])]
    metals_avg_change = metals['price_change_pct'].mean()
    report += f"- Average Daily Change: {metals_avg_change:+.2f}%\n"
    report += f"- Average Volatility: {metals['volatility'].mean():.2f}%\n"
    report += f"- Momentum Trend: {'POSITIVE' if metals_avg_change > 0 else 'NEGATIVE'}\n"
    
    report += f"""

---

## INVESTMENT RECOMMENDATIONS

### Risk/Reward Analysis

**High Opportunity (Uptrend + Growth)**:
"""
    opportunities = df_metrics[(df_metrics['trend'] > 2) & (df_metrics['volatility'] < 30)]
    for idx, row in opportunities.head(5).iterrows():
        report += f"- {row['symbol']}: {row['price_change_pct']:+.2f}% change, {row['volatility']:.2f}% volatility\n"
    
    report += f"""

**High Risk (High Volatility + Downtrend)**:
"""
    risks = df_metrics[(df_metrics['trend'] < -2) & (df_metrics['volatility'] > 25)]
    for idx, row in risks.head(5).iterrows():
        report += f"- {row['symbol']}: {row['price_change_pct']:+.2f}% change, {row['volatility']:.2f}% volatility\n"
    
    report += f"""

**Stable Performers (Sideways + Low Volatility)**:
"""
    stable = df_metrics[(abs(df_metrics['trend']) < 1) & (df_metrics['volatility'] < 20)]
    for idx, row in stable.head(5).iterrows():
        report += f"- {row['symbol']}: {row['price_change_pct']:+.2f}% change, {row['volatility']:.2f}% volatility\n"
    
    report += f"""

---

## MARKET OUTLOOK

### Weekly Summary
- **Market Sentiment**: {'BULLISH' if df_metrics['price_change_pct'].mean() > 0 else 'BEARISH'}
- **Volatility Environment**: {'HIGH' if df_metrics['volatility'].mean() > 25 else 'MODERATE' if df_metrics['volatility'].mean() > 15 else 'LOW'}
- **Trend Direction**: {'UPWARD' if df_metrics['trend'].mean() > 0.5 else 'DOWNWARD' if df_metrics['trend'].mean() < -0.5 else 'MIXED'}

### Key Observations
1. Average market volatility at {df_metrics['volatility'].mean():.2f}%, {'above' if df_metrics['volatility'].mean() > 20 else 'below'} normal levels
2. {len(df_metrics[df_metrics['price_change_pct'] > 0])} stocks in positive territory, {len(df_metrics[df_metrics['price_change_pct'] < 0])} in negative
3. Momentum trend {'positive' if df_metrics['momentum'].mean() > 0 else 'negative'} across portfolio
4. Banking sector showing {'strength' if banking_avg_change > 0 else 'weakness'}
5. IT sector showing {'strength' if it_avg_change > 0 else 'weakness'}

---

## DATA SOURCES AND METHODOLOGY

- **Data Source**: Yahoo Finance (Real-time)
- **Analysis Date**: {datetime.now().strftime('%B %d, %Y')}
- **Period Analyzed**: 3 months historical + current
- **Metrics Calculated**: Price change, volatility, trend, momentum
- **Stocks Covered**: {len(all_metrics)}/50 NIFTY 50 constituents

---

## DISCLAIMER

This report is generated for informational purposes only. All analysis is based on historical data and real-time market information. Past performance does not guarantee future results. Trading and investing involve risk. Please consult with a financial advisor before making investment decisions.

---

**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST  
**Next Update**: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}

---

*Generated by Phase 19 Market Surveillance System*
*NIFTY 50 Weekly Analysis Report*
"""
    
    return report, df_metrics, all_metrics


def run_nifty50_analysis():
    """Run complete NIFTY 50 weekly analysis."""
    
    print("\n" + "="*80)
    print("NIFTY 50 WEEKLY ANALYSIS REPORT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("="*80 + "\n")
    
    # Download data
    data = download_nifty50_data()
    
    if not data:
        print("ERROR: No data downloaded")
        return None
    
    # Generate report
    report, df_metrics, all_metrics = generate_nifty50_report(data)
    
    # Save report
    output_dir = Path('nifty50_analysis')
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / f'NIFTY50_WEEKLY_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"[OK] Report saved to: {report_file}")
    
    # Save metrics CSV
    csv_file = output_dir / f'NIFTY50_METRICS_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df_metrics.to_csv(csv_file, index=False)
    print(f"[OK] Metrics exported to: {csv_file}")
    
    # Save detailed JSON
    json_file = output_dir / f'NIFTY50_DETAILED_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_file, 'w') as f:
        json.dump(all_metrics, f, indent=2)
    print(f"[OK] Detailed data exported to: {json_file}")
    
    print("\n" + "="*80)
    print("NIFTY 50 ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"\nStocks Analyzed: {len(all_metrics)}/50")
    print(f"Average Daily Change: {df_metrics['price_change_pct'].mean():.2f}%")
    print(f"Average Volatility: {df_metrics['volatility'].mean():.2f}%")
    print(f"Average Momentum: {df_metrics['momentum'].mean():.2f}%")
    
    print(f"\nMarket Sentiment:")
    print(f"  Positive: {len(df_metrics[df_metrics['price_change_pct'] > 0])} stocks")
    print(f"  Negative: {len(df_metrics[df_metrics['price_change_pct'] < 0])} stocks")
    print(f"  Neutral: {len(df_metrics[df_metrics['price_change_pct'] == 0])} stocks")
    
    print(f"\nTop Gainer: {df_metrics.loc[df_metrics['price_change_pct'].idxmax(), 'symbol']} " +
          f"({df_metrics['price_change_pct'].max():.2f}%)")
    print(f"Top Loser: {df_metrics.loc[df_metrics['price_change_pct'].idxmin(), 'symbol']} " +
          f"({df_metrics['price_change_pct'].min():.2f}%)")
    
    print(f"\nReport Location: {output_dir}/")
    print(f"Files Generated:")
    print(f"  - NIFTY50_WEEKLY_*.md (Report)")
    print(f"  - NIFTY50_METRICS_*.csv (Metrics)")
    print(f"  - NIFTY50_DETAILED_*.json (Detailed Data)")
    
    print("\n" + "="*80)
    print("NIFTY 50 WEEKLY ANALYSIS COMPLETE")
    print("="*80 + "\n")
    
    return {
        'report': report,
        'metrics': df_metrics,
        'details': all_metrics,
        'report_file': str(report_file),
        'csv_file': str(csv_file),
        'json_file': str(json_file)
    }


if __name__ == '__main__':
    result = run_nifty50_analysis()
