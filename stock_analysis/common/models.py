"""
Core data models for the stock analysis engine.

These are pure data structures with no business logic.
They define the contracts between all modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from decimal import Decimal


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS - Decision and Status Types
# ═══════════════════════════════════════════════════════════════════════════

class DecisionType(Enum):
    """Investment decision outcomes"""
    ACCUMULATE = "accumulate"      # Strong business + favorable timing
    AVOID = "avoid"                # Good business but unclear timing
    EXIT = "exit"                  # Thesis broken
    HOLD = "hold"                  # Existing position, no action


class FundamentalStatus(Enum):
    """Fundamental business quality assessment"""
    EXCELLENT = "excellent"        # All rules pass with margin of safety
    GOOD = "good"                  # Most rules pass
    FAIR = "fair"                  # Some concerns but acceptable
    WEAK = "weak"                  # Multiple rules fail
    BROKEN = "broken"              # Critical failures


class TechnicalTrend(Enum):
    """Price trend assessment"""
    STRONG_UPTREND = "strong_uptrend"      # Above 200 SMA, strong momentum
    UPTREND = "uptrend"                    # Above 200 SMA, positive momentum
    WEAK_UPTREND = "weak_uptrend"          # Above 200 SMA, neutral momentum
    NEUTRAL = "neutral"                    # Between key moving averages
    WEAK_DOWNTREND = "weak_downtrend"      # Below 200 SMA, weak negative
    DOWNTREND = "downtrend"                # Below key SMAs, negative momentum
    STRONG_DOWNTREND = "strong_downtrend"  # Confirmed downtrend, strong negative


class VolatilityLevel(Enum):
    """Risk volatility classification"""
    VERY_LOW = "very_low"      # < 1% ATR
    LOW = "low"                 # 1-1.5% ATR
    MEDIUM = "medium"           # 1.5-2.5% ATR
    HIGH = "high"               # 2.5-3.5% ATR
    VERY_HIGH = "very_high"     # > 3.5% ATR


# ═══════════════════════════════════════════════════════════════════════════
# PRICE DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PriceBar:
    """
    Single trading day OHLCV data.
    
    Represents one day of price and volume information.
    Used as input to technical analysis.
    """
    date: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    
    # Optional: Adjusted close for corporate actions
    adjusted_close: Optional[Decimal] = None


@dataclass
class PriceHistory:
    """
    Historical price data for a stock.
    
    Contains all price bars up to analysis date.
    Used as input to technical indicators.
    """
    ticker: str
    bars: List[PriceBar]
    
    # Metadata
    data_start_date: datetime
    data_end_date: datetime
    total_bars: int = field(init=False)
    
    def __post_init__(self):
        self.total_bars = len(self.bars)


# ═══════════════════════════════════════════════════════════════════════════
# FUNDAMENTAL DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
@dataclass
class FundamentalData:
    """
    Complete fundamental metrics for a stock.
    
    Represents business quality through financial metrics.
    Usually updated quarterly when earnings are reported.
    """
    # Identification
    ticker: Optional[str] = None
    as_of_date: Optional[datetime] = None  # Report date (quarterly/annual)
    
    # Growth Metrics (% CAGR)
    revenue_cagr: Optional[Decimal] = None
    profit_cagr: Optional[Decimal] = None
    eps_cagr_5yr: Optional[Decimal] = None
    profit_growth_3yr: Optional[Decimal] = None
    
    # Profitability Metrics (%)
    net_profit_margin: Optional[Decimal] = None
    roe: Optional[Decimal] = None  # Return on Equity
    roce: Optional[Decimal] = None  # Return on Capital Employed
    net_profit: Optional[float] = None
    margin_trend: Optional[str] = None
    
    # Financial Health
    debt_to_equity: Optional[Decimal] = None
    debt_to_equity_num: Optional[float] = None
    current_ratio: Optional[Decimal] = None
    debt_service_coverage: Optional[Decimal] = None
    interest_coverage: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    
    # Valuation
    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    pe_historical_percentile: Optional[Decimal] = None  # 0-100: stock's PE vs 5-year history
    historical_pe_median: Optional[float] = None
    peg_ratio: Optional[float] = None
    
    # Optional: Historical context for ratios
    pe_5yr_high: Optional[Decimal] = None
    pe_5yr_low: Optional[Decimal] = None
    pe_5yr_median: Optional[Decimal] = None


@dataclass
class FundamentalScore:
    """
    Aggregated fundamental quality assessment.
    
    OUTPUT of fundamentals analysis module.
    Used by decision engine.
    
    Rules-based scoring where individual components are 0-100
    and overall is either PASS (all rules met) or FAIL (any rule fails).
    """
    # Individual rule assessments (0-100 per rule)
    profitability_score: Optional[float] = None      # Based on NPM, ROE, ROCE
    growth_score: Optional[float] = None             # Based on 5-year CAGR
    financial_strength_score: Optional[float] = None # Based on leverage and ratios
    valuation_score: Optional[float] = None          # Based on PE, PB, yield
    stability_score: Optional[float] = None          # Based on leverage and ratios
    
    # Overall Assessment
    status: Optional[str] = None       # EXCELLENT, GOOD, FAIR, WEAK, BROKEN
    overall_score: Optional[float] = None            # 0-100: average of all scores
    total_score: Optional[int] = None
    
    # Details for reasoning
    passing_rules: Optional[List[str]] = None        # Which rules passed
    failing_rules: Optional[List[str]] = None        # Which rules failed
    key_strengths: Optional[List[str]] = None        # Top 2-3 positive aspects
    key_concerns: Optional[List[str]] = None         # Top 2-3 concerns
    
    # Metadata
    symbol: Optional[str] = None
    as_of_date: Optional[datetime] = None
    
    # Confidence in assessment (0-100)
    data_quality_score: Optional[float] = None       # How complete/recent is data?
    confidence_level: Optional[float] = None         # Overall confidence in score


# ═══════════════════════════════════════════════════════════════════════════
# TECHNICAL INDICATOR MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class IndicatorData:
    """
    Technical indicators calculated from price history.
    
    OUTPUT of indicators module.
    Used by technical analysis module.
    
    Represents latest values of various technical indicators.
    """
    # Metadata
    symbol: Optional[str] = None
    as_of_date: Optional[datetime] = None
    
    # Current price levels
    current_price: Optional[Decimal] = None
    latest_price: Optional[Decimal] = None  # Alias for current_price
    price_52w_high: Optional[Decimal] = None
    price_52w_low: Optional[Decimal] = None
    
    # Moving Averages
    sma_20: Optional[Decimal] = None      # Short-term trend
    sma_50: Optional[Decimal] = None      # Medium-term trend
    sma_200: Optional[Decimal] = None     # Long-term trend
    dma_50: Optional[Decimal] = None      # Alias
    dma_200: Optional[Decimal] = None     # Alias
    dma_200_slope: Optional[Decimal] = None
    
    # Momentum Indicators
    rsi_14: Optional[float] = None        # 0-100: overbought > 70, oversold < 30
    macd_line: Optional[Decimal] = None
    macd_signal: Optional[Decimal] = None
    macd_histogram: Optional[Decimal] = None
    
    # Volatility
    atr_14: Optional[Decimal] = None                  # Average True Range
    atr_percent: Optional[float] = None               # ATR as % of price
    volatility_level: Optional[str] = None
    
    # Volume Analysis
    volume_current: Optional[int] = None
    volume_20d_avg: Optional[int] = None
    volume_trend: Optional[str] = None                # "increasing", "stable", "decreasing"
    
    # Momentum Strength
    rsi_above_50: Optional[bool] = None              # Is RSI > 50? (positive momentum)
    macd_positive: Optional[bool] = None             # Is MACD > signal? (upside momentum)
    
    # Position in bands/zones
    rsi_position: Optional[str] = None               # "oversold", "neutral", "overbought"
    bb_upper: Optional[Decimal] = None     # Bollinger Band upper
    bb_middle: Optional[Decimal] = None    # Bollinger Band middle
    bb_lower: Optional[Decimal] = None     # Bollinger Band lower
    
    # Relative Strength
    relative_strength_6m: Optional[float] = None
    relative_strength_12m: Optional[float] = None


@dataclass
@dataclass
class TechnicalScore:
    """
    Aggregated technical analysis assessment.
    
    OUTPUT of technical analysis module.
    Used by decision engine.
    """
    # Metadata
    symbol: Optional[str] = None
    as_of_date: Optional[datetime] = None
    
    # Score Components (0-100)
    trend_score: Optional[float] = None
    momentum_score: Optional[float] = None
    volume_score: Optional[float] = None
    volatility_score: Optional[float] = None
    total_score: Optional[int] = None
    
    # Trend Assessment
    trend: Optional[str] = None
    
    # Trend Quality Scoring (0-100)
    trend_strength: Optional[float] = None           # How strong is the trend?
    volume_confirmation: Optional[float] = None      # Volume supporting the move?
    overall_technical_score: Optional[float] = None
    overall_score: Optional[float] = None
    
    # Timing Favorability
    entry_quality: Optional[float] = None            # 0-100: How good is current entry?
    pullback_status: Optional[str] = None            # "In uptrend", "Pullback", "Reversal", etc.
    support_level: Optional[Decimal] = None          # Current support price
    resistance_level: Optional[Decimal] = None       # Current resistance price
    
    # Risk Metrics
    price_from_52w_high_pct: Optional[float] = None  # % below 52-week high
    price_from_52w_low_pct: Optional[float] = None   # % above 52-week low
    
    # Signals and Details
    bullish_signals: Optional[List[str]] = None      # Price above 200 SMA, RSI > 50, etc.
    bearish_signals: Optional[List[str]] = None      # Price below 200 SMA, RSI < 50, etc.
    key_observations: Optional[List[str]] = None     # Notable technical patterns


# ═══════════════════════════════════════════════════════════════════════════
# PRICE LEVEL MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class BuyZone:
    """
    Defined price zone where accumulation is favorable.
    
    OUTPUT of buy_zone module.
    Used by decision engine for entry recommendations.
    """
    # Zone boundaries
    zone_high: Decimal              # Top of buy zone
    zone_low: Decimal               # Bottom of buy zone
    zone_mid: Decimal               # Midpoint
    
    # Current status
    current_price: Decimal
    is_in_zone: bool
    percent_into_zone: float        # 0-100: where in zone is price?
    
    # Zone rationale
    basis: str                      # "Support level", "Pullback", "SMA support", etc.
    confidence: float               # 0-100: how confident in this zone?
    
    # Context
    volume_at_zone: str             # Expected volume: "high", "normal", "low"
    holding_period: str             # "Weeks to months", "Months to year+", etc.


@dataclass
class Targets:
    """
    Price targets and timeline expectations.
    
    OUTPUT of targets module.
    Defines what success looks like.
    """
    # Short-term target (3-6 months)
    target_3mo: Optional[Decimal] = None
    target_3mo_probability: Optional[float] = None
    
    # Medium-term target (6-12 months)
    target_6mo: Optional[Decimal] = None
    target_6mo_probability: Optional[float] = None
    
    # Long-term target (1-3 years)
    target_1yr: Optional[Decimal] = None
    target_1yr_probability: Optional[float] = None
    
    target_3yr: Optional[Decimal] = None
    target_3yr_probability: Optional[float] = None
    
    # Risk/Reward
    risk_reward_ratio: Optional[Decimal] = None      # Upside target / Downside stop loss
    expected_return_pct: Optional[float] = None      # Based on most likely scenario
    
    # Assumptions
    assumptions: Optional[List[str]] = None          # What needs to happen for targets
    catalysts: Optional[List[str]] = None            # Events that could trigger moves


@dataclass
class Invalidation:
    """
    Levels and conditions that would break the thesis.
    
    OUTPUT of invalidation module.
    Defines when to exit.
    """
    # Hard stops
    stop_loss_price: Decimal        # -10% technical stop
    hard_stop_reason: str           # Why this level matters
    
    # Soft signals (reassess)
    reassess_price: Decimal         # If price breaks here, reassess thesis
    reassess_reason: str
    
    # Fundamental breaks (automatic exit)
    fundamental_break_signals: List[str]  # e.g., "Dividend cut", "Earnings miss"
    
    # Technical breaks (likely exit)
    technical_break_signals: List[str]    # e.g., "Close below 200 SMA for 3 days"
    
    # Time-based
    reassess_after_days: int        # Even if no price action, reassess after X days
    
    # Context
    confidence_in_thesis: float     # 0-100: How confident is original thesis?


# ═══════════════════════════════════════════════════════════════════════════
# DECISION MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Decision:
    """
    Final investment decision for a stock.
    
    OUTPUT of decision engine.
    This is what the user sees and acts on.
    """
    # Stock identification
    ticker: str
    name: str
    sector: str
    decision_date: datetime
    
    # The Decision
    decision: DecisionType
    confidence_level: float         # 0-100: How confident in this decision?
    
    # Supporting analyses
    fundamental_score: FundamentalScore
    technical_score: TechnicalScore
    
    # Recommendation
    buy_zone: Optional[BuyZone]     # If ACCUMULATE
    targets: Optional[Targets]      # Expected outcomes
    invalidation: Optional[Invalidation]  # Exit conditions
    
    # Reasoning (for user understanding)
    summary: str                    # 1-2 sentence executive summary
    rationale: str                  # Paragraph explaining decision
    key_points: List[str]           # Top 3-5 reasons for decision
    risks: List[str]                # Top 3-5 risks to watch
    catalysts: List[str]            # Events that could change decision
    
    # Position Sizing (if ACCUMULATE)
    suggested_position_pct: Optional[float] = None  # 1-5% of portfolio
    max_position_pct: Optional[float] = None        # Absolute max
    
    # Holding Timeline
    minimum_holding_months: Optional[int] = None
    target_holding_years: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════════════
# BACKTESTING MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Snapshot:
    """
    Single point-in-time state of analysis.
    
    Used in backtesting: saves complete analysis state at a historical date.
    Allows replay of decisions to measure accuracy.
    
    ENHANCED with NEW fields:
    - momentum_score: Institutional accumulation indicator
    - fundamental_trend: Direction of fundamental improvement
    - stock_type: Classification for dynamic thresholds
    """
    # Time reference
    snapshot_date: datetime         # When was this analysis created?
    
    # Stock identification
    ticker: str
    
    # Historical state at this date
    price_at_date: Decimal          # What was the price?
    fundamental_data: FundamentalData
    indicators: IndicatorData
    
    # Analysis results at that time
    fundamental_score: FundamentalScore
    technical_score: TechnicalScore
    
    # NEW: Enhanced analysis components
    momentum_score: Optional[int] = None              # 0-100 institutional accumulation
    fundamental_trend: Optional[Dict] = None          # 'improving', 'stable', 'declining'
    stock_type: Optional[str] = None                  # 'government', 'highly_volatile', 'stable_quality', 'normal'
    
    # Decision at that time
    decision: str = None                              # Decision string (simplified for compatibility)
    
    # Analysis metadata
    data_sources: Optional[Dict[str, str]] = None    # Where did data come from?
    analysis_notes: Optional[str] = None             # Any special circumstances
    
    # What actually happened after?
    # (Filled in during backtesting evaluation)
    price_6_months_later: Optional[Decimal] = None
    price_1_year_later: Optional[Decimal] = None


@dataclass
class BacktestResult:
    """
    Performance metrics from backtesting a decision strategy.
    
    OUTPUT of backtest evaluator module.
    """
    # Test parameters
    ticker: str
    test_start_date: datetime
    test_end_date: datetime
    total_snapshots_analyzed: int
    
    # Decision Statistics
    decisions_made: int
    accumulate_count: int
    avoid_count: int
    exit_count: int
    
    # Performance (for ACCUMULATE decisions that were followed)
    accumulate_decisions_followed: int  # How many were actually bought?
    successful_entries: int             # Reached target within timeframe
    failed_entries: int                 # Hit stop loss
    partial_success: int                # Some upside but not full target
    
    # Returns
    avg_return_per_accumulate: float    # Average % gain
    best_return: float                  # Best single trade
    worst_return: float                 # Worst single trade
    max_drawdown: float                 # Largest peak-to-trough
    
    # Decision Accuracy
    decision_accuracy_pct: float        # % of decisions that played out as expected
    false_positives: int                # Bought (ACCUMULATE) but went down
    false_negatives: int                # Didn't buy (AVOID) but went up
    
    # Timing Quality
    entry_timing_score: float           # How good was entry timing? (0-100)
    exit_timing_score: float            # How good was exit timing? (0-100)
    
    # Risk Management
    average_max_loss_pct: float         # Average worst drawdown per position
    positions_stopped_out: int          # How many hit stop loss?
    
    # Conclusions
    strategy_conclusion: str            # Summary of strategy performance
    improvements_suggested: List[str]   # What could be improved


# ═══════════════════════════════════════════════════════════════════════════
# PORTFOLIO/BATCH MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PortfolioAnalysis:
    """
    Analysis results for a portfolio/batch of stocks.
    """
    analysis_date: datetime
    stocks_analyzed: int
    
    # Decision breakdown
    accumulate_stocks: List[Decision]
    avoid_stocks: List[Decision]
    exit_stocks: List[Decision]
    
    # Portfolio metrics
    avg_confidence: float
    sectors_represented: Dict[str, int]
    
    # Recommendations
    top_opportunities: List[Decision]   # Best ACCUMULATE recommendations
    stocks_to_monitor: List[Decision]   # AVOID but watch
    positions_to_exit: List[Decision]   # EXIT recommendations


# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY: Data Flow
# ═══════════════════════════════════════════════════════════════════════════

"""
DATA FLOW THROUGH THE SYSTEM:

