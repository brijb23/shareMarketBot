"""
NIFTY50 AUTOMATED WEEKLY RECOMMENDATION GENERATOR V3
Simplified version focusing on correct data handling

Usage:
    python nifty50_automated_weekly_v3.py
"""

import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from pathlib import Path
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

NIFTY50_STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'LT.NS',
    'ICICIBANK.NS', 'BAJAJFINSV.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'WIPRO.NS',
    'BAJAJ-AUTO.NS', 'NESTLEIND.NS', 'SBILIFE.NS', 'HINDALCO.NS', 'BPCL.NS',
    'DRREDDY.NS', 'M&M.NS', 'HCLTECH.NS', 'TITAN.NS', 'HEROMOTOCO.NS',
    'POWERGRID.NS', 'GAIL.NS', 'NTPC.NS', 'IOC.NS', 'ADANIGREEN.NS',
    'ADANIENT.NS', 'ITC.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'UPL.NS',
    'EICHERMOT.NS', 'SIEMENS.NS', 'BHARTIARTL.NS', 'SBIN.NS', 'HDFCLIFE.NS',
    'LTTS.NS', 'TECHM.NS', 'APOLLOHOSP.NS', 'BIOCON.NS', 'CIPLA.NS',
    'TORRENTPHARMA.NS', 'LUPIN.NS', 'DIVISLAB.NS', 'BANDHANBNK.NS', 'INDIGO.NS'
]

def download_stock_data(symbol):
    """Download data for single stock."""
    try:
        df = yf.download(symbol, period='3mo', progress=False, auto_adjust=True)
        if df is None or len(df) < 20:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.copy()  # CRITICAL: Make a copy to avoid reference issues
    except:
        return None

