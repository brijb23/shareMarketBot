"""
NIFTY 50 INVESTMENT RECOMMENDATION - JANUARY 10, 2026
Using Existing Data + Phase 19.1 Output Robustness Enhancements
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from phase19_1_output_robustness_enhancer import OutputRobustnessEnhancer
import warnings
warnings.filterwarnings('ignore')


def load_existing_data():
    """Load existing metrics CSV."""
    try:
        df = pd.read_csv('nifty50_analysis/NIFTY50_METRICS_20260110_131750.csv')
        return df
    except:
        return None


def generate_recommendation_from_csv():
    """Generate enhanced recommendations from existing data."""
    
    print('='*80)
    print('NIFTY 50 COMPREHENSIVE INVESTMENT RECOMMENDATION')
    print('January 10, 2026 - Using Existing Data + Phase 19.1 Enhancements')
    print('='*80)
    print()
    
    # Load data
    df = load_existing_data()
    if df is None or len(df) == 0:
        print('[ERROR] Could not load data')
        return []
    
    print(f'[OK] Loaded {len(df)} stocks from CSV')
    print()
    
    recommendations = []
    enhancer = OutputRobustnessEnhancer()
    
    for idx, row in df.iterrows():
        try:
            symbol = row['symbol']
            current_price = row['current_price']
            trend = row['trend']
            momentum = row['momentum']
            volatility = row['volatility']
            high_52w = row['high_52w']
            low_52w = row['low_52w']
            ma20 = row['ma20']
            
            # Calculate technical score
            score = 2.5  # Base
            if trend > 0 and momentum > 0:
                score += 1.0
            if current_price > ma20:
                score += 0.5
            if volatility < 15:
                score += 0.25
            score = min(5.0, score)
            
            # Recommendation logic
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
            
            # Targets
            entry_price = current_price
            target_1 = entry_price * (1 + (volatility / 100 * 0.5))
            target_2 = entry_price * (1 + (volatility / 100 * 1.0))
            stop_loss = entry_price * (1 - (volatility / 100 * 0.3))
            
            # ATR proxy
            atr = (high_52w - low_52w) / 20
            
            # Original recommendation
            original_rec = {
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
                existing_recommendation=original_rec,
                atr=atr,
                volatility=volatility,
                trend=trend,
                momentum=momentum,
            )
            
            recommendations.append(enhanced_rec)
            
            if (idx + 1) % 15 == 0:
                print(f'[{idx+1:2d}/{len(df)}] Enhanced recommendations generated...')
        
        except Exception as e:
            print(f'[ERROR] {row["symbol"]}: {str(e)[:50]}')
            continue
    
    print()
    print(f'OK - Analysis complete: {len(recommendations)} stocks processed')
    print()
    
    return recommendations


def create_report(recommendations):
    """Create comprehensive report."""
    
    # Statistics
    buy = sum(1 for r in recommendations if r['signal'] == 'BUY')
    hold = sum(1 for r in recommendations if r['signal'] == 'HOLD')
    sell = sum(1 for r in recommendations if r['signal'] == 'SELL')
    
    avg_trend = np.mean([r['trend'] for r in recommendations])
    avg_momentum = np.mean([r['momentum'] for r in recommendations])
    avg_vol = np.mean([r['volatility'] for r in recommendations])
    
    lines = []
    lines.append('# NIFTY 50 COMPREHENSIVE INVESTMENT RECOMMENDATION')
    lines.append('## January 10, 2026')
    lines.append('')
    lines.append('**System**: Combined Analysis + Phase 19.1 Output Robustness')
    lines.append(f'**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append(f'**Total Stocks**: {len(recommendations)}')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## EXECUTIVE SUMMARY')
    lines.append('')
    lines.append('### Recommendation Distribution')
    lines.append('')
    lines.append('| Signal | Count | Percentage |')
    lines.append('|--------|-------|-----------|')
    lines.append(f'| BUY | {buy} | {buy/len(recommendations)*100:.1f}% |')
    lines.append(f'| HOLD | {hold} | {hold/len(recommendations)*100:.1f}% |')
    lines.append(f'| SELL | {sell} | {sell/len(recommendations)*100:.1f}% |')
    lines.append('')
    
    lines.append('### Market Analysis')
    lines.append('')
    lines.append(f'- Average Trend (50-day): {avg_trend:+.2f}%')
    lines.append(f'- Average Momentum (10-day): {avg_momentum:+.2f}%')
    lines.append(f'- Average Volatility: {avg_vol:.2f}%')
    sentiment = 'BULLISH' if avg_trend > 0 else 'BEARISH'
    lines.append(f'- Market Sentiment: **{sentiment}**')
    lines.append('')
    
    lines.append('### Phase 19.1 Enhancements Applied')
    lines.append('')
    lines.append('✓ Volatility-aware buy zones (ATR-based entry ranges)')
    lines.append('✓ Regime-adaptive exit annotations (contextual guidance)')
    lines.append('✓ Explicit risk metadata (LOW/MEDIUM/HIGH classification)')
    lines.append('✓ Data confidence transparency (component availability)')
    lines.append('✓ Complete trading plans (entry to exit guidance)')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## TOP 15 BUY RECOMMENDATIONS')
    lines.append('')
    
    buy_recs = sorted([r for r in recommendations if r['signal'] == 'BUY'],
                     key=lambda x: x['risk_metrics']['reward_to_risk_ratio'],
                     reverse=True)
    
    for i, rec in enumerate(buy_recs[:15], 1):
        lines.append(f'### {i}. {rec["symbol"]} - {rec["confidence"]} BUY')
        lines.append('')
        lines.append(f'**Current Price**: Rs {rec["entry_price"]}')
        lines.append(f'**Buy Zone**: Rs {rec["buy_zone"]["low"]} - Rs {rec["buy_zone"]["high"]}')
        lines.append(f'**Target 1**: Rs {rec["target_1"]} | **Target 2**: Rs {rec["target_2"]}')
        lines.append(f'**Stop Loss**: Rs {rec["stop_loss"]}')
        lines.append(f'**Risk Bucket**: {rec["risk_metrics"]["risk_bucket"]} (R:R {rec["risk_metrics"]["reward_to_risk_ratio"]:.2f}:1)')
        lines.append(f'**Trend**: {rec["trend"]:+.2f}% | **Momentum**: {rec["momentum"]:+.2f}%')
        lines.append(f'**Exit Strategy**: {rec["exit_handling"]["strategy"]}')
        lines.append(f'**Data Confidence**: {rec["data_confidence"]["state"]}')
        lines.append('')
    
    lines.append('---')
    lines.append('')
    lines.append('## HOLD OPPORTUNITIES')
    lines.append('')
    
    hold_recs = [r for r in recommendations if r['signal'] == 'HOLD']
    lines.append(f'**Total**: {len(hold_recs)} stocks - Monitor and wait for better entry')
    lines.append('')
    lines.append('| # | Symbol | Price | Trend | Risk Bucket |')
    lines.append('|-|--------|-------|-------|------------|')
    
    for i, rec in enumerate(hold_recs[:20], 1):
        lines.append(f'| {i} | {rec["symbol"]} | Rs {rec["entry_price"]} | {rec["trend"]:+.2f}% | {rec["risk_metrics"]["risk_bucket"]} |')
    
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## SELL/AVOID STOCKS')
    lines.append('')
    
    sell_recs = [r for r in recommendations if r['signal'] == 'SELL']
    lines.append(f'**Total**: {len(sell_recs)} stocks - Avoid or exit')
    lines.append('')
    
    for rec in sell_recs:
        lines.append(f'- **{rec["symbol"]}**: Rs {rec["entry_price"]} (Trend {rec["trend"]:+.2f}%, Momentum {rec["momentum"]:+.2f}%)')
    
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('## KEY INSIGHTS')
    lines.append('')
    lines.append('### What\'s New in Phase 19.1')
    lines.append('- Volatility-aware zones for realistic fills')
    lines.append('- Regime-adaptive exit guidance')
    lines.append('- Explicit risk transparency with no suppression')
    lines.append('- Data confidence state transparency')
    lines.append('- Full backward compatibility')
    lines.append('')
    
    lines.append('### Trading Guidance')
    lines.append('1. Use buy zones instead of single entry prices')
    lines.append('2. Follow exit strategy hints (TRAILING vs FIXED)')
    lines.append('3. Size positions based on risk bucket')
    lines.append('4. Verify data confidence before trading')
    lines.append('5. Maintain stop losses regardless of signals')
    lines.append('')
    
    lines.append('---')
    lines.append('')
    lines.append('## METHODOLOGY')
    lines.append('')
    lines.append('### Technical Indicators')
    lines.append('- Trend: 50-day percentage change')
    lines.append('- Momentum: 10-day acceleration')
    lines.append('- Volatility: Standard deviation of returns')
    lines.append('- Support/Resistance: 52-week highs/lows')
    lines.append('- ATR: Average True Range for zone sizing')
    lines.append('')
    
    lines.append('### Phase 19.1 Enhancements')
    lines.append('1. Volatility-Aware Zones: Entry +/- (0.3 x ATR)')
    lines.append('2. Regime Classification: TRAILING/FIXED exit hints')
    lines.append('3. Risk Metrics: Reward-to-risk buckets and ratios')
    lines.append('4. Data Confidence: FULL/PARTIAL/MULTI_PARTIAL states')
    lines.append('5. Output Structure: Backward-compatible JSON format')
    lines.append('')
    
    lines.append('---')
    lines.append('')
    lines.append('## IMPORTANT DISCLAIMERS')
    lines.append('')
    lines.append('- Analysis based on historical data and technical indicators')
    lines.append('- Past performance does NOT guarantee future results')
    lines.append('- Recommendations are informational only')
    lines.append('- Always use proper risk management and stop losses')
    lines.append('- Consult financial advisors before investing')
    lines.append('- Markets are unpredictable - do your own research')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append(f'**Report Status**: PRODUCTION READY')
    lines.append(f'**System**: NIFTY 50 Comprehensive Analysis v19.1')
    lines.append('')
    
    return '\n'.join(lines)


if __name__ == '__main__':
    # Generate recommendations
    recommendations = generate_recommendation_from_csv()
    
    if not recommendations:
        print('[ERROR] Failed to generate recommendations')
        exit(1)
    
    # Create report
    report = create_report(recommendations)
    
    # Save outputs
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Markdown report
    report_file = f'NIFTY50_RECOMMENDATION_{ts}.md'
    Path(report_file).write_text(report, encoding='utf-8')
    print(f'Saved: {report_file}')
    
    # JSON
    json_file = f'NIFTY50_RECOMMENDATION_{ts}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2)
    print(f'Saved: {json_file}')
    
    # CSV
    csv_data = []
    for r in recommendations:
        csv_data.append({
            'symbol': r['symbol'],
            'signal': r['signal'],
            'price': r['entry_price'],
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
    print(f'Saved: {csv_file}')
    
    # Summary
    print()
    print('='*80)
    print('RECOMMENDATION SUMMARY')
    print('='*80)
    buy = sum(1 for r in recommendations if r['signal'] == 'BUY')
    hold = sum(1 for r in recommendations if r['signal'] == 'HOLD')
    sell = sum(1 for r in recommendations if r['signal'] == 'SELL')
    
    print(f'Total Stocks Analyzed: {len(recommendations)}')
    print(f'BUY:  {buy:2d} ({buy/len(recommendations)*100:5.1f}%)')
    print(f'HOLD: {hold:2d} ({hold/len(recommendations)*100:5.1f}%)')
    print(f'SELL: {sell:2d} ({sell/len(recommendations)*100:5.1f}%)')
    print()
    
    avg_trend = np.mean([r['trend'] for r in recommendations])
    avg_momentum = np.mean([r['momentum'] for r in recommendations])
    sentiment = 'BULLISH' if avg_trend > 0 else 'BEARISH'
    
    print(f'Market Sentiment: {sentiment}')
    print(f'Avg Trend: {avg_trend:+.2f}%')
    print(f'Avg Momentum: {avg_momentum:+.2f}%')
    print()
    print('Files Generated:')
    print(f'  1. {report_file}')
    print(f'  2. {json_file}')
    print(f'  3. {csv_file}')
    print()
    print('='*80)
    print('STATUS: PRODUCTION READY')
    print('='*80)
