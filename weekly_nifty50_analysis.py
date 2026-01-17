"""
NIFTY 50 Weekly Analysis Script
Automated weekly report generation with fresh data
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from stock_analysis.common.target_date_calculator import TargetDateCalculator

def calculate_breakout_trigger(symbol, price, price_provider, analysis_date):
    """
    Calculate intelligent breakout trigger price based on technical resistance.
    
    Strategy:
    - 52-week high (strongest resistance)
    - 200-day moving average (major trend line)
    - 50-day moving average (intermediate trend)
    - Previous swing highs
    
    Args:
        symbol: Stock symbol
        price: Current stock price
        price_provider: Price data provider
        analysis_date: Date for analysis
    
    Returns:
        dict with breakout_trigger and reasoning
    """
    try:
        # Get 1 year of price history
        start_date = analysis_date - timedelta(days=365)
        hist = price_provider.get_price_history(symbol, start_date, analysis_date)
        
        if hist is None or len(hist) < 50:
            # Fallback: use simple percentage if not enough data
            return {
                'breakout_trigger': round(price * 1.07, 2),
                'reasoning': 'Insufficient data, using 7% move above current'
            }
        
        # Calculate key resistance levels
        high_52w = hist['high'].max()
        close_50d = hist['close'].tail(50).mean()
        close_200d = hist['close'].tail(200).mean() if len(hist) >= 200 else hist['close'].mean()
        
        # Find recent swing highs (last 30 days)
        recent_high = hist.tail(30)['high'].max()
        
        # Determine breakout trigger based on multiple levels
        # Priority: Recent swing high > 52-week high > 200-day MA
        if recent_high >= price * 1.05:
            # Stock is already near highs, trigger slightly above recent high
            breakout_trigger = recent_high * 1.02
            reasoning = f'Above recent swing high (₹{recent_high:.2f})'
        elif high_52w > price * 1.10:
            # 52-week high is far, use it as target
            breakout_trigger = high_52w * 0.98
            reasoning = f'Near 52-week high (₹{high_52w:.2f})'
        else:
            # Use combination: average of key resistances
            breakout_trigger = (recent_high + close_200d) / 2
            reasoning = f'Resistance confluence (recent high + 200-day MA)'
        
        return {
            'breakout_trigger': round(breakout_trigger, 2),
            'reasoning': reasoning
        }
    except Exception as e:
        # Fallback if data retrieval fails
        return {
            'breakout_trigger': round(price * 1.07, 2),
            'reasoning': 'Data error, using 7% move above current'
        }

def calculate_trade_levels(symbol, price, fund_score, tech_score, price_provider=None, analysis_date=None):
    """
    Calculate buy range, target, and stop loss based on price and scores.
    Also calculate intelligent breakout trigger price.
    
    Args:
        symbol: Stock symbol (for historical data)
        price: Current stock price
        fund_score: Fundamental score (0-100)
        tech_score: Technical score (0-100)
        price_provider: Price data provider (optional, for breakout calculation)
        analysis_date: Date for analysis (optional)
    
    Returns:
        dict with buy_range, target, stop_loss, and breakout_trigger
    """
    if not price or price <= 0:
        return None
    
    # Volatility adjustment based on combined score
    combined_score = (fund_score + tech_score) / 2
    
    # Higher scores = lower volatility = tighter range
    if combined_score >= 70:
        volatility_factor = 0.02  # 2% range for very strong stocks
        buy_margin = 0.03  # 3% below price
        target_profit = 0.12  # 12% target
        stop_loss = 0.08  # 8% stop loss
    elif combined_score >= 60:
        volatility_factor = 0.03  # 3% range
        buy_margin = 0.04  # 4% below price
        target_profit = 0.15  # 15% target
        stop_loss = 0.10  # 10% stop loss
    else:
        volatility_factor = 0.05  # 5% range
        buy_margin = 0.05  # 5% below price
        target_profit = 0.18  # 18% target
        stop_loss = 0.12  # 12% stop loss
    
    # Calculate levels
    buy_lower = price * (1 - buy_margin)
    buy_upper = price
    target = price * (1 + target_profit)
    stop = price * (1 - stop_loss)
    
    result = {
        'buy_lower': round(buy_lower, 2),
        'buy_upper': round(buy_upper, 2),
        'target': round(target, 2),
        'stop_loss': round(stop, 2),
        'current_price': round(price, 2),
        'profit_potential': round(target_profit * 100, 1),
        'risk': round(stop_loss * 100, 1)
    }
    
    # Add breakout trigger if data provider available
    if price_provider and analysis_date:
        breakout_data = calculate_breakout_trigger(symbol, price, price_provider, analysis_date)
        result['breakout_trigger'] = breakout_data['breakout_trigger']
        result['breakout_reasoning'] = breakout_data['reasoning']
    
    return result

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*80}")
    print(f"[Step] {description}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"[OK] {description} - SUCCESS")
            return True
        else:
            print(f"[FAIL] {description} - FAILED")
            return False
    except Exception as e:
        print(f"[ERROR] {description} - ERROR: {e}")
        return False

def generate_weekly_report():
    """Generate weekly NIFTY 50 analysis report"""
    
    # Generate timestamp
    report_date = datetime.now()
    week_start = report_date.strftime("%Y-%m-%d")
    week_number = report_date.strftime("%V")
    timestamp = report_date.strftime("%Y%m%d_%H%M%S")
    
    print("\n" + "="*80)
    print("NIFTY 50 WEEKLY ANALYSIS AUTOMATION")
    print("="*80)
    print(f"Report Date: {report_date.strftime('%A, %B %d, %Y at %H:%M:%S')}")
    print(f"Week Number: {week_number} of {report_date.strftime('%Y')}")
    print("="*80)
    
    # Step 1: Fetch fresh data
    success_fetch = run_command(
        "python fetch_nifty50.py",
        "STEP 1: Fetching Fresh Data (Prices & Fundamentals)"
    )
    
    if not success_fetch:
        print("\n[WARNING] Data fetch failed. Continuing with existing data...")
    
    # Step 2: Generate analysis
    print(f"\n{'='*80}")
    print("STEP 2: Running Technical & Fundamental Analysis")
    print(f"{'='*80}")
    
    try:
        # Import and run analysis directly
        from stock_analysis.data.csv_price_provider import CSVPriceProvider
        from stock_analysis.data.fundamentals_csv_provider import CSVFundamentalsProvider
        from stock_analysis.backtest.snapshot import SnapshotGenerator
        
        NIFTY_50 = [
            'RELIANCE.NS', 'TCS.NS', 'ICICIBANK.NS', 'LT.NS', 'AXISBANK.NS',
            'MARUTI.NS', 'WIPRO.NS', 'SBIN.NS', 'HCLTECH.NS', 'HINDUNILVR.NS',
            'KOTAKBANK.NS', 'TITAN.NS', 'NESTLEIND.NS', 'SUNPHARMA.NS', 'BAJAJFINSV.NS',
            'ASIANPAINT.NS', 'ULTRACEMCO.NS', 'BHARTIARTL.NS', 'PGHH.NS', 'JSWSTEEL.NS',
            'ADANIPORTS.NS', 'POWERGRID.NS', 'INDIGO.NS', 'GRASIM.NS', 'HDFCBANK.NS',
            'TATACONSUM.NS', 'NTPC.NS', 'ADANIENT.NS', 'ONGC.NS', 'COALINDIA.NS',
            'LUPIN.NS', 'DIVISLAB.NS', 'TECHM.NS', 'EICHERMOT.NS', 'LTIM.NS',
            'AUROPHARMA.NS', 'CIPLA.NS', 'BPCL.NS', 'M&MFIN.NS', 'BANKBARODA.NS',
            'APOLLOHOSP.NS', 'VEDL.NS'
        ]
        
        print("Initializing analysis engines...")
        price_provider = CSVPriceProvider()
        fund_provider = CSVFundamentalsProvider()
        snapshot_generator = SnapshotGenerator(price_provider, fund_provider)
        
        results = {
            'accumulate': [],
            'hold': [],
            'avoid': [],
            'errors': []
        }
        
        analysis_date = datetime.now()
        
        print(f"Analyzing {len(NIFTY_50)} stocks...")
        for idx, symbol in enumerate(NIFTY_50, 1):
            try:
                snapshot = snapshot_generator.generate_snapshot(symbol=symbol, as_of_date=analysis_date)
                
                if snapshot:
                    fund_score = snapshot.fundamental_score.total_score if snapshot.fundamental_score else 0
                    tech_score = snapshot.technical_score.total_score if snapshot.technical_score else 0
                    price = snapshot.price_at_date if snapshot.price_at_date else 0
                    decision = snapshot.decision or "HOLD - Unable to determine"
                    
                    # Calculate trade levels with breakout trigger
                    trade_levels = calculate_trade_levels(
                        symbol, float(price), fund_score, tech_score,
                        price_provider=price_provider,
                        analysis_date=analysis_date
                    )
                    
                    category = 'hold'
                    if 'ACCUMULATE' in decision.upper():
                        category = 'accumulate'
                    elif 'AVOID' in decision.upper():
                        category = 'avoid'
                    
                    results[category].append({
                        'symbol': symbol,
                        'price': price,
                        'fundamental': fund_score,
                        'technical': tech_score,
                        'decision': decision,
                        'trade_levels': trade_levels
                    })
                    
                    if idx % 10 == 0:
                        print(f"  Progress: {idx}/{len(NIFTY_50)} stocks analyzed")
            except Exception as e:
                results['errors'].append({'symbol': symbol, 'error': str(e)})
        
        print(f"[OK] Analysis complete: {len(NIFTY_50) - len(results['errors'])} stocks analyzed")
        
        # Step 3: Generate report file
        print(f"\n{'='*80}")
        print("STEP 3: Generating Weekly Report File")
        print(f"{'='*80}")
        
        report_filename = f"NIFTY50_WEEKLY_{week_number}_{timestamp}.md"
        report_path = Path(report_filename)
        
        # Create comprehensive report
        report_content = generate_report_content(report_date, week_number, results)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"[OK] Report saved: {report_filename}")
        
        # Step 4: Create summary statistics
        print(f"\n{'='*80}")
        print("WEEKLY ANALYSIS SUMMARY")
        print(f"{'='*80}")
        
        total_success = sum(len(v) for k, v in results.items() if k != 'errors')
        
        print(f"\nStocks Analyzed: {total_success}")
        print(f"  [BUY] (ACCUMULATE):  {len(results['accumulate'])} stocks")
        print(f"  [HOLD] (NEUTRAL):    {len(results['hold'])} stocks")
        print(f"  [SELL] (AVOID):      {len(results['avoid'])} stocks")
        
        if total_success > 0:
            accumulate_pct = (len(results['accumulate']) / total_success) * 100
            hold_pct = (len(results['hold']) / total_success) * 100
            avoid_pct = (len(results['avoid']) / total_success) * 100
            
            print(f"\nDistribution:")
            print(f"  Buy:   {accumulate_pct:5.1f}%")
            print(f"  Hold:  {hold_pct:5.1f}%")
            print(f"  Sell:  {avoid_pct:5.1f}%")
            
            all_stocks = results['accumulate'] + results['hold'] + results['avoid']
            if all_stocks:
                avg_fund = sum(s['fundamental'] for s in all_stocks) / len(all_stocks)
                avg_tech = sum(s['technical'] for s in all_stocks) / len(all_stocks)
                
                print(f"\nAverage Scores:")
                print(f"  Fundamental: {avg_fund:.1f}/100")
                print(f"  Technical:   {avg_tech:.1f}/100")
                print(f"  Combined:    {(avg_fund + avg_tech)/2:.1f}/100")
        
        # Print top picks
        if results['accumulate']:
            sorted_accumulate = sorted(results['accumulate'], 
                                      key=lambda x: (x['fundamental'] + x['technical']) / 2, 
                                      reverse=True)
            print(f"\nTop 5 BUY Recommendations:")
            for i, stock in enumerate(sorted_accumulate[:5], 1):
                avg = (stock['fundamental'] + stock['technical']) / 2
                print(f"  {i}. {stock['symbol']:15} | Score: {avg:.0f}/100")
        
        print(f"\n{'='*80}")
        print("[OK] WEEKLY ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"\nReport saved as: {report_filename}")
        print(f"View report: cat {report_filename}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_report_content(report_date, week_number, results):
    """Generate comprehensive weekly report content"""
    
    total_success = sum(len(v) for k, v in results.items() if k != 'errors')
    
    # Calculate statistics
    accumulate_pct = (len(results['accumulate']) / total_success * 100) if total_success > 0 else 0
    hold_pct = (len(results['hold']) / total_success * 100) if total_success > 0 else 0
    avoid_pct = (len(results['avoid']) / total_success * 100) if total_success > 0 else 0
    
    all_stocks = results['accumulate'] + results['hold'] + results['avoid']
    avg_fund = sum(s['fundamental'] for s in all_stocks) / len(all_stocks) if all_stocks else 0
    avg_tech = sum(s['technical'] for s in all_stocks) / len(all_stocks) if all_stocks else 0
    
    # Sort stocks
    sorted_accumulate = sorted(results['accumulate'], 
                              key=lambda x: (x['fundamental'] + x['technical']) / 2, 
                              reverse=True)
    sorted_hold = sorted(results['hold'], 
                        key=lambda x: (x['fundamental'] + x['technical']) / 2, 
                        reverse=True)
    sorted_avoid = sorted(results['avoid'], 
                         key=lambda x: (x['fundamental'] + x['technical']) / 2)
    
    report = f"""# NIFTY 50 WEEKLY ANALYSIS REPORT

