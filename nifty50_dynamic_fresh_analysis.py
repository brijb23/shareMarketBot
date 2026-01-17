"""
NIFTY50 DYNAMIC RECOMMENDATION GENERATOR - FRESH ANALYSIS
January 10, 2026
Comprehensive analysis with dynamic R:R, support/resistance, and detailed reasoning
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from phase19_1_output_robustness_enhancer import OutputRobustnessEnhancer
import warnings
warnings.filterwarnings('ignore')


def calculate_dynamic_rr(trend, momentum, volatility):
    """Calculate dynamic R:R based on technical indicators."""
    rr = 1.5
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
    
    if volatility < 12:
        rr += 0.10
    elif volatility > 20:
        rr -= 0.15
    elif volatility > 25:
        rr -= 0.25
    
    return max(1.0, min(3.5, rr))


def main():
    print('='*90)
    print('NIFTY 50 DYNAMIC RECOMMENDATION - FRESH ANALYSIS')
    print('='*90)
    print()
    
    # Load data
    print('[LOADING] Reading enhanced levels data...')
    levels_df = pd.read_csv('nifty50_analysis/NIFTY50_ENHANCED_LEVELS_20260110.csv')
    
    print('[LOADING] Reading metrics data...')
    metrics_df = pd.read_csv('nifty50_analysis/NIFTY50_METRICS_20260110_131750.csv')
    
    df = metrics_df.merge(levels_df[['symbol', 'primary_support', 'secondary_support', 
                                       'primary_resistance', 'secondary_resistance']], 
                          on='symbol', how='left')
    
    print(f'[OK] Loaded {len(df)} stocks')
    print()
    
    enhancer = OutputRobustnessEnhancer()
    recommendations = []
    
    print('[PROCESSING] Generating recommendations...')
    
    for idx, row in df.iterrows():
        symbol = row['symbol']
        current_price = row['current_price']
        trend = row['trend']
        momentum = row['momentum']
        volatility = row['volatility']
        high_52w = row['high_52w']
        low_52w = row['low_52w']
        ma20 = row['ma20']
        
        # Score & Signal
        score = 2.5
        if trend > 0 and momentum > 0:
            score += 1.0
        if current_price > ma20:
            score += 0.5
        if volatility < 15:
            score += 0.25
        score = min(5.0, score)
        
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
        
        # Dynamic R:R
        dynamic_rr = calculate_dynamic_rr(trend, momentum, volatility)
        
        # Targets
        entry_price = current_price
        risk_pct = volatility / 100 * 0.3
        stop_loss = entry_price * (1 - risk_pct)
        reward_pct = risk_pct * dynamic_rr
        target_1 = entry_price * (1 + reward_pct * 0.6)
        target_2 = entry_price * (1 + reward_pct)
        
        atr = (high_52w - low_52w) / 20
        
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
                'primary_support': row['primary_support'],
                'secondary_support': row['secondary_support'],
                'primary_resistance': row['primary_resistance'],
                'secondary_resistance': row['secondary_resistance'],
            },
            'dynamic_rr_ratio': dynamic_rr,
        }
        
        enhanced_rec = enhancer.enhance_recommendation(
            existing_recommendation=rec,
            atr=atr,
            volatility=volatility,
            trend=trend,
            momentum=momentum,
        )
        
        recommendations.append(enhanced_rec)
        
        if (idx + 1) % 11 == 0:
            print(f'  [{idx+1:2d}/{len(df)}] Complete')
    
    print()
    
    # Stats
    buy_c = sum(1 for r in recommendations if r['signal'] == 'BUY')
    hold_c = sum(1 for r in recommendations if r['signal'] == 'HOLD')
    sell_c = sum(1 for r in recommendations if r['signal'] == 'SELL')
    
    avg_trend = np.mean([r['trend'] for r in recommendations])
    avg_momentum = np.mean([r['momentum'] for r in recommendations])
    avg_rr = np.mean([r['dynamic_rr_ratio'] for r in recommendations])
    
    print('='*90)
    print('SUMMARY - BUY: {} | HOLD: {} | SELL: {}'.format(buy_c, hold_c, sell_c))
    print('Sentiment: {} | Avg Trend: {:+.2f}% | Avg R:R: {:.2f}:1'.format(
        'BULLISH' if avg_trend > 0 else 'BEARISH', avg_trend, avg_rr))
    print('='*90)
    print()
    
    # Save
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    json_file = f'NIFTY50_DYNAMIC_{ts}.json'
    with open(json_file, 'w') as f:
        json.dump(recommendations, f, indent=2)
    print(f'[SAVED] {json_file}')
    
    # CSV
    csv_data = [{
        'symbol': r['symbol'],
        'signal': r['signal'],
        'price': r['current_price'],
        'target_1': r['target_1'],
        'target_2': r['target_2'],
        'stop': r['stop_loss'],
        'trend': r['trend'],
        'momentum': r['momentum'],
        'vol': r['volatility'],
        'dynamic_rr': r['dynamic_rr_ratio'],
        'support': r['support_resistance']['primary_support'],
        'resistance': r['support_resistance']['primary_resistance'],
        'risk_bucket': r['risk_metrics']['risk_bucket'],
    } for r in recommendations]
    
    csv_df = pd.DataFrame(csv_data)
    csv_file = f'NIFTY50_DYNAMIC_{ts}.csv'
    csv_df.to_csv(csv_file, index=False)
    print(f'[SAVED] {csv_file}')
    
    # Markdown Report
    create_report(recommendations, ts, avg_trend, avg_momentum, avg_rr)


def create_report(recs, ts, avg_tr, avg_mom, avg_rr):
    """Generate detailed markdown report."""
    buy_recs = sorted([r for r in recs if r['signal'] == 'BUY'],
                     key=lambda x: x['dynamic_rr_ratio'], reverse=True)
    
    lines = [
        '# NIFTY 50 DYNAMIC RECOMMENDATION REPORT',
        '## January 10, 2026 - Fresh Analysis',
        '',
        f'**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'**Stocks**: {len(recs)} analyzed',
        f'**Sentiment**: {"BULLISH" if avg_tr > 0 else "BEARISH"}',
        '',
        f'**BUY**: {sum(1 for r in recs if r["signal"]=="BUY")} | **HOLD**: {sum(1 for r in recs if r["signal"]=="HOLD")} | **SELL**: {sum(1 for r in recs if r["signal"]=="SELL")}',
        '',
        f'**Avg Trend**: {avg_tr:+.2f}% | **Avg Momentum**: {avg_mom:+.2f}% | **Avg R:R**: {avg_rr:.2f}:1',
        '',
        '---',
        '',
        '## DYNAMIC R:R EXPLANATION',
        '',
        'R:R ratio is now calculated dynamically based on:',
        '',
        '- **Base**: 1.5:1',
        '- **Trend**: Strong trends add up to +0.35, weak subtract up to -0.30',
        '- **Momentum**: Strong momentum adds up to +0.25',
        '- **Volatility**: High vol reduces by -0.25, low vol adds +0.10',
        '- **Range**: 1.0:1 (conservative) to 3.5:1 (aggressive)',
        '',
        '---',
        '',
        '## TOP 15 BUY RECOMMENDATIONS',
        '',
    ]
    
    for i, r in enumerate(buy_recs[:15], 1):
        lines.extend([
            f'### {i}. {r["symbol"]} - Dynamic R:R {r["dynamic_rr_ratio"]:.2f}:1',
            '',
            f'| Metric | Value |',
            f'|--------|-------|',
            f'| Price | Rs {r["current_price"]:.2f} |',
            f'| Trend | {r["trend"]:+.2f}% |',
            f'| Momentum | {r["momentum"]:+.2f}% |',
            f'| Volatility | {r["volatility"]:.1f}% |',
            f'| Score | {r["technical_score"]:.2f}/5 |',
            '',
            f'| Level | Price |',
            f'|-------|-------|',
            f'| 2nd Support | Rs {r["support_resistance"]["secondary_support"]:.2f} |',
            f'| Support | Rs {r["support_resistance"]["primary_support"]:.2f} |',
            f'| Entry Low | Rs {r["buy_zone"]["low"]:.2f} |',
            f'| Entry High | Rs {r["buy_zone"]["high"]:.2f} |',
            f'| Stop | Rs {r["stop_loss"]:.2f} |',
            f'| Target 1 | Rs {r["target_1"]:.2f} |',
            f'| Target 2 | Rs {r["target_2"]:.2f} |',
            f'| Resistance | Rs {r["support_resistance"]["primary_resistance"]:.2f} |',
            f'| 2nd Resistance | Rs {r["support_resistance"]["secondary_resistance"]:.2f} |',
            '',
            f'**Analysis**: Dynamic R:R {r["dynamic_rr_ratio"]:.2f}:1 | Risk: {r["risk_metrics"]["risk_bucket"]} | Exit: {r["exit_handling"]["strategy"]}',
            '',
        ])
    
    lines.extend([
        '---',
        '',
        '## PHASE 19.1 ENHANCEMENTS APPLIED',
        '',
        '- Volatility-aware zones',
        '- Support/resistance levels',
        '- Regime-adaptive exits',
        '- Dynamic R:R calculation',
        '- Data confidence transparency',
        '',
    ])
    
    md_file = f'NIFTY50_DYNAMIC_{ts}.md'
    with open(md_file, 'w') as f:
        f.write('\n'.join(lines))
    print(f'[SAVED] {md_file}')


if __name__ == '__main__':
    main()