def calculate_metrics(symbol, df):
    """Calculate metrics for a single stock with detailed analysis."""
    try:
        if df is None or len(df) < 20:
            return None
        
        # Extract values for this specific stock
        close = np.asarray(df['Close'].values, dtype=np.float64)
        high = np.asarray(df['High'].values, dtype=np.float64)
        low = np.asarray(df['Low'].values, dtype=np.float64)
        
        # Current price
        current_price = close[-1].item() if hasattr(close[-1], 'item') else float(close[-1])
        
        # 50-day MA and trend
        ma50 = np.mean(close[-50:])
        ma50_val = ma50.item() if hasattr(ma50, 'item') else float(ma50)
        trend = ((current_price - ma50_val) / ma50_val * 100) if ma50_val > 0 else 0.0
        
        # 10-day momentum
        price_10_ago = close[-10].item() if hasattr(close[-10], 'item') else float(close[-10]) if len(close) > 10 else current_price
        momentum = ((current_price - price_10_ago) / price_10_ago * 100) if price_10_ago > 0 else 0.0
        
        # Volatility
        returns = np.diff(close) / close[:-1]
        vol_std = np.std(returns[-20:])
        volatility = (vol_std * np.sqrt(252) * 100).item() if hasattr(vol_std * np.sqrt(252) * 100, 'item') else float(vol_std * np.sqrt(252) * 100)
        
        # Support/Resistance
        support = np.percentile(close, 25).item() if hasattr(np.percentile(close, 25), 'item') else float(np.percentile(close, 25))
        resistance = np.percentile(close, 75).item() if hasattr(np.percentile(close, 75), 'item') else float(np.percentile(close, 75))
        
        # High/Low 52-week
        high_52w = np.max(high)
        low_52w = np.min(low)
        
        # Calculate risk distance based on ATR and volatility
        atr = np.mean(high[-14:] - low[-14:]) if len(high) >= 14 else np.mean(high - low)
        risk_distance = atr * 0.8  # Risk = 80% of ATR
        
        # Buy Range: Entry zone based on volatility
        volatility_pct = volatility / 100
        buy_range_low = current_price - (current_price * volatility_pct * 0.3)
        buy_range_high = current_price + (current_price * volatility_pct * 0.3)
        
        # Stop Loss: Below support or below recent low
        stop_loss = max(support * 0.98, low[-5:].min())
        
        # Target based on risk/reward: 2:1 or 2.5:1 ratio
        risk_amount = current_price - stop_loss
        target_1 = current_price + (risk_amount * 1.5)  # 1.5:1 ratio
        target_2 = current_price + (risk_amount * 2.5)  # 2.5:1 ratio
        
        # Estimate timeline (in days) - based on ATR movement speed
        daily_movement = vol_std * 100
        days_to_target_1 = max(1, (target_1 - current_price) / (current_price * daily_movement / 100)) if daily_movement > 0 else 20
        days_to_target_2 = max(1, (target_2 - current_price) / (current_price * daily_movement / 100)) if daily_movement > 0 else 30
        
        # Limit timeline to realistic range
        timeline_target_1 = min(30, max(5, int(days_to_target_1)))
        timeline_target_2 = min(60, max(10, int(days_to_target_2)))
        
        # Generate signal
        score = 1.0
        reason_buy = []
        reason_caution = []
        
        # Trend analysis
        if trend > 3:
            score += 1.5
            reason_buy.append(f"Strong uptrend: {trend:.2f}% above 50-day MA")
        elif trend > 1:
            score += 0.9
            reason_buy.append(f"Moderate uptrend: {trend:.2f}% above 50-day MA")
        elif trend > 0:
            score += 0.4
            reason_buy.append(f"Weak uptrend: {trend:.2f}% above 50-day MA")
        else:
            score -= 0.5
            reason_caution.append(f"Downtrend: {trend:.2f}% below 50-day MA")
        
        # Momentum analysis
        if momentum > 10:
            score += 1.2
            reason_buy.append(f"Excellent momentum: {momentum:.2f}% gain in 10 days")
        elif momentum > 5:
            score += 0.8
            reason_buy.append(f"Good momentum: {momentum:.2f}% gain in 10 days")
        elif momentum > 0:
            score += 0.4
            reason_buy.append(f"Positive momentum: {momentum:.2f}% gain in 10 days")
        elif momentum > -5:
            score -= 0.3
            reason_caution.append(f"Weak momentum: {momentum:.2f}% in 10 days")
        else:
            score -= 0.8
            reason_caution.append(f"Negative momentum: {momentum:.2f}% loss in 10 days")
        
        # Volatility analysis
        if volatility < 12:
            score += 1.0
            reason_buy.append(f"Low volatility: {volatility:.2f}% (safe to trade)")
        elif volatility <= 20:
            score += 0.6
            reason_buy.append(f"Medium volatility: {volatility:.2f}% (acceptable)")
        elif volatility <= 25:
            score += 0.2
            reason_caution.append(f"Higher volatility: {volatility:.2f}%")
        else:
            score -= 0.5
            reason_caution.append(f"Very high volatility: {volatility:.2f}% (risky)")
        
        # Support/Resistance analysis
        if current_price > resistance:
            reason_caution.append(f"Trading above resistance: {resistance:.2f}")
        elif current_price < support:
            reason_caution.append(f"Trading below support: {support:.2f}")
        else:
            reason_buy.append(f"Good range: Between support ({support:.2f}) and resistance ({resistance:.2f})")
        
        score = min(5.0, max(1.0, score))
        
        # Determine signal
        if score >= 3.8 and (trend > -1 or momentum > 7):
            signal = 'BUY'
        elif score >= 3.0 and trend > -2:
            signal = 'BUY'
        elif score < 2.0 or (trend < -4 and momentum < -5):
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        analysis_text = f"{signal} Signal: {', '.join(reason_buy)}"
        if reason_caution:
            analysis_text += f". Caution: {', '.join(reason_caution)}"
        
        return {
            'symbol': symbol,
            'signal': signal,
            'current_price': round(current_price, 2),
            'buy_range_low': round(buy_range_low, 2),
            'buy_range_high': round(buy_range_high, 2),
            'stop_loss': round(stop_loss, 2),
            'target_1': round(target_1, 2),
            'timeline_target_1': timeline_target_1,
            'target_2': round(target_2, 2),
            'timeline_target_2': timeline_target_2,
            'trend': round(trend, 2),
            'momentum': round(momentum, 2),
            'volatility': round(volatility, 2),
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'score': round(score, 2),
            'analysis': analysis_text,
        }
    except Exception as e:
        print(f"  ERROR {symbol}: {str(e)[:60]}")
        import traceback
        traceback.print_exc()
        return None

