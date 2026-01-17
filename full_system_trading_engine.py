"""
NIFTY 100 FULL SYSTEM TRADING ANALYSIS: 2024-2026
Using REAL Snapshot Analysis (Fundamental + Technical)
Quarterly Portfolio Management with Complete System Integration
"""

import subprocess
import re
import time
import sys

# 30 major NIFTY stocks for realistic simulation
STOCKS = [
    'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
    'WIPRO.NS', 'AXISBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'MARUTI.NS',
    'LT.NS', 'ASIANPAINT.NS', 'BHARTIARTL.NS', 'SUNPHARMA.NS', 'NESTLEIND.NS',
    'DIVISLAB.NS', 'ULTRACEMCO.NS', 'GRASIM.NS', 'TATASTEEL.NS', 'TATAMOTORS.NS',
    'JSWSTEEL.NS', 'EICHERMOT.NS', 'BAJAJFINSV.NS', 'IOC.NS', 'NTPC.NS',
    'HDFC.NS', 'BAJAJFINSERV.NS', 'POWERGRID.NS', 'HEROMOTOCORP.NS', 'HCLTECH.NS'
]

class FullSystemTradingEngine:
    def __init__(self, capital=100000):
        self.capital = capital
        self.initial_capital = capital
        self.portfolio = {}
        self.trades_log = []
        self.snapshot_count = 0
        self.quarterly_data = []
        
    def get_snapshot(self, symbol, date_str):
        """Get snapshot from full system"""
        try:
            cmd = f'python main.py --mode snapshot --symbol {symbol} --as-of {date_str}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=12)
            self.snapshot_count += 1
            
            if result.returncode != 0:
                return None
            
            output = result.stdout
            if "ERROR" in output or "Price at Date" not in output:
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
            
            # Normalize decision names
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
    
    def process_quarterly_trading(self):
        """Process trading across 9 quarters"""
        quarters = [
            ('2024-03-31', 'Q1 2024'),
            ('2024-06-30', 'Q2 2024'),
            ('2024-09-30', 'Q3 2024'),
            ('2024-12-31', 'Q4 2024'),
            ('2025-03-31', 'Q1 2025'),
            ('2025-06-30', 'Q2 2025'),
            ('2025-09-30', 'Q3 2025'),
            ('2025-12-31', 'Q4 2025'),
            ('2026-01-09', 'Q1 2026'),
        ]
        
        print("\n" + "="*150)
        print("NIFTY 100 COMPLETE SYSTEM TRADING SIMULATION: 2024-2026")
        print("Full System Analysis (Fundamental + Technical Combined)")
        print("="*150)
        print(f"Capital: Rs{self.initial_capital:,} | Stocks: {len(STOCKS)} | Position: 5% per signal")
        print(f"Risk Management: 10% Stop Loss | 15% Profit Target")
        print("="*150 + "\n")
        
        for q_num, (date_str, q_name) in enumerate(quarters, 1):
            print(f"\n{'█'*150}")
            print(f"QUARTER {q_num}: {q_name} ({date_str})")
            print(f"{'█'*150}\n")
            
            buy_list = []
            sell_list = []
            
            # Run full analysis
            print(f"Snapshot Analysis of {len(STOCKS)} stocks:")
            for idx, symbol in enumerate(STOCKS):
                snapshot = self.get_snapshot(symbol, date_str)
                
                if snapshot:
                    if snapshot['decision'] == 'BUY':
                        buy_list.append(snapshot)
                    elif snapshot['decision'] == 'SELL':
                        sell_list.append(snapshot)
                
                if (idx + 1) % 10 == 0:
                    print(f"  └─ Analyzed {idx + 1}/{len(STOCKS)} stocks...")
            
            print(f"✓ Analysis Complete: {len(buy_list)} BUY | {len(sell_list)} SELL")
            
            # Close positions
            closed = self._process_existing_positions(date_str)
            
            # Process SELL signals
            for sell in sell_list:
                if sell['symbol'] in self.portfolio:
                    self._exit_trade(sell['symbol'], sell['price'], 'SELL SIGNAL')
            
            # Process BUY signals
            if buy_list:
                buy_list.sort(key=lambda x: x['combined'], reverse=True)
                self._enter_trades(buy_list, q_name)
            
            # Record quarter
            pv = sum(p['qty'] * p.get('current_price', p['entry_price']) for p in self.portfolio.values())
            tv = self.capital + pv
            self.quarterly_data.append({
                'q': q_name,
                'date': date_str,
                'capital': self.capital,
                'portfolio': pv,
                'total': tv,
                'pnl': tv - self.initial_capital,
                'ret': (tv - self.initial_capital) / self.initial_capital * 100,
                'open': len(self.portfolio),
                'buy': len(buy_list),
                'closed': closed
            })
            
            self._print_quarter_summary()
    
    def _process_existing_positions(self, date_str):
        """Check existing positions for stop loss and targets"""
        closed = 0
        for symbol in list(self.portfolio.keys()):
            pos = self.portfolio[symbol]
            snapshot = self.get_snapshot(symbol, date_str)
            
            if snapshot:
                price = snapshot['price']
                pos['current_price'] = price
                sl = pos['entry_price'] * 0.90
                tgt = pos['entry_price'] * 1.15
                
                if price <= sl:
                    self._exit_trade(symbol, sl, 'STOP LOSS')
                    closed += 1
                elif price >= tgt:
                    self._exit_trade(symbol, tgt, 'PROFIT TARGET')
                    closed += 1
        
        return closed
    
    def _enter_trades(self, buy_signals, q_name):
        """Enter new trades from BUY signals"""
        entered = 0
        print(f"\nNew Positions:")
        for signal in buy_signals:
            sym = signal['symbol']
            price = signal['price']
            
            if sym not in self.portfolio and self.capital > price:
                alloc = self.capital * 0.05
                qty = int(alloc / price)
                
                if qty > 0 and qty * price <= self.capital:
                    cost = qty * price
                    self.capital -= cost
                    
                    self.portfolio[sym] = {
                        'qty': qty,
                        'entry_price': price,
                        'current_price': price,
                        'entry_q': q_name,
                        'fund': signal['fund'],
                        'tech': signal['tech']
                    }
                    
                    print(f"  BUY  {sym:12s} x{qty:4d} @ Rs{price:8.2f} | "
                          f"Cost: Rs{cost:8,.0f} | Fund:{signal['fund']:3d} Tech:{signal['tech']:3d}")
                    entered += 1
        
        if entered == 0:
            print(f"  (No new positions - insufficient capital or signals)")
    
    def _exit_trade(self, symbol, exit_price, reason):
        """Exit a position"""
        pos = self.portfolio[symbol]
        qty = pos['qty']
        entry = pos['entry_price']
        cost = qty * entry
        revenue = qty * exit_price
        pnl = revenue - cost
        ret = (pnl / cost * 100) if cost > 0 else 0
        
        self.capital += revenue
        
        self.trades_log.append({
            'symbol': symbol,
            'qty': qty,
            'entry': entry,
            'exit': exit_price,
            'pnl': pnl,
            'ret': ret,
            'reason': reason
        })
        
        status = "✓" if pnl >= 0 else "✗"
        print(f"  {status} EXIT {symbol:12s} x{qty:4d} @ Rs{exit_price:8.2f} | "
              f"P&L: Rs{pnl:+8,.0f} ({ret:+6.2f}%) [{reason}]")
        
        del self.portfolio[symbol]
    
    def _print_quarter_summary(self):
        """Print current quarter summary"""
        data = self.quarterly_data[-1]
        print(f"\nQuarter Summary:")
        print(f"  Capital:  Rs{data['capital']:>12,.0f}")
        print(f"  Holdings: Rs{data['portfolio']:>12,.0f}")
        print(f"  Total:    Rs{data['total']:>12,.0f}")
        print(f"  Open:     {data['open']:>12d} positions")
        print(f"  P&L:      Rs{data['pnl']:>12,.0f} ({data['ret']:+.2f}%)")
    
    def print_final_report(self):
        """Generate final report"""
        print("\n" + "="*150)
        print("COMPLETE SYSTEM TRADING FINAL REPORT")
        print("="*150)
        
        tv = self.capital + sum(p['qty'] * p.get('current_price', p['entry_price']) for p in self.portfolio.values())
        total_pnl = tv - self.initial_capital
        total_ret = (total_pnl / self.initial_capital * 100) if self.initial_capital else 0
        
        # Summary
        print(f"\nPERFORMANCE METRICS:")
        print(f"  Initial Capital:        Rs{self.initial_capital:>12,.0f}")
        print(f"  Final Cash:             Rs{self.capital:>12,.0f}")
        print(f"  Current Holdings Value: Rs{tv - self.capital:>12,.0f}")
        print(f"  Final Portfolio Value:  Rs{tv:>12,.0f}")
        print(f"  {'─'*60}")
        print(f"  TOTAL PROFIT/LOSS:      Rs{total_pnl:>12,.0f}")
        print(f"  TOTAL RETURN:           {total_ret:>13.2f}%")
        
        # Trade stats
        if self.trades_log:
            wins = sum(1 for t in self.trades_log if t['pnl'] > 0)
            losses = sum(1 for t in self.trades_log if t['pnl'] < 0)
            win_pnl = sum(t['pnl'] for t in self.trades_log if t['pnl'] > 0)
            loss_pnl = sum(t['pnl'] for t in self.trades_log if t['pnl'] < 0)
            
            print(f"\nTRADE STATISTICS:")
            print(f"  Completed Trades:       {len(self.trades_log):>12d}")
            print(f"  Winning Trades:         {wins:>12d} ({wins/len(self.trades_log)*100:>5.1f}%)")
            print(f"  Losing Trades:          {losses:>12d} ({losses/len(self.trades_log)*100:>5.1f}%)")
            print(f"  Total Win P&L:          Rs{win_pnl:>12,.0f}")
            print(f"  Total Loss P&L:         Rs{loss_pnl:>12,.0f}")
            avg_ret = sum(t['ret'] for t in self.trades_log) / len(self.trades_log)
            print(f"  Average Return/Trade:   {avg_ret:>13.2f}%")
            
            if loss_pnl != 0:
                pf = abs(win_pnl / loss_pnl)
                print(f"  Profit Factor:          {pf:>13.2f}x")
        
        # Quarterly table
        print(f"\nQUARTERLY PROGRESSION:")
        print(f"{'Quarter':<12} {'Capital':>12} {'Holdings':>12} {'Total':>12} {'Open':>6} {'BUY':>5} {'P&L':>12} {'Return':>10}")
        print(f"{'-'*150}")
        
        for d in self.quarterly_data:
            print(f"{d['q']:<12} Rs{d['capital']:>10,.0f} Rs{d['portfolio']:>10,.0f} Rs{d['total']:>10,.0f} "
                  f"{d['open']:>6d} {d['buy']:>5d} Rs{d['pnl']:>10,.0f} {d['ret']:>9.2f}%")
        
        # Save to file
        with open('NIFTY100_FULL_SYSTEM_TRADING_RESULTS.txt', 'w') as f:
            f.write("="*150 + "\n")
            f.write("NIFTY 100 COMPLETE SYSTEM TRADING RESULTS: 2024-2026\n")
            f.write("="*150 + "\n\n")
            f.write(f"Initial Capital: Rs{self.initial_capital:,.0f}\n")
            f.write(f"Final Portfolio Value: Rs{tv:,.0f}\n")
            f.write(f"Total P&L: Rs{total_pnl:,.0f}\n")
            f.write(f"Total Return: {total_ret:+.2f}%\n\n")
            f.write(f"Snapshot Analysis Calls: {self.snapshot_count}\n")
            f.write(f"Total Trades Completed: {len(self.trades_log)}\n\n")
            
            f.write("QUARTERLY PERFORMANCE:\n")
            f.write("-"*150 + "\n")
            for d in self.quarterly_data:
                f.write(f"{d['q']:<12} | Capital: Rs{d['capital']:>10,.0f} | Holdings: Rs{d['portfolio']:>10,.0f} | "
                       f"P&L: Rs{d['pnl']:>10,.0f} ({d['ret']:+.2f}%)\n")
        
        print(f"\n✓ Results saved: NIFTY100_FULL_SYSTEM_TRADING_RESULTS.txt")
        print("="*150)

def main():
    engine = FullSystemTradingEngine(capital=100000)
    engine.process_quarterly_trading()
    engine.print_final_report()

if __name__ == "__main__":
    main()
