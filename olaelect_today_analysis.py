"""
OLA ELECTRIC (OLAELECT.NS) DETAILED ANALYSIS
Today's Full System Snapshot - January 9, 2026
Using Complete System (Fundamental + Technical Analysis)
"""

import subprocess
import re
from datetime import datetime

class OlaElectricAnalyzer:
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.symbol = 'OLAELEC.NS'
        
    def get_detailed_snapshot(self):
        """Get detailed snapshot for OLA ELECTRIC"""
        try:
            cmd = f'python main.py --mode snapshot --symbol {self.symbol} --as-of {self.today}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                print(f"[ERROR] Could not fetch data for {self.symbol}")
                return None
            
            return result.stdout
        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            return None
    
    def parse_snapshot(self, output):
        """Parse snapshot output into structured data"""
        data = {}
        
        # Extract price
        price_match = re.search(r'Price at Date:\s*Rs\s*([\d.]+)', output)
        if price_match:
            data['price'] = float(price_match.group(1))
        
        # Extract fundamental score
        fund_match = re.search(r'Fundamental Score:\s*(\d+)/100', output)
        if fund_match:
            data['fund_score'] = int(fund_match.group(1))
        
        # Extract technical score
        tech_match = re.search(r'Technical Score:\s*(\d+)/100', output)
        if tech_match:
            data['tech_score'] = int(tech_match.group(1))
        
        # Extract combined score
        if 'fund_score' in data and 'tech_score' in data:
            data['combined_score'] = (data['fund_score'] + data['tech_score']) / 2
        
        # Extract decision
        decision_match = re.search(r'Decision:\s*([^\n]+)', output)
        if decision_match:
            data['decision'] = decision_match.group(1).strip()
        
        # Extract rationale
        rationale_match = re.search(r'Rationale:\s*([^\n]+)', output)
        if rationale_match:
            data['rationale'] = rationale_match.group(1).strip()
        
        return data
    
    def run_analysis(self):
        """Run complete analysis"""
        print("\n" + "="*140)
        print("OLA ELECTRIC COMPREHENSIVE ANALYSIS")
        print(f"Analysis Date: {self.today} (January 9, 2026)")
        print("Full System: Fundamental + Technical Analysis")
        print("="*140 + "\n")
        
        print(f"Fetching snapshot for {self.symbol}...\n")
        
        output = self.get_detailed_snapshot()
        
        if not output:
            print("[ERROR] Failed to retrieve analysis")
            return
        
        # Print raw output
        print("RAW SYSTEM OUTPUT:")
        print("-"*140)
        print(output)
        print("-"*140 + "\n")
        
        # Parse and display structured data
        data = self.parse_snapshot(output)
        
        if not data:
            print("[ERROR] Could not parse snapshot data")
            return
        
        self.print_structured_analysis(data)
        self.save_results(output, data)
    
    def print_structured_analysis(self, data):
        """Print structured analysis"""
        print("\nSTRUCTURED ANALYSIS:")
        print("="*140)
        
        print(f"\nSTOCK: {self.symbol}")
        print(f"Analysis Date: {self.today}")
        
        if 'price' in data:
            print(f"\nCurrent Price: Rs {data['price']:.2f}")
        
        print(f"\nSCORING METRICS:")
        if 'fund_score' in data:
            fund = data['fund_score']
            print(f"  Fundamental Score: {fund}/100", end="")
            if fund >= 70:
                print(" [EXCELLENT]")
            elif fund >= 60:
                print(" [GOOD]")
            elif fund >= 50:
                print(" [FAIR]")
            else:
                print(" [WEAK]")
        
        if 'tech_score' in data:
            tech = data['tech_score']
            print(f"  Technical Score:   {tech}/100", end="")
            if tech >= 70:
                print(" [EXCELLENT]")
            elif tech >= 60:
                print(" [GOOD]")
            elif tech >= 50:
                print(" [FAIR]")
            else:
                print(" [WEAK]")
        
        if 'combined_score' in data:
            combined = data['combined_score']
            print(f"  Combined Score:    {combined:.1f}/100", end="")
            if combined >= 70:
                print(" [STRONG BUY]")
            elif combined >= 65:
                print(" [BUY]")
            elif combined >= 60:
                print(" [MODERATE BUY]")
            elif combined >= 50:
                print(" [HOLD]")
            else:
                print(" [WEAK]")
        
        print(f"\nDECISION:")
        if 'decision' in data:
            decision = data['decision']
            if 'BUY' in decision.upper() or 'ACCUMULATE' in decision.upper():
                print(f"  Status: BUY [Green Signal]")
            elif 'SELL' in decision.upper():
                print(f"  Status: SELL [Red Signal]")
            else:
                print(f"  Status: HOLD [Yellow Signal]")
            
            print(f"  Details: {decision}")
        
        if 'rationale' in data:
            print(f"\nRATIONALE:")
            print(f"  {data['rationale']}")
        
        # Trading recommendation
        print(f"\nTRADING RECOMMENDATION:")
        if 'combined_score' in data and 'price' in data:
            combined = data['combined_score']
            price = data['price']
            
            # Calculate target and stop loss
            target_price = price * 1.15
            stop_loss_price = price * 0.90
            
            print(f"  Entry Price: Rs {price:.2f}")
            print(f"  Target Price (15% upside): Rs {target_price:.2f}")
            print(f"  Stop Loss (10% downside): Rs {stop_loss_price:.2f}")
            print(f"  Risk:Reward Ratio: 1:1.5")
            
            if combined >= 65:
                print(f"  Recommendation: STRONG BUY - Enter on dips")
            elif combined >= 60:
                print(f"  Recommendation: BUY - Good entry point")
            elif combined >= 55:
                print(f"  Recommendation: WAIT - Monitor for better entry")
            else:
                print(f"  Recommendation: HOLD/AVOID - Wait for technical improvement")
        
        print("\n" + "="*140)
    
    def save_results(self, raw_output, data):
        """Save results to file"""
        filename = f"OLAELECT_ANALYSIS_{self.today.replace('-', '')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*140 + "\n")
            f.write("OLA ELECTRIC (OLAELECT.NS) COMPREHENSIVE ANALYSIS\n")
            f.write(f"Analysis Date: {self.today}\n")
            f.write("Full System: Fundamental + Technical Analysis\n")
            f.write("="*140 + "\n\n")
            
            if 'price' in data:
                f.write(f"Current Price: Rs {data['price']:.2f}\n\n")
            
            f.write("SCORING BREAKDOWN:\n")
            if 'fund_score' in data:
                f.write(f"  Fundamental Score: {data['fund_score']}/100\n")
            if 'tech_score' in data:
                f.write(f"  Technical Score: {data['tech_score']}/100\n")
            if 'combined_score' in data:
                f.write(f"  Combined Score: {data['combined_score']:.1f}/100\n\n")
            
            f.write("DECISION:\n")
            if 'decision' in data:
                f.write(f"  {data['decision']}\n\n")
            
            if 'rationale' in data:
                f.write("RATIONALE:\n")
                f.write(f"  {data['rationale']}\n\n")
            
            f.write("RAW SYSTEM OUTPUT:\n")
            f.write("-"*140 + "\n")
            f.write(raw_output)
            f.write("-"*140 + "\n")
        
        print(f"\nResults saved to: {filename}")

def main():
    analyzer = OlaElectricAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
