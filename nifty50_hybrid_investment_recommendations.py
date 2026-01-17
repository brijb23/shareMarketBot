"""
NIFTY 50 HYBRID INVESTMENT RECOMMENDATION SYSTEM
Technical + Fundamental + Complete Analysis
January 10, 2026

Combines ALL Parameters:
- Technical Indicators (Trend, Momentum, Support/Resistance)
- Fundamental Metrics (P/E, P/B, ROE, EPS, Debt, etc.)
- Valuation Metrics
- Growth Metrics
- Market Sentiment
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')


def get_fundamental_data(symbol):
    """Fetch fundamental data for stock."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        fundamentals = {
            'pe_ratio': info.get('trailingPE', None),
            'pb_ratio': info.get('priceToBook', None),
            'roe': info.get('returnOnEquity', None),
            'debt_to_equity': info.get('debtToEquity', None),
            'current_ratio': info.get('currentRatio', None),
            'eps': info.get('trailingEps', None),
            'dividend_yield': info.get('dividendYield', None),
            'revenue_growth': info.get('revenueGrowth', None),
            'profit_margin': info.get('profitMargins', None),
            'market_cap': info.get('marketCap', None),
            'beta': info.get('beta', None),
        }
        
        return fundamentals
    except Exception as e:
        return None


def calculate_technical_score(trend, momentum, price, ma20, ma50, volatility, rr_ratio):
    """Calculate technical analysis score (0-10)."""
    score = 0
    
    if trend > 2:
        score += 3
    elif trend > 0:
        score += 2
    elif trend > -1:
        score += 1
    
    if momentum > 5:
        score += 2
    elif momentum > 0:
        score += 1
    elif momentum > -5:
        score += 0.5
    
    if price > ma20 and price > ma50:
        score += 2
    elif price > ma20:
        score += 1
    
    if volatility > 25:
        score += 0.5
    elif volatility < 15:
        score += 1.5
    else:
        score += 1
    
    if rr_ratio > 3:
        score += 1.5
    elif rr_ratio > 2:
        score += 1
    elif rr_ratio > 1:
        score += 0.5
    
    return min(score, 10)


def calculate_fundamental_score(pe_ratio, pb_ratio, roe, debt_to_equity, 
                                 dividend_yield, revenue_growth, profit_margin, beta):
    """Calculate fundamental analysis score (0-10)."""
    score = 0
    max_score = 0
    
    if pe_ratio is not None and pe_ratio > 0:
        max_score += 2
        if pe_ratio < 15:
            score += 2
        elif pe_ratio < 20:
            score += 1.5
        elif pe_ratio < 25:
            score += 1
        elif pe_ratio < 30:
            score += 0.5
    
    if pb_ratio is not None and pb_ratio > 0:
        max_score += 1.5
        if pb_ratio < 1:
            score += 1.5
        elif pb_ratio < 1.5:
            score += 1
        elif pb_ratio < 2:
            score += 0.5
    
    if roe is not None:
        max_score += 2
        roe_pct = roe * 100 if roe < 1 else roe
        if roe_pct > 20:
            score += 2
        elif roe_pct > 15:
            score += 1.5
        elif roe_pct > 10:
            score += 1
        elif roe_pct > 5:
            score += 0.5
    
    if debt_to_equity is not None:
        max_score += 1.5
        if debt_to_equity < 0.5:
            score += 1.5
        elif debt_to_equity < 1:
            score += 1
        elif debt_to_equity < 1.5:
            score += 0.5
    
    if dividend_yield is not None:
        max_score += 1
        div_pct = dividend_yield * 100 if dividend_yield < 1 else dividend_yield
        if div_pct > 5:
            score += 1
        elif div_pct > 3:
            score += 0.7
        elif div_pct > 1:
            score += 0.4
    
    if revenue_growth is not None:
        max_score += 1.5
        rev_growth_pct = revenue_growth * 100 if revenue_growth < 1 else revenue_growth
        if rev_growth_pct > 20:
            score += 1.5
        elif rev_growth_pct > 10:
            score += 1
        elif rev_growth_pct > 5:
            score += 0.5
    
    if profit_margin is not None:
        max_score += 0.5
        margin_pct = profit_margin * 100 if profit_margin < 1 else profit_margin
        if margin_pct > 15:
            score += 0.5
        elif margin_pct > 10:
            score += 0.3
    
    if beta is not None:
        max_score += 0.5
        if beta < 1:
            score += 0.5
        elif beta > 1.5:
            score += 0
        else:
            score += 0.25
    
    if max_score > 0:
        normalized_score = (score / max_score) * 10
    else:
        normalized_score = 5
    
    return min(normalized_score, 10)


