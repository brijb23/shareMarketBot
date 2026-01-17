"""
Stock Analysis Engine - Main Entry Point

Modular orchestration of long-term stock analysis:
- SNAPSHOT: Single-stock analysis (fundamental, technical, levels, decision)
- BACKTEST: Historical simulation with trade tracking
- SCAN: Universe screening with buy signal detection

Usage:
    python main.py --mode snapshot --symbol TCS.NS --as-of 2025-12-31
    python main.py --mode backtest --symbol INFY.NS --start 2024-01-01 --end 2025-12-31
    python main.py --mode scan --universe NSE_LARGE_CAP
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Optional

# Data providers
from stock_analysis.data.csv_price_provider import CSVPriceProvider
from stock_analysis.data.fundamentals_csv_provider import CSVFundamentalsProvider

# Analysis engines
from stock_analysis.analysis.indicators import IndicatorEngine
from stock_analysis.analysis.fundamentals import FundamentalAnalyzer
from stock_analysis.analysis.technicals import TechnicalAnalyzer
from stock_analysis.analysis.decision_engine import DecisionEngine

# Price levels
from stock_analysis.levels.buy_zone import BuyZoneCalculator
from stock_analysis.levels.invalidation import InvalidationCalculator
from stock_analysis.levels.targets import TargetCalculator

# Backtest & snapshots
from stock_analysis.backtest.snapshot import SnapshotGenerator
from stock_analysis.backtest.simulator import BacktestSimulator
from stock_analysis.backtest.evaluator import BacktestEvaluator
from stock_analysis.backtest.metrics import BacktestMetrics

# Common
from stock_analysis.common.models import Snapshot
from stock_analysis.common.utils import ReportPrinter


# ============================================================================
# ARGUMENT VALIDATION
# ============================================================================

def validate_snapshot_args(args) -> None:
    """Validate required arguments for SNAPSHOT mode."""
    if not args.symbol:
        raise ValueError("SNAPSHOT mode requires: --symbol SYMBOL")
    if not args.as_of:
        raise ValueError("SNAPSHOT mode requires: --as-of DATE (YYYY-MM-DD)")
    
    try:
        datetime.strptime(args.as_of, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {args.as_of}. Use YYYY-MM-DD")


def validate_backtest_args(args) -> None:
    """Validate required arguments for BACKTEST mode."""
    if not args.symbol:
        raise ValueError("BACKTEST mode requires: --symbol SYMBOL")
    if not args.start:
        raise ValueError("BACKTEST mode requires: --start DATE (YYYY-MM-DD)")
    if not args.end:
        raise ValueError("BACKTEST mode requires: --end DATE (YYYY-MM-DD)")
    
    try:
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
        end_date = datetime.strptime(args.end, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    if start_date >= end_date:
        raise ValueError("Start date must be before end date")


def validate_scan_args(args) -> None:
    """Validate required arguments for SCAN mode."""
    if not args.universe:
        raise ValueError("SCAN mode requires: --universe UNIVERSE_NAME")


# ============================================================================
# MODE: SNAPSHOT
# ============================================================================

def mode_snapshot(args) -> None:
    """
    Generate analysis snapshot for single stock.
    
    Workflow:
    1. Initialize providers
    2. Generate snapshot (prices, fundamentals, indicators)
    3. Calculate scores (fundamental, technical)
    4. Calculate levels (buy zone, invalidation, targets)
    5. Make decision
    6. Print report
    """
    print(f"\n{'='*70}")
    print(f"SNAPSHOT MODE: {args.symbol}")
    print(f"{'='*70}\n")
    
    as_of_date = datetime.strptime(args.as_of, "%Y-%m-%d")
    
    # Initialize providers
    print("Initializing providers...")
    price_provider = CSVPriceProvider()
    fund_provider = CSVFundamentalsProvider()
    
    # Generate snapshot
    print(f"Generating snapshot as of {as_of_date}...")
    snapshot_gen = SnapshotGenerator(price_provider, fund_provider)
    snapshot = snapshot_gen.generate_snapshot(args.symbol, as_of_date)
    
    if not snapshot:
        print(f"ERROR: Could not generate snapshot for {args.symbol} on {as_of_date}")
        return
    
    # Print detailed report
    print("\n" + "="*70)
    print("ANALYSIS SNAPSHOT")
    print("="*70)
    
    ReportPrinter.print_snapshot(snapshot)
    
    print("\n" + "="*70)
    print("END OF SNAPSHOT")
    print("="*70 + "\n")


# ============================================================================
# MODE: BACKTEST
# ============================================================================

def mode_backtest(args) -> None:
    """
    Run historical backtest simulation.
    
    Workflow:
    1. Parse date range
    2. Generate snapshots at specified frequency
    3. Run BacktestSimulator
    4. Calculate metrics and print report
    """
    print(f"\n{'='*70}")
    print(f"BACKTEST MODE: {args.symbol}")
    print(f"{'='*70}\n")
    
    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")
    frequency = args.frequency or "quarterly"
    
    print(f"Period: {start_date} to {end_date}")
    print(f"Frequency: {frequency}\n")
    
    # Initialize providers
    print("Initializing providers...")
    price_provider = CSVPriceProvider()
    fund_provider = CSVFundamentalsProvider()
    
    # Generate snapshots at specified frequency
    print(f"Generating snapshots ({frequency})...")
    snapshots = _generate_snapshots_at_frequency(
        symbol=args.symbol,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        price_provider=price_provider,
        fund_provider=fund_provider
    )
    
    if not snapshots:
        print(f"ERROR: Could not generate snapshots for {args.symbol}")
        return
    
    print(f"Generated {len(snapshots)} snapshots\n")
    
    # Generate levels (buy zones, targets, invalidations) for each snapshot
    print("Generating trading levels...")
    from stock_analysis.common.models import BuyZone, Targets, Invalidation
    from decimal import Decimal
    
    snapshots_with_levels = []
    buy_zones_list = []
    targets_list = []
    invalidations_list = []
    
    for snapshot in snapshots:
        try:
            # Create simple synthetic levels based on current price
            entry_price = float(snapshot.price_at_date)
            
            # Create buy zone
            zone_low = Decimal(str(entry_price * 0.98))
            zone_high = Decimal(str(entry_price))
            zone_mid = (zone_low + zone_high) / 2
            
            current_price = Decimal(str(entry_price))
            is_in_zone = zone_low <= current_price <= zone_high
            percent_into_zone = float((current_price - zone_low) / (zone_high - zone_low) * 100) if zone_high > zone_low else 0
            
            buy_zone = BuyZone(
                zone_high=zone_high,
                zone_low=zone_low,
                zone_mid=zone_mid,
                current_price=current_price,
                is_in_zone=is_in_zone,
                percent_into_zone=percent_into_zone,
                basis="Pullback support (2% below entry)",
                confidence=70.0,
                volume_at_zone="normal",
                holding_period="Weeks to months"
            )
            
            # Create targets: 3% and 5% above entry
            targets = Targets(
                target1=Decimal(str(entry_price * 1.03)),
                target2=Decimal(str(entry_price * 1.05)),
                target3=None
            )
            
            # Create invalidation: 2% below buy zone
            invalidation = Invalidation(
                invalidation_level=Decimal(str(entry_price * 0.96))
            )
            
            snapshots_with_levels.append(snapshot)
            buy_zones_list.append(buy_zone)
            targets_list.append(targets)
            invalidations_list.append(invalidation)
        except Exception as e:
            print(f"WARNING: Could not create levels for snapshot on {snapshot.snapshot_date}: {e}")
            continue
    
    if not snapshots_with_levels:
        print("ERROR: Could not generate trading levels for any snapshots")
        return
    
    print(f"Generated levels for {len(snapshots_with_levels)} snapshots\n")
    
    # Run backtest simulator
    print("Running backtest simulation...")
    simulator = BacktestSimulator()
    trades = simulator.simulate_with_decisions(snapshots_with_levels, buy_zones_list, targets_list, invalidations_list)
    
    if not trades:
        print("No trades generated during backtest")
        return
    
    # Evaluate and print metrics
    print("\n" + "="*70)
    print("BACKTEST RESULTS")
    print("="*70)
    
    evaluator = BacktestEvaluator()
    metrics = evaluator.evaluate_trades(trades)
    
    metrics_printer = BacktestMetrics()
    report = metrics_printer.generate_report(trades)
    print(report)
    
    print("="*70)
    print("END OF BACKTEST")
    print("="*70 + "\n")


def _generate_snapshots_at_frequency(
    symbol: str,
    start_date,
    end_date,
    frequency: str,
    price_provider,
    fund_provider
) -> List[Snapshot]:
    """
    Generate snapshots at specified frequency.
    
    Frequency options:
    - daily: Every business day
    - weekly: Every Friday
    - monthly: Last business day of month
    - quarterly: Last business day of quarter
    """
    snapshot_gen = SnapshotGenerator(price_provider, fund_provider)
    snapshots = []
    
    current_date = start_date
    
    while current_date <= end_date:
        # Determine if we should take a snapshot at current_date
        should_snapshot = False
        
        if frequency == "daily":
            should_snapshot = True
        elif frequency == "weekly":
            # Friday = 4
            should_snapshot = (current_date.weekday() == 4)
        elif frequency == "monthly":
            # Last day of month
            next_date = current_date + timedelta(days=1)
            should_snapshot = (next_date.month != current_date.month)
        elif frequency == "quarterly":
            # Last day of quarter (Mar 31, Jun 30, Sep 30, Dec 31)
            should_snapshot = (
                (current_date.month in [3, 6, 9, 12]) and
                ((current_date + timedelta(days=1)).month != current_date.month)
            )
        
        if should_snapshot:
            snapshot = snapshot_gen.generate_snapshot(symbol, current_date)
            if snapshot:
                snapshots.append(snapshot)
        
        current_date += timedelta(days=1)
    
    return snapshots


# ============================================================================
# MODE: SCAN
# ============================================================================

def mode_scan(args) -> None:
    """
    Scan universe for buy signals.
    
    Workflow:
    1. Load universe (list of symbols)
    2. Generate snapshot for each symbol
    3. Filter for ACCUMULATE decisions
    4. Print shortlist with scores and reasons
    """
    print(f"\n{'='*70}")
    print(f"SCAN MODE: Universe = {args.universe}")
    print(f"{'='*70}\n")
    
    as_of_date = datetime.now()
    
    # Load universe
    print("Loading universe...")
    symbols = _load_universe(args.universe)
    
    if not symbols:
        print(f"ERROR: Could not load universe {args.universe}")
        return
    
    print(f"Loaded {len(symbols)} symbols\n")
    
    # Initialize providers
    print("Initializing providers...")
    price_provider = CSVPriceProvider()
    fund_provider = CSVFundamentalsProvider()
    
    # Generate snapshots and filter
    print(f"Scanning {len(symbols)} symbols...")
    snapshot_gen = SnapshotGenerator(price_provider, fund_provider)
    
    accumulate_signals = []
    
    for i, symbol in enumerate(symbols, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(symbols)}")
        
        try:
            snapshot = snapshot_gen.generate_snapshot(symbol, as_of_date)
            
            if snapshot and snapshot.decision and snapshot.decision.action.name == "ACCUMULATE":
                accumulate_signals.append(snapshot)
        
        except Exception as e:
            # Silently skip symbols that fail
            continue
    
    # Print shortlist
    print("\n" + "="*70)
    print(f"SCAN RESULTS: {len(accumulate_signals)} BUY SIGNALS")
    print("="*70)
    
    if not accumulate_signals:
        print("No buy signals found in universe")
        return
    
    # Sort by fundamental score (descending)
    accumulate_signals.sort(
        key=lambda s: s.fundamental_score.score if s.fundamental_score else 0,
        reverse=True
    )
    
    # Print each signal
    for i, snapshot in enumerate(accumulate_signals, 1):
        print(f"\n{i}. {snapshot.symbol}")
        print(f"   Fundamental Score: {snapshot.fundamental_score.score if snapshot.fundamental_score else 'N/A'}")
        print(f"   Technical Score: {snapshot.technical_score.score if snapshot.technical_score else 'N/A'}")
        print(f"   Current Price: {snapshot.latest_price}")
        print(f"   200 DMA: {snapshot.indicators.dma_200 if snapshot.indicators else 'N/A'}")
        
        if snapshot.buy_zone:
            print(f"   Buy Zone: {snapshot.buy_zone.lower:.2f} - {snapshot.buy_zone.upper:.2f}")
        
        if snapshot.targets:
            print(f"   Base Target: {snapshot.targets.base_target:.2f}")
        
        if snapshot.invalidation:
            print(f"   Stop Loss: {snapshot.invalidation.hard_stop:.2f}")
        
        if snapshot.decision:
            print(f"   Confidence: {snapshot.decision.confidence}%")
    
    print("\n" + "="*70)
    print("END OF SCAN")
    print("="*70 + "\n")


def _load_universe(universe_name: str) -> List[str]:
    """
    Load stock universe by name.
    
    Supported universes:
    - NIFTY_50: NIFTY 50 index constituents (50 stocks)
    - NSE_LARGE_CAP: 50 largest NSE stocks
    - NSE_MID_CAP: Mid-cap stocks
    - NSE_SMALL_CAP: Small-cap stocks
    - CUSTOM: Custom list (modify list below)
    - NSE_PICKS: Our selected stocks for analysis
    """
    universes = {
        "NIFTY_50": [
            'RELIANCE.NS', 'TCS.NS', 'INFOSY.NS', 'HDFC.NS', 'ICICIBANK.NS',
            'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'WIPRO.NS', 'SBIN.NS',
            'HCLTECH.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS', 'TITAN.NS', 'NESTLEIND.NS',
            'SUNPHARMA.NS', 'BAJAJFINSV.NS', 'ASIANPAINT.NS', 'ISBANK.NS', 'ULTRACEMCO.NS',
            'BHARTIARTL.NS', 'PGHH.NS', 'JSWSTEEL.NS', 'ADANIPORTS.NS', 'POWERGRID.NS',
            'INDIGO.NS', 'GRASIM.NS', 'HDFCBANK.NS', 'TATACONSUM.NS', 'MKRTL.NS',
            'NTPC.NS', 'ADANIENT.NS', 'ONGC.NS', 'IOCL.NS', 'COALINDIA.NS',
            'LUPIN.NS', 'DIVISLAB.NS', 'TECHM.NS', 'EICHERMOT.NS', 'LTIM.NS',
            'AUROPHARMA.NS', 'CIPLA.NS', 'HINDOILCORP.NS', 'SRTRANSFIN.NS', 'BPCL.NS',
            'M&MFIN.NS', 'BANKBARODA.NS', 'APOLLOHOSP.NS', 'VEDL.NS'
        ],
        "NSE_LARGE_CAP": [
            "TCS.NS", "INFY.NS", "WIPRO.NS", "HCL-TECH.NS", "RELIANCE.NS",
            "HDFC.NS", "ICICIBANK.NS", "SBIN.NS", "MARUTI.NS", "BAJAJ-AUTO.NS",
            "BHARTIARTL.NS", "SUNPHARMA.NS", "DMART.NS", "NESTLEIND.NS",
            "LTIM.NS", "LT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "NTPC.NS",
            "POWERGRID.NS"
        ],
        "NSE_MID_CAP": [
            "APOLLOHOSP.NS", "LUPIN.NS", "CIPLA.NS", "DIVISLAB.NS", "TITAN.NS",
            "ASIANPAINT.NS", "ITC.NS", "UPL.NS", "MONSANTO.NS", "GODREJCP.NS"
        ],
        "NSE_SMALL_CAP": [
            "CDSL.NS", "IRFC.NS", "CANBK.NS", "BANKNIFTY.NS", "IDFCBANK.NS",
            "AUBANK.NS", "AXISBANK.NS", "YESBANK.NS", "INDIGO.NS", "SPICEJET.NS"
        ],
        "CUSTOM": [
            "TCS.NS", "INFY.NS", "WIPRO.NS"
        ],
        "NSE_PICKS": [
            "ARKADE.NS", "CGPOWER.NS", "CMSINFO.NS", "Nuvama.NS", "TCS.NS"
        ]
    }
    
    return universes.get(universe_name, [])


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="Stock Analysis Engine",
        description="Modular long-term stock analysis system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode snapshot --symbol TCS.NS --as-of 2025-12-31
  python main.py --mode backtest --symbol INFY.NS --start 2024-01-01 --end 2025-12-31
  python main.py --mode scan --universe NSE_LARGE_CAP
        """
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["snapshot", "backtest", "scan"],
        required=True,
        help="Analysis mode (snapshot/backtest/scan)"
    )
    
    parser.add_argument(
        "--symbol",
        type=str,
        help="Stock symbol (e.g., TCS.NS) - required for snapshot & backtest"
    )
    
    parser.add_argument(
        "--as-of",
        type=str,
        dest="as_of",
        help="Snapshot date (YYYY-MM-DD) - required for snapshot"
    )
    
    parser.add_argument(
        "--start",
        type=str,
        help="Backtest start date (YYYY-MM-DD) - required for backtest"
    )
    
    parser.add_argument(
        "--end",
        type=str,
        help="Backtest end date (YYYY-MM-DD) - required for backtest"
    )
    
    parser.add_argument(
        "--frequency",
        type=str,
        choices=["daily", "weekly", "monthly", "quarterly"],
        default="quarterly",
        help="Snapshot frequency for backtest (default: quarterly)"
    )
    
    parser.add_argument(
        "--universe",
        type=str,
        help="Stock universe (NSE_LARGE_CAP/NSE_MID_CAP/NSE_SMALL_CAP/CUSTOM) - required for scan"
    )
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Validate and dispatch to appropriate mode
        if args.mode == "snapshot":
            validate_snapshot_args(args)
            mode_snapshot(args)
        
        elif args.mode == "backtest":
            validate_backtest_args(args)
            mode_backtest(args)
        
        elif args.mode == "scan":
            validate_scan_args(args)
            mode_scan(args)
    
    except ValueError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
