"""
Data models and structures for stock analysis
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
from datetime import datetime


class Decision(Enum):
    """Stock decision outcomes"""
    ACCUMULATE = "✅ Long-term Accumulate"
    AVOID = "⚠️ Avoid fresh buying at current levels"
    EXIT = "❌ Exit thesis broken"


@dataclass
class FundamentalMetrics:
    """Fundamental analysis metrics"""
    
    # Profitability
    net_profit_margin: float  # %
    roe: float  # Return on Equity %
    roce: float  # Return on Capital Employed %
    
    # Growth
    revenue_cagr_5yr: float  # %
    eps_cagr_5yr: float  # %
    profit_cagr_5yr: float  # %
    
    # Financial Health
    debt_to_equity: float
    current_ratio: float
    debt_service_coverage: float  # Interest coverage
    
    # Valuation
    pe_ratio: float
    pb_ratio: float
    dividend_yield: float  # %
    pe_percentile: float  # vs historical 5yr: 0-100
    
    # Assessment
    is_profitable: bool = field(init=False)
    is_growing: bool = field(init=False)
    is_stable: bool = field(init=False)
    is_fairly_valued: bool = field(init=False)
    
    def __post_init__(self):
        """Compute derived flags"""
        from .constants import FUNDAMENTAL_THRESHOLDS as T
        
        self.is_profitable = (
            self.net_profit_margin >= T["min_profit_margin_pct"] and
            self.roe >= T["min_roe_pct"] and
            self.roce >= T["min_roce_pct"]
        )
        
        self.is_growing = (
            self.revenue_cagr_5yr >= T["min_revenue_growth_5yr_pct"] and
            self.eps_cagr_5yr >= T["min_eps_growth_5yr_pct"]
        )
        
        self.is_stable = (
            self.debt_to_equity <= T["max_debt_to_equity"] and
            self.current_ratio >= T["min_current_ratio"] and
            self.debt_service_coverage >= T["min_debt_service_coverage"]
        )
        
        self.is_fairly_valued = (
            self.pe_percentile <= T["max_pe_ratio_percentile"] and
            self.pb_ratio <= T["max_pb_ratio"]
        )


@dataclass
class TechnicalMetrics:
    """Technical analysis metrics"""
    
    # Price levels
    current_price: float
    price_52w_high: float
    price_52w_low: float
    price_52w_avg: float
    
    # Moving averages
    sma_20: float
    sma_200: float
    
    # Momentum indicators
    rsi_14: float  # 0-100
    macd_line: float
    macd_signal: float
    macd_histogram: float
    
    # Volatility
    atr_14: float  # Average True Range
    
    # Volume
    avg_volume_20d: int
    current_volume: int
    volume_trend: str  # "increasing", "stable", "decreasing"
    
    # Trend assessment
    is_above_200sma: bool = field(init=False)
    is_above_20sma: bool = field(init=False)
    is_uptrend: bool = field(init=False)
    is_momentum_positive: bool = field(init=False)
    volume_confirmed: bool = field(init=False)
    
    def __post_init__(self):
        """Compute derived trend flags"""
        self.is_above_200sma = self.current_price > self.sma_200
        self.is_above_20sma = self.current_price > self.sma_20
        
        # Uptrend: Price above both SMAs and RSI > 50
        self.is_uptrend = (
            self.is_above_200sma and 
            self.is_above_20sma and 
            self.rsi_14 > 50
        )
        
        # Momentum: MACD positive and RSI not extreme
        self.is_momentum_positive = (
            self.macd_line > self.macd_signal and
            self.rsi_14 < 70
        )
        
        # Volume confirmation
        self.volume_confirmed = (
            self.current_volume > (self.avg_volume_20d * 1.2)
        )


@dataclass
class RiskAssessment:
    """Risk assessment and position sizing"""
    
    # Volatility risk
    atr_pct_of_price: float  # ATR / current price as %
    volatility_level: str  # "low", "medium", "high"
    
    # Position sizing
    max_position_size_pct: float  # Max % of portfolio
    suggested_position_size_pct: float  # Conservative allocation
    
    # Entry and exit levels
    entry_price: float
    target_price: float  # 3-5 year target
    stop_loss_price: float  # Hard stop
    support_level: float  # Technical support
    
    # Risk metrics
    risk_reward_ratio: float
    max_drawdown_pct: float
    
    def __post_init__(self):
        """Computed risk reward"""
        pass


@dataclass
class StockAnalysis:
    """Complete analysis result for a stock"""
    
    ticker: str
    name: str
    sector: str
    analysis_date: datetime
    
    # Component analyses
    fundamentals: FundamentalMetrics
    technicals: TechnicalMetrics
    risk: RiskAssessment
    
    # Final decision
    decision: Decision
    confidence_score: float  # 0-100: how certain is the decision
    reasoning: str  # Detailed explanation
    key_risks: List[str]  # Top 3-5 risks
    key_catalysts: List[str]  # Positive catalysts
    
    # Metadata
    data_quality_score: float  # 0-100: data completeness
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class PortfolioRecommendation:
    """Portfolio-level recommendation"""
    
    analysis_date: datetime
    stocks_analyzed: int
    
    # Recommendations by decision
    accumulate_stocks: List[str]  # Ticker symbols
    avoid_stocks: List[str]
    exit_stocks: List[str]
    
    # Portfolio metrics
    sector_allocation: Dict[str, float]  # Sector -> %
    total_recommended_allocation: float  # Should sum to 100
    
    # Commentary
    market_outlook: str
    key_themes: List[str]
    rebalancing_notes: str