def calculate_valuation_score(pe_ratio, pb_ratio, dividend_yield):
    """Calculate valuation attractiveness (0-10)."""
    score = 0
    industry_avg_pe = 20
    
    if pe_ratio is not None and pe_ratio > 0:
        pe_discount = ((industry_avg_pe - pe_ratio) / industry_avg_pe) * 100
        if pe_discount > 30:
            score += 3
        elif pe_discount > 15:
            score += 2
        elif pe_discount > 0:
            score += 1
    
    if pb_ratio is not None and pb_ratio > 0:
        if pb_ratio < 1.2:
            score += 2
        elif pb_ratio < 1.8:
            score += 1
    
    if dividend_yield is not None:
        div_pct = dividend_yield * 100 if dividend_yield < 1 else dividend_yield
        if div_pct > 4:
            score += 2
        elif div_pct > 2:
            score += 1
    
    return min(score, 10)


def calculate_growth_score(revenue_growth, profit_margin=None):
    """Calculate growth potential score (0-10)."""
    score = 0
    
    if revenue_growth is not None:
        rev_growth_pct = revenue_growth * 100 if revenue_growth < 1 else revenue_growth
        if rev_growth_pct > 25:
            score += 4
        elif rev_growth_pct > 15:
            score += 3
        elif rev_growth_pct > 10:
            score += 2
        elif rev_growth_pct > 5:
            score += 1
    
    if profit_margin is not None:
        margin_pct = profit_margin * 100 if profit_margin < 1 else profit_margin
        if margin_pct > 15:
            score += 3
        elif margin_pct > 10:
            score += 2
        elif margin_pct > 5:
            score += 1
    
    return min(score, 10)


def calculate_safety_score(debt_to_equity, current_ratio, beta, volatility):
    """Calculate investment safety score (0-10)."""
    score = 0
    
    if debt_to_equity is not None:
        if debt_to_equity < 0.5:
            score += 3
        elif debt_to_equity < 1:
            score += 2
        elif debt_to_equity < 1.5:
            score += 1
    
    if current_ratio is not None:
        if current_ratio > 2:
            score += 2
        elif current_ratio > 1.5:
            score += 1.5
        elif current_ratio > 1:
            score += 1
    
    if beta is not None:
        if beta < 0.8:
            score += 2
        elif beta < 1.2:
            score += 1
    
    if volatility is not None:
        if volatility < 15:
            score += 1.5
        elif volatility < 20:
            score += 1
    
    return min(score, 10)


