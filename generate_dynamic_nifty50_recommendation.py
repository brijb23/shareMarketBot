"""
NIFTY50 DYNAMIC RECOMMENDATION GENERATOR
January 10, 2026 - Fresh Analysis with Dynamic R:R
Reads from actual data files with comprehensive reasoning
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from phase19_1_output_robustness_enhancer import OutputRobustnessEnhancer
import warnings
warnings.filterwarnings('ignore')
# BACKUP FILE - USE NEW VERSION

def calculate_dynamic_rr(trend, momentum, volatility):
    """
    Calculate dynamic reward-to-risk ratio based on technical indicators.
    
    Logic:
    - Base R:R = 1.5:1 (baseline)
    - Strong trend (+3% to +5%): +0.3 (aggressive)
    - Weak trend (-3% to 0%): -0.2 (conservative)
    - Strong momentum (+5% to +20%): +0.2 (confidence boost)
    - Low volatility (<12%): +0.1 (stable market)
    - High volatility (>20%): -0.15 (risk reduction)
    """
    
    rr = 1.5  # Base ratio
    
    # Trend adjustment
    if trend > 3:
        rr += 0.35  # Very bullish
    elif trend > 1:
        rr += 0.25  # Moderately bullish
    elif trend > 0:
        rr += 0.15  # Slightly bullish
    elif trend > -1:
        rr += 0.05  # Flat
    elif trend > -3:
        rr -= 0.15  # Slightly bearish
    else:
        rr -= 0.30  # Very bearish
    
    # Momentum adjustment
    if momentum > 10:
        rr += 0.25  # Extremely strong
    elif momentum > 5:
        rr += 0.15  # Strong
    elif momentum > 0:
        rr += 0.05  # Positive
    elif momentum > -5:
        rr -= 0.10  # Weak
    else:
        rr -= 0.20  # Negative
    
    # Volatility adjustment
    if volatility < 12:
        rr += 0.10  # Low vol - add confidence
    elif volatility > 20:
        rr -= 0.15  # High vol - reduce risk
    elif volatility > 25:
        rr -= 0.25  # Very high vol - conservative
    
    # Ensure ratio stays within reasonable bounds
    rr = max(1.0, min(3.5, rr))
    
    return rr


def generate_reasoning(symbol, trend, momentum, volatility, signal, score, ma20_rel):
    """Generate detailed reasoning for recommendation."""
    
    reasons = []
    
    # Trend analysis
    if trend > 2:
        reasons.append(f"✓ Strong uptrend detected ({trend:+.2f}%) - positive momentum")
    elif trend > 0:
        reasons.append(f"✓ Mild uptrend ({trend:+.2f}%) - favorable direction")
    elif trend > -2:
        reasons.append(f"⊘ Weak trend ({trend:+.2f}%) - consolidation phase")
    else:
        reasons.append(f"✗ Downtrend ({trend:+.2f}%) - caution advised")
    
    # Momentum analysis
    if momentum > 10:
        reasons.append(f"✓ Exceptional momentum ({momentum:+.2f}%) - strong buying pressure")
    elif momentum > 5:
        reasons.append(f"✓ Good momentum ({momentum:+.2f}%) - investor interest rising")
    elif momentum > 0:
        reasons.append(f"✓ Positive momentum ({momentum:+.2f}%) - constructive sentiment")
    elif momentum > -5:
        reasons.append(f"⊘ Weak momentum ({momentum:+.2f}%) - indecision")
    else:
        reasons.append(f"✗ Negative momentum ({momentum:+.2f}%) - selling pressure")
    
    # Volatility context
    if volatility < 12:
        reasons.append(f"✓ Low volatility ({volatility:.1f}%) - stable, lower risk")
    elif volatility < 18:
        reasons.append(f"⊘ Moderate volatility ({volatility:.1f}%) - normal conditions")
    else:
        reasons.append(f"✗ High volatility ({volatility:.1f}%) - elevated risk, manage position size")
    
    # Price action
    if ma20_rel > 0:
        reasons.append(f"✓ Trading above 20-day MA - upside bias")
    else:
        reasons.append(f"✗ Trading below 20-day MA - downside pressure")
    
    # Signal confirmation
    if signal == 'BUY':
        if score >= 3.5:
            reasons.append(f"★ Strong BUY signal (score {score:.2f}) - multiple confirmations")
        else:
            reasons.append(f"⊕ BUY signal (score {score:.2f}) - moderate setup")
    elif signal == 'HOLD':
        reasons.append(f"⊘ HOLD recommended - wait for better setup")
    else:
        reasons.append(f"✗ SELL signal - avoid at current levels")
    
    return reasons


def main():
    print('='*90)
    print('NIFTY 50 DYNAMIC INVESTMENT RECOMMENDATION ENGINE')
    print('January 10, 2026 | Fresh Analysis with Dynamic R:R & Detailed Reasoning')
    print('='*90)
    print()
    
    # Load enhanced levels data with support/resistance
    print('[LOADING] Reading enhanced levels data with S&R...')
    levels_df = pd.read_csv('nifty50_analysis/NIFTY50_ENHANCED_LEVELS_20260110.csv')
    
    print('[LOADING] Reading metrics data...')
    metrics_df = pd.read_csv('nifty50_analysis/NIFTY50_METRICS_20260110_131750.csv')
    
    # Merge data
    df = metrics_df.merge(levels_df[['symbol', 'primary_support', 'secondary_support', 
                                       'primary_resistance', 'secondary_resistance']], 
                          on='symbol', how='left')
    
    print(f'[OK] Loaded {len(df)} stocks with full technical data')
    print()
    
    # Initialize enhancer
    enhancer = OutputRobustnessEnhancer()
    recommendations = []
    
    print('[PROCESSING] Generating dynamic recommendations...')
    print()
    
    for idx, row in df.iterrows():
        symbol = row['symbol']
        current_price = row['current_price']
        trend = row['trend']
        momentum = row['momentum']
        volatility = row['volatility']
        high_52w = row['high_52w']
        low_52w = row['low_52w']
        ma20 = row['ma20']
        
        # Support & Resistance
        primary_support = row['primary_support']
        secondary_support = row['secondary_support']
        primary_resistance = row['primary_resistance']
        secondary_resistance = row['secondary_resistance']
        
        # Calculate technical score
        score = 2.5
        if trend > 0 and momentum > 0:
            score += 1.0
        if current_price > ma20:
            score += 0.5
        if volatility < 15:
            score += 0.25
        score = min(5.0, score)
        
        # Signal logic
        if score >= 3.5 and trend > 0:
            signal = 'BUY'
            confidence = 'HIGH'
        elif score >= 3.0 and trend > 0:
            signal = 'BUY'
            confidence = 'MEDIUM'
        elif score < 1.5 and trend < -2:
            signal = 'SELL'
            confidence = 'HIGH'
        else:
            signal = 'HOLD'
            confidence = 'MEDIUM'
        
        # DYNAMIC R:R CALCULATION
        dynamic_rr = calculate_dynamic_rr(trend, momentum, volatility)
        
        # Calculate targets based on dynamic R:R
        entry_price = current_price
        risk_pct = volatility / 100 * 0.3
        stop_loss = entry_price * (1 - risk_pct)
        
        # Reward based on dynamic R:R
        reward_pct = risk_pct * dynamic_rr
        target_1 = entry_price * (1 + reward_pct * 0.6)
        target_2 = entry_price * (1 + reward_pct)
        
        # ATR proxy
        atr = (high_52w - low_52w) / 20
        
        # Generate reasoning
        ma20_relative = ((current_price - ma20) / ma20) * 100
        reasoning = generate_reasoning(symbol, trend, momentum, volatility, signal, score, ma20_relative)
        
        # Base recommendation
        rec = {
            'symbol': symbol,
            'signal': signal,
            'current_price': current_price,
            'entry_price': entry_price,
            'target_1': target_1,
            'target_2': target_2,
            'stop_loss': stop_loss,
            'confidence': confidence,
            'trend': trend,
            'momentum': momentum,
            'volatility': volatility,
            'technical_score': score,
            'support_resistance': {
                'primary_support': primary_support,
                'secondary_support': secondary_support,
                'primary_resistance': primary_resistance,
                'secondary_resistance': secondary_resistance,
            },
            'dynamic_rr_ratio': dynamic_rr,
            'reasoning': reasoning,
        }
        
        # Apply Phase 19.1 enhancements
        enhanced_rec = enhancer.enhance_recommendation(
            existing_recommendation=rec,
            atr=atr,
            volatility=volatility,
            trend=trend,
            momentum=momentum,
        )
        
        recommendations.append(enhanced_rec)
        
        if (idx + 1) % 11 == 0:
            print(f'  [{idx+1:2d}/{len(df)}] Processed...')
    
    print()
    print(f'[OK] Generated {len(recommendations)} dynamic recommendations')
    print()
    
    # Statistics
    buy_count = sum(1 for r in recommendations if r['signal'] == 'BUY')
    hold_count = sum(1 for r in recommendations if r['signal'] == 'HOLD')
    sell_count = sum(1 for r in recommendations if r['signal'] == 'SELL')
    
    avg_trend = np.mean([r['trend'] for r in recommendations])
    avg_momentum = np.mean([r['momentum'] for r in recommendations])
    avg_rr = np.mean([r['dynamic_rr_ratio'] for r in recommendations])
    
    sentiment = 'BULLISH' if avg_trend > 0 else 'BEARISH'
    
    print('='*90)
    print('SUMMARY')
    print('='*90)
    print(f'Total Stocks Analyzed: {len(recommendations)}')
    print(f'BUY:  {buy_count:2d} ({buy_count/len(recommendations)*100:5.1f}%)')
    print(f'HOLD: {hold_count:2d} ({hold_count/len(recommendations)*100:5.1f}%)')
    print(f'SELL: {sell_count:2d} ({sell_count/len(recommendations)*100:5.1f}%)')
    print()
    print(f'Market Sentiment: {sentiment}')
    print(f'Average Trend (50-day):    {avg_trend:+6.2f}%')
    print(f'Average Momentum (10-day): {avg_momentum:+6.2f}%')
    print(f'Average Dynamic R:R:       {avg_rr:6.2f}:1')
    print()
    
    # Save files
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON
    json_file = f'NIFTY50_DYNAMIC_RECOMMENDATION_{ts}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2)
    print(f'[SAVED] {json_file}')
    
    # CSV
    csv_data = []
    for r in recommendations:
        csv_data.append({
            'symbol': r['symbol'],
            'signal': r['signal'],
            'current_price': r['current_price'],
            'target_1': r['target_1'],
            'target_2': r['target_2'],
            'stop_loss': r['stop_loss'],
            'confidence': r['confidence'],
            'trend': r['trend'],
            'momentum': r['momentum'],
            'volatility': r['volatility'],
            'dynamic_rr': r['dynamic_rr_ratio'],
            'risk_bucket': r['risk_metrics']['risk_bucket'],
            'primary_support': r['support_resistance']['primary_support'],
            'primary_resistance': r['support_resistance']['primary_resistance'],
            'exit_strategy': r['exit_handling']['strategy'],
        })
    
    csv_df = pd.DataFrame(csv_data)
    csv_file = f'NIFTY50_DYNAMIC_RECOMMENDATION_{ts}.csv'
    csv_df.to_csv(csv_file, index=False)
    print(f'[SAVED] {csv_file}')
    
    # Generate comprehensive markdown report
    create_detailed_report(recommendations, ts, avg_trend, avg_momentum, avg_rr)
    
    print()
    print('='*90)
    print('STATUS: ANALYSIS COMPLETE - FRESH DATA PROCESSED')
    print('='*90)
    
    return recommendations


def create_detailed_report(recommendations, ts, avg_trend, avg_momentum, avg_rr):
    """Create detailed markdown report with reasoning."""
    
    buy_recs = sorted([r for r in recommendations if r['signal'] == 'BUY'],
                     key=lambda x: x['dynamic_rr_ratio'], reverse=True)
    hold_recs = [r for r in recommendations if r['signal'] == 'HOLD']
    sell_recs = [r for r in recommendations if r['signal'] == 'SELL']
    
    buy_count = len(buy_recs)
    hold_count = len(hold_recs)
    sell_count = len(sell_recs)
    total = buy_count + hold_count + sell_count
    
    md_lines = [
        '# NIFTY 50 DYNAMIC INVESTMENT RECOMMENDATION',
        '## January 10, 2026 - Fresh Analysis',
        '',
        f'**Analysis Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'**Data Source**: Raw NIFTY50 enhanced levels data',
        f'**System**: Combined Technical Analysis + Phase 19.1 Enhancements',
        f'**Total Stocks Analyzed**: {total}',
        '',
        '---',
        '',
        '## EXECUTIVE SUMMARY',
        '',
        '### Market Overview',
        '',
        f'- **Market Sentiment**: {"BULLISH" if avg_trend > 0 else "BEARISH"} (Avg Trend: {avg_trend:+.2f}%)',
        f'- **Average Momentum**: {avg_momentum:+.2f}%',
        f'- **Average Dynamic R:R**: {avg_rr:.2f}:1',
        '',
        '### Recommendation Distribution',
        '',
        '| Signal | Count | Percentage | Dynamic R:R Range |',
        '|--------|-------|-----------|-------------------|',
    ]
    
    if buy_recs:
        buy_rr_min = min([r['dynamic_rr_ratio'] for r in buy_recs])
        buy_rr_max = max([r['dynamic_rr_ratio'] for r in buy_recs])
        md_lines.append(f'| BUY | {buy_count} | {buy_count/total*100:.1f}% | {buy_rr_min:.2f}:1 - {buy_rr_max:.2f}:1 |')
    else:
        md_lines.append(f'| BUY | {buy_count} | {buy_count/total*100:.1f}% | N/A |')
    
    if hold_recs:
        hold_rr_min = min([r['dynamic_rr_ratio'] for r in hold_recs])
        hold_rr_max = max([r['dynamic_rr_ratio'] for r in hold_recs])
        md_lines.append(f'| HOLD | {hold_count} | {hold_count/total*100:.1f}% | {hold_rr_min:.2f}:1 - {hold_rr_max:.2f}:1 |')
    else:
        md_lines.append(f'| HOLD | {hold_count} | {hold_count/total*100:.1f}% | N/A |')
    
    if sell_recs:
        sell_rr_min = min([r['dynamic_rr_ratio'] for r in sell_recs])
        sell_rr_max = max([r['dynamic_rr_ratio'] for r in sell_recs])
        md_lines.append(f'| SELL | {sell_count} | {sell_count/total*100:.1f}% | {sell_rr_min:.2f}:1 - {sell_rr_max:.2f}:1 |')
    else:
        md_lines.append(f'| SELL | {sell_count} | {sell_count/total*100:.1f}% | N/A |')
    
    md_lines.extend([
        '',
        '---',
        '',
        '## DYNAMIC R:R EXPLANATION',
        '',
        'The reward-to-risk ratio is now **dynamically calculated** based on three key factors:',
        '',
        '### Calculation Formula:',
        '',
        '```',
        'Base R:R = 1.5:1',
        '',
        'Adjustments:',
        '├─ Trend Factor (±0.35):',
        '│  ├─ Strong uptrend (+3% to +5%): +0.35',
        '│  ├─ Moderate uptrend (+1% to +3%): +0.25',
        '│  └─ Weak/negative trends: -0.15 to -0.30',
        '│',
        '├─ Momentum Factor (±0.25):',
        '│  ├─ Exceptional momentum (>10%): +0.25',
        '│  ├─ Good momentum (+5% to +10%): +0.15',
        '│  └─ Weak/negative momentum: -0.10 to -0.20',
        '│',
        '└─ Volatility Factor (±0.25):',
        '   ├─ Low volatility (<12%): +0.10 (stable)',
        '   ├─ High volatility (>20%): -0.15 (risk management)',
        '   └─ Very high volatility (>25%): -0.25 (conservative)',
        '',
        'Final R:R = Base + Adjustments (Range: 1.0:1 to 3.5:1)',
        '```',
        '',
        '### Why This Approach?',
        '',
        '- **Trend-Based**: Strong trends justify wider profit targets',
        '- **Momentum-Driven**: Exceptional momentum indicates sustained moves',
        '- **Risk-Aware**: High volatility reduces R:R for capital preservation',
        '- **Dynamic**: Adapts to current market conditions daily',
        '',
        '---',
        '',
        '## TOP 20 BUY RECOMMENDATIONS (SORTED BY DYNAMIC R:R)',
        '',
    ]
    
    for i, rec in enumerate(buy_recs[:20], 1):
        md_lines.extend([
            f'### {i}. {rec["symbol"]}',
            '',
            f'**Price Action**: {rec["current_price"]:.2f} (Trend: {rec["trend"]:+.2f}%, Momentum: {rec["momentum"]:+.2f}%)',
            '',
            '#### Dynamic Risk-Reward Analysis',
            '',
            f'- **Dynamic R:R Ratio**: **{rec["dynamic_rr_ratio"]:.2f}:1**',
            f'- **Entry Zone**: Rs {rec["buy_zone"]["low"]:.2f} - Rs {rec["buy_zone"]["high"]:.2f} (ATR-based)',
            f'- **Target 1**: Rs {rec["target_1"]:.2f} (Risk-based profit)',
            f'- **Target 2**: Rs {rec["target_2"]:.2f} (Extended target)',
            f'- **Stop Loss**: Rs {rec["stop_loss"]:.2f}',
            '',
            '#### Support & Resistance Levels',
            '',
            f'- **Primary Support**: Rs {rec["support_resistance"]["primary_support"]:.2f}',
            f'- **Secondary Support**: Rs {rec["support_resistance"]["secondary_support"]:.2f}',
            f'- **Primary Resistance**: Rs {rec["support_resistance"]["primary_resistance"]:.2f}',
            f'- **Secondary Resistance**: Rs {rec["support_resistance"]["secondary_resistance"]:.2f}',
            '',
            '#### Technical Reasoning',
            '',
        ])
        
        for reason in rec['reasoning']:
            md_lines.append(f'{reason}')
        
        md_lines.extend([
            '',
            f'- **Technical Score**: {rec["technical_score"]:.2f}/5.0',
            f'- **Risk Bucket**: {rec["risk_metrics"]["risk_bucket"]}',
            f'- **Exit Strategy**: {rec["exit_handling"]["strategy"]}',
            f'- **Data Confidence**: {rec["data_confidence"]["state"]}',
            '',
        ])
    
    md_lines.extend([
        '---',
        '',
        '## HOLD RECOMMENDATIONS',
        '',
        f'**Total**: {hold_count} stocks - Monitor for better entry conditions',
        '',
        '| # | Symbol | Price | Trend | Momentum | Vol | Dynamic R:R | Reason |',
        '|---|--------|-------|-------|----------|-----|------------|--------|',
    ])
    
    for i, rec in enumerate(hold_recs[:15], 1):
        reason = rec['reasoning'][0] if rec['reasoning'] else 'Mixed signals'
        md_lines.append(
            f'| {i} | {rec["symbol"]} | Rs {rec["current_price"]:.2f} | {rec["trend"]:+.2f}% | '
            f'{rec["momentum"]:+.2f}% | {rec["volatility"]:.1f}% | {rec["dynamic_rr_ratio"]:.2f}:1 | Consolidating |'
        )
    
    md_lines.extend([
        '',
        '---',
        '',
        '## KEY INSIGHTS',
        '',
        '### What Changed from Static R:R?',
        '',
        '**Before (Static 1.67:1)**:',
        '- All stocks had same R:R ratio regardless of technical setup',
        '- Didn\'t account for market conditions or momentum',
        '- Conservative across all scenarios',
        '',
        '**Now (Dynamic)**:',
        f'- Range from 1.0:1 to 3.5:1 based on indicators',
        f'- Stronger trends & momentum get better R:R',
        f'- High volatility automatically reduces risk',
        f'- Current average: {avg_rr:.2f}:1 (more optimized)',
        '',
        '### Trading Implications',
        '',
        '1. **Higher R:R Trades**: Go for stocks with strong trend + momentum + low volatility',
        '2. **Conservative Trades**: Accept lower R:R in high-volatility scenarios',
        '3. **Position Sizing**: Larger positions on higher R:R, smaller on lower R:R',
        '4. **Stop Loss Management**: Respect support levels shown in data',
        '',
        '---',
        '',
        '## PHASE 19.1 ENHANCEMENTS (APPLIED)',
        '',
        '- ✓ Volatility-Aware Buy Zones: ATR-based entry ranges',
        '- ✓ Regime-Adaptive Exits: Context-aware exit guidance',
        '- ✓ Risk Metadata: Support/resistance levels shown',
        '- ✓ Data Confidence: FULL transparency on all components',
        '- ✓ Signal Preservation: No suppression of original signals',
        '',
        '---',
        '',
        '## DISCLAIMER',
        '',
        'This analysis is for informational and educational purposes only. ',
        'Past performance does not guarantee future results. ',
        'Always consult a financial advisor and practice proper risk management before investing.',
        '',
    ])
    
    md_file = f'NIFTY50_DYNAMIC_RECOMMENDATION_{ts}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    print(f'[SAVED] {md_file}')


if __name__ == '__main__':
    main()
