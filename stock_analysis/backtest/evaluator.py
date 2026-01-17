"""
Backtest Evaluator

Analyzes trade outcomes and evaluates decision quality.
Focuses on decision quality, not prediction accuracy.
"""

from typing import List
from datetime import datetime, timedelta
from stock_analysis.backtest.simulator import TradeRecord, TradeOutcome


class BacktestEvaluator:
    """
    Evaluate backtesting results and quantify decision quality.
    
    Key distinction:
    - NOT predicting if stock will go up/down
    - EVALUATING if decision framework is sound (risk/reward, stops, targets)
    
    Quality metrics:
    - Did we capture upside when entry conditions met?
    - Did we avoid large losses (stop placement)?
    - Was risk/reward ratio favorable?
    - Did max drawdown match our thesis?
    
    Example:
        evaluator = BacktestEvaluator()
        analysis = evaluator.evaluate_trades(trade_records)
        print(analysis.summary)
    """
    
    @staticmethod
    def evaluate_trades(trades: List[TradeRecord]) -> dict:
        """
        Evaluate quality of trades.
        
        Args:
            trades: List of TradeRecord objects with outcomes
        
        Returns:
            Dict with:
            - success_rate: % of successful trades
            - failure_rate: % of failed trades
            - no_entry_rate: % that never entered
            - avg_drawdown: Average max drawdown %
            - median_time_to_outcome: Median days to resolution
            - analysis: Detailed breakdown
        
        Raises:
            ValueError: If trades invalid
        
        Example:
            >>> evaluator = BacktestEvaluator()
            >>> results = evaluator.evaluate_trades(trades)
            >>> print(f"Success rate: {results['success_rate']}%")
        """
        try:
            if not isinstance(trades, list):
                raise ValueError("trades must be list of TradeRecord")
            
            if len(trades) == 0:
                return BacktestEvaluator._empty_results()
            
            # Categorize trades
            successful = [t for t in trades if t.outcome == TradeOutcome.SUCCESS]
            failed = [t for t in trades if t.outcome == TradeOutcome.FAILURE]
            no_entry = [t for t in trades if t.outcome == TradeOutcome.NO_ENTRY]
            entered = [t for t in trades if t.entry_date is not None]
            
            # Calculate rates
            total_count = len(trades)
            entered_count = len(entered)
            
            success_rate = (len(successful) / entered_count * 100) if entered_count > 0 else 0.0
            failure_rate = (len(failed) / entered_count * 100) if entered_count > 0 else 0.0
            no_entry_rate = (len(no_entry) / total_count * 100) if total_count > 0 else 0.0
            
            # Average drawdown
            avg_drawdown = 0.0
            if entered:
                avg_drawdown = sum(t.max_drawdown_pct for t in entered) / len(entered)
            
            # Median time to outcome
            median_time = BacktestEvaluator._calculate_median_time(entered)
            
            # Win/loss analysis
            win_loss = BacktestEvaluator._analyze_wins_losses(successful, failed)
            
            # Entry quality analysis
            entry_quality = BacktestEvaluator._analyze_entry_quality(entered)
            
            return {
                "success_rate": round(success_rate, 2),
                "failure_rate": round(failure_rate, 2),
                "no_entry_rate": round(no_entry_rate, 2),
                "avg_drawdown": round(avg_drawdown, 2),
                "median_time_to_outcome": median_time,
                "total_trades": total_count,
                "entered_trades": entered_count,
                "successful_trades": len(successful),
                "failed_trades": len(failed),
                "no_entry_trades": len(no_entry),
                "win_loss_analysis": win_loss,
                "entry_quality": entry_quality
            }
            
        except Exception as e:
            raise ValueError(f"Error evaluating trades: {str(e)}")
    
    @staticmethod
    def _calculate_median_time(entered: List[TradeRecord]) -> str:
        """Calculate median days to outcome."""
        if not entered:
            return "N/A"
        
        times_to_outcome = []
        for trade in entered:
            if trade.outcome_date and trade.entry_date:
                days = (trade.outcome_date - trade.entry_date).days
                times_to_outcome.append(days)
        
        if not times_to_outcome:
            return "N/A"
        
        times_to_outcome.sort()
        median = times_to_outcome[len(times_to_outcome) // 2]
        
        return f"{median} days"
    
    @staticmethod
    def _analyze_wins_losses(successful: List[TradeRecord],
                            failed: List[TradeRecord]) -> dict:
        """Analyze win/loss characteristics."""
        
        win_returns = []
        loss_returns = []
        
        for trade in successful:
            if trade.entry_actual_price and trade.outcome_price:
                ret = ((trade.outcome_price - trade.entry_actual_price) / 
                       trade.entry_actual_price * 100)
                win_returns.append(ret)
        
        for trade in failed:
            if trade.entry_actual_price and trade.outcome_price:
                ret = ((trade.entry_actual_price - trade.outcome_price) / 
                       trade.entry_actual_price * 100)
                loss_returns.append(ret)
        
        avg_win = sum(win_returns) / len(win_returns) if win_returns else 0.0
        avg_loss = sum(loss_returns) / len(loss_returns) if loss_returns else 0.0
        
        return {
            "avg_win_pct": round(avg_win, 2),
            "avg_loss_pct": round(avg_loss, 2),
            "best_win": round(max(win_returns), 2) if win_returns else 0.0,
            "worst_loss": round(max(loss_returns), 2) if loss_returns else 0.0,
            "profit_factor": round(sum(win_returns) / sum(loss_returns), 2) if loss_returns and sum(loss_returns) > 0 else 0.0
        }
    
    @staticmethod
    def _analyze_entry_quality(entered: List[TradeRecord]) -> dict:
        """Analyze entry positioning within buy zone."""
        
        if not entered:
            return {}
        
        entry_positions = []  # % into buy zone
        
        for trade in entered:
            zone_size = trade.buy_zone_upper - trade.buy_zone_lower
            if zone_size > 0:
                position = ((trade.entry_actual_price - trade.buy_zone_lower) / zone_size) * 100
                entry_positions.append(position)
        
        if not entry_positions:
            return {}
        
        avg_position = sum(entry_positions) / len(entry_positions)
        
        return {
            "avg_entry_position": round(avg_position, 2),
            "avg_position_note": f"Entered {avg_position:.0f}% into buy zone (50% is midpoint)"
        }
    
    @staticmethod
    def _empty_results() -> dict:
        """Return empty results template."""
        return {
            "success_rate": 0.0,
            "failure_rate": 0.0,
            "no_entry_rate": 0.0,
            "avg_drawdown": 0.0,
            "median_time_to_outcome": "N/A",
            "total_trades": 0,
            "entered_trades": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "no_entry_trades": 0,
            "win_loss_analysis": {},
            "entry_quality": {}
        }
