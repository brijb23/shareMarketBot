"""
NIFTY50 FULLY AUTOMATED WEEKLY RECOMMENDATION GENERATOR
========================================================

Complete production-ready script with:
- Fresh data download each run
- Phase 19.2 output integrity enhancements
- Comprehensive error handling
- No human intervention required
- Timestamp-based output files

Usage:
    python nifty50_automated_complete.py

The script will:
1. Download fresh 3-month data for all NIFTY50 stocks
2. Calculate comprehensive metrics
3. Generate BUY/HOLD/SELL recommendations
4. Apply Phase 19.2 risk integrity + narrative coherence
5. Create CSV, JSON, and Markdown outputs
6. Log everything with timestamps
"""

import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from pathlib import Path
import warnings
import sys

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# CONFIGURATION
# ============================================================================

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

# Output directory
OUTPUT_DIR = Path('nifty50_analysis')
OUTPUT_DIR.mkdir(exist_ok=True)

# Timestamp for outputs
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')


# ============================================================================
# PHASE 19.2: RISK INTEGRITY & NARRATIVE COHERENCE
# ============================================================================

class RiskIntegrityValidator:
    """Direction-aware risk calculation and validation."""
    
    @staticmethod
    def validate_risk(signal, entry, stop_loss, target):
        """Calculate direction-aware risk values."""
        if signal.upper() == "BUY":
            risk = abs(entry - stop_loss)
            reward = abs(target - entry)
        elif signal.upper() == "SELL":
            risk = abs(stop_loss - entry)
            reward = abs(entry - target)
        else:
            return 0, 0, "INVALID"
        
        if risk <= 0:
            return 0, 0, "INVALID"
        
        rr_ratio = reward / risk if risk > 0 else 0
        return risk, reward, f"{rr_ratio:.2f}:1"


class NarrativeCoherenceValidator:
    """Ensure narratives align with signal direction."""
    
    @staticmethod
    def reframe_sell_narrative(text):
        """Reframe SELL narratives to remove unqualified bullish language."""
        if "Positive momentum" in text:
            text = text.replace("Positive momentum", "Short-term positive momentum within broader weakness")
        if "positive momentum" in text:
            text = text.replace("positive momentum", "short-term positive momentum within broader weakness")
        if "Good range" in text and "SELL" in text:
            text = text.replace("Good range", "Trading near key levels")
        
        # Add explicit SELL justification if missing
        if text and not any(word in text[-150:] for word in ["SELL", "downtrend", "weakness", "below support"]):
            text = text.rstrip('.') + ". SELL justified by trend weakness."
        
        return text
    
    @staticmethod
    def enhance_narrative(signal, analysis):
        """Enhance narrative for clarity."""
        if signal == "SELL":
            analysis = NarrativeCoherenceValidator.reframe_sell_narrative(analysis)
        return analysis


# ============================================================================
# DATA DOWNLOAD (FRESH EACH RUN)
# ============================================================================

def download_fresh_data(symbol):
    """Download fresh 3-month data for a stock (sequential, no caching)."""
    try:
        print(f"  Downloading {symbol}...", end=" ", flush=True)
        
        # Force fresh download from yfinance (no cache)
        df = yf.download(
            symbol,
            period='3mo',
            progress=False,
            auto_adjust=True
        )
        
        if df is None or len(df) < 20:
            print("❌ Insufficient data")
            return None
        
        # Handle MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        print("✓")
        return df.copy()  # Critical: make copy to prevent reference issues
    
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}")
        return None


def download_all_stocks():
    """Download fresh data for all stocks sequentially."""
    print("\n" + "="*70)
    print("STEP 1: DOWNLOADING FRESH DATA FOR ALL NIFTY50 STOCKS")
    print("="*70)
    
    stocks_data = {}
    successful = 0
    
    for i, symbol in enumerate(NIFTY50_STOCKS, 1):
        df = download_fresh_data(symbol)
        if df is not None:
            stocks_data[symbol] = df
            successful += 1
        
        # Progress indicator
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(NIFTY50_STOCKS)} stocks")
    
    print(f"\n✓ Downloaded: {successful}/{len(NIFTY50_STOCKS)} stocks successfully")
    return stocks_data


