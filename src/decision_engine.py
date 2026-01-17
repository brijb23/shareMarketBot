"""
Decision Engine - Improved Version
Combines fundamental and technical analysis into final investment decision
Now with dynamic thresholds based on stock type
"""

from typing import Tuple
from .data_models import (
    FundamentalMetrics, TechnicalMetrics, RiskAssessment, 
    StockAnalysis, Decision
)
from .fundamental_analysis import FundamentalAnalyzer
from .technical_analysis import TechnicalAnalyzer
from datetime import datetime


class DecisionEngine:
    """
    Final decision maker: Combines fundamental + technical analysis.
    
    IMPROVED with dynamic thresholds by stock type
    """
    
    def __init__(self):
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
    
    def decide(
        self, 
        ticker: str,
        name: str,
        sector: str,
        fundamentals: FundamentalMetrics,
        technicals: TechnicalMetrics,
        risk: RiskAssessment,
        stock_type: str = 'blue_chip',
        fundamental_trend: dict = None,
        momentum_score: float = 50,
    ) -> StockAnalysis:
        """Make investment decision with DYNAMIC thresholds by stock type."""
        
        # Analyze fundamentals
        is_fundamental_sound, fund_details = self.fundamental_analyzer.analyze(fundamentals)
        fund_score = self.fundamental_analyzer.get_fundamental_score(fundamentals)
        
        # Analyze technicals
        trend_assessment, tech_details = self.technical_analyzer.analyze(technicals)
        timing_score = self.technical_analyzer.get_timing_score(technicals)
        entry_timing = self.technical_analyzer.get_entry_timing(technicals)
        
        # Apply stock-type-specific decision logic
        decision, confidence, reasoning, risks, catalysts = self._make_decision_dynamic(
            ticker, fund_score, trend_assessment, timing_score,
            fundamentals, technicals, risk,
            stock_type, fundamental_trend, momentum_score
        )
        
        return StockAnalysis(
            ticker=ticker,
            name=name,
            sector=sector,
            analysis_date=datetime.now(),
            fundamentals=fundamentals,
            technicals=technicals,
            risk=risk,
            decision=decision,
            confidence_score=confidence,
            reasoning=reasoning,
            key_risks=risks,
            key_catalysts=catalysts,
            data_quality_score=95.0,
        )
    
    def _make_decision(
        self,
        is_fundamentally_sound: bool,
        fund_score: float,
        trend_assessment: str,
        timing_score: float,
        fundamentals: FundamentalMetrics,
        technicals: TechnicalMetrics,
        risk: RiskAssessment,
    ) -> Tuple[Decision, float, str, list, list]:
        """Original decision logic (kept for backward compatibility)"""
        
        confidence = 0.0
        reasoning = ""
        risks = []
        catalysts = []
        
        if not is_fundamentally_sound:
            decision = Decision.EXIT
            confidence = 95.0
            reasoning = "Fundamental break: Business fundamentals are weak."
            risks = ["Weak profitability or growth", "High leverage concerns"]
            return decision, confidence, reasoning, risks, catalysts
        
        if trend_assessment == "uptrend":
            decision = Decision.ACCUMULATE
            confidence = max(70.0, min(95.0, (fund_score + timing_score) / 2))
            reasoning = "Accumulate: Strong fundamentals + favorable timing"
            catalysts = ["Revenue/earnings growth", "Market recognizing quality"]
            risks = ["Market volatility", "Execution risk"]
        
        elif trend_assessment == "downtrend":
            decision = Decision.EXIT
            confidence = 85.0
            reasoning = "Exit thesis broken: Technicals deteriorating despite sound fundamentals"
            risks = ["Downtrend momentum", "Risk of deeper decline"]
            catalysts = ["Technical recovery if support holds"]
        
        else:
            decision = Decision.AVOID
            confidence = 75.0
            reasoning = "Avoid: Fundamentals strong but technical setup unclear"
            risks = ["Unclear market direction"]
            catalysts = ["Clarification of technical trend"]
        
        return decision, confidence, reasoning, risks, catalysts
    
    def _make_decision_dynamic(
        self,
        ticker: str,
        fund_score: float,
        trend_assessment: str,
        timing_score: float,
        fundamentals: FundamentalMetrics,
        technicals: TechnicalMetrics,
        risk: RiskAssessment,
        stock_type: str = 'blue_chip',
        fundamental_trend: dict = None,
        momentum_score: float = 50,
    ) -> Tuple[Decision, float, str, list, list]:
        """
        Improved dynamic decision logic based on stock type.
        Applies different thresholds for each stock type.
        """
        from .stock_classifier import StockClassifier
        
        # Get type-specific thresholds
        thresholds = StockClassifier.get_thresholds(stock_type)
        fund_min = thresholds.get('fund_min', 65)
        tech_min = thresholds.get('tech_min', 65)
        
        confidence = 0.0
        reasoning = ""
        risks = []
        catalysts = []
        
        # RULE 1: Fundamental check
        if fund_score < fund_min:
            decision = Decision.EXIT if fund_score < 40 else Decision.AVOID
            confidence = 85.0
            reasoning = f"Fundamental break: Score {fund_score:.0f} < {fund_min} threshold"
            risks = ["Weak profitability or growth"]
            return decision, confidence, reasoning, risks, catalysts
        
        # RULE 2: Technical check
        if trend_assessment == "uptrend" and timing_score >= tech_min:
            decision = Decision.ACCUMULATE
            confidence = max(70.0, min(95.0, (fund_score + timing_score) / 2))
            reasoning = f"ACCUMULATE ({stock_type}): Fund {fund_score:.0f} + Tech {timing_score:.0f}"
            catalysts = ["Quality business", "Uptrend with positive momentum"]
            risks = ["Market volatility", "Execution risk"]
        
        elif trend_assessment == "downtrend":
            decision = Decision.EXIT
            confidence = 85.0
            reasoning = f"EXIT: Thesis broken - technicals deteriorating"
            risks = ["Continued downtrend"]
            catalysts = ["Technical recovery"]
        
        else:
            decision = Decision.AVOID
            confidence = 60.0
            reasoning = f"HOLD: Fundamentals okay, technicals unclear"
            risks = ["Unclear trend"]
            catalysts = ["Breakout confirmation"]
        
        return decision, confidence, reasoning, risks, catalysts
    
    def get_decision_summary(self, analysis: StockAnalysis) -> str:
        """Format analysis for display"""
        summary = f"""
╔════════════════════════════════════════════════════════════╗
║  {analysis.ticker} - {analysis.name}
║  {analysis.sector} | {analysis.analysis_date.strftime('%Y-%m-%d')}
╚════════════════════════════════════════════════════════════╝

📊 DECISION: {analysis.decision.value} ({analysis.confidence_score:.0f}%)
💡 {analysis.reasoning}

⚠️  RISKS: {', '.join(analysis.key_risks[:2])}
🚀 CATALYSTS: {', '.join(analysis.key_catalysts[:2])}
"""
        return summary
