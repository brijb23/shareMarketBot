"""
Decision Engine

Converts analysis scores and price levels into actionable investment decisions.
Enhanced with momentum scoring, sector context, and fundamental trends to catch
recovery stock rallies without missing quality stock signals.
"""

from stock_analysis.common.models import (
    Decision, DecisionType, FundamentalScore, TechnicalScore,
    BuyZone, Invalidation
)
from stock_analysis.common.stock_classifier import StockClassifier
from stock_analysis.common.momentum_score import MomentumScorer
from stock_analysis.common.sector_analyzer import SectorAnalyzer


class DecisionEngine:
    """
    Make investment decisions based on comprehensive analysis.
    
    ENHANCED Decision Framework:
    - AVOID: One or more critical filters fail
    - ACCUMULATE: All filters pass (long-term holding strategy)
    - HOLD: In recovery with convergence signal
    - EXIT: Fundamental or structural break
    
    Fresh Buying Filters (adapted by stock type):
    1. Adjusted Fundamental threshold (varies by stock type)
    2. Adjusted Technical threshold (varies by stock type)
    3. Momentum score >= stock-type threshold (NEW)
    4. Current price >= 200 DMA (above support trend)
    5. Invalidation exists (clear stop loss defined)
    
    NEW Convergence Signal for Recovery Stocks:
    - Government/Infrastructure stocks with:
      - Technical score >= 65 AND
      - Momentum score >= 65 AND
      - Fundamental score >= 50
    - → HOLD signal (institutional accumulation detected)
    
    Exit Conditions (sell existing position):
    1. Fundamental deterioration (FundamentalScore drops)
    2. 200 DMA trend break (price below 200 DMA)
    
    Philosophy:
    - Accumulation is long-term (hold through noise)
    - Convergence catches recovery rallies (tech + momentum + fund improving)
    - Avoidance is not bearish (just wait for better setup)
    - Exit only on fundamental or structural break
    """
    
    @staticmethod
    def make_decision(fund_score: FundamentalScore,
                     tech_score: TechnicalScore,
                     buy_zone: BuyZone,
                     invalidation: Invalidation,
                     current_price: float,
                     dma_200: float = None,
                     symbol: str = None,
                     momentum_score: int = None,
                     fundamental_trend: dict = None,
                     price_data = None) -> Decision:
        """
        Make investment decision based on all analysis components.
        
        Args:
            fund_score: FundamentalScore object (0-100)
            tech_score: TechnicalScore object (0-100)
            buy_zone: BuyZone object with entry range
            invalidation: Invalidation object with stop loss
            current_price: Current stock price (float)
            dma_200: 200-day moving average (optional, for exit check)
            symbol: Stock symbol (optional, for logging)
            momentum_score: Momentum score 0-100 (NEW, optional)
            fundamental_trend: Trend dict with 'trend', 'roe_change' etc (NEW, optional)
            price_data: Price DataFrame for momentum calculation (NEW, optional)
        
        Returns:
            Decision object with:
            - decision_type: ACCUMULATE, AVOID, EXIT, HOLD, CONVERGENCE
            - confidence: 0-100 indicating decision strength
            - reasoning: Detailed explanation
            - entry_price: Suggested entry (if ACCUMULATE)
            - stop_loss: Stop loss level
        
        Raises:
            ValueError: If required inputs missing or invalid
        
        Example:
            >>> engine = DecisionEngine()
            >>> decision = engine.make_decision(
            ...     fund_score=score_f,
            ...     tech_score=score_t,
            ...     buy_zone=zone,
            ...     invalidation=inv,
            ...     current_price=102.5,
            ...     dma_200=100.0,
            ...     symbol='HCC.NS',
            ...     momentum_score=75
            ... )
            >>> print(decision.decision_type)
            DecisionType.ACCUMULATE
        """
        try:
            # Validate inputs
            if not isinstance(fund_score, FundamentalScore):
                raise ValueError(f"fund_score must be FundamentalScore, "
                               f"got {type(fund_score).__name__}")
            
            if not isinstance(tech_score, TechnicalScore):
                raise ValueError(f"tech_score must be TechnicalScore, "
                               f"got {type(tech_score).__name__}")
            
            if not isinstance(buy_zone, BuyZone):
                raise ValueError(f"buy_zone must be BuyZone, "
                               f"got {type(buy_zone).__name__}")
            
            if invalidation is not None and not isinstance(invalidation, Invalidation):
                raise ValueError(f"invalidation must be Invalidation or None, "
                               f"got {type(invalidation).__name__}")
            
            if current_price is None or not isinstance(current_price, (int, float)):
                raise ValueError("current_price must be numeric")
            
            if current_price <= 0:
                raise ValueError("current_price must be positive")
            
            # Classify stock and get adjusted thresholds (NEW)
            stock_type = StockClassifier.classify_stock(symbol) if symbol else 'normal'
            thresholds = StockClassifier.get_adjusted_thresholds(stock_type)
            
            # Calculate momentum score if not provided (NEW)
            if momentum_score is None and price_data is not None:
                try:
                    from datetime import datetime
                    momentum_score = MomentumScorer.calculate_momentum_score(price_data, datetime.now())
                except:
                    momentum_score = 50  # Default
            else:
                momentum_score = momentum_score or 50
            
            # Get sector adjustments (NEW)
            sector_adj = SectorAnalyzer.get_sector_adjustment(
                symbol, fund_score.total_score, tech_score.total_score, momentum_score
            ) if symbol else {'adjustment': 1.0, 'reason': 'No sector context'}
            
            # Determine decision based on enhanced filters
            decision_logic = DecisionEngine._evaluate_filters(
                fund_score, tech_score, buy_zone, invalidation,
                current_price, dma_200, stock_type, thresholds,
                momentum_score, fundamental_trend, sector_adj, symbol
            )
            
            # Create Decision object
            decision = Decision(
                symbol=symbol or "UNKNOWN",
                decision_type=decision_logic["type"],
                confidence=decision_logic["confidence"],
                reasoning=decision_logic["reasoning"],
                entry_price=decision_logic.get("entry_price"),
                stop_loss=invalidation.hard_stop_price if invalidation else None,
                buy_zone_lower=buy_zone.lower_bound,
                buy_zone_upper=buy_zone.upper_bound,
                tags=decision_logic.get("tags", [])
            )
            
            return decision
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error making decision: {str(e)}")
    
    @staticmethod
    def _evaluate_filters(fund_score: FundamentalScore,
                         tech_score: TechnicalScore,
                         buy_zone: BuyZone,
                         invalidation: Invalidation,
                         current_price: float,
                         dma_200: float = None,
                         stock_type: str = 'normal',
                         thresholds: dict = None,
                         momentum_score: int = 50,
                         fundamental_trend: dict = None,
                         sector_adj: dict = None,
                         symbol: str = None) -> dict:
        """
        Evaluate all decision filters with enhancements for recovery stocks.
        
        Returns dict with decision_type, confidence, and reasoning.
        """
        
        # Set defaults
        if thresholds is None:
            thresholds = StockClassifier.get_adjusted_thresholds('normal')
        if sector_adj is None:
            sector_adj = {'adjustment': 1.0, 'reason': 'No sector context'}
        if fundamental_trend is None:
            fundamental_trend = {'trend': 'unknown'}
        
        # Check exit conditions first
        exit_reason = DecisionEngine._check_exit_conditions(
            fund_score, tech_score, current_price, dma_200
        )
        
        if exit_reason:
            return {
                "type": DecisionType.EXIT,
                "confidence": 85,
                "reasoning": exit_reason,
                "tags": ["exit", "structural_break"]
            }
        
        # NEW: Check for Convergence Signal (recovery stock with tech + momentum + trend improving)
        convergence_result = DecisionEngine._check_convergence_signal(
            fund_score, tech_score, momentum_score, fundamental_trend, 
            stock_type, thresholds, symbol
        )
        
        if convergence_result and convergence_result["type"] == DecisionType.ACCUMULATE:
            return convergence_result
        
        # Check fresh buying filters with enhanced thresholds
        filters_passed, filter_reason, failed_filter = DecisionEngine._check_buying_filters(
            fund_score, tech_score, buy_zone, invalidation, current_price,
            stock_type, thresholds, momentum_score
        )
        
        if not filters_passed:
            return {
                "type": DecisionType.AVOID,
                "confidence": 70,
                "reasoning": filter_reason,
                "tags": ["avoid", failed_filter]
            }
        
        # All filters passed → ACCUMULATE with sector adjustment
        entry_price = (buy_zone.lower_bound + buy_zone.upper_bound) / 2.0
        
        confidence = DecisionEngine._calculate_confidence(fund_score, tech_score, momentum_score)
        
        adj_confidence = int(confidence * sector_adj.get('adjustment', 1.0))
        adj_confidence = min(95, max(60, adj_confidence))  # Clamp between 60-95
        
        reasoning = (
            f"All conditions met for long-term accumulation. "
            f"Fundamentals: {fund_score.total_score}/100 (Threshold: {thresholds.get('fund', 60)}). "
            f"Technicals: {tech_score.total_score}/100 (Threshold: {thresholds.get('tech', 60)}). "
            f"Momentum: {momentum_score}/100 (Threshold: {thresholds.get('momentum', 60)}). "
            f"Entry zone: Rs {buy_zone.lower_bound:.2f}-Rs {buy_zone.upper_bound:.2f}. "
            f"Stop loss: Rs {invalidation.hard_stop_price:.2f}. "
            f"Stock Type: {stock_type}. {sector_adj.get('reason', '')}."
        )
        
        return {
            "type": DecisionType.ACCUMULATE,
            "confidence": adj_confidence,
            "reasoning": reasoning,
            "entry_price": entry_price,
            "tags": ["accumulate", "long_term", f"stock_type:{stock_type}"]
        }
    
    @staticmethod
    def _check_convergence_signal(fund_score: FundamentalScore,
                                 tech_score: TechnicalScore,
                                 momentum_score: int,
                                 fundamental_trend: dict,
                                 stock_type: str,
                                 thresholds: dict,
                                 symbol: str = None) -> dict:
        """
        NEW: Check for convergence signal (tech + momentum aligning with improving fundamentals).
        
        This catches recovery/government stocks where institutional money enters
        before quarterly financials improve (fundamental lag issue).
        
        Triggers for recovery stocks when:
        - Tech score >= 65 (strong recovery)
        - Momentum score >= 65 (strong accumulation)
        - Fundamental score >= 50 (not broken)
        - Fundamental trend = 'improving' (direction matters, not absolute level)
        
        Returns dict with type and reasoning, or None if no convergence.
        """
        
        if stock_type not in ['government', 'highly_volatile']:
            return None  # Convergence only for recovery stocks
        
        # Check convergence conditions
        has_strong_tech = tech_score.total_score >= 65
        has_strong_momentum = momentum_score >= 65
        has_reasonable_funds = fund_score.total_score >= 50
        is_trending_better = fundamental_trend.get('trend') in ['improving', 'stable']
        roe_improving = fundamental_trend.get('roe_change', 0) > 0
        
        if (has_strong_tech and has_strong_momentum and 
            has_reasonable_funds and is_trending_better):
            
            confidence = 80
            
            reasoning = (
                f"CONVERGENCE SIGNAL DETECTED for {stock_type} stock '{symbol}'. "
                f"Technical recovery ({tech_score.total_score}/100) + "
                f"Momentum accumulation ({momentum_score}/100) detected while "
                f"Fundamentals improving (trend: {fundamental_trend.get('trend')}, "
                f"ROE change: {fundamental_trend.get('roe_change', 0):+.1f}). "
                f"Institutional buying likely before quarterly metrics fully reflect improvement. "
                f"BUY for recovery accumulation."
            )
            
            if roe_improving:
                confidence = 85
                reasoning += " ROE already improving - strong signal."
            
            return {
                "type": DecisionType.ACCUMULATE,
                "confidence": confidence,
                "reasoning": reasoning,
                "tags": ["convergence_signal", f"recovery_{stock_type}"]
            }
        
        return None
    
    @staticmethod
    def _check_buying_filters(fund_score: FundamentalScore,
                             tech_score: TechnicalScore,
                             buy_zone: BuyZone,
                             invalidation: Invalidation,
                             current_price: float,
                             stock_type: str = 'normal',
                             thresholds: dict = None,
                             momentum_score: int = 50) -> tuple:
        """
        Check all fresh buying filters with dynamic thresholds by stock type.
        
        Returns (passed: bool, reason: str, failed_filter: str)
        """
        
        if thresholds is None:
            thresholds = StockClassifier.get_adjusted_thresholds(stock_type)
        
        # NEW: Dynamic Fundamental Threshold (based on stock type)
        fund_threshold = thresholds.get('fund', 60)
        if fund_score.total_score < fund_threshold:
            return (False,
                   f"Fundamental score ({fund_score.total_score}/100) below threshold ({fund_threshold}). "
                   f"Business quality insufficient for {stock_type} stock. Avoid fresh buying.",
                   "fundamental_weak")
        
        # NEW: Dynamic Technical Threshold (based on stock type)
        tech_threshold = thresholds.get('tech', 60)
        if tech_score.total_score < tech_threshold:
            return (False,
                   f"Technical score ({tech_score.total_score}/100) below threshold ({tech_threshold}). "
                   f"Technical setup not favorable for {stock_type} stock. Avoid fresh buying.",
                   "technical_weak")
        
        # NEW: Momentum Score Filter (added as 4th metric)
        momentum_threshold = thresholds.get('momentum', 60)
        if momentum_score < momentum_threshold:
            return (False,
                   f"Momentum score ({momentum_score}/100) below threshold ({momentum_threshold}). "
                   f"No institutional accumulation detected. Avoid fresh buying.",
                   "momentum_weak")
        
        # Filter 3: Price vs 200 DMA (requires dma_200 in tech_score)
        if tech_score.dma_200 is not None and current_price < tech_score.dma_200:
            return (False,
                   f"Price (Rs {current_price:.2f}) below 200 DMA (Rs {tech_score.dma_200:.2f}). "
                   f"Not in primary uptrend. Avoid fresh buying.",
                   "below_200dma")
        
        # Filter 4: Invalidation Exists
        if invalidation is None:
            return (False,
                   f"No clear invalidation (stop loss) level defined. "
                   f"Risk management unclear. Avoid trade.",
                   "no_stop_loss")
        
        # All filters passed
        return (True, "", "")
    
    @staticmethod
    def _check_exit_conditions(fund_score: FundamentalScore,
                              tech_score: TechnicalScore,
                              current_price: float,
                              dma_200: float = None) -> str:
        """
        Check if existing position should be exited.
        
        Returns exit reason string if triggered, empty string if no exit.
        """
        
        # Exit Condition 1: Fundamental deterioration
        # (Score below 50 indicates broken fundamentals)
        if fund_score.total_score < 50:
            return (f"Fundamental score deteriorated to {fund_score.total_score}/100. "
                   f"Business quality compromised - exit position.")
        
        # Exit Condition 2: 200 DMA trend break
        if dma_200 is not None and current_price < dma_200:
            # But only if technical score also reflects the breakdown
            if tech_score.total_score < 40:
                return (f"Price (${current_price:.2f}) broke below 200 DMA "
                       f"(${dma_200:.2f}) and technical score dropped. "
                       f"Structural trend broken - exit position.")
        
        # No exit triggered
        return ""
    
    @staticmethod
    def _calculate_confidence(fund_score: FundamentalScore,
                             tech_score: TechnicalScore,
                             momentum_score: int = 50) -> int:
        """
        Calculate decision confidence (0-100) based on ALL analysis components.
        
        NOW includes momentum as third metric for stronger signals.
        Higher scores = higher confidence in ACCUMULATE decision.
        """
        
        # Weight: Fund 40%, Tech 35%, Momentum 25% (NEW)
        weighted_score = (
            (fund_score.total_score * 0.40) +
            (tech_score.total_score * 0.35) +
            (momentum_score * 0.25)
        )
        
        # Map to confidence
        if weighted_score >= 75:
            confidence = 90
        elif weighted_score >= 65:
            confidence = 80
        elif weighted_score >= 55:
            confidence = 70
        else:
            confidence = 60
        
        return int(min(95, confidence))