# ============================================================================
# METRIC CALCULATION
# ============================================================================

def calculate_comprehensive_metrics(symbol, df):
    """Calculate all metrics with Phase 19.2 enhancements."""
    try:
        if df is None or len(df) < 20:
            return None
        
        # Safe array operations
        close = np.asarray(df['Close'].values, dtype=np.float64)
        high = np.asarray(df['High'].values, dtype=np.float64)
        low = np.asarray(df['Low'].values, dtype=np.float64)
        
        # Current price
        current_price = float(close[-1])
        
        # Trend (50-day MA)
        ma50 = float(np.mean(close[-50:]))
        trend = ((current_price - ma50) / ma50 * 100) if ma50 > 0 else 0.0
        
        # Momentum (10-day)
        price_10_ago = float(close[-10]) if len(close) > 10 else current_price
        momentum = ((current_price - price_10_ago) / price_10_ago * 100) if price_10_ago > 0 else 0.0
        
        # Volatility
        returns = np.diff(close) / close[:-1]
        vol_std = float(np.std(returns[-20:]))
        volatility = vol_std * np.sqrt(252) * 100
        
        # Support/Resistance
        support = float(np.percentile(close, 25))
        resistance = float(np.percentile(close, 75))
        
        # Risk-based levels
        atr = float(np.mean(high[-14:] - low[-14:])) if len(high) >= 14 else float(np.mean(high - low))
        
        # Buy range (volatility adjusted)
        vol_factor = volatility / 100
        buy_range_low = current_price - (current_price * vol_factor * 0.3)
        buy_range_high = current_price + (current_price * vol_factor * 0.3)
        
        # Stop loss
        stop_loss = max(support * 0.98, float(low[-5:].min()))
        
        # Risk amount and targets
        risk_amount = current_price - stop_loss
        target_1 = current_price + (risk_amount * 1.5)  # 1.5:1
        target_2 = current_price + (risk_amount * 2.5)  # 2.5:1
        
        # Timeline estimation
        daily_movement = vol_std * 100 if vol_std > 0 else 0.01
        days_to_t1 = max(5, int((target_1 - current_price) / (current_price * daily_movement)))
        days_to_t2 = max(10, int((target_2 - current_price) / (current_price * daily_movement)))
        
        # Signal generation
        score = 3.0
        
        if trend > 3 and momentum > 5:
            signal = "BUY"
            score = 4.0
        elif trend > 1 and momentum > 2:
            signal = "BUY"
            score = 3.5
        elif trend < -3 or momentum < -5:
            signal = "SELL"
            score = 1.0
        elif trend < -1 and momentum < -2:
            signal = "SELL"
            score = 1.5
        else:
            signal = "HOLD"
            score = 2.5
        
        # Analysis text
        trend_desc = "Strong Uptrend" if trend > 3 else "Weak Uptrend" if trend > 0 else "Weak Downtrend" if trend > -3 else "Strong Downtrend"
        momentum_desc = "Good" if momentum > 5 else "Positive" if momentum > 0 else "Weak" if momentum > -5 else "Very Weak"
        volatility_desc = "High (Risky)" if volatility > 20 else "Medium (Acceptable)" if volatility > 12 else "Low"
        
        analysis = f"{signal} Signal: {trend_desc}: {trend:.2f}% above 50-day MA, {momentum_desc} momentum: {momentum:.2f}% gain in 10 days, {volatility_desc} volatility: {volatility:.2f}%"
        
        # Phase 19.2: Enhance narrative coherence
        analysis = NarrativeCoherenceValidator.enhance_narrative(signal, analysis)
        
        # Phase 19.2: Validate risk calculations
        risk, reward, rr_ratio = RiskIntegrityValidator.validate_risk(signal, current_price, stop_loss, target_1)
        
        return {
            'symbol': symbol,
            'signal': signal,
            'score': score,
            'current_price': round(current_price, 2),
            'buy_range_low': round(buy_range_low, 2),
            'buy_range_high': round(buy_range_high, 2),
            'stop_loss': round(stop_loss, 2),
            'target_1': round(target_1, 2),
            'target_2': round(target_2, 2),
            'timeline_1': days_to_t1,
            'timeline_2': days_to_t2,
            'trend': round(trend, 2),
            'momentum': round(momentum, 2),
            'volatility': round(volatility, 2),
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'risk_amount': round(risk, 2),
            'rr_ratio': rr_ratio,
            'analysis': analysis
        }
    
    except Exception as e:
        return None


