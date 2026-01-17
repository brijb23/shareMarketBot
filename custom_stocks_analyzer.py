#!/usr/bin/env python3
"""
CUSTOM STOCKS ANALYZER
Analyzes any stocks you specify and generates detailed trading reports
Same format as weekly automation - just for custom stock lists!
"""

import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys
import json
from datetime import datetime
import traceback

# ============================================================================
# CUSTOM LOGGER (Pure ASCII - No Unicode)
# ============================================================================

class CustomLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"{timestamp} | {message}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')

# ============================================================================
# DATA COLLECTOR
# ============================================================================

class DataCollector:
    def __init__(self, logger):
        self.logger = logger
        
    def fetch_stock_data(self, ticker, period='1y'):
        """Fetch 1 year of historical data for a stock"""
        try:
            # Ensure ticker has .NS extension
            if not ticker.endswith('.NS'):
                ticker = ticker + '.NS'
            
            data = yf.download(ticker, period=period, progress=False, 
                             threads=False, timeout=30)
            
            if data is None or data.empty or len(data) < 50:
                return None
            
            return data
        except Exception as e:
            return None
    
    def fetch_all(self, stocks):
        """Fetch data for all stocks"""
        self.logger.log(f"Fetching {len(stocks)} stocks...")
        
        all_data = {}
        successful = 0
        
        for ticker in stocks:
            data = self.fetch_stock_data(ticker)
            if data is not None and not data.empty:
                # Ensure ticker has .NS extension for consistency
                key = ticker if ticker.endswith('.NS') else ticker + '.NS'
                all_data[key] = data
                successful += 1
                self.logger.log(f"  [OK] {key}")
            else:
                self.logger.log(f"  [SKIP] {ticker} - No data")
        
        self.logger.log(f"[OK] {successful}/{len(stocks)} stocks fetched")
        return all_data

# ============================================================================
# ANALYSIS ENGINE (Phase 19.2)
# ============================================================================

class AnalysisEngine:
    def __init__(self, logger):
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
            ten_days_ago = float(close.iloc[-10])
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
        """Calculate Average True Range for entry/stop/target pricing"""
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
        """Generate BUY/HOLD/SELL signal based on trend and momentum"""
        if trend > 0.5 and momentum > 1.0:
            return "BUY"
        elif trend < -0.5 and momentum < -1.0:
            return "SELL"
        else:
            return "HOLD"
    
    def analyze(self, all_data):
        """Perform Phase 19.2 analysis on all stocks"""
        self.logger.log("[STEP 2] PHASE 19.2 TRADING ANALYSIS")
        
        results = {}
        
        for ticker, data in all_data.items():
            try:
                current_price = float(data['Close'].iloc[-1])
                trend = self.calc_trend(data)
                momentum = self.calc_momentum(data)
                volatility = self.calc_volatility(data)
                atr = self.calc_atr(data)
                signal = self.generate_signal(trend, momentum)
                
                # Calculate Entry, Stop, Target based on ATR
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
                else:  # HOLD
                    entry_low = current_price - atr
                    entry_high = current_price + atr
                    target = current_price + (atr * 1.5)
                    stop_loss = current_price - (atr * 1.5)
                
                # Calculate RR Ratio
                rr_ratio = abs(target - current_price) / abs(stop_loss - current_price) if stop_loss != current_price else 0
                
                # Confidence
                confidence = min(95, max(50, (abs(trend) + abs(momentum)) / 2 + 40))
                
                results[ticker] = {
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
                    'rr_ratio': round(rr_ratio, 2),
                    'confidence': round(confidence, 1)
                }
            except Exception as e:
                self.logger.log(f"  [ERROR] {ticker} - {str(e)}")
        
        self.logger.log(f"[OK] Analyzed {len(results)} stocks")
        return results

# ============================================================================
# PHASE 19.3 ENHANCER
# ============================================================================

