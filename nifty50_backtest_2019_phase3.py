#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIFTY50 BACKTEST 2019 TO DATE - PHASE 3 (SELL AT TARGET)
Backtests trading recommendations from 2019 till present
with 10 lakh working capital
Weekly basis analysis - SELL IMMEDIATELY when target achieved
(No intelligent target improvement logic - just mechanical exit)
"""

import os, json, csv, pandas as pd, numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from pathlib import Path
import traceback
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    NIFTY50_STOCKS = [
        'RELIANCE.NS', 'TCS.NS', 'ICICIBANK.NS', 'SBIN.NS',
        'BHARTIARTL.NS', 'ITC.NS', 'LT.NS', 'MARUTI.NS', 'ADANIPORTS.NS',
        'ASIANPAINT.NS', 'BAJAJ-AUTO.NS', 'BAJAJFINSV.NS', 'BPCL.NS', 'BRITANNIA.NS',
        'CIPLA.NS', 'COALINDIA.NS', 'COLPAL.NS', 'DIVISLAB.NS', 'DRREDDY.NS',
        'EICHERMOT.NS', 'GAIL.NS', 'GRASIM.NS', 'HCLTECH.NS', 'HDFCBANK.NS',
        'HEROMOTOCO.NS', 'HINDUNILVR.NS', 'INFY.NS', 'JSWSTEEL.NS', 'KOTAKBANK.NS',
        'LTIM.NS', 'M&M.NS', 'NESTLEIND.NS', 'NTPC.NS', 'ONGC.NS',
        'POLICYBZR.NS', 'POWERGRID.NS', 'SBILIFE.NS', 'SUNPHARMA.NS', 'TECHM.NS',
        'TITAN.NS', 'TATACONSUM.NS', 'TATASTEEL.NS', 'ULTRACEMCO.NS', 'VBL.NS',
        'WIPRO.NS', 'ZEEL.NS'
    ]
    
    INITIAL_CAPITAL = 1000000  # 10 lakh
    TREND_THRESHOLD = 0.5
    MOMENTUM_THRESHOLD = 1.0
    VOLATILITY_LOW = 12
    VOLATILITY_NORMAL = 20
    
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / 'nifty50_analysis'
    LOG_DIR = BASE_DIR / 'logs'
    
    @classmethod
    def ensure_directories(cls):
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.LOG_DIR.mkdir(exist_ok=True)

# ============================================================================
# LOGGING
# ============================================================================

class BacktestLogger:
    def __init__(self, name):
        Config.ensure_directories()
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = Config.LOG_DIR / f'BACKTEST_PHASE3_2019_{self.timestamp}.txt'
        self.messages = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"{timestamp} | {message}"
        print(log_msg)
        self.messages.append(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')

logger = BacktestLogger('BACKTEST_PHASE3_2019')

# ============================================================================
# DATA COLLECTOR
# ============================================================================

class BacktestDataCollector:
    def __init__(self):
        self.logger = logger
        
    def fetch_stock_data(self, ticker, start_date, end_date):
        """Fetch data for a stock for the entire period"""
        try:
            data = yf.download(ticker, start=start_date, end=end_date, 
                             progress=False, threads=False, timeout=30)
            if data is None or data.empty or len(data) < 50:
                return None
            return data
        except Exception as e:
            return None
    
    def fetch_all_data(self, start_date, end_date):
        """Fetch data for all stocks for the period"""
        self.logger.log("[STEP 1] DOWNLOADING MARKET DATA FROM YFINANCE")
        self.logger.log(f"Period: {start_date} to {end_date}")
        
        all_data = {}
        successful = 0
        
        for ticker in Config.NIFTY50_STOCKS:
            data = self.fetch_stock_data(ticker, start_date, end_date)
            if data is not None and not data.empty:
                all_data[ticker] = data
                successful += 1
        
        self.logger.log(f"[OK] {successful}/{len(Config.NIFTY50_STOCKS)} stocks downloaded")
        return all_data

# ============================================================================
# ANALYSIS ENGINE (Phase 19.2)
# ============================================================================

class BacktestAnalysisEngine:
    def __init__(self):
        self.logger = logger
    
    def calc_trend(self, data):
        """Calculate trend using 50-day moving average"""
        try:
            close = data['Close'].astype(float)
            ma50 = close.rolling(50).mean()
            current = float(close.iloc[-1])
            ma50_val = float(ma50.iloc[-1])
            if pd.isna(ma50_val) or ma50_val == 0:
                return 0.0
            return ((current - ma50_val) / ma50_val) * 100
        except:
            return 0.0
    
    def calc_momentum(self, data):
        """Calculate momentum using 10-day price change"""
        try:
            close = data['Close'].astype(float)
            current = float(close.iloc[-1])
            ten_days_ago = float(close.iloc[-10]) if len(close) >= 10 else float(close.iloc[0])
            if ten_days_ago == 0:
                return 0.0
            return ((current - ten_days_ago) / ten_days_ago) * 100
        except:
            return 0.0
    
    def calc_volatility(self, data):
        """Calculate volatility using 20-day standard deviation"""
        try:
            close = data['Close'].astype(float)
            returns = close.pct_change() * 100
            volatility = returns.rolling(20).std().iloc[-1]
            return float(volatility) if not pd.isna(volatility) else 0.0
        except:
            return 0.0
    
    def calc_atr(self, data, period=14):
        """Calculate Average True Range"""
        try:
            high = data['High'].astype(float)
            low = data['Low'].astype(float)
            close = data['Close'].astype(float)
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(period).mean().iloc[-1]
            
            return float(atr) if not pd.isna(atr) else 0.0
        except:
            return 0.0
    
    def generate_signal(self, trend, momentum):
        """Generate BUY/HOLD/SELL signal"""
        if trend > Config.TREND_THRESHOLD and momentum > Config.MOMENTUM_THRESHOLD:
            return "BUY"
        elif trend < -Config.TREND_THRESHOLD and momentum < -Config.MOMENTUM_THRESHOLD:
            return "SELL"
        else:
            return "HOLD"
    
    def analyze_at_date(self, all_data, analysis_date):
        """Analyze all stocks at a specific date"""
        results = {}
        
        for ticker, data in all_data.items():
            try:
                # Get data up to analysis date
                data_till_date = data[data.index <= pd.Timestamp(analysis_date)]
                if len(data_till_date) < 50:
                    continue
                
                current_price = float(data_till_date['Close'].iloc[-1])
                trend = self.calc_trend(data_till_date)
                momentum = self.calc_momentum(data_till_date)
                volatility = self.calc_volatility(data_till_date)
                atr = self.calc_atr(data_till_date)
                signal = self.generate_signal(trend, momentum)
                
                # Entry, Stop, Target
                if signal == "BUY":
                    entry_low = current_price - atr
                    entry_high = current_price + (atr * 0.5)
                    target = current_price + (atr * 2)
                    stop_loss = current_price - (atr * 1.5)
                elif signal == "SELL":
                    entry_low = current_price - (atr * 0.5)
                    entry_high = current_price + atr
                    target = current_price - (atr * 2)
                    stop_loss = current_price + (atr * 1.5)
                else:
                    entry_low = current_price - atr
                    entry_high = current_price + atr
                    target = current_price + (atr * 1.5)
                    stop_loss = current_price - (atr * 1.5)
                
                rr_ratio = abs(target - current_price) / abs(stop_loss - current_price) if stop_loss != current_price else 0
                
                results[ticker] = {
                    'date': analysis_date,
                    'current_price': round(current_price, 2),
                    'trend': round(trend, 2),
                    'momentum': round(momentum, 2),
                    'volatility': round(volatility, 2),
                    'atr': round(atr, 2),
                    'signal': signal,
                    'entry_low': round(entry_low, 2),
                    'entry_high': round(entry_high, 2),
                    'target': round(target, 2),
                    'stop_loss': round(stop_loss, 2),
                    'rr_ratio': round(rr_ratio, 2)
                }
            except:
                continue
        
        return results

# ============================================================================
# BACKTEST EXECUTOR
# ============================================================================

class BacktestExecutor:
    def __init__(self, all_data):
        self.logger = logger
        self.all_data = all_data
        self.engine = BacktestAnalysisEngine()
        
    def execute(self):
        """Execute weekly backtest"""
        self.logger.log("[STEP 2] EXECUTING WEEKLY BACKTEST")
        
        # Get date range
        all_dates = []
        for ticker, data in self.all_data.items():
            all_dates.extend(data.index.tolist())
        
        if not all_dates:
            self.logger.log("[ERROR] No dates found")
            return None
        
        start_date = min(all_dates)
        end_date = max(all_dates)
        
        self.logger.log(f"Backtest period: {start_date.date()} to {end_date.date()}")
        
        # Get week-end dates (Friday or last trading day of week)
        current_date = pd.Timestamp(start_date)
        week_ends = []
        
        while current_date <= end_date:
            # Get Friday of current week (or last trading day before Friday)
            days_to_friday = (4 - current_date.dayofweek) % 7
            if days_to_friday == 0 and current_date.dayofweek != 4:
                days_to_friday = 7
            
            friday = current_date + pd.Timedelta(days=days_to_friday)
            
            # Find actual last trading day at or before Friday
            last_trading_date = None
            for ticker, data in self.all_data.items():
                valid_dates = data[data.index <= friday]
                if len(valid_dates) > 0:
                    last_trading_date = valid_dates.index[-1]
                    break
            
            if last_trading_date and last_trading_date not in week_ends:
                week_ends.append(last_trading_date)
            
            # Move to next week
            current_date = friday + pd.Timedelta(days=1)
        
        return week_ends

# ============================================================================
# PORTFOLIO MANAGER
# ============================================================================

class PortfolioManager:
    def __init__(self, initial_capital):
        self.logger = logger
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.positions = {}  # ticker -> {entry_price, qty, entry_date, cost, target, stop_loss}
        self.trades = []
        self.monthly_results = []
        self.STOP_LOSS_PERCENT = 0.10  # 10% stop loss
        
    def allocate_capital_to_signal(self, signal_count, per_signal_allocation=None):
        """Allocate capital based on signals"""
        if signal_count == 0:
            return 0
        
        # Conservative: allocate 5% of capital per BUY signal
        if per_signal_allocation is None:
            per_signal_allocation = self.capital * 0.05
        
        return per_signal_allocation
    
    def execute_buy(self, ticker, entry_price, target, stop_loss, signal_date, allocation):
        """Execute BUY trade"""
        if entry_price <= 0:
            return
        
        qty = int(allocation / entry_price)
        if qty <= 0:
            return
        
        cost = qty * entry_price
        self.capital -= cost
        
        self.positions[ticker] = {
            'entry_price': entry_price,
            'qty': qty,
            'entry_date': signal_date,
            'cost': cost,
            'target': target,
            'stop_loss': stop_loss
        }
    
    def check_and_close_positions(self, recommendations, current_date):
        """Check if any positions hit stop loss or target - PHASE 3 LOGIC
        SELL IMMEDIATELY when target or stop loss is hit (no intelligent decisions)
        """
        closed_count = 0
        sl_count = 0
        target_count = 0
        
        for ticker, position in list(self.positions.items()):
            if ticker not in recommendations:
                continue
            
            current_price = recommendations[ticker]['current_price']
            
            # Check if hit stop loss (hard stop, must close)
            if current_price <= position['stop_loss']:
                self.execute_sell(ticker, current_price, current_date, 'STOP_LOSS')
                closed_count += 1
                sl_count += 1
            # Check if hit target (mechanical close - no analysis)
            elif current_price >= position['target']:
                self.execute_sell(ticker, current_price, current_date, 'TARGET')
                closed_count += 1
                target_count += 1
        
        return closed_count, sl_count, target_count
    
    def execute_sell(self, ticker, exit_price, signal_date, reason='SIGNAL'):
        """Execute SELL trade"""
        if ticker not in self.positions:
            return 0
        
        position = self.positions[ticker]
        proceeds = position['qty'] * exit_price
        pnl = proceeds - position['cost']
        self.capital += proceeds
        
        self.trades.append({
            'ticker': ticker,
            'entry_date': position['entry_date'],
            'entry_price': position['entry_price'],
            'exit_date': signal_date,
            'exit_price': exit_price,
            'qty': position['qty'],
            'cost': position['cost'],
            'proceeds': proceeds,
            'pnl': pnl,
            'reason': reason,
            'target': position['target'],
            'stop_loss': position['stop_loss']
        })
        
        del self.positions[ticker]
        return pnl
    
    def get_monthly_summary(self, month_date, recommendations):
        """Get summary for a week"""
        buy_count = sum(1 for r in recommendations.values() if r['signal'] == 'BUY')
        hold_count = sum(1 for r in recommendations.values() if r['signal'] == 'HOLD')
        sell_count = sum(1 for r in recommendations.values() if r['signal'] == 'SELL')
        
        # Calculate unrealized PnL
        unrealized_pnl = 0
        for ticker, position in self.positions.items():
            if ticker in recommendations:
                current_price = recommendations[ticker]['current_price']
                unrealized_pnl += (current_price - position['entry_price']) * position['qty']
        
        realized_pnl = sum(t['pnl'] for t in self.trades)
        total_pnl = realized_pnl + unrealized_pnl
        
        return {
            'date': month_date,
            'buy_signals': buy_count,
            'hold_signals': hold_count,
            'sell_signals': sell_count,
            'capital': round(self.capital, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'realized_pnl': round(realized_pnl, 2),
            'total_pnl': round(total_pnl, 2),
            'total_value': round(self.capital + unrealized_pnl, 2),
            'return_percent': round((total_pnl / self.initial_capital) * 100, 2),
            'positions_count': len(self.positions)
        }

# ============================================================================
# BACKTEST RUNNER
# ============================================================================

class BacktestRunner:
    def __init__(self, initial_capital):
        self.logger = logger
        self.collector = BacktestDataCollector()
        self.engine = BacktestAnalysisEngine()
        self.portfolio = PortfolioManager(initial_capital)
        self.executor = BacktestExecutor({})
        
    def run(self):
        """Run complete backtest"""
        try:
            self.logger.log("\n" + "="*70)
            self.logger.log("NIFTY50 BACKTEST 2019 TO DATE - PHASE 3 (SELL AT TARGET)")
            self.logger.log("="*70)
            self.logger.log(f"Initial Capital: {Config.INITIAL_CAPITAL:,} INR")
            self.logger.log("Strategy: Sell immediately when target achieved (no intelligent logic)")
            
            # Step 1: Download data
            start_date = pd.Timestamp('2019-01-01')
            end_date = pd.Timestamp.now()
            
            all_data = self.collector.fetch_all_data(start_date, end_date)
            if not all_data:
                self.logger.log("[ERROR] Could not download data")
                return
            
            self.executor.all_data = all_data
            
            # Step 2: Get week-end dates
            week_ends = self.executor.execute()
            if not week_ends:
                self.logger.log("[ERROR] No week ends found")
                return
            
            self.logger.log(f"[STEP 3] PROCESSING {len(week_ends)} WEEKS")
            
            # Step 3: Process each week
            for i, analysis_date in enumerate(week_ends, 1):
                try:
                    week_str = pd.Timestamp(analysis_date).strftime('%Y-%m-%d')
                    self.logger.log(f"Week {i}: {week_str}")
                    
                    # Get recommendations for this date
                    recommendations = self.engine.analyze_at_date(all_data, analysis_date)
                    if not recommendations:
                        self.logger.log(f"  [SKIP] No recommendations for {week_str}")
                        continue
                    
                    # Step 3a: Check and close positions (PHASE 3: mechanical exit at target or SL)
                    closed_count, sl_count, target_count = self.portfolio.check_and_close_positions(recommendations, analysis_date)
                    if closed_count > 0:
                        self.logger.log(f"  Closed {closed_count} positions (SL: {sl_count}, Target: {target_count})")
                    
                    # Step 3b: Update existing positions with new targets/stop losses
                    for ticker, position in list(self.portfolio.positions.items()):
                        if ticker in recommendations:
                            rec = recommendations[ticker]
                            position['target'] = rec['target']
                            position['stop_loss'] = rec['stop_loss']
                    
                    # Step 3c: Execute NEW BUY signals only for stocks not already held
                    buy_sigs = [r for r in recommendations.values() if r['signal'] == 'BUY']
                    if len(buy_sigs) > 0:
                        allocation = self.portfolio.allocate_capital_to_signal(len(buy_sigs))
                        for ticker, rec in recommendations.items():
                            # Only buy if not already holding and have capital
                            if (rec['signal'] == 'BUY' and 
                                ticker not in self.portfolio.positions and 
                                self.portfolio.capital > allocation):
                                
                                target = rec['target']
                                stop_loss = max(rec['entry_low'] * (1 - self.portfolio.STOP_LOSS_PERCENT), rec['stop_loss'])
                                
                                self.portfolio.execute_buy(
                                    ticker, 
                                    rec['entry_low'], 
                                    target, 
                                    stop_loss, 
                                    analysis_date, 
                                    allocation
                                )
                    
                    # Get weekly summary
                    summary = self.portfolio.get_monthly_summary(analysis_date, recommendations)
                    self.portfolio.monthly_results.append(summary)
                    
                    self.logger.log(f"  Active Positions: {summary['positions_count']} | Capital: {summary['capital']:,.0f} | PnL: {summary['total_pnl']:,.0f} ({summary['return_percent']:.2f}%)")
                    
                except Exception as e:
                    self.logger.log(f"  [ERROR] {str(e)}")
                    import traceback
                    self.logger.log(traceback.format_exc())
                    continue
            
            # Step 4: Generate outputs
            self.logger.log("[STEP 4] GENERATING BACKTEST REPORTS")
            self.generate_outputs()
            
            # Final summary
            self.logger.log("\n" + "="*70)
            self.logger.log("BACKTEST COMPLETED SUCCESSFULLY")
            self.logger.log("="*70)
            
            if self.portfolio.monthly_results:
                final = self.portfolio.monthly_results[-1]
                self.logger.log(f"\nFinal Capital: {final['total_value']:,.0f} INR")
                self.logger.log(f"Total Profit/Loss: {final['total_pnl']:,.0f} INR")
                self.logger.log(f"Return %: {final['return_percent']:.2f}%")
                self.logger.log(f"Total Trades: {len(self.portfolio.trades)}")
            
            self.logger.log("="*70 + "\n")
            
        except Exception as e:
            self.logger.log(f"[FATAL] {str(e)}")
            self.logger.log(traceback.format_exc())
    
    def generate_outputs(self):
        """Generate CSV and JSON outputs"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV output
        csv_file = Config.OUTPUT_DIR / f'BACKTEST_WEEKLY_PHASE3_2019_{timestamp}.csv'
        if self.portfolio.monthly_results:
            df = pd.DataFrame(self.portfolio.monthly_results)
            df.to_csv(csv_file, index=False)
            self.logger.log(f"[OK] CSV: {csv_file.name}")
        
        # Trades CSV
        trades_file = Config.OUTPUT_DIR / f'BACKTEST_TRADES_PHASE3_2019_{timestamp}.csv'
        if self.portfolio.trades:
            df_trades = pd.DataFrame(self.portfolio.trades)
            df_trades.to_csv(trades_file, index=False)
            self.logger.log(f"[OK] Trades: {trades_file.name}")
        
        # JSON output
        json_file = Config.OUTPUT_DIR / f'BACKTEST_RESULTS_PHASE3_2019_{timestamp}.json'
        output = {
            'metadata': {
                'generated': timestamp,
                'strategy': 'Phase 3 - Sell at Target (Mechanical)',
                'period': '2019-01-01 to 2026-01-12',
                'initial_capital': Config.INITIAL_CAPITAL,
                'total_weeks': len(self.portfolio.monthly_results),
                'total_trades': len(self.portfolio.trades)
            },
            'monthly_results': self.portfolio.monthly_results,
            'trades': self.portfolio.trades
        }
        
        with open(json_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        self.logger.log(f"[OK] JSON: {json_file.name}")
        
        # Summary text
        summary_file = Config.OUTPUT_DIR / f'BACKTEST_SUMMARY_PHASE3_2019_{timestamp}.txt'
        with open(summary_file, 'w') as f:
            f.write("NIFTY50 BACKTEST SUMMARY (PHASE 3) - SELL AT TARGET\n")
            f.write("="*60 + "\n\n")
            f.write("Strategy: Mechanical exits when target achieved\n")
            f.write("No intelligent target improvement logic\n\n")
            f.write(f"Initial Capital: {Config.INITIAL_CAPITAL:,} INR\n")
            f.write(f"Period: 2019-01-01 to {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"Total Weeks: {len(self.portfolio.monthly_results)}\n")
            f.write(f"Total Trades: {len(self.portfolio.trades)}\n\n")
            
            if self.portfolio.monthly_results:
                final = self.portfolio.monthly_results[-1]
                f.write("FINAL RESULTS:\n")
                f.write(f"Final Capital: {final['total_value']:,.0f} INR\n")
                f.write(f"Total Profit/Loss: {final['total_pnl']:,.0f} INR\n")
                f.write(f"Return %: {final['return_percent']:.2f}%\n")
                f.write(f"Positions Open: {final['positions_count']}\n\n")
                
                f.write("WEEKLY SUMMARY (Last 50 weeks shown):\n")
                f.write("-"*60 + "\n")
                for result in self.portfolio.monthly_results[-50:]:
                    date_str = pd.Timestamp(result['date']).strftime('%Y-%m-%d')
                    f.write(f"{date_str:15} | Capital: {result['capital']:12,.0f} | PnL: {result['total_pnl']:12,.0f} | Return: {result['return_percent']:7.2f}%\n")
        
        self.logger.log(f"[OK] Summary: {summary_file.name}")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    runner = BacktestRunner(Config.INITIAL_CAPITAL)
    runner.run()
