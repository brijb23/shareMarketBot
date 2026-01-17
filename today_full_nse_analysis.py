"""
TODAY'S COMPREHENSIVE NSE ANALYSIS
Full System Snapshot for ALL Available NSE Stocks as of January 9, 2026
Using Complete System (Fundamental + Technical Analysis)
"""

import subprocess
import re
import os
from datetime import datetime
from collections import defaultdict

# Get all stocks from data directory
def get_all_nse_stocks():
    """Get all available NSE stocks from data directory"""
    stocks = set()
    data_dir = 'data/prices'
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.csv'):
                stock = file.replace('.csv', '')
                stocks.add(stock)
    
    # Add manual list as fallback
    manual_stocks = [
        'ADANIENT.NS', 'ADANIPORTS.NS', 'APOLLOHOSP.NS', 'ARKADE.NS', 'ASIANPAINT.NS',
        'AUROPHARMA.NS', 'AXISBANK.NS', 'BAJAJFINSV.NS', 'BANKBARODA.NS', 'BHARTIARTL.NS',
        'BPCL.NS', 'CGPOWER.NS', 'CIPLA.NS', 'CMSINFO.NS', 'COALINDIA.NS',
        'DIVISLAB.NS', 'EICHERMOT.NS', 'ETERNAL.NS', 'GRASIM.NS', 'HCC.NS',
        'HCLTECH.NS', 'HDFCBANK.NS', 'HINDUNILVR.NS', 'HUDCO.NS', 'ICICIBANK.NS',
        'INDIGO.NS', 'INFY.NS', 'JSWSTEEL.NS', 'KOTAKBANK.NS', 'LT.NS',
        'LTIM.NS', 'LUPIN.NS', 'MARUTI.NS', 'MRF.NS', 'NESTLEIND.NS',
        'NTPC.NS', 'ONGC.NS', 'PGHH.NS', 'POWERGRID.NS', 'RELIANCE.NS',
        'SBIN.NS', 'SUNPHARMA.NS', 'TATACONSUM.NS', 'TATASTEEL.NS', 'TCS.NS',
        'TECHM.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'VEDL.NS', 'WIPRO.NS',
        'HEROMOTOCORP.NS', 'IOC.NS', 'M&MFIN.NS', 'BAJAJFINSERV.NS', 'HDFC.NS', 'NUVAMA.NS'
    ]
    
    for stock in manual_stocks:
        stocks.add(stock)
    
    return sorted(list(stocks))

STOCKS = get_all_nse_stocks()

