"""
Event-Based Backtesting Simulator

Replays historical decisions and tracks outcomes.
Uses same analysis engine as live trading (no parameter optimization).
"""

from enum import Enum
from datetime import datetime
from typing import List
from stock_analysis.common.models import Snapshot


class TradeOutcome(Enum):
    """Possible outcomes for a trade."""
    SUCCESS = "success"           # Hit base target before stop loss
    PARTIAL = "partial"           # Hit some upside but then stopped out
    FAILURE = "failure"           # Hit stop loss without target
    NO_ENTRY = "no_entry"         # Price never entered buy zone


class TradeRecord:
    """Record of a single trade from snapshot to outcome."""
    
    def __init__(self, symbol: str, decision_date: datetime,
                 entry_price: float, buy_zone_lower: float, buy_zone_upper: float,
                 base_target: float, stop_loss: float):
        """
        Initialize trade record.
        
        Args:
            symbol: Stock symbol
            decision_date: Date analysis was made
            entry_price: Midpoint of buy zone
            buy_zone_lower: Lower bound of entry zone
            buy_zone_upper: Upper bound of entry zone
            base_target: Target profit price
            stop_loss: Stop loss price
        """
        self.symbol = symbol
        self.decision_date = decision_date
        self.entry_price = entry_price
        self.buy_zone_lower = buy_zone_lower
        self.buy_zone_upper = buy_zone_upper
        self.base_target = base_target
        self.stop_loss = stop_loss
        
        # Track state
        self.entry_date = None
        self.entry_actual_price = None
        self.max_drawdown = 0.0
        self.max_drawdown_pct = 0.0
        self.outcome = None
        self.outcome_date = None
        self.outcome_price = None
    
    def is_entry_triggered(self, price: float) -> bool:
        """Check if current price enters buy zone."""
        if self.entry_date is not None:
            return False  # Already entered
        
        return self.buy_zone_lower <= price <= self.buy_zone_upper
    
    def update_with_price(self, price: float, date: datetime) -> TradeOutcome:
        """
        Update trade with new price data.
        
        Returns outcome if trade completes, None if still open.
        """
        # Check if we haven't entered yet
        if self.entry_date is None:
            if self.is_entry_triggered(price):
                self.entry_date = date
                self.entry_actual_price = price
                return None
            else:
                return None
        
        # Trade is open, check for target/stop hit
        risk = self.entry_actual_price - self.stop_loss
        
        # Calculate drawdown
        drawdown = self.entry_actual_price - price
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
            self.max_drawdown_pct = (drawdown / self.entry_actual_price) * 100
        
        # Check stop loss hit
        if price <= self.stop_loss:
            self.outcome = TradeOutcome.FAILURE
            self.outcome_date = date
            self.outcome_price = price
            return TradeOutcome.FAILURE
        
        # Check base target hit
        if price >= self.base_target:
            self.outcome = TradeOutcome.SUCCESS
            self.outcome_date = date
            self.outcome_price = price
            return TradeOutcome.SUCCESS
        
        # Trade still open
        return None