def generate_hybrid_recommendation():
    """Generate comprehensive hybrid investment recommendations."""
    
    metrics_file = Path('nifty50_analysis/NIFTY50_METRICS_20260110_131750.csv')
    
    if not metrics_file.exists():
        print("ERROR: Metrics file not found")
        return None
    
    df_metrics = pd.read_csv(metrics_file)
    
    print("\n" + "="*80)
    print("FETCHING FUNDAMENTAL DATA FOR ALL STOCKS")
    print("="*80 + "\n")
    
    recommendations = []
    
    for idx, row in df_metrics.iterrows():
        symbol = row['symbol']
        current_price = row['current_price']
        trend = row['trend']
        momentum = row['momentum']
        volatility = row['volatility']
        
        print("[{}/{}] Processing: {}...".format(idx+1, len(df_metrics), symbol), end=" ")
        
        fundamentals = get_fundamental_data(symbol)
        
        if fundamentals is None:
            print("SKIP (No data)")
            continue
        
        try:
            data = yf.download(symbol, period='2mo', progress=False)
            
            if len(data) < 20:
                print("SKIP (Insufficient data)")
                continue
            
            prices = data['Close'].values
            highs = data['High'].values
            lows = data['Low'].values
            
            ma20 = np.mean(prices[-20:])
            ma50 = np.mean(prices[-50:]) if len(prices) >= 50 else ma20
            primary_support = np.min(lows[-20:])
            primary_resistance = np.max(highs[-20:])
            
            buy_target = primary_resistance
            risk = current_price - primary_support
            reward = buy_target - current_price
            rr_ratio = reward / risk if risk > 0 else 0
            
            technical_score = calculate_technical_score(
                trend, momentum, current_price, ma20, ma50, volatility, rr_ratio
            )
            
            fundamental_score = calculate_fundamental_score(
                fundamentals['pe_ratio'],
                fundamentals['pb_ratio'],
                fundamentals['roe'],
                fundamentals['debt_to_equity'],
                fundamentals['dividend_yield'],
                fundamentals['revenue_growth'],
                fundamentals['profit_margin'],
                fundamentals['beta']
            )
            
            valuation_score = calculate_valuation_score(
                fundamentals['pe_ratio'],
                fundamentals['pb_ratio'],
                fundamentals['dividend_yield']
            )
            
            growth_score = calculate_growth_score(
                fundamentals['revenue_growth'],
                fundamentals['profit_margin']
            )
            
            safety_score = calculate_safety_score(
                fundamentals['debt_to_equity'],
                fundamentals['current_ratio'],
                fundamentals['beta'],
                volatility
            )
            
            hybrid_score = (
                (technical_score * 0.30) +
                (fundamental_score * 0.25) +
                (valuation_score * 0.20) +
                (growth_score * 0.15) +
                (safety_score * 0.10)
            )
            
            if hybrid_score >= 7.5:
                recommendation = "STRONG_BUY"
                confidence = "HIGH"
            elif hybrid_score >= 6.5:
                recommendation = "BUY"
                confidence = "MEDIUM"
            elif hybrid_score >= 5.5:
                recommendation = "HOLD"
                confidence = "MEDIUM"
            elif hybrid_score >= 4.5:
                recommendation = "WEAK_HOLD"
                confidence = "LOW"
            else:
                recommendation = "SELL"
                confidence = "MEDIUM"
            
            recommendations.append({
                'symbol': symbol,
                'current_price': float(current_price),
                'trend': float(trend),
                'momentum': float(momentum),
                'volatility': float(volatility),
                'technical_score': float(technical_score),
                'fundamental_score': float(fundamental_score),
                'valuation_score': float(valuation_score),
                'growth_score': float(growth_score),
                'safety_score': float(safety_score),
                'hybrid_score': float(hybrid_score),
                'recommendation': recommendation,
                'confidence': confidence,
                'pe_ratio': float(fundamentals['pe_ratio']) if fundamentals['pe_ratio'] else None,
                'pb_ratio': float(fundamentals['pb_ratio']) if fundamentals['pb_ratio'] else None,
                'roe': float(fundamentals['roe']) if fundamentals['roe'] else None,
                'debt_to_equity': float(fundamentals['debt_to_equity']) if fundamentals['debt_to_equity'] else None,
                'dividend_yield': float(fundamentals['dividend_yield']) if fundamentals['dividend_yield'] else None,
                'revenue_growth': float(fundamentals['revenue_growth']) if fundamentals['revenue_growth'] else None,
                'profit_margin': float(fundamentals['profit_margin']) if fundamentals['profit_margin'] else None,
                'beta': float(fundamentals['beta']) if fundamentals['beta'] else None,
                'rr_ratio': float(rr_ratio),
                'ma20': float(ma20),
                'ma50': float(ma50),
                'support': float(primary_support),
                'resistance': float(primary_resistance),
            })
            
            print("OK (Score: {:.2f})".format(hybrid_score))
            
        except Exception as e:
            print("ERROR")
            continue
    
    if not recommendations:
        print("\nERROR: No recommendations generated")
        return None
    
    return pd.DataFrame(recommendations)


