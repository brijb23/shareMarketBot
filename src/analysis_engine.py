"""
Main Stock Analysis Orchestrator
Entry point for comprehensive analysis
"""

from typing import List, Optional
from datetime import datetime
from .data_models import (
    FundamentalMetrics, TechnicalMetrics, RiskAssessment, StockAnalysis, Decision
)
from .fundamental_analysis import FundamentalAnalyzer
from .technical_analysis import TechnicalAnalyzer
from .decision_engine import DecisionEngine


class StockAnalysisEngine:
    """
    Main orchestrator for stock analysis.
    Coordinates fundamental, technical, and decision engines.
    """
    
    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.analysis_history = {}  # ticker -> list of analyses
    
    def analyze_stock(
        self,
        ticker: str,
        name: str,
        sector: str,
        fundamentals: FundamentalMetrics,
        technicals: TechnicalMetrics,
        risk: RiskAssessment,
    ) -> StockAnalysis:
        """
        Perform comprehensive analysis on a single stock.
        
        Args:
            ticker: Stock ticker symbol (e.g., "TCS")
            name: Company name
            sector: Industry sector
            fundamentals: FundamentalMetrics object
            technicals: TechnicalMetrics object
            risk: RiskAssessment object
            
        Returns:
            StockAnalysis with decision and reasoning
        """
        analysis = self.decision_engine.decide(
            ticker=ticker,
            name=name,
            sector=sector,
            fundamentals=fundamentals,
            technicals=technicals,
            risk=risk,
        )
        
        # Store in history
        if ticker not in self.analysis_history:
            self.analysis_history[ticker] = []
        self.analysis_history[ticker].append(analysis)
        
        return analysis
    
    def analyze_portfolio(
        self,
        stocks: List[dict]
    ) -> dict:
        """
        Analyze a portfolio of stocks.
        
        Args:
            stocks: List of dicts with keys:
                    - ticker, name, sector, fundamentals, technicals, risk
                    
        Returns:
            {
                'analyses': [StockAnalysis, ...],
                'summary': {
                    'total_stocks': int,
                    'accumulate': int,
                    'avoid': int,
                    'exit': int,
                    'avg_confidence': float,
                }
            }
        """
        analyses = []
        for stock_data in stocks:
            analysis = self.analyze_stock(
                ticker=stock_data['ticker'],
                name=stock_data['name'],
                sector=stock_data['sector'],
                fundamentals=stock_data['fundamentals'],
                technicals=stock_data['technicals'],
                risk=stock_data['risk'],
            )
            analyses.append(analysis)
        
        # Compute summary
        accumulate_count = sum(1 for a in analyses if a.decision == Decision.ACCUMULATE)
        avoid_count = sum(1 for a in analyses if a.decision == Decision.AVOID)
        exit_count = sum(1 for a in analyses if a.decision == Decision.EXIT)
        avg_confidence = sum(a.confidence_score for a in analyses) / len(analyses)
        
        return {
            'analyses': analyses,
            'summary': {
                'total_stocks': len(analyses),
                'accumulate': accumulate_count,
                'avoid': avoid_count,
                'exit': exit_count,
                'avg_confidence': avg_confidence,
            }
        }
    
    def get_recommendations(self, analyses: List[StockAnalysis]) -> dict:
        """
        Group recommendations by decision type.
        """
        accumulate = [a for a in analyses if a.decision == Decision.ACCUMULATE]
        avoid = [a for a in analyses if a.decision == Decision.AVOID]
        exit_list = [a for a in analyses if a.decision == Decision.EXIT]
        
        return {
            'accumulate': sorted(accumulate, key=lambda x: x.confidence_score, reverse=True),
            'avoid': sorted(avoid, key=lambda x: x.confidence_score, reverse=True),
            'exit': sorted(exit_list, key=lambda x: x.confidence_score, reverse=True),
        }
    
    def print_analysis(self, analysis: StockAnalysis):
        """Pretty print analysis"""
        print(self.decision_engine.get_decision_summary(analysis))
    
    def print_portfolio_summary(self, portfolio_result: dict):
        """Pretty print portfolio summary"""
        summary = portfolio_result['summary']
        analyses = portfolio_result['analyses']
        
        print("\n" + "="*70)
        print("PORTFOLIO ANALYSIS SUMMARY")
        print("="*70)
        print(f"Total Stocks Analyzed: {summary['total_stocks']}")
        print(f"✅ Accumulate: {summary['accumulate']}")
        print(f"⚠️  Avoid: {summary['avoid']}")
        print(f"❌ Exit: {summary['exit']}")
        print(f"Average Confidence: {summary['avg_confidence']:.0f}%")
        print("="*70 + "\n")
        
        # Group by decision
        recommendations = self.get_recommendations(analyses)
        
        if recommendations['accumulate']:
            print("✅ STRONG BUY (Accumulate):")
            for a in recommendations['accumulate']:
                print(f"   {a.ticker:10} {a.name:30} Conf: {a.confidence_score:.0f}%")
            print()
        
        if recommendations['avoid']:
            print("⚠️  AVOID (Wait for Better Timing):")
            for a in recommendations['avoid']:
                print(f"   {a.ticker:10} {a.name:30} Conf: {a.confidence_score:.0f}%")
            print()
        
        if recommendations['exit']:
            print("❌ SELL/AVOID (Exit Thesis Broken):")
            for a in recommendations['exit']:
                print(f"   {a.ticker:10} {a.name:30} Conf: {a.confidence_score:.0f}%")
            print()