def format_recommendation(idx, rec):
    """Format a single recommendation for markdown output."""
    text = f"### {idx}. {rec['symbol']} - {rec['signal']} Signal\n\n"
    text += f"**Score**: {rec['score']:.2f}/5.0\n\n"
    
    text += f"#### Key Price Levels\n\n"
    text += f"| Level | Price (Rs) | Details |\n"
    text += f"|-------|-----------|----------|\n"
    text += f"| Current Price | {rec['current_price']:.2f} | Current market price |\n"
    text += f"| Buy Range | {rec['buy_range_low']:.2f} - {rec['buy_range_high']:.2f} | Safe entry zone |\n"
    text += f"| Stop Loss | {rec['stop_loss']:.2f} | Exit point if wrong |\n"
    text += f"| Target 1 | {rec['target_1']:.2f} | (~{rec['timeline_target_1']} days) |\n"
    text += f"| Target 2 | {rec['target_2']:.2f} | (~{rec['timeline_target_2']} days) |\n"
    text += f"| Support | {rec['support']:.2f} | Buying pressure |\n"
    text += f"| Resistance | {rec['resistance']:.2f} | Selling pressure |\n\n"
    
    text += f"#### Technical Analysis\n\n"
    text += f"| Metric | Value | Status |\n"
    text += f"|--------|-------|--------|\n"
    text += f"| Trend (50-day MA) | {rec['trend']:+.2f}% | "
    if rec['trend'] > 3: text += "Strong Uptrend |\n"
    elif rec['trend'] > 0: text += "Weak Uptrend |\n"
    elif rec['trend'] > -3: text += "Mild Downtrend |\n"
    else: text += "Strong Downtrend |\n"
    
    text += f"| Momentum (10-day) | {rec['momentum']:+.2f}% | "
    if rec['momentum'] > 10: text += "Excellent |\n"
    elif rec['momentum'] > 5: text += "Good |\n"
    elif rec['momentum'] > 0: text += "Positive |\n"
    elif rec['momentum'] > -5: text += "Weak |\n"
    else: text += "Negative |\n"
    
    text += f"| Volatility | {rec['volatility']:.2f}% | "
    if rec['volatility'] < 12: text += "Low (Safe) |\n"
    elif rec['volatility'] <= 20: text += "Medium (Acceptable) |\n"
    elif rec['volatility'] <= 25: text += "High (Risky) |\n"
    else: text += "Very High (Avoid) |\n\n"
    
    text += f"#### Detailed Analysis\n\n"
    text += f"{rec['analysis']}\n\n"
    
    # Risk/Reward calculation
    risk = rec['current_price'] - rec['stop_loss']
    reward_t1 = rec['target_1'] - rec['current_price']
    reward_t2 = rec['target_2'] - rec['current_price']
    rr_t1 = reward_t1 / risk if risk > 0 else 0
    rr_t2 = reward_t2 / risk if risk > 0 else 0
    
    text += f"#### Risk/Reward Ratio\n\n"
    text += f"- **Risk Amount**: Rs {risk:.2f} (from current to stop loss)\n"
    text += f"- **Target 1 R:R**: {rr_t1:.2f}:1 (Risk Rs {risk:.2f} to Gain Rs {reward_t1:.2f})\n"
    text += f"- **Target 2 R:R**: {rr_t2:.2f}:1 (Risk Rs {risk:.2f} to Gain Rs {reward_t2:.2f})\n\n"
    
    text += f"#### Trading Plan\n\n"
    text += f"1. **Enter** when price is in Buy Range: Rs {rec['buy_range_low']:.2f} - Rs {rec['buy_range_high']:.2f}\n"
    text += f"2. **Exit** at Stop Loss (Rs {rec['stop_loss']:.2f}) if trend reverses\n"
    text += f"3. **Take Profit 1** at Rs {rec['target_1']:.2f} (expect ~{rec['timeline_target_1']} days)\n"
    text += f"4. **Take Profit 2** at Rs {rec['target_2']:.2f} (expect ~{rec['timeline_target_2']} days)\n"
    text += f"5. **Monitor** support at Rs {rec['support']:.2f} and resistance at Rs {rec['resistance']:.2f}\n\n"
    text += f"---\n\n"
    
    return text

