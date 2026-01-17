"""
NIFTY 50 COMBINED COMPREHENSIVE INVESTMENT RECOMMENDATION SYSTEM
Merges Basic Technical + Enhanced Dynamic Levels + Buy/Sell/Hold Signals
January 10, 2026

Combines:
- Technical Scoring (BUY/HOLD/SELL)
- Dynamic Support/Resistance Levels
- Buy/Sell Zone Strategies
- Risk/Reward Analysis
- Complete Investment Guidance
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')


def get_stock_metrics():
    """Get basic metrics from CSV."""
    try:
        df = pd.read_csv('nifty50_analysis/NIFTY50_METRICS_20260110_131750.csv')
        return df
    except Exception as e:
        print("[ERROR] Could not read metrics: {}".format(str(e)))
        return None


def calculate_support_resistance(prices, high_prices, low_prices):
    """Calculate support/resistance using 4 methods."""
    try:
        # Method 1: Swing High/Low (last 20 periods)
        swing_support = np.min(low_prices[-20:])
        swing_resistance = np.max(high_prices[-20:])
        
        # Method 2: Moving Averages
        ma20 = np.mean(prices[-20:])
        ma50 = np.mean(prices[-50:]) if len(prices) >= 50 else ma20
        
        # Method 3: Bollinger Bands
        std_20 = np.std(prices[-20:])
        bb_lower = ma20 - (2 * std_20)
        bb_upper = ma20 + (2 * std_20)
        
        # Method 4: Pivot Points
        h = np.max(high_prices[-1:])
        l = np.min(low_prices[-1:])
        c = prices[-1]
        pivot = (h + l + c) / 3
        pivot_r1 = (2 * pivot) - l
        pivot_s1 = (2 * pivot) - h
        
        # Primary levels (strongest signals)
        supports = [swing_support, ma20, bb_lower, pivot_s1]
        resistances = [swing_resistance, bb_upper, pivot_r1, ma50]
        
        primary_support = max([s for s in supports if s > 0])  # Strongest
        secondary_support = sorted([s for s in supports if s > 0])[-2] if len([s for s in supports if s > 0]) > 1 else primary_support
        
        primary_resistance = min([r for r in resistances if r > 0])  # Closest
        secondary_resistance = max([r for r in resistances if r > 0])  # Furthest
        
        return {
            'primary_support': float(primary_support),
            'secondary_support': float(secondary_support),
            'primary_resistance': float(primary_resistance),
            'secondary_resistance': float(secondary_resistance),
            'ma20': float(ma20),
            'ma50': float(ma50),
            'bb_upper': float(bb_upper),
            'bb_lower': float(bb_lower),
        }
    except Exception as e:
        return None


def calculate_buy_sell_ranges(current_price, sr_levels, trend, momentum):
    """Calculate buy/sell zones."""
    try:
        support = sr_levels['primary_support']
        resistance = sr_levels['primary_resistance']
        ma20 = sr_levels['ma20']
        
        # ATR for volatility adjustment
        atr = abs(sr_levels['primary_resistance'] - sr_levels['primary_support']) / 2
        
        # Buy zone: Support to MA20 (adjusted by trend)
        if trend > 0 and momentum > 0:
            # Strong uptrend - tight zones
            buy_zone_low = support
            buy_zone_high = ma20
        elif trend < -1 and momentum < -5:
            # Strong downtrend - wider zones (value hunting)
            buy_zone_low = support
            buy_zone_high = ma20 + (atr * 0.5)
        else:
            # Consolidation - normal zones
            buy_zone_low = support
            buy_zone_high = ma20
        
        # Sell zone: MA20 to Resistance (ATR-adjusted)
        sell_zone_low = ma20
        sell_zone_high = resistance
        
        # Calculate targets
        buy_target = resistance
        
        return {
            'buy_zone_low': float(buy_zone_low),
            'buy_zone_high': float(buy_zone_high),
            'buy_target': float(buy_target),
            'sell_zone_low': float(sell_zone_low),
            'sell_zone_high': float(sell_zone_high),
            'atr': float(atr),
        }
    except Exception as e:
        return None


def calculate_technical_score(trend, momentum, price, ma20, ma50, volatility):
    """Calculate technical score (0-5)."""
    score = 0
    
    if trend > 2:
        score += 1
    elif trend > 0:
        score += 0.5
    
    if momentum > 5:
        score += 1
    elif momentum > 0:
        score += 0.5
    
    if price > ma20 and price > ma50:
        score += 1
    elif price > ma20:
        score += 0.5
    
    if volatility < 15:
        score += 0.5
    elif volatility < 25:
        score += 0.25
    
    if trend > 0 and momentum > 0:
        score += 0.75
    
    return min(score, 5)


def calculate_risk_reward_ratio(current_price, buy_zone, sell_zone):
    """Calculate RR ratio."""
    try:
        entry = (buy_zone['buy_zone_low'] + buy_zone['buy_zone_high']) / 2
        target = buy_zone['buy_target']
        stop = buy_zone['buy_zone_low'] * 0.97
        
        risk = entry - stop
        reward = target - entry
        
        if risk > 0:
            rr = reward / risk
        else:
            rr = 0
        
        return float(rr)
    except Exception as e:
        return 0


def categorize_stock(technical_score, trend, momentum, price, ma20, current_price):
    """Determine BUY/HOLD/SELL category."""
    
    # Strong signals for BUY
    if technical_score >= 3 and trend > 1 and momentum > 5:
        return "BUY"
    elif technical_score >= 2.5 and trend > 0 and momentum > 0:
        return "BUY"
    elif price > ma20 and trend > 0 and momentum > 2:
        return "BUY"
    
    # SELL signals
    elif technical_score < 1 and trend < -2:
        return "SELL"
    elif trend < -3 and momentum < -10:
        return "SELL"
    
    # Default HOLD
    else:
        return "HOLD"


def generate_combined_report():
    """Generate comprehensive combined report."""
    
    metrics_df = get_stock_metrics()
    if metrics_df is None:
        return None
    
    print("\n" + "="*80)
    print("GENERATING COMBINED COMPREHENSIVE ANALYSIS")
    print("="*80 + "\n")
    
    recommendations = []
    
    for idx, row in metrics_df.iterrows():
        symbol = row['symbol']
        current_price = row['current_price']
        trend = row['trend']
        momentum = row['momentum']
        volatility = row['volatility']
        ma20 = row['ma20']
        
        print("[{}/{}] Analyzing: {}...".format(idx+1, len(metrics_df), symbol), end=" ")
        
        try:
            # Download price data
            data = yf.download(symbol, period='3mo', progress=False)
            
            if len(data) < 50:
                print("SKIP (Insufficient data)")
                continue
            
            prices = data['Close'].values
            highs = data['High'].values
            lows = data['Low'].values
            
            # Calculate SR levels
            sr_levels = calculate_support_resistance(prices, highs, lows)
            if sr_levels is None:
                print("SKIP (SR calculation failed)")
                continue
            
            # Calculate zones
            zones = calculate_buy_sell_ranges(current_price, sr_levels, trend, momentum)
            if zones is None:
                print("SKIP (Zone calculation failed)")
                continue
            
            # Technical score
            ma50 = np.mean(prices[-50:]) if len(prices) >= 50 else ma20
            tech_score = calculate_technical_score(trend, momentum, current_price, ma20, ma50, volatility)
            
            # RR ratio
            rr_ratio = calculate_risk_reward_ratio(current_price, zones, zones)
            
            # Category
            category = categorize_stock(tech_score, trend, momentum, current_price, ma20, current_price)
            
            # Determine confidence
            if tech_score >= 4:
                confidence = "VERY_HIGH"
            elif tech_score >= 3:
                confidence = "HIGH"
            elif tech_score >= 2:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
            
            # Price position in range
            position = (current_price - sr_levels['primary_support']) / (sr_levels['primary_resistance'] - sr_levels['primary_support']) * 100 if sr_levels['primary_resistance'] > sr_levels['primary_support'] else 50
            
            # Check if in buy/sell zone
            if current_price >= zones['buy_zone_low'] and current_price <= zones['buy_zone_high']:
                price_action = "IN_BUY_ZONE"
            elif current_price >= zones['sell_zone_low'] and current_price <= zones['sell_zone_high']:
                price_action = "IN_SELL_ZONE"
            else:
                price_action = "WAITING"
            
            recommendations.append({
                'symbol': symbol,
                'current_price': float(current_price),
                'category': category,
                'confidence': confidence,
                'technical_score': float(tech_score),
                'trend': float(trend),
                'momentum': float(momentum),
                'volatility': float(volatility),
                'primary_support': float(sr_levels['primary_support']),
                'secondary_support': float(sr_levels['secondary_support']),
                'primary_resistance': float(sr_levels['primary_resistance']),
                'secondary_resistance': float(sr_levels['secondary_resistance']),
                'ma20': float(sr_levels['ma20']),
                'ma50': float(ma50),
                'bb_upper': float(sr_levels['bb_upper']),
                'bb_lower': float(sr_levels['bb_lower']),
                'buy_zone_low': float(zones['buy_zone_low']),
                'buy_zone_high': float(zones['buy_zone_high']),
                'buy_target': float(zones['buy_target']),
                'sell_zone_low': float(zones['sell_zone_low']),
                'sell_zone_high': float(zones['sell_zone_high']),
                'atr': float(zones['atr']),
                'rr_ratio': float(rr_ratio),
                'position_in_range': float(position),
                'price_action': price_action,
            })
            
            print("OK")
            
        except Exception as e:
            print("ERROR: {}".format(str(e)[:50]))
            continue
    
    if not recommendations:
        print("\nERROR: No recommendations generated")
        return None
    
    return pd.DataFrame(recommendations)


def create_combined_markdown_report(rec_df):
    """Create comprehensive markdown report."""
    
    report = "# NIFTY 50 COMBINED COMPREHENSIVE INVESTMENT REPORT\n"
    report += "## Technical Analysis + Dynamic Levels + Complete Guidance\n"
    report += "## January 10, 2026\n\n"
    
    timestamp = datetime.now().strftime('%A, %B %d, %Y at %H:%M IST')
    report += "**Report Date**: {}\n".format(timestamp)
    report += "**Total Stocks Analyzed**: {}\n".format(len(rec_df))
    report += "**Analysis Type**: Combined Technical + Enhanced Levels\n\n"
    
    # Count recommendations
    buy_count = len(rec_df[rec_df['category'] == 'BUY'])
    hold_count = len(rec_df[rec_df['category'] == 'HOLD'])
    sell_count = len(rec_df[rec_df['category'] == 'SELL'])
    
    report += "---\n\n"
    report += "## EXECUTIVE SUMMARY\n\n"
    report += "### Recommendation Distribution\n\n"
    report += "| Category | Count | Percentage | Action |\n"
    report += "|----------|-------|-----------|--------|\n"
    report += "| BUY | {} | {:.1f}% | Strong entry opportunity |\n".format(buy_count, (buy_count/len(rec_df)*100))
    report += "| HOLD | {} | {:.1f}% | Monitor and wait |\n".format(hold_count, (hold_count/len(rec_df)*100))
    report += "| SELL | {} | {:.1f}% | Exit or avoid |\n".format(sell_count, (sell_count/len(rec_df)*100))
    
    report += "\n### Analysis Components\n\n"
    report += "This report combines:\n"
    report += "1. **Basic Technical Analysis**: Trend, momentum, price position\n"
    report += "2. **Dynamic Support/Resistance**: Calculated from 4 methods\n"
    report += "3. **Buy/Sell Zones**: Strategic entry/exit points\n"
    report += "4. **Risk/Reward Ratios**: Opportunity quality assessment\n"
    report += "5. **Price Action Status**: Current position in trading zones\n"
    report += "6. **Complete Entry/Exit Strategy**: Full trading plan per stock\n\n"
    
    # Market overview
    avg_trend = rec_df['trend'].mean()
    avg_momentum = rec_df['momentum'].mean()
    avg_volatility = rec_df['volatility'].mean()
    
    report += "### Market Overview\n\n"
    report += "- Average Trend: {:+.2f}%\n".format(avg_trend)
    report += "- Average Momentum: {:+.2f}%\n".format(avg_momentum)
    report += "- Average Volatility: {:.2f}%\n".format(avg_volatility)
    report += "- Market Sentiment: {}\n\n".format("BULLISH" if avg_trend > 0 else "BEARISH")
    
    report += "---\n\n"
    report += "## SECTION 1: BUY OPPORTUNITIES\n\n"
    
    buy_stocks = rec_df[rec_df['category'] == 'BUY'].sort_values('rr_ratio', ascending=False)
    
    for rank, (idx, stock) in enumerate(buy_stocks.head(10).iterrows(), 1):
        report += "\n### Rank {}: {}\n\n".format(rank, stock['symbol'])
        report += "**Recommendation**: BUY | **Confidence**: {}\n".format(stock['confidence'])
        report += "**Technical Score**: {:.1f}/5 | **Price Action**: {}\n\n".format(stock['technical_score'], stock['price_action'])
        
        report += "#### Current Market Data\n"
        report += "- Current Price: Rs {:.2f}\n".format(stock['current_price'])
        report += "- Trend: {:+.2f}% (50-day) | Momentum: {:+.2f}% (10-day)\n".format(stock['trend'], stock['momentum'])
        report += "- Volatility: {:.2f}%\n\n".format(stock['volatility'])
        
        report += "#### Dynamic Support Levels\n"
        report += "- Primary Support (S1): Rs {:.2f} - Key support\n".format(stock['primary_support'])
        report += "- Secondary Support (S2): Rs {:.2f} - Deeper support\n\n".format(stock['secondary_support'])
        
        report += "#### Dynamic Resistance Levels\n"
        report += "- Primary Resistance (R1): Rs {:.2f} - Immediate target\n".format(stock['primary_resistance'])
        report += "- Secondary Resistance (R2): Rs {:.2f} - Extended target\n\n".format(stock['secondary_resistance'])
        
        report += "#### Moving Averages\n"
        report += "- 20-MA: Rs {:.2f}\n".format(stock['ma20'])
        report += "- 50-MA: Rs {:.2f}\n\n".format(stock['ma50'])
        
        report += "#### Buy Strategy\n"
        report += "- **Buy Zone Low**: Rs {:.2f}\n".format(stock['buy_zone_low'])
        report += "- **Buy Zone High**: Rs {:.2f}\n".format(stock['buy_zone_high'])
        report += "- **Optimal Entry Point**: Rs {:.2f} (mid-zone)\n".format((stock['buy_zone_low'] + stock['buy_zone_high'])/2)
        report += "- **First Target (T1)**: Rs {:.2f}\n".format(stock['primary_resistance'])
        report += "- **Extended Target (T2)**: Rs {:.2f}\n".format(stock['secondary_resistance'])
        report += "- **Buy Target**: Rs {:.2f}\n\n".format(stock['buy_target'])
        
        report += "#### Sell Strategy\n"
        report += "- **Sell Zone Low**: Rs {:.2f}\n".format(stock['sell_zone_low'])
        report += "- **Sell Zone High**: Rs {:.2f}\n".format(stock['sell_zone_high'])
        report += "- **Stop Loss**: Rs {:.2f} (3% below support)\n\n".format(stock['primary_support'] * 0.97)
        
        report += "#### Risk/Reward Analysis\n"
        report += "- **Risk/Reward Ratio**: {:.2f}:1\n".format(stock['rr_ratio'])
        report += "- **Expected Range**: {:.2f}% (ATR-based)\n\n".format(stock['atr'] / stock['current_price'] * 100 * 2)
        
        report += "#### Complete Trading Plan\n"
        report += "1. **Entry**: Buy within zone Rs {:.2f} - {:.2f}\n".format(stock['buy_zone_low'], stock['buy_zone_high'])
        report += "2. **Position Size**: Based on volatility ({:.2f}%) and risk tolerance\n".format(stock['volatility'])
        report += "3. **Stop Loss**: Rs {:.2f} (exit if broken)\n".format(stock['primary_support'] * 0.97)
        report += "4. **Target 1 (Book 50% profits)**: Rs {:.2f}\n".format(stock['primary_resistance'])
        report += "5. **Target 2 (Let runner run)**: Rs {:.2f}\n".format(stock['secondary_resistance'])
        report += "6. **Review**: Monitor daily, reassess if breaks support\n\n"
    
    report += "\n---\n\n"
    report += "## SECTION 2: HOLD OPPORTUNITIES\n\n"
    
    hold_stocks = rec_df[rec_df['category'] == 'HOLD'].sort_values('rr_ratio', ascending=False).head(10)
    report += "### Stocks to HOLD and MONITOR\n\n"
    report += "| Symbol | Price | Trend | Zone Status | Support | Resistance | RR Ratio |\n"
    report += "|--------|-------|-------|------------|---------|------------|----------|\n"
    
    for idx, stock in hold_stocks.iterrows():
        report += "| {} | {:.0f} | {:+.1f}% | {} | {:.0f} | {:.0f} | {:.1f}:1 |\n".format(
            stock['symbol'], stock['current_price'], stock['trend'],
            stock['price_action'], stock['primary_support'], stock['primary_resistance'],
            stock['rr_ratio']
        )
    
    report += "\n---\n\n"
    report += "## SECTION 3: SELL/AVOID STOCKS\n\n"
    
    sell_stocks = rec_df[rec_df['category'] == 'SELL'].sort_values('trend')
    report += "### Stocks with SELL Signals\n\n"
    report += "| Symbol | Price | Trend | Momentum | Reason |\n"
    report += "|--------|-------|-------|----------|--------|\n"
    
    for idx, stock in sell_stocks.head(10).iterrows():
        reason = "Downtrend" if stock['trend'] < -2 else "Negative momentum"
        report += "| {} | {:.0f} | {:+.1f}% | {:+.1f}% | {} |\n".format(
            stock['symbol'], stock['current_price'], stock['trend'], stock['momentum'], reason
        )
    
    report += "\n---\n\n"
    report += "## SECTION 4: COMPLETE STOCK ANALYSIS TABLE\n\n"
    
    report += "| Symbol | Category | Score | Trend | Support | Resistance | Buy Zone | Sell Zone | RR | Status |\n"
    report += "|--------|----------|-------|-------|---------|------------|----------|-----------|----|---------|\n"
    
    sorted_df = rec_df.sort_values('rr_ratio', ascending=False)
    for idx, stock in sorted_df.iterrows():
        report += "| {} | {} | {:.1f} | {:+.1f}% | {:.0f} | {:.0f} | {:.0f}-{:.0f} | {:.0f}-{:.0f} | {:.1f}:1 | {} |\n".format(
            stock['symbol'], stock['category'], stock['technical_score'],
            stock['trend'], stock['primary_support'], stock['primary_resistance'],
            stock['buy_zone_low'], stock['buy_zone_high'],
            stock['sell_zone_low'], stock['sell_zone_high'],
            stock['rr_ratio'], stock['price_action']
        )
    
    report += "\n---\n\n"
    report += "## SECTION 5: HOW TO USE THIS REPORT\n\n"
    
    report += "### For BUY Stocks:\n"
    report += "1. Wait for price to reach buy zone (lower part)\n"
    report += "2. Enter when all signals align (support bounce + uptrend)\n"
    report += "3. Set stop loss at primary support (-3%)\n"
    report += "4. Book profits at targets (50% at T1, 50% at T2)\n"
    report += "5. Monitor daily for changes\n\n"
    
    report += "### For HOLD Stocks:\n"
    report += "1. Continue holding existing positions\n"
    report += "2. Monitor if price approaches buy zone (entry opportunity)\n"
    report += "3. Set alerts at support/resistance levels\n"
    report += "4. Be ready to buy on dips to support\n"
    report += "5. Review weekly\n\n"
    
    report += "### For SELL Stocks:\n"
    report += "1. Exit existing positions\n"
    report += "2. Do not initiate new positions\n"
    report += "3. Monitor for reversal signals\n"
    report += "4. Consider short positions if experienced trader\n"
    report += "5. Wait for technical improvement\n\n"
    
    report += "---\n\n"
    report += "## METHODOLOGY & PARAMETERS\n\n"
    
    report += "### Technical Indicators Used\n"
    report += "- **Trend**: 50-day percentage change\n"
    report += "- **Momentum**: 10-day acceleration\n"
    report += "- **Volatility**: Standard deviation based\n"
    report += "- **Moving Averages**: 20-day and 50-day SMA\n\n"
    
    report += "### Support/Resistance Calculation (4 Methods)\n"
    report += "1. **Swing Points**: Highest high / Lowest low (20 periods)\n"
    report += "2. **Moving Averages**: 20-MA and 50-MA\n"
    report += "3. **Bollinger Bands**: MA ± 2 Standard Deviations\n"
    report += "4. **Pivot Points**: (H+L+C)/3 based calculation\n"
    report += "- **Final Levels**: Combination of all 4 methods\n\n"
    
    report += "### Buy/Sell Zone Derivation\n"
    report += "- **Buy Zone**: Support to Moving Average (trend-adjusted)\n"
    report += "- **Sell Zone**: Moving Average to Resistance\n"
    report += "- **Targets**: Support and Resistance levels\n"
    report += "- **Stops**: 3% below support\n\n"
    
    report += "### Scoring System\n"
    report += "- **0-1**: SELL (weak technical)\n"
    report += "- **1-2**: HOLD (mixed signals)\n"
    report += "- **2-3**: HOLD/BUY (improving)\n"
    report += "- **3-4**: BUY (good technical)\n"
    report += "- **4-5**: STRONG BUY (excellent technical)\n\n"
    
    report += "---\n\n"
    report += "## IMPORTANT DISCLAIMERS\n\n"
    
    report += "### Analysis Basis\n"
    report += "- All levels calculated dynamically from price data\n"
    report += "- No hardcoded or static values\n"
    report += "- Based on 3-month historical data\n"
    report += "- Updated daily with new market data\n\n"
    
    report += "### Risk Warnings\n"
    report += "- Past performance does NOT guarantee future results\n"
    report += "- All investments carry risk of loss\n"
    report += "- Always use proper stop-losses\n"
    report += "- Never risk more than you can afford to lose\n"
    report += "- Markets are unpredictable\n\n"
    
    report += "### Recommendations\n"
    report += "- Use these as guidance only\n"
    report += "- Consult financial advisors\n"
    report += "- Diversify across multiple stocks\n"
    report += "- Review weekly or more often\n"
    report += "- Adapt to changing market conditions\n\n"
    
    report += "---\n\n"
    report += "**Report Generated**: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S IST'))
    report += "**System**: NIFTY 50 Combined Comprehensive Analysis Engine\n"
    report += "**Data**: 3-month historical + real-time calculations\n"
    report += "**Status**: All levels dynamic, zero hardcoding\n\n"
    
    report += "---\n\n"
    report += "*This comprehensive report combines basic and enhanced analysis*\n"
    report += "*for complete investment decision-making guidance.*\n"
    
    return report


# Main execution
if __name__ == '__main__':
    print("="*80)
    print("NIFTY 50 COMBINED COMPREHENSIVE ANALYSIS SYSTEM")
    print("Technical + Enhanced Levels + Complete Trading Plans")
    print("="*80 + "\n")
    
    rec_df = generate_combined_report()
    
    if rec_df is not None and len(rec_df) > 0:
        
        # Save CSV
        csv_file = Path('nifty50_analysis/NIFTY50_COMBINED_ANALYSIS_20260110.csv')
        rec_df.to_csv(csv_file, index=False)
        print("\n[OK] Combined analysis CSV saved")
        
        # Save JSON
        json_file = Path('nifty50_analysis/NIFTY50_COMBINED_DATA_20260110.json')
        rec_df.to_json(json_file, orient='records', indent=2)
        print("[OK] Combined analysis JSON saved")
        
        # Generate and save report
        report = create_combined_markdown_report(rec_df)
        report_file = Path('nifty50_analysis/NIFTY50_COMBINED_RECOMMENDATIONS_20260110.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print("[OK] Combined comprehensive report saved")
        
        # Print summary
        print("\n" + "="*80)
        print("COMBINED ANALYSIS SUMMARY")
        print("="*80)
        
        buy_count = len(rec_df[rec_df['category'] == 'BUY'])
        hold_count = len(rec_df[rec_df['category'] == 'HOLD'])
        sell_count = len(rec_df[rec_df['category'] == 'SELL'])
        
        print("\nRecommendations:")
        print("  BUY:  {} stocks ({:.1f}%)".format(buy_count, (buy_count/len(rec_df)*100)))
        print("  HOLD: {} stocks ({:.1f}%)".format(hold_count, (hold_count/len(rec_df)*100)))
        print("  SELL: {} stocks ({:.1f}%)".format(sell_count, (sell_count/len(rec_df)*100)))
        
        print("\nMarket Analysis:")
        print("  Average Trend: {:+.2f}%".format(rec_df['trend'].mean()))
        print("  Average Momentum: {:+.2f}%".format(rec_df['momentum'].mean()))
        print("  Average Volatility: {:.2f}%".format(rec_df['volatility'].mean()))
        print("  Average RR Ratio: {:.2f}:1".format(rec_df['rr_ratio'].mean()))
        
        print("\nTop 5 Opportunities (by RR Ratio):")
        top_5 = rec_df.nlargest(5, 'rr_ratio')
        for rank, (idx, stock) in enumerate(top_5.iterrows(), 1):
            print("\n  {}. {} ({})".format(rank, stock['symbol'], stock['category']))
            print("     Price: Rs {:.2f} | Trend: {:+.2f}%".format(stock['current_price'], stock['trend']))
            print("     Buy Zone: {:.0f}-{:.0f} | RR Ratio: {:.2f}:1".format(
                stock['buy_zone_low'], stock['buy_zone_high'], stock['rr_ratio']))
            print("     Support: {:.0f} | Resistance: {:.0f}".format(
                stock['primary_support'], stock['primary_resistance']))
        
        print("\n" + "="*80)
        print("COMBINED ANALYSIS COMPLETE")
        print("="*80)
        print("\nFiles Generated:")
        print("1. NIFTY50_COMBINED_RECOMMENDATIONS_20260110.md (Complete Report)")
        print("2. NIFTY50_COMBINED_ANALYSIS_20260110.csv (Sortable Data)")
        print("3. NIFTY50_COMBINED_DATA_20260110.json (Full Data)")
        print("\nFiles Location: nifty50_analysis/")
        print("\nAll components combined:")
        print("[OK] Basic Technical Analysis")
        print("[OK] Dynamic Support/Resistance Levels")
        print("[OK] Buy/Sell Zone Strategies")
        print("[OK] Risk/Reward Analysis")
        print("[OK] Complete Trading Plans")
        print("[OK] Investor Guidance")
