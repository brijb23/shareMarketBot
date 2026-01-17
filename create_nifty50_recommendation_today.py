"""
Generate NIFTY50 Recommendation - January 10, 2026
Using existing data with Phase 19.1 Output Robustness Enhancements
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from phase19_1_output_robustness_enhancer import OutputRobustnessEnhancer
import warnings
warnings.filterwarnings('ignore')


def main():
    print('='*80)
    print('NIFTY 50 INVESTMENT RECOMMENDATION - JANUARY 10, 2026')
    print('='*80)
    print()
    
    # Load existing data
    print('[LOADING] Reading NIFTY50 metrics data...')
    df = pd.read_csv('nifty50_analysis/NIFTY50_METRICS_20260110_131750.csv')
    print(f'[OK] Loaded {len(df)} stocks')
    print()
    
    # Initialize enhancer
    enhancer = OutputRobustnessEnhancer()
    recommendations = []
    
    print('[PROCESSING] Generating recommendations with Phase 19.1 enhancements...')
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
        
        # Calculate targets
        entry_price = current_price
        target_1 = entry_price * (1 + (volatility / 100 * 0.5))
        target_2 = entry_price * (1 + (volatility / 100 * 1.0))
        stop_loss = entry_price * (1 - (volatility / 100 * 0.3))
        
        # ATR proxy
        atr = (high_52w - low_52w) / 20
        
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
    print(f'[OK] Generated {len(recommendations)} enhanced recommendations')
    print()
    
    # Statistics
    buy_count = sum(1 for r in recommendations if r['signal'] == 'BUY')
    hold_count = sum(1 for r in recommendations if r['signal'] == 'HOLD')
    sell_count = sum(1 for r in recommendations if r['signal'] == 'SELL')
    
    avg_trend = np.mean([r['trend'] for r in recommendations])
    avg_momentum = np.mean([r['momentum'] for r in recommendations])
    sentiment = 'BULLISH' if avg_trend > 0 else 'BEARISH'
    
    print('='*80)
    print('SUMMARY')
    print('='*80)
    print(f'Total Stocks: {len(recommendations)}')
    print(f'BUY:  {buy_count:2d} ({buy_count/len(recommendations)*100:5.1f}%)')
    print(f'HOLD: {hold_count:2d} ({hold_count/len(recommendations)*100:5.1f}%)')
    print(f'SELL: {sell_count:2d} ({sell_count/len(recommendations)*100:5.1f}%)')
    print()
    print(f'Market Sentiment: {sentiment}')
    print(f'Average Trend (50-day):    {avg_trend:+6.2f}%')
    print(f'Average Momentum (10-day): {avg_momentum:+6.2f}%')
    print()
    
    # Save files
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON
    json_file = f'NIFTY50_RECOMMENDATION_{ts}.json'
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
            'risk_bucket': r['risk_metrics']['risk_bucket'],
            'reward_to_risk': r['risk_metrics']['reward_to_risk_ratio'],
            'exit_strategy': r['exit_handling']['strategy'],
            'data_confidence': r['data_confidence']['state'],
        })
    
    csv_df = pd.DataFrame(csv_data)
    csv_file = f'NIFTY50_RECOMMENDATION_{ts}.csv'
    csv_df.to_csv(csv_file, index=False)
    print(f'[SAVED] {csv_file}')
    
    # Markdown Report
    md_lines = [
        '# NIFTY 50 INVESTMENT RECOMMENDATION',
        '## January 10, 2026',
        '',
        f'**Analysis Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'**System**: Combined Analysis + Phase 19.1 Output Robustness',
        f'**Total Stocks Analyzed**: {len(recommendations)}',
        '',
        '---',
        '',
        '## EXECUTIVE SUMMARY',
        '',
        '### Recommendation Distribution',
        '',
        '| Signal | Count | Percentage |',
        '|--------|-------|-----------|',
        f'| BUY | {buy_count} | {buy_count/len(recommendations)*100:.1f}% |',
        f'| HOLD | {hold_count} | {hold_count/len(recommendations)*100:.1f}% |',
        f'| SELL | {sell_count} | {sell_count/len(recommendations)*100:.1f}% |',
        '',
        '### Market Analysis',
        '',
        f'- **Average Trend (50-day)**: {avg_trend:+.2f}%',
        f'- **Average Momentum (10-day)**: {avg_momentum:+.2f}%',
        f'- **Market Sentiment**: **{sentiment}**',
        '',
        '---',
        '',
        '## TOP 15 BUY RECOMMENDATIONS',
        '',
    ]
    
    buy_recs = sorted([r for r in recommendations if r['signal'] == 'BUY'],
                     key=lambda x: x['risk_metrics']['reward_to_risk_ratio'],
                     reverse=True)
    
    for i, rec in enumerate(buy_recs[:15], 1):
        md_lines.extend([
            f'### {i}. {rec["symbol"]}',
            '',
            f'- **Current Price**: Rs {rec["entry_price"]:.2f}',
            f'- **Target 1**: Rs {rec["target_1"]:.2f} | **Target 2**: Rs {rec["target_2"]:.2f}',
            f'- **Stop Loss**: Rs {rec["stop_loss"]:.2f}',
            f'- **Buy Zone**: Rs {rec["buy_zone"]["low"]:.2f} - Rs {rec["buy_zone"]["high"]:.2f}',
            f'- **Confidence**: {rec["confidence"]}',
            f'- **Trend**: {rec["trend"]:+.2f}% | **Momentum**: {rec["momentum"]:+.2f}%',
            f'- **Risk Bucket**: {rec["risk_metrics"]["risk_bucket"]} (R:R {rec["risk_metrics"]["reward_to_risk_ratio"]:.2f}:1)',
            f'- **Exit Strategy**: {rec["exit_handling"]["strategy"]}',
            '',
        ])
    
    md_lines.extend([
        '---',
        '',
        '## HOLD OPPORTUNITIES',
        '',
        f'**Total**: {hold_count} stocks - Monitor for better entry',
        '',
        '| # | Symbol | Price | Trend | Risk |',
        '|-|--------|-------|-------|------|',
    ])
    
    for i, rec in enumerate([r for r in recommendations if r['signal'] == 'HOLD'][:20], 1):
        md_lines.append(f'| {i} | {rec["symbol"]} | Rs {rec["current_price"]:.2f} | {rec["trend"]:+.2f}% | {rec["risk_metrics"]["risk_bucket"]} |')
    
    md_lines.extend([
        '',
        '---',
        '',
        '## PHASE 19.1 ENHANCEMENTS',
        '',
        '- **Volatility-Aware Zones**: Entry +/- (0.3 x ATR)',
        '- **Regime-Adaptive Exits**: TRAILING/FIXED/TIGHT guidance',
        '- **Risk Metrics**: LOW/MEDIUM/HIGH with reward-to-risk ratios',
        '- **Data Confidence**: FULL/PARTIAL transparency',
        '- **Backward Compatible**: No signal changes from original analysis',
        '',
        '---',
        '',
        '## DISCLAIMER',
        '',
        'This analysis is for informational purposes only. Past performance does not guarantee future results. Please consult a financial advisor before making investment decisions.',
        '',
    ])
    
    md_file = f'NIFTY50_RECOMMENDATION_{ts}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    print(f'[SAVED] {md_file}')
    
    print()
    print('='*80)
    print('STATUS: PRODUCTION READY')
    print('='*80)


if __name__ == '__main__':
    main()