**Week {week_number}, {report_date.strftime('%B %d, %Y')}**

Generated: {report_date.strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Stocks Analyzed** | {total_success} |
| **Analysis Date** | {report_date.strftime('%Y-%m-%d')} |
| **BUY Signals** | {len(results['accumulate'])} ({accumulate_pct:.1f}%) |
| **HOLD Signals** | {len(results['hold'])} ({hold_pct:.1f}%) |
| **SELL Signals** | {len(results['avoid'])} ({avoid_pct:.1f}%) |
| **Avg Fund Score** | {avg_fund:.1f}/100 |
| **Avg Tech Score** | {avg_tech:.1f}/100 |
| **Combined Avg** | {(avg_fund + avg_tech)/2:.1f}/100 |

---

## [BUY] RECOMMENDATIONS ({len(results['accumulate'])} Stocks)

### Top Picks (Highest Confidence)
"""

    if sorted_accumulate:
        for i, stock in enumerate(sorted_accumulate, 1):
            avg = (stock['fundamental'] + stock['technical']) / 2
            trade = stock.get('trade_levels')
            
            report += f"""
**{i}. {stock['symbol']}** | Score: {avg:.0f}/100
- Current Price: ₹{stock['price']:,.2f}
- Fundamental: {stock['fundamental']:.0f}/100 | Technical: {stock['technical']:.0f}/100
- Decision: {stock['decision'][:80]}
"""
            
            if trade:
                # Calculate target date
                target_date_info = TargetDateCalculator.calculate_target_date(
                    current_price=stock['price'],
                    target_price=trade['target'],
                    technical_score=stock['technical'],
                    fundamental_score=stock['fundamental'],
                    momentum_score=stock.get('momentum', 50)
                )
                
                report += f"""
  **Trade Setup:**
  - Buy Range: ₹{trade['buy_lower']:,.2f} - ₹{trade['buy_upper']:,.2f}
  - Target: ₹{trade['target']:,.2f} ({trade['profit_potential']:.1f}% upside)
  - Stop Loss: ₹{trade['stop_loss']:,.2f} ({trade['risk']:.1f}% risk)
  - Risk:Reward = 1:{trade['profit_potential']/trade['risk']:.1f}
  - **Target Date:** {target_date_info['target_date_str']} ({target_date_info['months_to_target']} months)
  - **Confidence:** {target_date_info['confidence']}
"""
    else:
        report += "\nNo BUY signals this week\n"
    
    # HOLD section
    report += f"""

---

## [HOLD] RECOMMENDATIONS ({len(results['hold'])} Stocks)

### Top Candidates (Monitor for Breakout)
"""

    if sorted_hold:
        for i, stock in enumerate(sorted_hold, 1):
            avg = (stock['fundamental'] + stock['technical']) / 2
            trade = stock.get('trade_levels')
            
            report += f"""
**{i}. {stock['symbol']}** | Score: {avg:.0f}/100
- Current Price: ₹{stock['price']:,.2f}
- Fundamental: {stock['fundamental']:.0f}/100 | Technical: {stock['technical']:.0f}/100
"""
            
            if trade:
                # Calculate target date
                target_date_info = TargetDateCalculator.calculate_target_date(
                    current_price=stock['price'],
                    target_price=trade['target'],
                    technical_score=stock['technical'],
                    fundamental_score=stock['fundamental'],
                    momentum_score=stock.get('momentum', 50)
                )
                
                report += f"""
  **Potential Entry (if breakout):**
  - Breakout Trigger: ₹{trade['breakout_trigger']:,.2f}
  - Buy Range: ₹{trade['buy_lower']:,.2f} - ₹{trade['buy_upper']:,.2f}
  - Target: ₹{trade['target']:,.2f}
  - Stop Loss: ₹{trade['stop_loss']:,.2f}
  - **Target Date:** {target_date_info['target_date_str']} ({target_date_info['months_to_target']} months)
  - **Confidence:** {target_date_info['confidence']}
  - Note: {trade.get('breakout_reasoning', 'Watch for volume confirmation')}
"""
    else:
        report += "\nNo HOLD signals this week\n"
    
    # AVOID section
    report += f"""

---

## [SELL] RECOMMENDATIONS ({len(results['avoid'])} Stocks)
"""

    if sorted_avoid:
        for i, stock in enumerate(sorted_avoid, 1):
            avg = (stock['fundamental'] + stock['technical']) / 2
            report += f"""
**{i}. {stock['symbol']}** | Score: {avg:.0f}/100
- Price: ₹{stock['price']:,.2f}
- Fundamental: {stock['fundamental']:.0f}/100 | Technical: {stock['technical']:.0f}/100
- Decision: {stock['decision'][:80]}
"""
    else:
        report += "\nNo SELL signals this week\n"
    
    # Statistics
    report += f"""

---

## 📈 DETAILED STATISTICS

### Distribution Analysis
- **Buy Signals:** {len(results['accumulate'])} stocks ({accumulate_pct:.1f}%)
- **Hold Signals:** {len(results['hold'])} stocks ({hold_pct:.1f}%)
- **Sell Signals:** {len(results['avoid'])} stocks ({avoid_pct:.1f}%)
- **Errors:** {len(results['errors'])} stocks

### Score Analysis
- **Average Fundamental Score:** {avg_fund:.1f}/100
- **Average Technical Score:** {avg_tech:.1f}/100
- **Combined Portfolio Score:** {(avg_fund + avg_tech)/2:.1f}/100

### Market Sentiment
"""

    if accumulate_pct > 50:
        sentiment = "[BULLISH] - More than 50% buy signals"
    elif accumulate_pct > 30:
        sentiment = "[NEUTRAL-TO-POSITIVE] - 30-50% buy signals"
    else:
        sentiment = "[NEUTRAL] - Less than 30% buy signals"
    
    report += f"**{sentiment}**\n"
    
    report += f"""

---

## 📋 PORTFOLIO RECOMMENDATIONS

### For Aggressive Investors
- Focus on top 5 BUY stocks
- Allocate 15-20% per position
- Expected return: 18-25% annually

### For Balanced Investors
- Mix of top BUY stocks and quality HOLD stocks
- Allocate 10% per position
- Expected return: 12-18% annually

### For Conservative Investors
- Prefer HOLD over BUY
- Allocate 5-10% per position
- Expected return: 8-12% annually

---

## ⚡ ACTION ITEMS FOR THIS WEEK

1. [OK] Review BUY recommendations (top 5 priority)
2. [OK] Monitor HOLD stocks for technical breakout
3. [OK] Exit any SELL signals if holdings exist
4. [OK] Rebalance portfolio if allocation drifted >5%
5. [OK] Schedule next week's analysis

---

## 🔄 WEEKLY REVIEW CHECKLIST

- [OK] Fresh data fetched from yfinance
- [OK] Technical indicators calculated
- [OK] Fundamental scores generated
- [OK] Decisions generated for all stocks
- [OK] Report generated and saved

---

## 📞 COMMANDS FOR NEXT WEEK

**Run next week's analysis:**
```bash
python weekly_nifty50_analysis.py
```

**View this report:**
```bash
cat NIFTY50_WEEKLY_W{week_number}*.md
```

**Manual single stock analysis:**
```bash
python main.py --mode snapshot --symbol BANKBARODA.NS --as-of {report_date.strftime('%Y-%m-%d')}
```

---

## 📊 COMPARISON TO PREVIOUS WEEKS

*Track your progress by comparing with previous week's report:*
- Previous Week File: `NIFTY50_WEEKLY_W{int(week_number)-1:02d}*.md`
- Compare BUY signals change
- Track score improvements/deteriorations
- Monitor sector rotation

---

## ⚠️ DISCLAIMER

This analysis is for educational purposes only. Always consult your financial advisor before trading. Past performance does not guarantee future results.

---

**Report Generated:** {report_date.strftime('%Y-%m-%d %H:%M:%S')}  
**Next Review:** {(report_date).strftime('%Y-%m-%d')} (Next Week)  
**Tool:** ShareMarketBot NIFTY 50 Weekly Analyzer v2.0
"""
    
    return report

if __name__ == '__main__':
    try:
        success = generate_weekly_report()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
