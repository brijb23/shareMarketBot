"""
NIFTY50 AUTOMATED WEEKLY RECOMMENDATION GENERATOR V2
Complete automation with fixed data duplication issues

Usage:
    python nifty50_automated_weekly_generator_v2.py
"""

import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from pathlib import Path
import sys
import traceback
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress FutureWarnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)


# NIFTY 50 constituents
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


class NiftyAutomatedGeneratorV2:
    """Fully automated NIFTY50 recommendation generator with fixed deduplication."""
    
    def __init__(self):
        self.analysis_dir = Path('nifty50_analysis')
        self.analysis_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stocks_data = {}
        self.recommendations = []
        
    def log(self, message, level="INFO"):
        """Print formatted log messages."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def download_stock_data(self):
        """Download fresh data for all NIFTY50 stocks in parallel."""
        self.log("=" * 80)
        self.log("DOWNLOADING NIFTY50 STOCK DATA")
        self.log("=" * 80)
        
        downloaded = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_symbol = {
                executor.submit(self._download_single_stock, symbol): symbol 
                for symbol in NIFTY50_STOCKS
            }
            
            for i, future in enumerate(as_completed(future_to_symbol), 1):
                symbol = future_to_symbol[future]
                try:
                    df = future.result()
                    if df is not None and not df.empty:
                        self.stocks_data[symbol] = df
                        downloaded += 1
                except Exception as e:
                    failed += 1
                    self.log(f"Failed to download {symbol}: {str(e)[:40]}", "WARN")
                
                if i % 10 == 0:
                    self.log(f"Progress: {i}/{len(NIFTY50_STOCKS)} stocks processed")
        
        self.log(f"Download Complete: {downloaded}/{len(NIFTY50_STOCKS)} successful")
        self.log("")
        
        if downloaded < 30:
            self.log("ERROR: Too many download failures. Aborting.", "ERROR")
            return False
        return True
    
    def _download_single_stock(self, symbol):
        """Download data for single stock."""
        try:
            df = yf.download(symbol, period='3mo', progress=False, 
                           auto_adjust=True)
            if df is None or len(df) < 20:
                return None
            
            # Handle MultiIndex columns from yfinance
            if isinstance(df.columns, pd.MultiIndex):
                # Flatten columns for single symbol download
                df.columns = df.columns.get_level_values(0)
            
            return df
        except Exception:
            return None
    
    def generate_recommendations(self):
        """Generate BUY/HOLD/SELL recommendations directly from downloaded data."""
        self.log("GENERATING RECOMMENDATIONS")
        self.log("-" * 80)
        
        self.recommendations = []
        
        for idx, symbol in enumerate(NIFTY50_STOCKS, 1):
            if symbol not in self.stocks_data:
                continue
            
            try:
                df = self.stocks_data[symbol]
                if df is None or len(df) < 20:
                    continue
                
                # Get current price
                close_values = df['Close'].values
                current_price = float(close_values[-1].item() if hasattr(close_values[-1], 'item') else close_values[-1])
                
                # Calculate 50-day moving average (Trend)
                ma50_values = close_values[-50:]
                ma50 = np.mean(ma50_values) if len(ma50_values) > 0 else current_price
                ma50 = float(ma50.item() if hasattr(ma50, 'item') else ma50)
                trend = ((current_price - ma50) / ma50 * 100) if ma50 > 0 else 0
                
                # Calculate 10-day momentum
                if len(close_values) > 10:
                    price_10_ago = float(close_values[-10].item() if hasattr(close_values[-10], 'item') else close_values[-10])
                else:
                    price_10_ago = current_price
                momentum = ((current_price - price_10_ago) / price_10_ago * 100) if price_10_ago > 0 else 0
                
                # Calculate 20-day volatility (annualized)
                returns = np.diff(close_values) / close_values[:-1]
                recent_returns = returns[-20:] if len(returns) >= 20 else returns
                volatility = float((np.std(recent_returns) * np.sqrt(252) * 100).item() if hasattr(np.std(recent_returns), 'item') else np.std(recent_returns) * np.sqrt(252) * 100)
                
                # Calculate ATR
                high_values = df['High'].values
                low_values = df['Low'].values
                tr = high_values - low_values
                atr_mean = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
                atr = float(atr_mean.item() if hasattr(atr_mean, 'item') else atr_mean)
                
                # Get support/resistance
                close_sorted = np.sort(close_values)
                support = float(close_sorted[len(close_sorted) // 4].item() if hasattr(close_sorted[len(close_sorted) // 4], 'item') else close_sorted[len(close_sorted) // 4])
                resistance = float(close_sorted[3 * len(close_sorted) // 4].item() if hasattr(close_sorted[3 * len(close_sorted) // 4], 'item') else close_sorted[3 * len(close_sorted) // 4])
                high_52w = float(np.max(high_values).item() if hasattr(np.max(high_values), 'item') else np.max(high_values))
                low_52w = float(np.min(low_values).item() if hasattr(np.min(low_values), 'item') else np.min(low_values))
                
                # Calculate dynamic R:R
                dynamic_rr = self.calculate_dynamic_rr(trend, momentum, volatility)
                
                # Calculate score
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
                
                # Generate signal
                if score >= 3.5 and (trend > -2 or momentum > 5):
                    signal = 'BUY'
                elif score < 2.5 or (trend < -3 and momentum < 0):
                    signal = 'SELL'
                else:
                    signal = 'HOLD'
                
                # Calculate stops and targets
                risk_distance = (volatility / 100) * current_price * 0.3
                stop = current_price - risk_distance
                target_1 = current_price + (risk_distance * 1.2)
                target_2 = current_price + (risk_distance * dynamic_rr)
                
                # Entry zones
                atr_pct = volatility / 100 * 0.3
                entry_low = current_price * (1 - atr_pct)
                entry_high = current_price * (1 + atr_pct)
                
                # Risk classification
                if volatility < 15 and trend > 2:
                    risk = 'LOW'
                elif volatility > 20 or trend < 2:
                    risk = 'HIGH'
                else:
                    risk = 'MEDIUM'
                
                # Exit strategy
                if momentum > 10 and trend > 2:
                    exit_strategy = 'TRAILING_EXIT_PREFERRED'
                elif volatility > 20:
                    exit_strategy = 'TIGHT_STOPS_RECOMMENDED'
                else:
                    exit_strategy = 'FIXED_EXIT_STANDARD'
                
                rec = {
                    'symbol': symbol,
                    'signal': signal,
                    'price': round(current_price, 2),
                    'trend': round(trend, 2),
                    'momentum': round(momentum, 2),
                    'volatility': round(volatility, 2),
                    'score': round(score, 2),
                    'dynamic_rr': round(dynamic_rr, 2),
                    'entry_low': round(entry_low, 2),
                    'entry_high': round(entry_high, 2),
                    'stop': round(stop, 2),
                    'target_1': round(target_1, 2),
                    'target_2': round(target_2, 2),
                    'risk': risk,
                    'exit_strategy': exit_strategy,
                    'support': round(support, 2),
                    'resistance': round(resistance, 2),
                }
                
                self.recommendations.append(rec)
            
            except Exception as e:
                self.log(f"Error generating recommendation for {symbol}: {str(e)[:40]}", "WARN")
                continue
            
            if idx % 10 == 0:
                self.log(f"  {idx}/{len(NIFTY50_STOCKS)} processed")
        
        self.log(f"Generated {len(self.recommendations)} recommendations")
        self.log("")
        return len(self.recommendations) > 0
    
    def calculate_dynamic_rr(self, trend, momentum, volatility):
        """Calculate dynamic R:R based on market conditions."""
        rr = 1.5
        
        # Trend adjustment
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
        
        # Momentum adjustment
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
        
        # Volatility adjustment
        if volatility < 12:
            rr += 0.10
        elif volatility <= 20:
            rr += 0.00
        elif volatility <= 25:
            rr -= 0.15
        else:
            rr -= 0.25
        
        return max(1.0, min(3.5, rr))
    
    def save_outputs(self):
        """Save recommendations to CSV, JSON, and Markdown."""
        self.log("SAVING OUTPUTS")
        self.log("-" * 80)
        
        if not self.recommendations:
            self.log("ERROR: No recommendations to save", "ERROR")
            return False
        
        try:
            # Count signals and calculate averages
            buy_count = sum(1 for r in self.recommendations if r['signal'] == 'BUY')
            hold_count = sum(1 for r in self.recommendations if r['signal'] == 'HOLD')
            sell_count = sum(1 for r in self.recommendations if r['signal'] == 'SELL')
            
            avg_trend = np.mean([r['trend'] for r in self.recommendations])
            avg_momentum = np.mean([r['momentum'] for r in self.recommendations])
            avg_rr = np.mean([r['dynamic_rr'] for r in self.recommendations])
            
            sentiment = 'BULLISH' if avg_trend > 0 else 'BEARISH'
            
            # Save CSV
            csv_file = self.analysis_dir / f'NIFTY50_DYNAMIC_{self.timestamp}.csv'
            df = pd.DataFrame(self.recommendations)
            df.to_csv(csv_file, index=False)
            self.log(f"[SAVED] {csv_file.name} ({len(self.recommendations)} stocks)")
            
            # Save JSON
            json_file = self.analysis_dir / f'NIFTY50_DYNAMIC_{self.timestamp}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'generated': datetime.now().isoformat(),
                    'summary': {
                        'stocks_analyzed': len(self.recommendations),
                        'buy': buy_count,
                        'hold': hold_count,
                        'sell': sell_count,
                        'sentiment': sentiment,
                        'avg_trend': round(avg_trend, 2),
                        'avg_momentum': round(avg_momentum, 2),
                        'avg_rr': round(avg_rr, 2),
                    },
                    'recommendations': self.recommendations
                }, f, indent=2)
            self.log(f"[SAVED] {json_file.name}")
            
            # Save Markdown with all details for EVERY stock
            md_file = self.analysis_dir / f'NIFTY50_DYNAMIC_{self.timestamp}.md'
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write("# NIFTY 50 DYNAMIC RECOMMENDATION REPORT\n")
                f.write(f"## {datetime.now().strftime('%B %d, %Y')} - Automated Analysis\n\n")
                f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Stocks**: {len(self.recommendations)} analyzed\n")
                f.write(f"**Sentiment**: {sentiment}\n\n")
                f.write(f"**BUY**: {buy_count} | **HOLD**: {hold_count} | **SELL**: {sell_count}\n\n")
                f.write(f"**Avg Trend**: {avg_trend:+.2f}% | **Avg Momentum**: {avg_momentum:+.2f}% | **Avg R:R**: {avg_rr:.2f}:1\n\n")
                f.write("---\n\n")
                
                f.write("## HOW SIGNALS ARE GENERATED\n\n")
                f.write("Each stock is analyzed using a scoring system (0-5 points):\n\n")
                f.write("**Trend Score** (0-1.5 points): Based on 50-day moving average\n")
                f.write("- +1.0 point: Trend > +3% (strong uptrend)\n")
                f.write("- +0.7 points: Trend > +1% (moderate uptrend)\n")
                f.write("- +0.4 points: Trend > 0% (slight uptrend)\n")
                f.write("- 0 points: Trend <= 0% (neutral or downtrend)\n\n")
                f.write("**Momentum Score** (0-1.5 points): Based on 10-day returns\n")
                f.write("- +1.0 point: Momentum > +10% (very strong buying)\n")
                f.write("- +0.8 points: Momentum > +5% (strong buying)\n")
                f.write("- +0.5 points: Momentum > 0% (moderate buying)\n")
                f.write("- 0 points: Momentum <= 0% (no buying pressure)\n\n")
                f.write("**Volatility Score** (0-1.5 points): Based on 20-day volatility\n")
                f.write("- +1.0 point: Volatility < 12% (very safe)\n")
                f.write("- +0.9 points: Volatility 12-20% (safe)\n")
                f.write("- +0.5 points: Volatility 20-25% (moderate risk)\n")
                f.write("- +0.2 points: Volatility > 25% (high risk)\n\n")
                f.write("**Final Signal:**\n")
                f.write("- **BUY**: Score >= 3.5 AND (Trend > -2% OR Momentum > 5%)\n")
                f.write("- **SELL**: Score < 2.5 OR (Trend < -3% AND Momentum < 0%)\n")
                f.write("- **HOLD**: Everything else\n\n")
                f.write("---\n\n")
                
                f.write("## ALL RECOMMENDATIONS - COMPLETE ANALYSIS\n\n")
                
                # Sort by signal type, then by R:R
                buy_recs = [r for r in self.recommendations if r['signal'] == 'BUY']
                hold_recs = [r for r in self.recommendations if r['signal'] == 'HOLD']
                sell_recs = [r for r in self.recommendations if r['signal'] == 'SELL']
                
                buy_recs.sort(key=lambda x: x['dynamic_rr'], reverse=True)
                hold_recs.sort(key=lambda x: x['dynamic_rr'], reverse=True)
                sell_recs.sort(key=lambda x: x['dynamic_rr'], reverse=True)
                
                # Write each recommendation with full analysis
                for section_name, recs in [("BUY SIGNALS", buy_recs), ("HOLD SIGNALS", hold_recs), ("SELL SIGNALS", sell_recs)]:
                    if recs:
                        f.write(f"## {section_name} ({len(recs)} Stocks)\n\n")
                        
                        for idx, rec in enumerate(recs, 1):
                            f.write(f"### {idx}. {rec['symbol']} - {rec['signal']} (R:R {rec['dynamic_rr']:.2f}:1)\n\n")
                            
                            # Current metrics
                            f.write("**Current Metrics & Analysis:**\n\n")
                            f.write(f"- **Price**: Rs {rec['price']:.2f}\n")
                            f.write(f"- **Trend**: {rec['trend']:+.2f}% " + 
                                   ("(Strong uptrend - EXCELLENT)" if rec['trend'] > 3 else 
                                    "(Moderate uptrend - GOOD)" if rec['trend'] > 1 else
                                    "(Weak uptrend)" if rec['trend'] > 0 else
                                    "(Downtrend - WEAK)") + "\n")
                            f.write(f"- **Momentum**: {rec['momentum']:+.2f}% " +
                                   ("(Very strong - buying pressure)" if rec['momentum'] > 10 else
                                    "(Good - moderate buying)" if rec['momentum'] > 5 else
                                    "(Slight buying)" if rec['momentum'] > 0 else
                                    "(Selling pressure)") + "\n")
                            f.write(f"- **Volatility**: {rec['volatility']:.1f}% " +
                                   ("(Very safe)" if rec['volatility'] < 12 else
                                    "(Safe)" if rec['volatility'] <= 20 else
                                    "(Moderate risk)" if rec['volatility'] <= 25 else
                                    "(High risk)") + "\n")
                            f.write(f"- **Score**: {rec['score']:.2f}/5.0\n")
                            f.write(f"- **Risk Level**: {rec['risk']}\n\n")
                            
                            # Why this signal?
                            f.write(f"**Why {rec['signal']}?**\n\n")
                            if rec['signal'] == 'BUY':
                                f.write("- Strong setup with good risk/reward potential\n")
                                if rec['trend'] > 0:
                                    f.write(f"- Positive trend: Stock {rec['trend']:.2f}% above 50-day average\n")
                                if rec['momentum'] > 0:
                                    f.write(f"- Good momentum: {rec['momentum']:.2f}% gain in 10 days\n")
                                if rec['volatility'] < 20:
                                    f.write(f"- Manageable volatility: {rec['volatility']:.1f}%\n")
                            elif rec['signal'] == 'HOLD':
                                f.write("- Not ready for entry yet, conditions need improvement\n")
                                if rec['trend'] < 1:
                                    f.write(f"- Weak trend: {rec['trend']:.2f}%\n")
                                if rec['momentum'] < 5:
                                    f.write(f"- Low momentum: {rec['momentum']:.2f}%\n")
                            else:  # SELL
                                f.write("- Weak setup, avoid for now\n")
                                if rec['trend'] < 0:
                                    f.write(f"- Negative trend: {rec['trend']:.2f}% below average\n")
                                if rec['momentum'] < 0:
                                    f.write(f"- Selling pressure: {rec['momentum']:.2f}%\n")
                            
                            f.write("\n**Entry & Exit Levels:**\n\n")
                            f.write(f"- **Support**: Rs {rec['support']:.2f}\n")
                            f.write(f"- **Entry Low**: Rs {rec['entry_low']:.2f}\n")
                            f.write(f"- **Entry High**: Rs {rec['entry_high']:.2f}\n")
                            f.write(f"- **Stop Loss**: Rs {rec['stop']:.2f}\n")
                            f.write(f"- **Target 1**: Rs {rec['target_1']:.2f} (+{((rec['target_1']-rec['price'])/rec['price']*100):.1f}%)\n")
                            f.write(f"- **Target 2**: Rs {rec['target_2']:.2f} (+{((rec['target_2']-rec['price'])/rec['price']*100):.1f}%)\n")
                            f.write(f"- **Resistance**: Rs {rec['resistance']:.2f}\n\n")
                            f.write(f"**Exit Strategy**: {rec['exit_strategy']}\n\n")
                            f.write("---\n\n")
            
            self.log(f"[SAVED] {md_file.name}")
            
            # Print summary
            self.log("")
            self.log("=" * 80)
            self.log("GENERATION SUMMARY")
            self.log("=" * 80)
            self.log(f"BUY: {buy_count} | HOLD: {hold_count} | SELL: {sell_count}")
            self.log(f"Sentiment: {sentiment}")
            self.log(f"Avg Trend: {avg_trend:+.2f}% | Avg Momentum: {avg_momentum:+.2f}% | Avg R:R: {avg_rr:.2f}:1")
            self.log("")
            self.log("Output Files:")
            self.log(f"  1. {csv_file.name}")
            self.log(f"  2. {json_file.name}")
            self.log(f"  3. {md_file.name}")
            self.log("")
            
            return True
        
        except Exception as e:
            self.log(f"ERROR saving outputs: {str(e)}", "ERROR")
            traceback.print_exc()
            return False
    
    def cleanup_old_files(self):
        """Delete old recommendation files, keep only latest 3."""
        self.log("CLEANING UP OLD FILES")
        self.log("-" * 80)
        
        try:
            # Get all NIFTY50_DYNAMIC files
            dynamic_files = sorted(
                self.analysis_dir.glob('NIFTY50_DYNAMIC_*.csv'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Keep only 3 latest, delete rest
            deleted = 0
            for old_file in dynamic_files[3:]:
                # Delete associated json and md files too
                timestamp = old_file.stem.replace('NIFTY50_DYNAMIC_', '')
                for ext in ['.csv', '.json', '.md']:
                    file_to_delete = self.analysis_dir / f'NIFTY50_DYNAMIC_{timestamp}{ext}'
                    if file_to_delete.exists():
                        file_to_delete.unlink()
                        deleted += 1
            
            if deleted > 0:
                self.log(f"Deleted {deleted} old recommendation files (kept 3 latest)")
            self.log("")
            
        except Exception as e:
            self.log(f"Warning during cleanup: {str(e)}", "WARN")
    
    def run(self):
        """Execute complete workflow."""
        print("\n")
        self.log("=" * 80)
        self.log(" NIFTY50 AUTOMATED WEEKLY RECOMMENDATION GENERATOR V2 ".center(80))
        self.log(f" {datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')} ".center(80))
        self.log("=" * 80)
        self.log("")
        
        try:
            # Step 1: Download data
            if not self.download_stock_data():
                return False
            
            # Step 2: Generate recommendations
            if not self.generate_recommendations():
                return False
            
            # Step 3: Save outputs
            if not self.save_outputs():
                return False
            
            # Step 4: Cleanup old files
            self.cleanup_old_files()
            
            # Final message
            self.log("=" * 80)
            self.log("AUTOMATION COMPLETE - RECOMMENDATIONS READY FOR TRADING")
            self.log("=" * 80)
            self.log("")
            
            return True
        
        except Exception as e:
            self.log(f"FATAL ERROR: {str(e)}", "ERROR")
            traceback.print_exc()
            return False


if __name__ == '__main__':
    generator = NiftyAutomatedGeneratorV2()
    success = generator.run()
    sys.exit(0 if success else 1)