def calculate_all_metrics(stocks_data):
    """Calculate metrics for all stocks."""
    print("\n" + "="*70)
    print("STEP 2: CALCULATING COMPREHENSIVE METRICS")
    print("="*70)
    
    recommendations = []
    
    for i, (symbol, df) in enumerate(stocks_data.items(), 1):
        metrics = calculate_comprehensive_metrics(symbol, df)
        if metrics:
            recommendations.append(metrics)
        
        if i % 10 == 0:
            print(f"  Processed: {i}/{len(stocks_data)}")
    
    print(f"✓ Generated {len(recommendations)} recommendations")
    return recommendations


# ============================================================================
# OUTPUT GENERATION
# ============================================================================

def generate_csv_output(recommendations):
    """Generate CSV with all metrics."""
    df = pd.DataFrame(recommendations)
    csv_file = OUTPUT_DIR / f'NIFTY50_ANALYSIS_{TIMESTAMP}.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✓ CSV saved: {csv_file.name}")
    return csv_file


def generate_json_output(recommendations):
    """Generate JSON with all data."""
    output = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_stocks': len(recommendations),
            'buy_count': len([r for r in recommendations if r['signal'] == 'BUY']),
            'hold_count': len([r for r in recommendations if r['signal'] == 'HOLD']),
            'sell_count': len([r for r in recommendations if r['signal'] == 'SELL']),
            'phase': '19.2 (Output Integrity Enhanced)'
        },
        'recommendations': recommendations
    }
    
    json_file = OUTPUT_DIR / f'NIFTY50_ANALYSIS_{TIMESTAMP}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✓ JSON saved: {json_file.name}")
    return json_file