# Main execution
if __name__ == '__main__':
    print("="*80)
    print("NIFTY 50 HYBRID INVESTMENT RECOMMENDATION SYSTEM")
    print("Technical + Fundamental + All Parameters Combined")
    print("="*80 + "\n")
    
    rec_df = generate_hybrid_recommendation()
    
    if rec_df is not None and len(rec_df) > 0:
        
        # Save CSV
        csv_file = Path('nifty50_analysis/NIFTY50_HYBRID_ANALYSIS_20260110.csv')
        rec_df.to_csv(csv_file, index=False)
        print("\n[OK] Hybrid analysis CSV saved")
        
        # Save JSON
        json_file = Path('nifty50_analysis/NIFTY50_HYBRID_DATA_20260110.json')
        rec_df.to_json(json_file, orient='records', indent=2)
        print("[OK] Hybrid analysis JSON saved")
        
        # Print summary
        print("\n" + "="*80)
        print("HYBRID ANALYSIS SUMMARY")
        print("="*80)
        
        strong_buy = len(rec_df[rec_df['hybrid_score'] >= 7.5])
        buy = len(rec_df[(rec_df['hybrid_score'] >= 6.5) & (rec_df['hybrid_score'] < 7.5)])
        hold = len(rec_df[(rec_df['hybrid_score'] >= 5.5) & (rec_df['hybrid_score'] < 6.5)])
        weak_hold = len(rec_df[(rec_df['hybrid_score'] >= 4.5) & (rec_df['hybrid_score'] < 5.5)])
        sell = len(rec_df[rec_df['hybrid_score'] < 4.5])
        
        print("\nStocks by Recommendation:")
        print("  STRONG BUY: {} stocks (Score >= 7.5)".format(strong_buy))
        print("  BUY:        {} stocks (Score 6.5-7.5)".format(buy))
        print("  HOLD:       {} stocks (Score 5.5-6.5)".format(hold))
        print("  WEAK HOLD:  {} stocks (Score 4.5-5.5)".format(weak_hold))
        print("  SELL:       {} stocks (Score < 4.5)".format(sell))
        
        print("\nScores Summary:")
        print("  Average Hybrid Score:  {:.2f}/10".format(rec_df['hybrid_score'].mean()))
        print("  Median Hybrid Score:   {:.2f}/10".format(rec_df['hybrid_score'].median()))
        print("  Highest Hybrid Score:  {:.2f}/10".format(rec_df['hybrid_score'].max()))
        print("  Lowest Hybrid Score:   {:.2f}/10".format(rec_df['hybrid_score'].min()))
        
        print("\nTop 5 Recommendations (Highest Scores):")
        top_5 = rec_df.nlargest(5, 'hybrid_score')
        for rank, (idx, stock) in enumerate(top_5.iterrows(), 1):
            print("\n  Rank {}: {}".format(rank, stock['symbol']))
            print("    Hybrid Score: {:.2f}/10 ({})".format(stock['hybrid_score'], stock['recommendation']))
            print("    Components - Tech: {:.1f} | Fund: {:.1f} | Val: {:.1f} | Growth: {:.1f} | Safety: {:.1f}".format(
                stock['technical_score'], stock['fundamental_score'], stock['valuation_score'],
                stock['growth_score'], stock['safety_score']))
            print("    Price: Rs {:.2f} | Trend: {:+.1f}% | P/E: {} | ROE: {}%".format(
                stock['current_price'], stock['trend'],
                "{:.1f}".format(stock['pe_ratio']) if stock['pe_ratio'] is not None else "N/A",
                "{:.1f}".format(stock['roe']*100) if stock['roe'] is not None else "N/A"
            ))
        
        print("\n" + "="*80)
        print("HYBRID INVESTMENT SYSTEM COMPLETE")
        print("="*80)
        print("\nAll files saved to: nifty50_analysis/")
        print("\nFiles Generated:")
        print("1. NIFTY50_HYBRID_ANALYSIS_20260110.csv (Sortable Data)")
        print("2. NIFTY50_HYBRID_DATA_20260110.json (Full Data)")
        print("\nIncludes:")
        print("[OK] Technical Analysis (30% weight)")
        print("[OK] Fundamental Analysis (25% weight)")
        print("[OK] Valuation Analysis (20% weight)")
        print("[OK] Growth Analysis (15% weight)")
        print("[OK] Safety Analysis (10% weight)")
        print("\nWeighting explains recommendations:")
        print("- STRONG_BUY (7.5+): All components aligned")
        print("- BUY (6.5-7.5): Mostly positive signals")
        print("- HOLD (5.5-6.5): Mixed signals")
        print("- WEAK_HOLD (4.5-5.5): Mostly negative")
        print("- SELL (<4.5): Significantly negative")