class BacktestSimulator:
    """
    Event-based backtesting simulator.
    
    Replays historical snapshots and tracks trade outcomes.
    
    Process:
    1. For each snapshot (decision point):
       - If ACCUMULATE decision: Create trade record
       - Track forward through future snapshots
       - Record when target or stop loss hit
    
    2. Calculates:
       - Trade outcomes (SUCCESS/PARTIAL/FAILURE/NO_ENTRY)
       - Max drawdown from entry
       - Win rate and statistics
    
    Key principle: Same analysis engine as live (no parameter tweaking).
    
    Example:
        simulator = BacktestSimulator()
        results = simulator.simulate(snapshots)
        print(f"Win rate: {results.win_rate}%")
    """
    
    @staticmethod
    def simulate(snapshots: List[Snapshot]) -> dict:
        """
        Run backtest on list of snapshots.
        
        Args:
            snapshots: List of Snapshot objects sorted by date (oldest first)
        
        Returns:
            Dict with:
            - trades: List of TradeRecord objects with outcomes
            - stats: Performance statistics
            - win_rate: % of successful trades
            - failure_rate: % of failed trades
            - avg_drawdown: Average max drawdown
        
        Raises:
            ValueError: If snapshots invalid or not sorted
        
        Example:
            >>> results = BacktestSimulator.simulate(snapshots)
            >>> print(f"Completed {len(results['trades'])} trades")
            >>> print(f"Win rate: {results['stats']['win_rate']}%")
        """
        try:
            # Validate inputs
            if not isinstance(snapshots, list) or len(snapshots) == 0:
                raise ValueError("snapshots must be non-empty list")
            
            # Verify snapshots sorted by date
            for i in range(len(snapshots) - 1):
                if snapshots[i].snapshot_date > snapshots[i+1].snapshot_date:
                    raise ValueError("snapshots must be sorted by date (oldest first)")
            
            # Track active trades
            active_trades = []
            completed_trades = []
            
            # Process each snapshot
            for i, snapshot in enumerate(snapshots):
                # Check existing trades for completion
                trades_to_remove = []
                
                for trade in active_trades:
                    outcome = trade.update_with_price(
                        snapshot.price, snapshot.snapshot_date
                    )
                    
                    if outcome is not None:
                        completed_trades.append(trade)
                        trades_to_remove.append(trade)
                
                # Remove completed trades
                for trade in trades_to_remove:
                    active_trades.remove(trade)
                
                # Check for new entry signals
                # Only from ACCUMULATE decisions with valid analysis
                if snapshot.technical_score and snapshot.fundamental_score:
                    # Reconstruct decision logic (same as live engine)
                    fund_score = snapshot.fundamental_score.total_score
                    tech_score = snapshot.technical_score.total_score
                    
                    if (fund_score >= 60 and tech_score >= 50 and
                        snapshot.price >= snapshot.indicators.dma_200):
                        
                        # Would create trade, but we need buy_zone and invalidation
                        # from the analysis (which snapshot should contain)
                        # For now, we skip creating new trades in simulator
                        # since Snapshot doesn't store those yet
                        pass
            
            # Compile results
            all_trades = completed_trades + active_trades
            
            stats = BacktestSimulator._calculate_statistics(all_trades)
            
            return {
                "trades": all_trades,
                "stats": stats,
                "win_rate": stats["win_rate"],
                "failure_rate": stats["failure_rate"],
                "avg_drawdown": stats["avg_drawdown"]
            }
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error running backtest: {str(e)}")
    
    @staticmethod
    def simulate_with_decisions(snapshots: List[Snapshot],
                               buy_zones: List,
                               targets: List,
                               invalidations: List) -> dict:
        """
        Run backtest with explicit buy zones, targets, invalidations.
        
        Args:
            snapshots: List of Snapshot objects (sorted by date)
            buy_zones: Parallel list of BuyZone objects
            targets: Parallel list of Targets objects
            invalidations: Parallel list of Invalidation objects
        
        Returns:
            Dict with trade outcomes and statistics
        
        Raises:
            ValueError: If lists have different lengths or invalid data
        """
        try:
            if not (len(snapshots) == len(buy_zones) == 
                   len(targets) == len(invalidations)):
                raise ValueError("All lists must have equal length")
            
            # Track active trades
            active_trades = []
            completed_trades = []
            
            # Process each snapshot
            for i, snapshot in enumerate(snapshots):
                buy_zone = buy_zones[i]
                target = targets[i]
                invalidation = invalidations[i]
                
                if buy_zone is None or target is None or invalidation is None:
                    continue  # Skip this snapshot
                
                # Check existing trades
                trades_to_remove = []
                
                for trade in active_trades:
                    outcome = trade.update_with_price(
                        snapshot.price, snapshot.snapshot_date
                    )
                    
                    if outcome is not None:
                        completed_trades.append(trade)
                        trades_to_remove.append(trade)
                
                for trade in trades_to_remove:
                    active_trades.remove(trade)
                
                # Create new trade from decision
                entry_price = (buy_zone.lower_bound + buy_zone.upper_bound) / 2.0
                
                trade = TradeRecord(
                    symbol=snapshot.symbol,
                    decision_date=snapshot.snapshot_date,
                    entry_price=entry_price,
                    buy_zone_lower=buy_zone.lower_bound,
                    buy_zone_upper=buy_zone.upper_bound,
                    base_target=target.base_target,
                    stop_loss=invalidation.hard_stop_price
                )
                
                # Check if entry triggered immediately
                if trade.is_entry_triggered(snapshot.price):
                    trade.entry_date = snapshot.snapshot_date
                    trade.entry_actual_price = snapshot.price
                
                active_trades.append(trade)
            
            # Compile results
            all_trades = completed_trades + active_trades
            stats = BacktestSimulator._calculate_statistics(all_trades)
            
            return {
                "trades": all_trades,
                "stats": stats,
                "win_rate": stats["win_rate"],
                "failure_rate": stats["failure_rate"],
                "avg_drawdown": stats["avg_drawdown"]
            }
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error running backtest with decisions: {str(e)}")
    
    @staticmethod
    def _calculate_statistics(trades: List[TradeRecord]) -> dict:
        """Calculate backtest statistics."""
        
        if len(trades) == 0:
            return {
                "total_trades": 0,
                "successful": 0,
                "failed": 0,
                "no_entry": 0,
                "win_rate": 0.0,
                "failure_rate": 0.0,
                "avg_drawdown": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0
            }
        
        successful = [t for t in trades if t.outcome == TradeOutcome.SUCCESS]
        failed = [t for t in trades if t.outcome == TradeOutcome.FAILURE]
        no_entry = [t for t in trades if t.outcome == TradeOutcome.NO_ENTRY]
        entered_trades = [t for t in trades if t.entry_date is not None]
        
        win_rate = (len(successful) / len(entered_trades) * 100) if entered_trades else 0.0
        failure_rate = (len(failed) / len(entered_trades) * 100) if entered_trades else 0.0
        
        avg_drawdown = 0.0
        if entered_trades:
            avg_drawdown = sum(t.max_drawdown_pct for t in entered_trades) / len(entered_trades)
        
        avg_win = 0.0
        if successful:
            avg_win = sum((t.outcome_price - t.entry_actual_price) / t.entry_actual_price * 100
                         for t in successful) / len(successful)
        
        avg_loss = 0.0
        if failed:
            avg_loss = sum((t.entry_actual_price - t.outcome_price) / t.entry_actual_price * 100
                          for t in failed) / len(failed)
        
        return {
            "total_trades": len(trades),
            "successful": len(successful),
            "failed": len(failed),
            "no_entry": len(no_entry),
            "entered_trades": len(entered_trades),
            "win_rate": round(win_rate, 2),
            "failure_rate": round(failure_rate, 2),
            "avg_drawdown": round(avg_drawdown, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2)
        }
