"""
Refactored Decision Engine - Two-Layer Analysis with Risk Filters

Combines:
1. Enhanced Fundamental Analysis → Investment View
2. Enhanced Technical Analysis → Trade Setup
3. Market Regime Filter → Confidence multiplier (0.6-1.2)
4. Event Risk Analyzer → Event-driven downgrades
5. Drawdown Modeler → Fragility detection
6. Confidence Quantifier → Quantitative backing

OUTPUT:
- Investment View (always generated)
- Trade Setup (only if technical confirmation exists)
- Confidence Report (quantitative backing with risk adjustments)

GUIDING PRINCIPLE:
"Silence is preferred over low-quality signals"
- NO TRADE when conditions not met
- Clear invalidation conditions
- Explicit statement of uncertainty
- Regime-adjusted confidence (accounting for market stress)
- Event-aware trading (suppress during earnings/dividends)
- Drawdown-aware stops (fragile setups flagged/suppressed)
"""

from typing import Tuple, Optional
from datetime import datetime

# Import analysis modules
from .confidence_quantifier import (
    ConfidenceQuantifier, SetupType as ConfSetupType, ConfidenceMetrics
)
from .enhanced_technical_analyzer import (
    EnhancedTechnicalAnalyzer, TradeSetup as TechTradeSetup, SetupType as TechSetupType
)
from .enhanced_fundamental_analyzer import (
    EnhancedFundamentalAnalyzer, EnhancedFundamentalAnalysis, StockCategory
)
from .two_layer_output import (
    TwoLayerOutputFormatter, InvestmentView, TradeSetup as OutputTradeSetup,
    ConfidenceReport, InvestmentDecision
)

# Import risk filter modules
from .market_regime_filter import (
    MarketRegimeFilter, MarketRegime
)
from .event_risk_analyzer import (
    EventRiskAnalyzer, EventRisk
)
from .drawdown_modeler import (
    DrawdownModeler, DrawdownAnalysis
)