def main():
    print("\n" + "=" * 80)
    print("NIFTY50 AUTOMATED RECOMMENDATION GENERATOR V3 (FIX DATA DUPLICATION)".center(80))
    print("=" * 80)
    
    # Step 1: Download all data SEQUENTIALLY (yfinance concurrent downloads are buggy)
    print("\nSTEP 1: Downloading data for all stocks (sequential to avoid yfinance bugs)...")
    stocks_data = {}
    for i, symbol in enumerate(NIFTY50_STOCKS, 1):
        try:
            df = download_stock_data(symbol)
            if df is not None:
                stocks_data[symbol] = df
        except:
            pass
        
        if i % 10 == 0:
            print(f"  Downloaded {i}/{len(NIFTY50_STOCKS)}")
    
    print(f"  Downloaded: {len(stocks_data)}/{len(NIFTY50_STOCKS)} stocks")
    
    # Step 2: Calculate metrics for each stock individually
    print("\nSTEP 2: Calculating metrics for each stock...")
    recommendations = []
    for i, symbol in enumerate(NIFTY50_STOCKS, 1):
        if symbol not in stocks_data:
            continue
        
        # CRITICAL: Pass fresh data copy to calculation function
        metrics = calculate_metrics(symbol, stocks_data[symbol])
        if metrics:
            recommendations.append(metrics)
        
        if i % 10 == 0:
            print(f"  Processed {i}/{len(NIFTY50_STOCKS)}")
    
    print(f"  Generated {len(recommendations)} recommendations")
    
    # Step 3: Save outputs
    if recommendations:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_dir = Path('nifty50_analysis')
        analysis_dir.mkdir(exist_ok=True)
        
        # CSV
        csv_file = analysis_dir / f'NIFTY50_DYNAMIC_{timestamp}.csv'
        df_out = pd.DataFrame(recommendations)
        df_out.to_csv(csv_file, index=False)
        print(f"\nSaved: {csv_file.name}")
        
        # Verify - print first 10 rows
        print("\nVERIFICATION - Sample Recommendations:")
        print(df_out[['symbol', 'signal', 'current_price', 'buy_range_low', 'buy_range_high', 'target_1', 'stop_loss', 'volatility', 'trend']].head(10).to_string())
        
        # JSON
        json_file = analysis_dir / f'NIFTY50_DYNAMIC_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({'generated': datetime.now().isoformat(), 'recommendations': [rec for rec in recommendations]}, f, indent=2)
        print(f"\nSaved: {json_file.name}")
        
        # Markdown with FULL DETAILED ANALYSIS
        md_file = analysis_dir / f'NIFTY50_DYNAMIC_{timestamp}.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# NIFTY50 AUTOMATED WEEKLY RECOMMENDATIONS\n")
            f.write(f"**Generated**: {datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')}\n")
            f.write(f"**Total Stocks Analyzed**: {len(recommendations)}\n\n")
            
            # Summary statistics
            buy_count = sum(1 for r in recommendations if r['signal'] == 'BUY')
            hold_count = sum(1 for r in recommendations if r['signal'] == 'HOLD')
            sell_count = sum(1 for r in recommendations if r['signal'] == 'SELL')
            
            f.write(f"## MARKET SUMMARY\n\n")
            f.write(f"- **BUY Signals**: {buy_count}\n")
            f.write(f"- **HOLD Signals**: {hold_count}\n")
            f.write(f"- **SELL Signals**: {sell_count}\n")
            f.write(f"- **Average Volatility**: {np.mean([r['volatility'] for r in recommendations]):.2f}%\n")
            f.write(f"- **Average Trend**: {np.mean([r['trend'] for r in recommendations]):+.2f}%\n\n")
            
            f.write(f"---\n\n")
            
            # BUY recommendations
            buy_recs = [r for r in recommendations if r['signal'] == 'BUY']
            if buy_recs:
                f.write(f"## BUY RECOMMENDATIONS ({len(buy_recs)} Stocks)\n\n")
                for idx, rec in enumerate(buy_recs, 1):
                    f.write(format_recommendation(idx, rec))
            
            # HOLD recommendations
            hold_recs = [r for r in recommendations if r['signal'] == 'HOLD']
            if hold_recs:
                f.write(f"## HOLD RECOMMENDATIONS ({len(hold_recs)} Stocks)\n\n")
                for idx, rec in enumerate(hold_recs, 1):
                    f.write(format_recommendation(idx, rec))
            
            # SELL recommendations
            sell_recs = [r for r in recommendations if r['signal'] == 'SELL']
            if sell_recs:
                f.write(f"## SELL/AVOID RECOMMENDATIONS ({len(sell_recs)} Stocks)\n\n")
                for idx, rec in enumerate(sell_recs, 1):
                    f.write(format_recommendation(idx, rec))
        
        print(f"Saved: {md_file.name}")
        
        print("\n" + "=" * 80)
        print("SUCCESS: All files generated with detailed analysis")
        print("=" * 80)
    else:
        print("\nERROR: No recommendations generated")

if __name__ == '__main__':
    main()