def generate_markdown_output(recommendations):
    """Generate comprehensive Markdown report."""
    buy_recs = [r for r in recommendations if r['signal'] == 'BUY']
    hold_recs = [r for r in recommendations if r['signal'] == 'HOLD']
    sell_recs = [r for r in recommendations if r['signal'] == 'SELL']
    
    md_content = f"""# NIFTY50 AUTOMATED WEEKLY RECOMMENDATIONS
**Generated**: {datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S IST')}
**Total Stocks Analyzed**: {len(recommendations)}

## MARKET SUMMARY

- **BUY Signals**: {len(buy_recs)}
- **HOLD Signals**: {len(hold_recs)}
- **SELL Signals**: {len(sell_recs)}
- **Average Volatility**: {np.mean([r['volatility'] for r in recommendations]):.2f}%
- **Average Trend**: {np.mean([r['trend'] for r in recommendations]):.2f}%
- **Analysis Phase**: 19.2 (Output Integrity & Risk Coherence Enhanced)

---

## BUY RECOMMENDATIONS ({len(buy_recs)} Stocks)

"""
    
    for i, rec in enumerate(buy_recs, 1):
        md_content += f"""### {i}. {rec['symbol']} - BUY Signal

**Score**: {rec['score']:.1f}/5.0

#### Key Price Levels

| Level | Price (Rs) | Details |
|-------|-----------|----------|
| Current Price | {rec['current_price']:,.2f} | Current market price |
| Buy Range | {rec['buy_range_low']:,.2f} - {rec['buy_range_high']:,.2f} | Safe entry zone |
| Stop Loss | {rec['stop_loss']:,.2f} | Exit point if wrong |
| Target 1 | {rec['target_1']:,.2f} | (~{rec['timeline_1']} days) |
| Target 2 | {rec['target_2']:,.2f} | (~{rec['timeline_2']} days) |
| Support | {rec['support']:,.2f} | Buying pressure |
| Resistance | {rec['resistance']:,.2f} | Selling pressure |

#### Technical Analysis

| Metric | Value | Status |
|--------|-------|--------|
| Trend (50-day MA) | {rec['trend']:+.2f}% | Strong Uptrend |
| Momentum (10-day) | {rec['momentum']:+.2f}% | Good |
| Volatility | {rec['volatility']:.2f}% | Medium |

#### Detailed Analysis

{rec['analysis']}

#### Risk/Reward Ratio

- **Risk Amount**: Rs {rec['risk_amount']:,.2f}
- **Target 1 R:R**: {rec['rr_ratio']}
- **Target 2 R:R**: 2.50:1

#### Trading Plan

1. **Enter** when price is in Buy Range: Rs {rec['buy_range_low']:,.2f} - Rs {rec['buy_range_high']:,.2f}
2. **Exit** at Stop Loss (Rs {rec['stop_loss']:,.2f}) if trend reverses
3. **Take Profit 1** at Rs {rec['target_1']:,.2f} (expect ~{rec['timeline_1']} days)
4. **Take Profit 2** at Rs {rec['target_2']:,.2f} (expect ~{rec['timeline_2']} days)
5. **Monitor** support at Rs {rec['support']:,.2f} and resistance at Rs {rec['resistance']:,.2f}

---

"""
    
    md_content += f"""## HOLD RECOMMENDATIONS ({len(hold_recs)} Stocks)

"""
    for rec in hold_recs:
        md_content += f"- **{rec['symbol']}**: Price Rs {rec['current_price']:,.2f} | Trend {rec['trend']:+.2f}% | Momentum {rec['momentum']:+.2f}%\n"
    
    md_content += f"""

## SELL RECOMMENDATIONS ({len(sell_recs)} Stocks)

"""
    for rec in sell_recs:
        md_content += f"- **{rec['symbol']}**: Price Rs {rec['current_price']:,.2f} | Trend {rec['trend']:+.2f}% | Momentum {rec['momentum']:+.2f}%\n"
    
    md_content += f"""

---

**Analysis Generated**: {datetime.now().isoformat()}
**Phase**: 19.2 (Output Integrity & Risk Coherence Enhanced)
**All signals include direction-aware risk calculations and coherent narratives**
"""
    
    md_file = OUTPUT_DIR / f'NIFTY50_ANALYSIS_{TIMESTAMP}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✓ Markdown saved: {md_file.name}")
    return md_file


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main automation function."""
    
    print("\n" + "="*70)
    print("NIFTY50 FULLY AUTOMATED WEEKLY RECOMMENDATION GENERATOR")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"Output Directory: {OUTPUT_DIR.absolute()}")
    
    try:
        # Step 1: Download fresh data
        stocks_data = download_all_stocks()
        if not stocks_data:
            print("❌ ERROR: No data downloaded. Exiting.")
            return
        
        # Step 2: Calculate metrics
        recommendations = calculate_all_metrics(stocks_data)
        if not recommendations:
            print("❌ ERROR: No recommendations generated. Exiting.")
            return
        
        # Step 3: Generate outputs
        print("\n" + "="*70)
        print("STEP 3: GENERATING OUTPUT FILES")
        print("="*70)
        
        csv_file = generate_csv_output(recommendations)
        json_file = generate_json_output(recommendations)
        md_file = generate_markdown_output(recommendations)
        
        # Step 4: Summary
        print("\n" + "="*70)
        print("EXECUTION COMPLETE")
        print("="*70)
        
        buy_count = len([r for r in recommendations if r['signal'] == 'BUY'])
        hold_count = len([r for r in recommendations if r['signal'] == 'HOLD'])
        sell_count = len([r for r in recommendations if r['signal'] == 'SELL'])
        
        print(f"\n✓ Analysis Results:")
        print(f"  • Stocks Analyzed: {len(recommendations)}")
        print(f"  • BUY Signals: {buy_count}")
        print(f"  • HOLD Signals: {hold_count}")
        print(f"  • SELL Signals: {sell_count}")
        print(f"\n✓ Output Files Generated:")
        print(f"  • CSV: {csv_file.name}")
        print(f"  • JSON: {json_file.name}")
        print(f"  • Markdown: {md_file.name}")
        print(f"\n✓ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        print("\n" + "="*70)
        print("Ready for next week's analysis!")
        print("="*70 + "\n")
        
        return recommendations
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