class Phase19_3Enhancer:
    def __init__(self, logger):
        self.logger = logger
    
    def enhance(self, results):
        """Apply Phase 19.3 enhancements to results"""
        self.logger.log("[STEP 3] PHASE 19.3 OUTPUT ENHANCEMENT")
        
        enhanced = {}
        
        for ticker, metrics in results.items():
            entry_low = metrics['entry_low']
            entry_high = metrics['entry_high']
            signal = metrics['signal']
            volatility = metrics['volatility']
            
            # BUY Entry Quality Zones
            if signal == "BUY":
                buy_range_low = entry_low
                buy_range_high = entry_high
                span = buy_range_high - buy_range_low
                buy_optimal_upper = buy_range_low + (span * 0.40)
                
                entry_quality = {
                    'optimal': f"{buy_range_low:.2f} - {buy_optimal_upper:.2f}",
                    'extended': f"{buy_optimal_upper:.2f} - {buy_range_high:.2f}"
                }
            else:
                entry_quality = None
            
            # Risk Context
            if volatility <= 12:
                risk_context = "LOW"
            elif volatility <= 20:
                risk_context = "NORMAL"
            else:
                risk_context = "ELEVATED"
            
            # HOLD Rationale
            if signal == "HOLD":
                trend = metrics['trend']
                momentum = metrics['momentum']
                
                if abs(trend) < 0.5 and abs(momentum) < 1.0:
                    rationale = "Mixed signals - waiting for clarity"
                elif trend > 0 and momentum < 0:
                    rationale = "Trend positive but momentum weak - consolidation"
                elif trend < 0 and momentum > 0:
                    rationale = "Trend negative but momentum recovering - recovery phase"
                else:
                    rationale = "Conflicting indicators - hold position"
            else:
                rationale = None
            
            enhanced[ticker] = {
                **metrics,
                'entry_quality': entry_quality,
                'risk_context': risk_context,
                'hold_rationale': rationale
            }
        
        self.logger.log(f"[OK] Enhanced {len(enhanced)} signals")
        return enhanced

# ============================================================================
# OUTPUT GENERATOR
# ============================================================================