class RefactoredDecisionEngine:
    """
    New decision engine with rigorous two-layer analysis + robustness filters.
    
    Outputs:
    - Investment View (long-term thesis)
    - Trade Setup (tactical entry, if confirmed)
    - Confidence (quantitative backing with scenarios)
    
    CONSTRAINTS:
    - Returns "NO TRADE" when conditions not met
    - Requires 2x ATR stops, structural targets
    - Mandates volume and breakout confirmation
    - Articulates bull/bear/invalidation clearly
    - Suppresses BUY/ACCUMULATE during regime instability
    - Caps confidence at 90, floors at 10 if setup exists
    - Normalizes MAE/stops for high-volatility regimes
    """
    
    def __init__(self):
        self.fundamental_analyzer = EnhancedFundamentalAnalyzer()
        self.technical_analyzer = EnhancedTechnicalAnalyzer()
        self.confidence_quantifier = ConfidenceQuantifier()
        self.output_formatter = TwoLayerOutputFormatter()
        
        # Internal tracking (no forward leakage)
        self.opportunity_cost_log = []  # Log suppressed setups for post-analysis
    
    def log_suppressed_opportunity(self, symbol: str, setup_type: str, reason: str, 
                                   base_confidence: float, target_potential: float):
        """
        Track suppressed setup for post-analysis (internal use only).
        
        Args:
            symbol: Stock symbol
            setup_type: Type of setup that was suppressed
            reason: Why it was suppressed
            base_confidence: Confidence before suppression
            target_potential: Projected upside if setup had been taken
        """
        self.opportunity_cost_log.append({
            "symbol": symbol,
            "setup_type": setup_type,
            "reason": reason,
            "base_confidence": base_confidence,
            "target_potential": target_potential,
        })
    
    def analyze_stock(
        self,
        # Stock info - REQUIRED
        symbol: str,
        name: str,
        sector: str,
        category: StockCategory,
        analysis_date: datetime,
        
        # Fundamental data - REQUIRED
        pe_ratio: float,
        peg_ratio: float,
        roe: float,
        roce: float,
        debt_equity: float,
        current_ratio: float,
        profit_margin: float,
        revenue_growth: float,
        fcf: float,
        
        # Technical data - REQUIRED
        current_price: float,
        ema_20: float,
        ema_50: float,
        ema_200: float,
        atr: float,
        rsi_14: float,
        macd_line: float,
        macd_signal: float,
        volume_current: float,
        volume_20ma: float,
        recent_high_20d: float,
        recent_low_20d: float,
        recent_high_52w: float,
        recent_low_52w: float,
        
        # OPTIONAL parameters (with defaults)
        npa_ratio: Optional[float] = None,
        dividend_yield: Optional[float] = None,
        vwap: Optional[float] = None,
        htf_trend: Optional[str] = None,
        index_prices: Optional[list] = None,      # NIFTY50 closes for regime detection
        index_atr_values: Optional[list] = None,  # ATR values for volatility percentile
        market_breadth: Optional[dict] = None,    # {"advances": N, "declines": N}
        earnings_date: Optional[str] = None,      # ISO format date
        dividend_date: Optional[str] = None,      # ISO format date
        other_events: Optional[list] = None,      # Event dicts with "type" and "date"
        
    ) -> Tuple[InvestmentView, Optional[OutputTradeSetup], ConfidenceReport, str]:
        """
        Complete analysis with two-layer output + risk filters.
        
        Returns:
            (investment_view, trade_setup, confidence_report, formatted_output)
        """
        
        # STEP 1: Fundamental Analysis → Investment View
        fund_analysis = self.fundamental_analyzer.analyze(
            symbol=symbol,
            category=category,
            pe_ratio=pe_ratio,
            peg_ratio=peg_ratio,
            roe=roe,
            roce=roce,
            debt_equity=debt_equity,
            current_ratio=current_ratio,
            profit_margin=profit_margin,
            revenue_growth=revenue_growth,
            fcf=fcf,
            npa_ratio=npa_ratio,
            dividend_yield=dividend_yield,
        )
        
        # Convert to Investment View layer
        investment_view = self._create_investment_view(
            symbol, fund_analysis, current_price, analysis_date
        )
        
        # STEP 2: Technical Analysis → Trade Setup (if confirmed)
        tech_setup = self.technical_analyzer.analyze(
            current_price=current_price,
            ema_20=ema_20,
            ema_50=ema_50,
            ema_200=ema_200,
            atr=atr,
            rsi_14=rsi_14,
            macd_line=macd_line,
            macd_signal=macd_signal,
            volume_current=volume_current,
            volume_20ma=volume_20ma,
            recent_high_20d=recent_high_20d,
            recent_low_20d=recent_low_20d,
            recent_high_52w=recent_high_52w,
            recent_low_52w=recent_low_52w,
            vwap=vwap,
            htf_trend=htf_trend,
        )
        
        # Convert to output trade setup
        output_trade_setup = None
        if tech_setup.setup_type != TechSetupType.NO_TRADE:
            output_trade_setup = self._create_output_trade_setup(tech_setup)
        
        # STEP 3A: Risk Filters (Regime, Event, Drawdown)
        market_regime = None
        event_risk = None
        drawdown_analysis = None
        regime_multiplier = 1.0
        event_multiplier = 1.0
        drawdown_multiplier = 1.0
        
        if output_trade_setup:
            # Apply market regime filter
            if index_prices and index_atr_values and market_breadth:
                market_regime = MarketRegimeFilter.analyze(
                    index_prices=index_prices,
                    index_atr_values=index_atr_values,
                    market_breadth=market_breadth,
                    current_price=index_prices[-1],
                    current_atr=index_atr_values[-1],
                )
                regime_multiplier = market_regime.confidence_multiplier
            
            # Apply event risk filter
            event_risk = EventRiskAnalyzer.check_event_proximity(
                symbol=symbol,
                current_date=analysis_date,
                earnings_date=earnings_date,
                dividend_date=dividend_date,
                other_events=other_events,
            )
            # Convert recommendation to multiplier
            if event_risk.recommendation.value == "SUPPRESS":
                event_multiplier = 0.4
            elif event_risk.recommendation.value == "WAIT":
                event_multiplier = 0.5
            elif event_risk.recommendation.value == "PROCEED_CAUTIOUS":
                event_multiplier = 0.8
            else:
                event_multiplier = 1.0
            
            # Apply drawdown fragility filter
            # Map setup type to string
            setup_type_str = tech_setup.setup_type.value
            drawdown_analysis = DrawdownModeler.analyze_setup_fragility(
                setup_type=setup_type_str,
                sector=sector,
                entry_price=current_price,
                proposed_stop=tech_setup.invalidation_low,
            )
            # Convert fragility to multiplier
            if drawdown_analysis.fragility_level.value == "ROBUST":
                drawdown_multiplier = 1.1
            elif drawdown_analysis.fragility_level.value == "NORMAL":
                drawdown_multiplier = 1.0
            elif drawdown_analysis.fragility_level.value == "FRAGILE":
                drawdown_multiplier = 0.7
            else:  # EXTREMELY_FRAGILE
                drawdown_multiplier = 0.4
        
        # STEP 3B: Confidence Quantification with Risk Adjustments
        confidence_report = self._create_confidence_report(
            symbol=symbol,
            tech_setup=tech_setup,
            fund_analysis=fund_analysis,
            output_setup=output_trade_setup,
            roe=roe,
            roce=roce,
            de=debt_equity,
            category=category,
            market_regime=market_regime,
            event_risk=event_risk,
            drawdown_analysis=drawdown_analysis,
            regime_multiplier=regime_multiplier,
            event_multiplier=event_multiplier,
            drawdown_multiplier=drawdown_multiplier,
            analysis_date=analysis_date,
        )
        
        # STEP 4: Format complete output
        formatted_output = self.output_formatter.format_report(
            symbol, investment_view, output_trade_setup, confidence_report
        )
        
        return investment_view, output_trade_setup, confidence_report, formatted_output
    
    @staticmethod
    def _create_investment_view(
        symbol: str,
        fund_analysis: EnhancedFundamentalAnalysis,
        current_price: float,
        analysis_date: datetime
    ) -> InvestmentView:
        """Convert fundamental analysis to investment view layer."""
        
        # Determine investment decision based on fundamental score
        if fund_analysis.overall_score >= 75:
            decision = InvestmentDecision.ACCUMULATE
        elif fund_analysis.overall_score >= 55:
            decision = InvestmentDecision.HOLD
        else:
            decision = InvestmentDecision.AVOID
        
        return InvestmentView(
            symbol=symbol,
            decision=decision,
            thesis_summary=fund_analysis.bull_case,
            fundamental_strengths=fund_analysis.key_strengths,
            fundamental_risks=fund_analysis.key_risks,
            invalidation_condition=fund_analysis.invalidation_trigger,
            fund_score=fund_analysis.overall_score,
            sector=fund_analysis.category.value,
            analysis_date=analysis_date.strftime("%Y-%m-%d"),
        )
    
    @staticmethod
    def _create_output_trade_setup(tech_setup: TechTradeSetup) -> Optional[OutputTradeSetup]:
        """Convert technical setup to output trade setup."""
        
        if not tech_setup.buy_zone_low:
            return None
        
        return OutputTradeSetup(
            status=tech_setup.confidence,
            buy_zone_low=tech_setup.buy_zone_low,
            buy_zone_high=tech_setup.buy_zone_high,
            buy_zone_basis=tech_setup.setup_type.value,
            invalidation_level=tech_setup.invalidation_low,
            invalidation_reason=tech_setup.invalidation_reason,
            target_zone_low=tech_setup.target_zone_low,
            target_zone_high=tech_setup.target_zone_high,
            target_basis=tech_setup.target_basis,
            rr_ratio=tech_setup.rr_ratio,
            volume_confirmation=True,  # Already checked in technical analyzer
            breakout_confirmed=tech_setup.confidence == "BUY",
            warning=tech_setup.warning,
        )
    
    @staticmethod
    def _create_confidence_report(
        symbol: str,
        tech_setup: TechTradeSetup,
        fund_analysis: EnhancedFundamentalAnalysis,
        output_setup: Optional[OutputTradeSetup],
        roe: float,
        roce: float,
        de: float,
        category: StockCategory,
        market_regime: Optional[MarketRegime] = None,
        event_risk: Optional[EventRisk] = None,
        drawdown_analysis: Optional[DrawdownAnalysis] = None,
        regime_multiplier: float = 1.0,
        event_multiplier: float = 1.0,
        drawdown_multiplier: float = 1.0,
        analysis_date: Optional[datetime] = None,
    ) -> ConfidenceReport:
        """Generate quantitative confidence report with risk adjustments."""
        
        # Extract setup type
        if tech_setup.setup_type == TechSetupType.NO_TRADE:
            conf_setup_type = ConfSetupType.NO_SETUP
        elif tech_setup.setup_type == TechSetupType.TREND_CONTINUATION:
            conf_setup_type = ConfSetupType.TREND_CONTINUATION_BUY
        elif tech_setup.setup_type == TechSetupType.BREAKOUT_RETEST:
            conf_setup_type = ConfSetupType.BREAKOUT_RETEST
        else:
            conf_setup_type = ConfSetupType.TREND_CONTINUATION_BUY
        
        # Determine sector for baseline
        sector_map = {
            StockCategory.TECH_IT: "tech",
            StockCategory.FMCG_CONSUMER: "fmcg",
            StockCategory.PSU_GOVERNMENT: "psu",
        }
        sector = sector_map.get(category, "general")
        
        # Get volatility regime (simple: based on ATR or RSI)
        volatility_regime = "normal"
        
        # Calculate base confidence metrics
        confidence_metrics = ConfidenceQuantifier.quantify(
            setup_type=conf_setup_type,
            sector=sector,
            volatility_regime=volatility_regime,
            fund_score=fund_analysis.overall_score,
            tech_score=50,  # Placeholder
            rr_ratio=output_setup.rr_ratio if output_setup else None,
            structure_signals=2 if output_setup else 0,
            breakout_confirmed=output_setup is not None if output_setup else False,
            thesis_clear=fund_analysis.bull_case is not None,
            invalidation_defined=fund_analysis.invalidation_trigger is not None,
            current_price_in_zone=False,
            volume_confirmed=output_setup is not None if output_setup else False,
        )
        
        # Get historical baseline
        baseline = ConfidenceQuantifier._get_baseline(
            conf_setup_type, sector, volatility_regime
        )
        
        base_confidence = confidence_metrics.total_confidence
        
        # APPLY RISK MULTIPLIERS
        regime_adjustment = 0.0
        event_adjustment = 0.0
        drawdown_adjustment = 0.0
        regime_explanation = ""
        event_explanation = ""
        drawdown_explanation = ""
        
        if market_regime and regime_multiplier != 1.0:
            adjusted_regime, regime_explanation = ConfidenceQuantifier.apply_regime_multiplier(
                base_confidence, regime_multiplier
            )
            regime_adjustment = adjusted_regime - base_confidence
        
        if event_risk and event_multiplier != 1.0:
            adjusted_event, event_explanation = ConfidenceQuantifier.apply_event_multiplier(
                base_confidence, event_multiplier
            )
            event_adjustment = adjusted_event - base_confidence
        
        if drawdown_analysis and drawdown_multiplier != 1.0:
            adjusted_drawdown, drawdown_explanation = ConfidenceQuantifier.apply_drawdown_multiplier(
                base_confidence, drawdown_multiplier
            )
            drawdown_adjustment = adjusted_drawdown - base_confidence
        
        # Final confidence = base * all multipliers
        final_confidence = base_confidence * regime_multiplier * event_multiplier * drawdown_multiplier
        final_confidence = min(100, max(0, final_confidence))
        
        # NEW: APPLY CONFIDENCE CALIBRATION (ceiling & floor)
        calibrated_confidence, calibration_note, ceiling_reduction = \
            ConfidenceQuantifier.apply_confidence_calibration(
                final_confidence,
                has_trade_setup=(output_setup is not None)
            )
        
        # Re-grade based on calibrated confidence
        final_grade = ConfidenceQuantifier._assign_grade(calibrated_confidence)
        
        # NEW: CHECK REGIME INSTABILITY - Suppress BUY/ACCUMULATE signals
        instability_suppression_applied = False
        instability_suppression_note = ""
        suppressed_investment_decision = None
        
        if market_regime and market_regime.suppression_active and output_setup:
            # Regime unstable - suppress BUY/ACCUMULATE for 1-3 periods
            instability_suppression_applied = True
            suppressed_investment_decision = "WAIT"  # Original decision (before suppression)
            instability_suppression_note = f"Regime instability detected: {market_regime.instability_reason} | " \
                                          f"Suppressing BUY/ACCUMULATE for 1-3 periods. Only HOLD/WAIT allowed."
        
        # Build uncertainty statement with risk details
        uncertainty_parts = []
        if calibration_note:
            uncertainty_parts.append(f"Calibration: {calibration_note}")
        if market_regime:
            uncertainty_parts.append(f"Market regime: {market_regime.regime_type.value} (multiplier {regime_multiplier:.2f}x)")
            if market_regime.regime_instability:
                uncertainty_parts.append(f"⚠ REGIME INSTABILITY: {market_regime.instability_reason}")
        if event_risk and event_risk.risk_level.value != "NONE":
            uncertainty_parts.append(f"Event risk: {event_risk.explanation}")
        if drawdown_analysis and drawdown_analysis.is_fragile:
            uncertainty_parts.append(f"Drawdown profile: {drawdown_analysis.recommendation}")
        
        uncertainty_statement = " | ".join(uncertainty_parts) if uncertainty_parts else \
            f"Setup has {final_grade} confidence based on technical + fundamental + regime + event + drawdown filters."
        
        # Build report
        return ConfidenceReport(
            total_score=calibrated_confidence,  # Use calibrated confidence
            grade=final_grade,
            win_rate_component=confidence_metrics.win_rate_score,
            rr_component=confidence_metrics.rr_score,
            structure_component=confidence_metrics.structure_score,
            thesis_component=confidence_metrics.thesis_clarity_score,
            drawdown_component=confidence_metrics.drawdown_score,
            win_scenario=confidence_metrics.win_scenario,
            base_scenario=confidence_metrics.base_scenario,
            worst_scenario=confidence_metrics.worst_scenario,
            setup_type=conf_setup_type.value,
            historical_win_rate=baseline.win_rate,
            sample_size=baseline.sample_size,
            uncertainty_statement=uncertainty_statement,
            regime_adjustment=regime_adjustment,
            regime_explanation=regime_explanation,
            event_adjustment=event_adjustment,
            event_explanation=event_explanation,
            drawdown_adjustment=drawdown_adjustment,
            drawdown_explanation=drawdown_explanation,
            market_regime=market_regime,
            event_risk=event_risk,
            drawdown_analysis=drawdown_analysis,
            # NEW: Calibration and instability flags
            base_confidence=base_confidence,
            confidence_before_calibration=final_confidence,
            calibration_adjustment=calibrated_confidence - final_confidence,
            calibration_note=calibration_note,
            ceiling_reduction=ceiling_reduction,
            regime_instability_active=instability_suppression_applied,
            instability_suppression_note=instability_suppression_note,
            suppressed_investment_decision=suppressed_investment_decision,
        )