1. DATA PROVIDERS (data/)
   Input:  None
   Output: PriceHistory, FundamentalData

2. INDICATORS (analysis/indicators.py)
   Input:  PriceHistory
   Output: IndicatorData

3. FUNDAMENTALS (analysis/fundamentals.py)
   Input:  FundamentalData
   Output: FundamentalScore

4. TECHNICALS (analysis/technicals.py)
   Input:  IndicatorData
   Output: TechnicalScore

5. BUY ZONE (levels/buy_zone.py)
   Input:  Current price, TechnicalScore, IndicatorData
   Output: BuyZone

6. TARGETS (levels/targets.py)
   Input:  FundamentalData, FundamentalScore, TechnicalScore
   Output: Targets

7. INVALIDATION (levels/invalidation.py)
   Input:  Current price, Targets, TechnicalScore
   Output: Invalidation

8. DECISION ENGINE (analysis/decision_engine.py)
   Input:  FundamentalScore, TechnicalScore, BuyZone, Targets, Invalidation
   Output: Decision

9. SNAPSHOT (backtest/snapshot.py)
   Input:  All of the above
   Output: Snapshot (stores complete state)

10. SIMULATOR (backtest/simulator.py)
    Input:  List[Snapshot] (historical analyses)
    Output: Historical performance

11. EVALUATOR (backtest/evaluator.py)
    Input:  Simulation results
    Output: BacktestResult (metrics and conclusions)
"""
