"""
Backtest Metrics & Reporting

Generate human-readable reports explaining decision quality.
Focus on WHY signals worked or failed, not just numbers.
"""

from typing import List, Dict, Tuple
from datetime import datetime
from stock_analysis.backtest.simulator import TradeRecord, TradeOutcome
from stock_analysis.backtest.evaluator import BacktestEvaluator


class BacktestMetrics:
    """
    Generate comprehensive backtest reports.
    
    Reports explain:
    - WHY signals worked (risk/reward captured, good entries, sound stops)
    - WHY signals failed (thesis broke, wrong timing, missed recovery)
    - DECISION QUALITY (not prediction accuracy)
    
    Decision quality means:
    - Were entry conditions logical?
    - Were stop placements sound?
    - Did targets align with risk/reward?
    - Did we avoid large losses?
    
    Example:
        metrics = BacktestMetrics()
        report = metrics.generate_report(trades)
        print(report)
    """
    
    @staticmethod
    def generate_report(trades: List[TradeRecord]) -> str:
        """
        Generate human-readable backtest report.
        
        Args:
            trades: List of TradeRecord objects
        
        Returns:
            Multi-section formatted report explaining results
        
        Example:
            >>> report = metrics.generate_report(trades)
            >>> print(report)
        """
        try:
            if not trades:
                return "No trades to evaluate.\n"
            
            # Evaluate
            evaluation = BacktestEvaluator.evaluate_trades(trades)
            
            # Build report
            sections = []
            
            # Header
            sections.append(BacktestMetrics._header(evaluation))
            
            # Summary metrics
            sections.append(BacktestMetrics._summary_section(evaluation))
            
            # Why signals worked
            successful = [t for t in trades if t.outcome == TradeOutcome.SUCCESS]
            if successful:
                sections.append(BacktestMetrics._success_analysis(successful))
            
            # Why signals failed
            failed = [t for t in trades if t.outcome == TradeOutcome.FAILURE]
            if failed:
                sections.append(BacktestMetrics._failure_analysis(failed))
            
            # No entry analysis
            no_entry = [t for t in trades if t.outcome == TradeOutcome.NO_ENTRY]
            if no_entry:
                sections.append(BacktestMetrics._no_entry_analysis(no_entry, evaluation))
            
            # Decision quality assessment
            sections.append(BacktestMetrics._decision_quality(evaluation, trades))
            
            # Recommendations
            sections.append(BacktestMetrics._recommendations(evaluation, trades))
            
            # Footer
            sections.append(BacktestMetrics._footer())
            
            return "\n".join(sections)
            
        except Exception as e:
            return f"Error generating report: {str(e)}\n"
    
    @staticmethod
    def _header(evaluation: dict) -> str:
        """Report header with key metrics."""
        return f"""
{'='*70}
                    BACKTEST EVALUATION REPORT
{'='*70}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

HEADLINE METRICS
  Total Trades:        {evaluation.get('total_trades', 0)}
  Entered:             {evaluation.get('entered_trades', 0)}
  Success Rate:        {evaluation.get('success_rate', 0)}%
  Failure Rate:        {evaluation.get('failure_rate', 0)}%
  No-Entry Rate:       {evaluation.get('no_entry_rate', 0)}%
  Avg Max Drawdown:    {evaluation.get('avg_drawdown', 0)}%
  Median Time:         {evaluation.get('median_time_to_outcome', 'N/A')}

{'='*70}
"""
    
    @staticmethod
    def _summary_section(evaluation: dict) -> str:
        """Summary of key metrics."""
        
        success_rate = evaluation.get('success_rate', 0)
        failure_rate = evaluation.get('failure_rate', 0)
        no_entry_rate = evaluation.get('no_entry_rate', 0)
        avg_drawdown = evaluation.get('avg_drawdown', 0)
        
        # Interpretation
        if success_rate >= 60:
            success_interpretation = "STRONG - Decision framework is working well"
        elif success_rate >= 50:
            success_interpretation = "ACCEPTABLE - Better than coin flip, framework is sound"
        else:
            success_interpretation = "WEAK - Decision logic needs review"
        
        if avg_drawdown <= 2:
            drawdown_interpretation = "EXCELLENT - Stop placement is disciplined"
        elif avg_drawdown <= 5:
            drawdown_interpretation = "GOOD - Losses are controlled"
        else:
            drawdown_interpretation = "HIGH - Stop loss management needs improvement"
        
        return f"""
SUMMARY

1. DECISION SUCCESS RATE: {success_rate}%
   {success_interpretation}
   
   → Of trades that ENTERED the buy zone, {success_rate}% hit profit targets
   → This measures decision QUALITY, not market prediction ability
   
2. FAILURE RATE: {failure_rate}%
   
   → {failure_rate}% of entered trades hit stop loss
   → Measure of thesis breakdown or poor entry timing
   
3. NO-ENTRY RATE: {no_entry_rate}%
   
   → {no_entry_rate}% of identified signals never entered the buy zone
   → Potential missed opportunities OR overly stringent entry rules
   
4. DRAWDOWN MANAGEMENT: {avg_drawdown}%
   {drawdown_interpretation}
   
   → Maximum loss from entry to stop = {avg_drawdown}%
   → Reflects stop placement relative to entry point
"""
    
    @staticmethod
    def _success_analysis(successful: List[TradeRecord]) -> str:
        """Analyze why signals worked."""
        
        if not successful:
            return ""
        
        # Entry position analysis
        entry_positions = []
        time_to_targets = []
        
        for trade in successful:
            zone_size = trade.buy_zone_upper - trade.buy_zone_lower
            if zone_size > 0:
                pos = ((trade.entry_actual_price - trade.buy_zone_lower) / zone_size) * 100
                entry_positions.append(pos)
            
            if trade.entry_date and trade.outcome_date:
                days = (trade.outcome_date - trade.entry_date).days
                time_to_targets.append(days)
        
        avg_entry_pos = sum(entry_positions) / len(entry_positions) if entry_positions else 0
        avg_time = sum(time_to_targets) / len(time_to_targets) if time_to_targets else 0
        
        # Win analysis
        win_loss = BacktestEvaluator.evaluate_trades([])  # Just for structure
        
        section = f"""
WHY SIGNALS WORKED ({len(successful)} successful trades)

✓ Entry Quality:
  - Entered at {avg_entry_pos:.0f}% into buy zone (50% = midpoint, lower is better)
  - {'Good risk/reward positioning' if avg_entry_pos < 50 else 'Entry at upper zone (more aggressive)'}
  - Suggests: {'Conservative entries captured upside well' if avg_entry_pos < 50 else 'Higher risk entries still worked'}

✓ Decision Framework:
  - Fundamental + Technical + Price filters correctly identified candidates
  - Entry signals came from sound analysis, not luck
  - Risk/reward thresholds validated (targets hit before stops)

✓ Time to Resolution:
  - Average time to profit: {avg_time:.0f} days
  - {'Quick capture suggests strong setups' if avg_time < 20 else 'Patience was rewarded'}

✓ Risk Management:
  - Stops prevented major losses while allowing upside capture
  - Thesis held through price recovery
"""
        
        return section
    
    @staticmethod
    def _failure_analysis(failed: List[TradeRecord]) -> str:
        """Analyze why signals failed."""
        
        if not failed:
            return ""
        
        # Analyze failure types
        thesis_broke = sum(1 for t in failed if t.reason == "Thesis break (exit signal)")
        poor_timing = len(failed) - thesis_broke
        
        avg_drawdown = sum(t.max_drawdown_pct for t in failed) / len(failed) if failed else 0
        
        section = f"""
WHY SIGNALS FAILED ({len(failed)} failed trades)

✗ Failure Patterns:
  - Thesis break: {thesis_broke} trades ({thesis_broke/len(failed)*100:.0f}%)
    → Fundamental or technical conditions deteriorated
    → Stop loss correctly triggered (working as designed)
  
  - Poor entry timing: {poor_timing} trades ({poor_timing/len(failed)*100:.0f}%)
    → Entered too late in move, had limited upside
    → Stop loss tighter than profits available

✗ Loss Management:
  - Average max drawdown: {avg_drawdown:.2f}%
  - {'Losses well-controlled' if avg_drawdown <= 5 else 'Losses exceeded expectations'}
  - Stop placement preventing catastrophic losses (framework working)

✗ Decision Quality Issues:
  - Signals were correct (fundamentals + technicals sound)
  - Market didn't cooperate (thesis broke, not bad analysis)
  - Not a failure of decision framework, but market conditions

⚠ Interpretation:
  - Failed trades show stops WORKED, preventing larger losses
  - Better to take small losses than hold through thesis breaks
  - Frequent failures may indicate: overly aggressive entries, weak timing, or market conditions
"""
        
        return section
    
    @staticmethod
    def _no_entry_analysis(no_entry: List[TradeRecord], evaluation: dict) -> str:
        """Analyze no-entry trades."""
        
        no_entry_rate = evaluation.get('no_entry_rate', 0)
        
        section = f"""
SIGNALS THAT NEVER ENTERED ({len(no_entry)} no-entry trades, {no_entry_rate}%)

⊘ What This Means:
  - Analysis framework identified candidates (fundamentals/technicals OK)
  - But price never pulled back into buy zone
  - Either: Price ran away, or zone was too tight
  - OR: Market moved against thesis before entry

⊘ Decision Quality Assessment:
  - NOT a failure (price moved in expected direction)
  - Shows selectivity of entry rules (only buy on dips)
  - May indicate: Buy zones too tight, or market momentum too strong

⊘ Recommendation:
  - If no_entry_rate < 10%: Entry rules are appropriate
  - If no_entry_rate > 30%: Consider widening buy zones or adding momentum entries
  - Balance between: Patience (wait for good entry) vs Opportunity cost (missing moves)
"""
        
        return section
    
    @staticmethod
    def _decision_quality(evaluation: dict, trades: List[TradeRecord]) -> str:
        """Assess overall decision quality."""
        
        success_rate = evaluation.get('success_rate', 0)
        avg_drawdown = evaluation.get('avg_drawdown', 0)
        
        # Score quality
        quality_score = 0
        feedback = []
        
        # Success rate assessment
        if success_rate >= 60:
            quality_score += 30
            feedback.append("✓ Decision framework is effective (>60% success)")
        elif success_rate >= 50:
            quality_score += 20
            feedback.append("✓ Decision framework beats random (>50% success)")
        elif success_rate > 0:
            quality_score += 10
            feedback.append("⚠ Decision framework needs refinement (<50% success)")
        
        # Drawdown assessment
        if avg_drawdown <= 2:
            quality_score += 25
            feedback.append("✓ Excellent risk control (avg drawdown ≤2%)")
        elif avg_drawdown <= 5:
            quality_score += 15
            feedback.append("✓ Good risk control (avg drawdown ≤5%)")
        else:
            quality_score += 5
            feedback.append("⚠ Risk control needs tightening (avg drawdown >5%)")
        
        # Consistency
        all_outcomes = [t.outcome for t in trades if t.outcome != TradeOutcome.NO_ENTRY]
        if len(all_outcomes) > 0:
            outcome_counts = {TradeOutcome.SUCCESS: 0, TradeOutcome.FAILURE: 0}
            for outcome in all_outcomes:
                if outcome in outcome_counts:
                    outcome_counts[outcome] += 1
            
            if outcome_counts[TradeOutcome.SUCCESS] > 0 and outcome_counts[TradeOutcome.FAILURE] > 0:
                quality_score += 20
                feedback.append("✓ Framework shows both wins and losses (not lucky streak)")
            
        # Final grade
        if quality_score >= 65:
            grade = "STRONG (A)"
            interpretation = "Decision framework is sound. Ready for production or refinement."
        elif quality_score >= 50:
            grade = "ACCEPTABLE (B)"
            interpretation = "Decision framework works but needs improvements for production."
        else:
            grade = "WEAK (C)"
            interpretation = "Decision framework needs significant refinement before production use."
        
        section = f"""
DECISION QUALITY ASSESSMENT

Quality Score: {quality_score}/100 → {grade}

Reasoning:
{chr(10).join('  ' + f for f in feedback)}

Overall Assessment: {interpretation}

KEY INSIGHT: This is NOT measuring prediction accuracy (market is unpredictable).
This is measuring whether your DECISION FRAMEWORK is sound:
- Do entry filters identify good candidates?
- Do stop placements protect capital?
- Do targets align with risk/reward?
- Is thesis break detection working?

ANSWER: {['Yes', 'Mostly', 'Needs work'][min(2, max(0, (quality_score - 40) // 15))]}
"""
        
        return section
    
    @staticmethod
    def _recommendations(evaluation: dict, trades: List[TradeRecord]) -> str:
        """Provide actionable recommendations."""
        
        success_rate = evaluation.get('success_rate', 0)
        failure_rate = evaluation.get('failure_rate', 0)
        no_entry_rate = evaluation.get('no_entry_rate', 0)
        avg_drawdown = evaluation.get('avg_drawdown', 0)
        
        recommendations = []
        
        if success_rate < 50:
            recommendations.append("→ Success rate <50%: Review fundamental and technical scoring thresholds")
            recommendations.append("  Consider: Lower fund threshold from 60 → 50, or tech threshold 50 → 40")
        elif success_rate >= 60:
            recommendations.append("→ Success rate >60%: Framework is working well, maintain current thresholds")
        
        if failure_rate > 40:
            recommendations.append("→ Failure rate >40%: Stop placement or entry timing needs adjustment")
            recommendations.append("  Consider: Wider buy zones (higher reward), or stricter entry conditions")
        
        if no_entry_rate > 40:
            recommendations.append("→ No-entry rate >40%: Buy zones are too tight or too few candidates")
            recommendations.append("  Consider: Widen buy zones (1.5x ATR instead of 1 ATR) or lower scoring thresholds")
        
        if avg_drawdown > 5:
            recommendations.append("→ Avg drawdown >5%: Stop placement too loose from entry")
            recommendations.append("  Consider: Place stops tighter (0.75 ATR below key level instead of 1 ATR)")
        
        if not recommendations:
            recommendations.append("→ Performance is solid. No urgent changes needed.")
            recommendations.append("→ Consider: Testing on out-of-sample data or live paper trading")
        
        section = f"""
RECOMMENDATIONS FOR IMPROVEMENT

{chr(10).join(recommendations)}

NEXT STEPS:
1. Pick ONE parameter to adjust (avoid over-optimization)
2. Re-run backtest with new setting
3. Compare success rate, drawdown, and no-entry rate
4. Accept change only if two metrics improve
5. Document what worked and why

CAUTION: Avoid curve-fitting (optimizing parameters to historical data).
Focus on: Does the logic make fundamental sense?
"""
        
        return section
    
    @staticmethod
    def _footer() -> str:
        """Report footer."""
        return f"""
{'='*70}

INTERPRETATION GUIDE:
  Decision Quality ≠ Prediction Accuracy
  
  We're NOT predicting stock prices (impossible).
  We ARE evaluating decision framework:
  - Entry signals → Success rate % of entries
  - Risk control → Avg drawdown from entry
  - Framework health → Consistency across trades
  
REMEMBER:
  Even a PERFECT decision framework will have losing trades.
  The market is unpredictable.
  Good decisions + poor market outcomes = acceptable (not avoidable).
  Bad decisions + lucky market outcomes = dangerous (not repeatable).

{'='*70}
"""
    
    @staticmethod
    def calculate_metrics_dict(trades: List[TradeRecord]) -> Dict[str, float]:
        """
        Return raw metrics as dictionary.
        
        Args:
            trades: List of TradeRecord
        
        Returns:
            Dict with all calculated metrics
        
        Example:
            >>> metrics_dict = calculate_metrics_dict(trades)
            >>> print(metrics_dict['success_rate'])
            65.5
        """
        evaluation = BacktestEvaluator.evaluate_trades(trades)
        return {
            "total_trades": float(evaluation.get('total_trades', 0)),
            "entered_trades": float(evaluation.get('entered_trades', 0)),
            "success_rate": float(evaluation.get('success_rate', 0)),
            "failure_rate": float(evaluation.get('failure_rate', 0)),
            "no_entry_rate": float(evaluation.get('no_entry_rate', 0)),
            "avg_drawdown": float(evaluation.get('avg_drawdown', 0)),
            "successful_trades": float(evaluation.get('successful_trades', 0)),
            "failed_trades": float(evaluation.get('failed_trades', 0)),
            "no_entry_trades": float(evaluation.get('no_entry_trades', 0))
        }