class OutputGenerator:
    def __init__(self, logger, timestamp):
        self.logger = logger
        self.timestamp = timestamp
        self.output_dir = 'nifty50_analysis'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_all(self, results):
        """Generate all output formats"""
        self.logger.log("[STEP 4] GENERATING OUTPUT FILES")
        
        # CSV
        csv_file = self._generate_csv(results)
        
        # JSON
        json_file = self._generate_json(results)
        
        # Markdown
        md_file = self._generate_markdown(results)
        
        # Text
        txt_file = self._generate_text(results)
        
        return csv_file, json_file, md_file, txt_file
    
    def _generate_csv(self, results):
        """Generate CSV output"""
        rows = []
        for ticker, data in results.items():
            row = {
                'Stock': ticker,
                'Price': data['current_price'],
                'Trend%': data['trend'],
                'Momentum%': data['momentum'],
                'Volatility%': data['volatility'],
                'ATR': data['atr'],
                'Signal': data['signal'],
                'Entry_Low': data['entry_low'],
                'Entry_High': data['entry_high'],
                'Target': data['target'],
                'Stop_Loss': data['stop_loss'],
                'RR_Ratio': data['rr_ratio'],
                'Confidence%': data['confidence'],
                'Risk_Context': data['risk_context']
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        filename = f"{self.output_dir}/CUSTOM_ANALYSIS_{self.timestamp}.csv"
        df.to_csv(filename, index=False)
        self.logger.log(f"[OK] CSV: {filename}")
        return filename
    
    def _generate_json(self, results):
        """Generate JSON output"""
        output = {
            'metadata': {
                'generated': self.timestamp,
                'total_stocks': len(results),
                'signal_summary': self._get_signal_summary(results)
            },
            'stocks': results
        }
        
        filename = f"{self.output_dir}/CUSTOM_ANALYSIS_{self.timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        self.logger.log(f"[OK] JSON: {filename}")
        return filename
    
    def _generate_markdown(self, results):
        """Generate Markdown report"""
        md = f"# CUSTOM STOCKS ANALYSIS REPORT\n"
        md += f"**Generated:** {self.timestamp}\n"
        md += f"**Total Stocks:** {len(results)}\n\n"
        
        # Summary
        buy_count = sum(1 for r in results.values() if r['signal'] == 'BUY')
        hold_count = sum(1 for r in results.values() if r['signal'] == 'HOLD')
        sell_count = sum(1 for r in results.values() if r['signal'] == 'SELL')
        
        md += f"## SIGNAL SUMMARY\n"
        md += f"- **BUY:** {buy_count} stocks\n"
        md += f"- **HOLD:** {hold_count} stocks\n"
        md += f"- **SELL:** {sell_count} stocks\n\n"
        
        # BUY Signals
        if buy_count > 0:
            md += f"## BUY SIGNALS ({buy_count})\n\n"
            for ticker, data in results.items():
                if data['signal'] == 'BUY':
                    md += f"### {ticker}\n"
                    md += f"- **Current Price:** {data['current_price']}\n"
                    md += f"- **Trend:** {data['trend']}%\n"
                    md += f"- **Momentum:** {data['momentum']}%\n"
                    md += f"- **Entry Optimal:** {data['entry_quality']['optimal']}\n"
                    md += f"- **Entry Extended:** {data['entry_quality']['extended']}\n"
                    md += f"- **Target:** {data['target']}\n"
                    md += f"- **Stop Loss:** {data['stop_loss']}\n"
                    md += f"- **Risk Context:** {data['risk_context']}\n"
                    md += f"- **Confidence:** {data['confidence']}%\n\n"
        
        # HOLD Signals
        if hold_count > 0:
            md += f"## HOLD SIGNALS ({hold_count})\n\n"
            for ticker, data in results.items():
                if data['signal'] == 'HOLD':
                    md += f"### {ticker}\n"
                    md += f"- **Current Price:** {data['current_price']}\n"
                    md += f"- **Trend:** {data['trend']}%\n"
                    md += f"- **Momentum:** {data['momentum']}%\n"
                    md += f"- **Volatility:** {data['volatility']}%\n"
                    md += f"- **Risk Context:** {data['risk_context']}\n"
                    md += f"- **Reason:** {data['hold_rationale']}\n\n"
        
        # SELL Signals
        if sell_count > 0:
            md += f"## SELL SIGNALS ({sell_count})\n\n"
            for ticker, data in results.items():
                if data['signal'] == 'SELL':
                    md += f"### {ticker}\n"
                    md += f"- **Current Price:** {data['current_price']}\n"
                    md += f"- **Trend:** {data['trend']}%\n"
                    md += f"- **Momentum:** {data['momentum']}%\n"
                    md += f"- **Target:** {data['target']}\n"
                    md += f"- **Stop Loss:** {data['stop_loss']}\n"
                    md += f"- **Risk Context:** {data['risk_context']}\n"
                    md += f"- **Confidence:** {data['confidence']}%\n\n"
        
        filename = f"{self.output_dir}/CUSTOM_ANALYSIS_{self.timestamp}_REPORT.md"
        with open(filename, 'w') as f:
            f.write(md)
        self.logger.log(f"[OK] Report: {filename}")
        return filename
    
    def _generate_text(self, results):
        """Generate text summary"""
        txt = f"CUSTOM STOCKS ANALYSIS SUMMARY\n"
        txt += f"{'='*60}\n"
        txt += f"Generated: {self.timestamp}\n"
        txt += f"Total Stocks Analyzed: {len(results)}\n\n"
        
        # Summary
        buy_count = sum(1 for r in results.values() if r['signal'] == 'BUY')
        hold_count = sum(1 for r in results.values() if r['signal'] == 'HOLD')
        sell_count = sum(1 for r in results.values() if r['signal'] == 'SELL')
        
        txt += f"SIGNAL SUMMARY:\n"
        txt += f"  [BUY]  {buy_count} stocks\n"
        txt += f"  [HOLD] {hold_count} stocks\n"
        txt += f"  [SELL] {sell_count} stocks\n\n"
        
        # Quick list
        txt += f"QUICK STOCK LIST:\n"
        for ticker, data in sorted(results.items()):
            txt += f"  {ticker:12} [{data['signal']:4}] Price: {data['current_price']:8.2f} Trend: {data['trend']:7.2f}% Confidence: {data['confidence']:5.1f}%\n"
        
        filename = f"{self.output_dir}/CUSTOM_ANALYSIS_{self.timestamp}_SUMMARY.txt"
        with open(filename, 'w') as f:
            f.write(txt)
        self.logger.log(f"[OK] Summary: {filename}")
        return filename
    
    def _get_signal_summary(self, results):
        """Get signal counts"""
        return {
            'BUY': sum(1 for r in results.values() if r['signal'] == 'BUY'),
            'HOLD': sum(1 for r in results.values() if r['signal'] == 'HOLD'),
            'SELL': sum(1 for r in results.values() if r['signal'] == 'SELL')
        }

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class Orchestrator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/CUSTOM_LOG_{self.timestamp}.txt"
        self.logger = CustomLogger(self.log_file)
        
        self.data_collector = DataCollector(self.logger)
        self.analysis_engine = AnalysisEngine(self.logger)
        self.enhancer = Phase19_3Enhancer(self.logger)
        self.output_generator = OutputGenerator(self.logger, self.timestamp)
    
    def load_stocks_from_file(self, filename='custom_stocks_list.txt'):
        """Load stock list from configuration file"""
        self.logger.log(f"[STEP 0] LOADING STOCK LIST FROM {filename}")
        
        if not os.path.exists(filename):
            self.logger.log(f"[ERROR] File not found: {filename}")
            return []
        
        stocks = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        stocks.append(line)
            
            self.logger.log(f"[OK] Loaded {len(stocks)} stocks")
            for stock in stocks:
                self.logger.log(f"     - {stock}")
            
            return stocks
        except Exception as e:
            self.logger.log(f"[ERROR] Failed to read file: {str(e)}")
            return []
    
    def run(self):
        """Execute the complete analysis pipeline"""
        try:
            self.logger.log("\n" + "="*70)
            self.logger.log("CUSTOM STOCKS ANALYZER - STARTING")
            self.logger.log("="*70)
            
            start_time = datetime.now()
            
            # Step 0: Load stocks
            stocks = self.load_stocks_from_file()
            if not stocks:
                self.logger.log("[ERROR] No stocks to analyze")
                return
            
            # Step 1: Collect data
            self.logger.log("[STEP 1] COLLECTING MARKET DATA")
            all_data = self.data_collector.fetch_all(stocks)
            if not all_data:
                self.logger.log("[ERROR] No data collected")
                return
            
            # Step 2: Analyze
            results = self.analysis_engine.analyze(all_data)
            
            # Step 3: Enhance
            enhanced = self.enhancer.enhance(results)
            
            # Step 4: Generate outputs
            self.output_generator.generate_all(enhanced)
            
            # Summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.log("\n" + "="*70)
            self.logger.log("CUSTOM STOCKS ANALYZER - COMPLETED SUCCESSFULLY")
            self.logger.log("="*70)
            
            signal_summary = self.output_generator._get_signal_summary(enhanced)
            self.logger.log(f"\nSignal Summary:")
            self.logger.log(f"  [BUY]  {signal_summary['BUY']} stocks")
            self.logger.log(f"  [HOLD] {signal_summary['HOLD']} stocks")
            self.logger.log(f"  [SELL] {signal_summary['SELL']} stocks")
            self.logger.log(f"\nExecution Time: {duration:.1f}s")
            self.logger.log(f"Log File: {self.log_file}")
            self.logger.log("="*70 + "\n")
            
        except Exception as e:
            self.logger.log(f"[FATAL] {str(e)}")
            self.logger.log(traceback.format_exc())

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    orchestrator = Orchestrator()
    orchestrator.run()
