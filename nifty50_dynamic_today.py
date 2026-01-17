"""
NIFTY 50 DYNAMIC RECOMMENDATION - TODAY'S ANALYSIS
January 12, 2026 - Fresh Data

This script uses the latest available metrics and enhanced levels data
to generate fresh recommendations with dynamic R:R ratios.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path


def calculate_dynamic_rr(trend, momentum, volatility):
    """Calculate dynamic R:R based on trend, momentum, volatility."""
    rr = 1.5
    
    # Trend adjustment (±0.35)
    if trend > 3:
        rr += 0.35
    elif trend > 1:
        rr += 0.25
    elif trend > 0:
        rr += 0.15
    elif trend > -1:
        rr += 0.05
    elif trend > -3:
        rr -= 0.15
    else:
        rr -= 0.30
    
    # Momentum adjustment (±0.25)
    if momentum > 10:
        rr += 0.25
    elif momentum > 5:
        rr += 0.15
    elif momentum > 0:
        rr += 0.05
    elif momentum > -5:
        rr -= 0.10
    else:
        rr -= 0.20
    
    # Volatility adjustment (±0.25)
    if volatility < 12:
        rr += 0.10
    elif volatility <= 20:
        rr += 0.00
    elif volatility <= 25:
        rr -= 0.15
    else:
        rr -= 0.25
    
    return max(1.0, min(3.5, rr))


def main():
    """Generate fresh NIFTY50 recommendations for today."""
    
    print("="*80)
    print("NIFTY 50 DYNAMIC RECOMMENDATION - FRESH ANALYSIS FOR TODAY")
    print("="*80)
    print()
    
    # Find the latest metrics and enhanced levels files
    analysis_dir = Path('nifty50_analysis')
    
    # Get latest NIFTY50_METRICS file
    metrics_files = sorted(analysis_dir.glob('NIFTY50_METRICS_*.csv'), 
                          key=lambda x: x.stat().st_mtime, reverse=True)
    if not metrics_files:
        print("[ERROR] No NIFTY50_METRICS file found!")
        return
    
    metrics_file = metrics_files[0]
    print(f"[LOADING] Reading metrics data: {metrics_file.name}")
    
    # Get latest NIFTY50_ENHANCED_LEVELS file
    levels_files = sorted(analysis_dir.glob('NIFTY50_ENHANCED_LEVELS_*.csv'), 
                         key=lambda x: x.stat().st_mtime, reverse=True)
    if not levels_files:
        print("[ERROR] No NIFTY50_ENHANCED_LEVELS file found!")
        return
    
    levels_file = levels_files[0]
    print(f"[LOADING] Reading enhanced levels data: {levels_file.name}")
    
    try:
        levels_df = pd.read_csv(levels_file)
        metrics_df = pd.read_csv(metrics_file)
    except Exception as e:
        print(f"[ERROR] Failed to load files: {e}")
        return
    
    print(f"[OK] Loaded {len(metrics_df)} stocks")
    print()
    
    # Merge data on symbol
    df = levels_df.merge(metrics_df, on='symbol', how='inner', suffixes=('_levels', '_metrics'))
    
    # Use the metrics version of trend/momentum (more accurate)
    df['trend'] = df['trend_metrics']
    df['momentum'] = df['momentum_metrics']
    df['volatility'] = df['volatility']
    df['current_price'] = df['current_price_metrics']
    
    recommendations = []
    
    print("[PROCESSING] Generating recommendations...")
    
    for idx, row in df.iterrows():
        try:
            symbol = row['symbol']
            price = row.get('current_price', row.get('price', 0))
            trend = row.get('trend', 0)
            momentum = row.get('momentum', 0)
            volatility = row.get('volatility', 15)
            
            # Calculate dynamic R:R
            dynamic_rr = calculate_dynamic_rr(trend, momentum, volatility)
            
            # Calculate technical score
            score = 1.0
            if trend > 3:
                score += 1.0
            elif trend > 1:
                score += 0.7
            elif trend > 0:
                score += 0.4
            
            if momentum > 10:
                score += 1.0
            elif momentum > 5:
                score += 0.8
            elif momentum > 0:
                score += 0.5
            
            if volatility < 12:
                score += 1.0
            elif volatility <= 20:
                score += 0.9
            elif volatility <= 25:
                score += 0.5
            else:
                score += 0.2
            
            score = min(5.0, score)
            
            # Generate signal based on score and conditions
            # More lenient signal generation based on actual market conditions
            if score >= 3.5 and (trend > -2 or momentum > 5):
                signal = 'BUY'
            elif score < 2.5 or (trend < -3 and momentum < 0):
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            # Calculate stop and targets
            risk_distance = (volatility / 100) * price * 0.3
            stop = price - risk_distance
            target1 = price + (risk_distance * 1.2)
            target2 = price + (risk_distance * dynamic_rr)
            
            # Entry zones based on ATR
            atr_pct = volatility / 100 * 0.3
            entry_low = price * (1 - atr_pct)
            entry_high = price * (1 + atr_pct)
            
            # Create base recommendation
            base_rec = {
                'symbol': symbol,
                'signal': signal,
                'price': round(price, 2),
                'trend': round(trend, 2),
                'momentum': round(momentum, 2),
                'volatility': round(volatility, 2),
                'score': round(score, 2),
                'dynamic_rr': round(dynamic_rr, 2),
                'entry_low': round(entry_low, 2),
                'entry_high': round(entry_high, 2),
                'stop': round(stop, 2),
                'target_1': round(target1, 2),
                'target_2': round(target2, 2),
            }
            
            # Add support/resistance if available
            if 'primary_support' in row:
                base_rec['support'] = round(row['primary_support'], 2)
            if 'primary_resistance' in row:
                base_rec['resistance'] = round(row['primary_resistance'], 2)
            
            # Determine risk level
            if volatility < 15 and trend > 2:
                risk = 'LOW'
            elif volatility > 20 or trend < 2:
                risk = 'HIGH'
            else:
                risk = 'MEDIUM'
            
            # Determine exit strategy
            if momentum > 10 and trend > 2:
                exit_strategy = 'TRAILING_EXIT_PREFERRED'
            elif volatility > 20:
                exit_strategy = 'TIGHT_STOPS_RECOMMENDED'
            else:
                exit_strategy = 'FIXED_EXIT_STANDARD'
            
            base_rec['risk'] = risk
            base_rec['exit_strategy'] = exit_strategy
            
            recommendations.append(base_rec)
            
            if (idx + 1) % 11 == 0:
                print(f"  [{idx + 1}/{len(df)}] Complete")
        
        except Exception as e:
            print(f"  [SKIP] {row.get('symbol', 'Unknown')}: {str(e)[:30]}")
            continue
    
    print(f"[OK] Generated {len(recommendations)} dynamic recommendations")
    print()
    
    # Count signals
    buy_count = sum(1 for r in recommendations if r['signal'] == 'BUY')
    hold_count = sum(1 for r in recommendations if r['signal'] == 'HOLD')
    sell_count = sum(1 for r in recommendations if r['signal'] == 'SELL')
    
    # Calculate averages
    avg_trend = np.mean([r['trend'] for r in recommendations])
    avg_momentum = np.mean([r['momentum'] for r in recommendations])
    avg_rr = np.mean([r['dynamic_rr'] for r in recommendations])
    
    sentiment = 'BULLISH' if avg_trend > 0 else 'BEARISH'
    
    print("="*80)
    print(f"SUMMARY - BUY: {buy_count} | HOLD: {hold_count} | SELL: {sell_count}")
    print(f"Sentiment: {sentiment} | Avg Trend: {avg_trend:+.2f}% | Avg R:R: {avg_rr:.2f}:1")
    print("="*80)
    print()
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path('nifty50_analysis')
    output_dir.mkdir(exist_ok=True)
    
    # Save JSON
    json_file = output_dir / f'NIFTY50_DYNAMIC_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'summary': {
                'stocks_analyzed': len(recommendations),
                'buy': buy_count,
                'hold': hold_count,
                'sell': sell_count,
                'sentiment': sentiment,
                'avg_trend': round(avg_trend, 2),
                'avg_momentum': round(avg_momentum, 2),
                'avg_rr': round(avg_rr, 2),
            },
            'recommendations': recommendations
        }, f, indent=2)
    print(f"[SAVED] {json_file.name}")
    
    # Save CSV
    csv_file = output_dir / f'NIFTY50_DYNAMIC_{timestamp}.csv'
    df_output = pd.DataFrame(recommendations)
    df_output.to_csv(csv_file, index=False)
    print(f"[SAVED] {csv_file.name}")
    
    # Generate Markdown report
    md_file = output_dir / f'NIFTY50_DYNAMIC_{timestamp}.md'
    with open(md_file, 'w') as f:
        f.write("# NIFTY 50 DYNAMIC RECOMMENDATION REPORT\n")
        f.write(f"## {datetime.now().strftime('%B %d, %Y')} - Fresh Analysis\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Stocks**: {len(recommendations)} analyzed\n")
        f.write(f"**Sentiment**: {sentiment}\n\n")
        f.write(f"**BUY**: {buy_count} | **HOLD**: {hold_count} | **SELL**: {sell_count}\n\n")
        f.write(f"**Avg Trend**: {avg_trend:+.2f}% | **Avg Momentum**: {avg_momentum:+.2f}% | **Avg R:R**: {avg_rr:.2f}:1\n\n")
        f.write("---\n\n")
        f.write("## DYNAMIC R:R EXPLANATION\n\n")
        f.write("R:R ratio is now calculated dynamically based on:\n\n")
        f.write("- **Base**: 1.5:1\n")
        f.write("- **Trend**: Strong trends add up to +0.35, weak subtract up to -0.30\n")
        f.write("- **Momentum**: Strong momentum adds up to +0.25\n")
        f.write("- **Volatility**: High vol reduces by -0.25, low vol adds +0.10\n")
        f.write("- **Range**: 1.0:1 (conservative) to 3.5:1 (aggressive)\n\n")
        f.write("---\n\n")
        f.write("## TOP 15 BUY RECOMMENDATIONS\n\n")
        
        # Sort by R:R descending
        buy_recs = [r for r in recommendations if r['signal'] == 'BUY']
        buy_recs.sort(key=lambda x: x['dynamic_rr'], reverse=True)
        
        for idx, rec in enumerate(buy_recs[:15], 1):
            f.write(f"### {idx}. {rec['symbol']} - Dynamic R:R {rec['dynamic_rr']:.2f}:1\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Price | Rs {rec['price']:.2f} |\n")
            f.write(f"| Trend | {rec['trend']:+.2f}% |\n")
            f.write(f"| Momentum | {rec['momentum']:+.2f}% |\n")
            f.write(f"| Volatility | {rec['volatility']:.1f}% |\n")
            f.write(f"| Score | {rec['score']:.2f}/5 |\n\n")
            
            f.write("| Level | Price |\n")
            f.write("|-------|-------|\n")
            if 'secondary_support' in rec:
                f.write(f"| 2nd Support | Rs {rec.get('secondary_support', '—')} |\n")
            if 'support' in rec:
                f.write(f"| Support | Rs {rec['support']:.2f} |\n")
            f.write(f"| Entry Low | Rs {rec['entry_low']:.2f} |\n")
            f.write(f"| Entry High | Rs {rec['entry_high']:.2f} |\n")
            f.write(f"| Stop | Rs {rec['stop']:.2f} |\n")
            f.write(f"| Target 1 | Rs {rec['target_1']:.2f} |\n")
            f.write(f"| Target 2 | Rs {rec['target_2']:.2f} |\n")
            if 'resistance' in rec:
                f.write(f"| Resistance | Rs {rec['resistance']:.2f} |\n")
            if 'secondary_resistance' in rec:
                f.write(f"| 2nd Resistance | Rs {rec.get('secondary_resistance', '—')} |\n")
            
            f.write(f"\n**Analysis**: Dynamic R:R {rec['dynamic_rr']:.2f}:1 | Risk: {rec['risk']} | Exit: {rec['exit_strategy']}\n\n")
    
    print(f"[SAVED] {md_file.name}")
    print()
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