class TodayNSEAnalyzer:
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.results = {
            'BUY': [],
            'HOLD': [],
            'SELL': [],
            'ERROR': []
        }
        self.snapshot_count = 0
        
    def get_snapshot(self, symbol):
        """Get today's snapshot for a stock"""
        try:
            cmd = f'python main.py --mode snapshot --symbol {symbol} --as-of {self.today}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=12)
            self.snapshot_count += 1
            
            if result.returncode != 0 or "ERROR" in result.stdout:
                return None
            
            output = result.stdout
            if "Price at Date" not in output:
                return None
            
            # Parse price
            price_match = re.search(r'Price at Date:\s*Rs\s*([\d.]+)', output)
            if not price_match:
                return None
            price = float(price_match.group(1))
            
            # Parse scores
            fund_match = re.search(r'Fundamental Score:\s*(\d+)/100', output)
            tech_match = re.search(r'Technical Score:\s*(\d+)/100', output)
            if not (fund_match and tech_match):
                return None
            
            fund_score = int(fund_match.group(1))
            tech_score = int(tech_match.group(1))
            combined = (fund_score + tech_score) / 2
            
            # Parse decision
            decision_match = re.search(r'Decision:\s*([A-Z_]+)', output)
            decision = decision_match.group(1) if decision_match else 'HOLD'
            
            # Normalize decision
            if 'ACCUMULATE' in decision or 'BUY' in decision:
                decision = 'BUY'
            elif 'SELL' in decision:
                decision = 'SELL'
            else:
                decision = 'HOLD'
            
            return {
                'symbol': symbol,
                'price': price,
                'fund': fund_score,
                'tech': tech_score,
                'combined': combined,
                'decision': decision
            }
        except:
            return None
    
    def run_analysis(self):
        """Run analysis on all stocks"""
        print("\n" + "="*140)
        print("TODAY'S COMPREHENSIVE NSE ANALYSIS")
        print(f"Analysis Date: {self.today} (January 9, 2026)")
        print("Full System: Fundamental + Technical Analysis Combined")
        print("="*140)
        print(f"\nAnalyzing {len(STOCKS)} stocks from NSE...\n")
        
        for idx, symbol in enumerate(STOCKS, 1):
            snapshot = self.get_snapshot(symbol)
            
            if snapshot:
                decision = snapshot['decision']
                self.results[decision].append(snapshot)
                
                status = "✓" if decision == 'BUY' else ("✗" if decision == 'SELL' else "─")
                print(f"[{status}] {symbol:15s} | Price: Rs{snapshot['price']:8.2f} | "
                      f"Fund: {snapshot['fund']:3d} | Tech: {snapshot['tech']:3d} | "
                      f"Combined: {snapshot['combined']:5.1f} | {decision}")
            else:
                self.results['ERROR'].append(symbol)
                print(f"[!] {symbol:15s} | ERROR: Could not fetch data")
            
            if idx % 10 == 0:
                print(f"    └─ Progress: {idx}/{len(STOCKS)} stocks analyzed\n")
        
        # Sort by combined score
        for decision in ['BUY', 'HOLD', 'SELL']:
            self.results[decision].sort(key=lambda x: x['combined'], reverse=True)
    
    def print_summary(self):
        """Print final summary"""
        print("\n" + "="*140)
        print("TODAY'S TRADING SIGNALS SUMMARY")
        print("="*140)
        
        total_analyzed = sum(len(v) for k, v in self.results.items() if k != 'ERROR')
        
        print(f"\nOVERALL STATISTICS:")
        print(f"  Stocks Analyzed: {total_analyzed}/{len(STOCKS)}")
        print(f"  Snapshot Calls: {self.snapshot_count}")
        print(f"  Success Rate: {total_analyzed/len(STOCKS)*100:.1f}%")
        
        print(f"\nSIGNAL BREAKDOWN:")
        buy_count = len(self.results['BUY'])
        hold_count = len(self.results['HOLD'])
        sell_count = len(self.results['SELL'])
        
        print(f"  🟢 BUY Signals:   {buy_count:3d} ({buy_count/total_analyzed*100 if total_analyzed > 0 else 0:5.1f}%)")
        print(f"  🟡 HOLD Signals:  {hold_count:3d} ({hold_count/total_analyzed*100 if total_analyzed > 0 else 0:5.1f}%)")
        print(f"  🔴 SELL Signals:  {sell_count:3d} ({sell_count/total_analyzed*100 if total_analyzed > 0 else 0:5.1f}%)")
        
        # Average scores
        all_scores = self.results['BUY'] + self.results['HOLD'] + self.results['SELL']
        if all_scores:
            avg_fund = sum(s['fund'] for s in all_scores) / len(all_scores)
            avg_tech = sum(s['tech'] for s in all_scores) / len(all_scores)
            avg_combined = sum(s['combined'] for s in all_scores) / len(all_scores)
            
            print(f"\nAVERAGE SCORES:")
            print(f"  Fundamental: {avg_fund:5.1f}/100")
            print(f"  Technical:   {avg_tech:5.1f}/100")
            print(f"  Combined:    {avg_combined:5.1f}/100")
        
        # Top BUY recommendations
        if self.results['BUY']:
            print(f"\n{'='*140}")
            print("TOP BUY RECOMMENDATIONS (By Combined Score)")
            print(f"{'='*140}\n")
            print(f"{'Rank':<6} {'Symbol':<12} {'Price':>10} {'Fund':>6} {'Tech':>6} {'Combined':>10} {'Decision':<12}")
            print(f"{'-'*140}")
            
            for rank, stock in enumerate(self.results['BUY'][:15], 1):
                print(f"{rank:<6} {stock['symbol']:<12} Rs{stock['price']:>8.2f} "
                      f"{stock['fund']:>6} {stock['tech']:>6} {stock['combined']:>9.1f}  BUY")
        
        # HOLD list
        if self.results['HOLD']:
            print(f"\n{'='*140}")
            print(f"HOLD SIGNALS ({len(self.results['HOLD'])} stocks)")
            print(f"{'='*140}\n")
            
            # Show top HOLD candidates
            print("Top HOLD candidates (Best technicals/fundamentals):\n")
            for rank, stock in enumerate(self.results['HOLD'][:10], 1):
                print(f"{rank:2d}. {stock['symbol']:12s} | Fund: {stock['fund']:3d} | Tech: {stock['tech']:3d} | "
                      f"Combined: {stock['combined']:5.1f} | Price: Rs{stock['price']:8.2f}")
        
        # Save to file
        self._save_results()
    
    def _save_results(self):
        """Save results to file"""
        filename = f"TODAY_NSE_ANALYSIS_{self.today.replace('-', '')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*140 + "\n")
            f.write("TODAY'S COMPREHENSIVE NSE ANALYSIS\n")
            f.write(f"Analysis Date: {self.today}\n")
            f.write("Full System: Fundamental + Technical Analysis\n")
            f.write("="*140 + "\n\n")
            
            total = sum(len(v) for k, v in self.results.items() if k != 'ERROR')
            f.write(f"SUMMARY:\n")
            f.write(f"  Total Stocks Analyzed: {total}\n")
            f.write(f"  BUY Signals: {len(self.results['BUY'])} ({len(self.results['BUY'])/total*100 if total > 0 else 0:.1f}%)\n")
            f.write(f"  HOLD Signals: {len(self.results['HOLD'])} ({len(self.results['HOLD'])/total*100 if total > 0 else 0:.1f}%)\n")
            f.write(f"  SELL Signals: {len(self.results['SELL'])} ({len(self.results['SELL'])/total*100 if total > 0 else 0:.1f}%)\n\n")
            
            # BUY recommendations
            f.write("="*140 + "\n")
            f.write("BUY RECOMMENDATIONS\n")
            f.write("="*140 + "\n\n")
            f.write(f"{'Rank':<6} {'Symbol':<12} {'Price':>10} {'Fund':>6} {'Tech':>6} {'Combined':>10}\n")
            f.write("-"*140 + "\n")
            
            for rank, stock in enumerate(self.results['BUY'], 1):
                f.write(f"{rank:<6} {stock['symbol']:<12} Rs{stock['price']:>8.2f} "
                       f"{stock['fund']:>6} {stock['tech']:>6} {stock['combined']:>9.1f}\n")
            
            # HOLD list
            f.write("\n" + "="*140 + "\n")
            f.write("HOLD SIGNALS\n")
            f.write("="*140 + "\n\n")
            f.write(f"{'Rank':<6} {'Symbol':<12} {'Price':>10} {'Fund':>6} {'Tech':>6} {'Combined':>10}\n")
            f.write("-"*140 + "\n")
            
            for rank, stock in enumerate(self.results['HOLD'], 1):
                f.write(f"{rank:<6} {stock['symbol']:<12} Rs{stock['price']:>8.2f} "
                       f"{stock['fund']:>6} {stock['tech']:>6} {stock['combined']:>9.1f}\n")
            
            # SELL signals
            if self.results['SELL']:
                f.write("\n" + "="*140 + "\n")
                f.write("SELL SIGNALS\n")
                f.write("="*140 + "\n\n")
                f.write(f"{'Rank':<6} {'Symbol':<12} {'Price':>10} {'Fund':>6} {'Tech':>6} {'Combined':>10}\n")
                f.write("-"*140 + "\n")
                
                for rank, stock in enumerate(self.results['SELL'], 1):
                    f.write(f"{rank:<6} {stock['symbol']:<12} Rs{stock['price']:>8.2f} "
                           f"{stock['fund']:>6} {stock['tech']:>6} {stock['combined']:>9.1f}\n")
        
        print(f"\n✓ Results saved to: {filename}")

def main():
    analyzer = TodayNSEAnalyzer()
    analyzer.run_analysis()
    analyzer.print_summary()

if __name__ == "__main__":
    main()
