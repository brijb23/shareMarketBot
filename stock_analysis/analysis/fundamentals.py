"""
Fundamental Analysis Scoring Engine

Scores business quality based on financial metrics.
No ML, no normalization - pure rule-based scoring.
"""

from stock_analysis.common.models import FundamentalData, FundamentalScore


class FundamentalAnalyzer:
    """
    Analyze fundamental strength and business quality.
    
    Scoring system (0-100 total):
    - Growth: 30 points (Revenue + Profit CAGR)
    - Profitability: 30 points (ROCE + ROE + Margin Trend)
    - Financial Strength: 25 points (D/E + Interest Coverage + OCF)
    - Valuation: 15 points max (P/E + PEG - never reduces score)
    
    Pure rule-based scoring with exact thresholds.
    No machine learning, no normalization.
    
    Example:
        analyzer = FundamentalAnalyzer()
        score = analyzer.score_fundamentals(fund_data)
        print(f"Total Score: {score.total_score}")
    """
    
    @staticmethod
    def score_fundamentals(fundamentals: FundamentalData) -> FundamentalScore:
        """
        Calculate comprehensive fundamental score.
        
        Args:
            fundamentals: FundamentalData object with financial metrics
        
        Returns:
            FundamentalScore with individual and total scores
        
        Raises:
            ValueError: If data invalid or missing required fields
        
        Example:
            >>> analyzer = FundamentalAnalyzer()
            >>> score = analyzer.score_fundamentals(fund_data)
            >>> print(f"Profitability: {score.profitability_score}")
            >>> print(f"Total: {score.total_score}")
        """
        try:
            if not isinstance(fundamentals, FundamentalData):
                raise ValueError(f"Expected FundamentalData, got {type(fundamentals).__name__}")
            
            # Calculate individual component scores
            growth_score = FundamentalAnalyzer._score_growth(fundamentals)
            profitability_score = FundamentalAnalyzer._score_profitability(fundamentals)
            financial_strength_score = FundamentalAnalyzer._score_financial_strength(fundamentals)
            valuation_score = FundamentalAnalyzer._score_valuation(fundamentals)
            
            # Total score: sum of all components (max 100)
            # Valuation maxes at 15, others at their full amounts
            total_score = min(100, growth_score + profitability_score + 
                            financial_strength_score + valuation_score)
            
            return FundamentalScore(
                symbol=fundamentals.ticker or "UNKNOWN",
                as_of_date=fundamentals.as_of_date,
                growth_score=growth_score,
                profitability_score=profitability_score,
                financial_strength_score=financial_strength_score,
                valuation_score=valuation_score,
                total_score=int(total_score)
            )
            
        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Error scoring fundamentals: {str(e)}")
    
    @staticmethod
    def _score_growth(fund: FundamentalData) -> int:
        """
        Score growth metrics (Revenue CAGR + Profit CAGR).
        
        Maximum: 30 points (15 each)
        
        Revenue CAGR thresholds:
        >=15% → 15, 10-15% → 12, 5-10% → 8, 0-5% → 4, <0% → 0
        
        Profit CAGR: Same thresholds
        """
        revenue_score = FundamentalAnalyzer._score_cagr(fund.revenue_cagr)
        profit_score = FundamentalAnalyzer._score_cagr(fund.profit_cagr)
        
        return revenue_score + profit_score
    
    @staticmethod
    def _score_cagr(cagr: float) -> int:
        """
        Score a CAGR value.
        
        >=15% → 15
        10–15% → 12
        5–10% → 8
        0–5% → 4
        <0% → 0
        """
        if cagr >= 15:
            return 15
        elif cagr >= 10:
            return 12
        elif cagr >= 5:
            return 8
        elif cagr >= 0:
            return 4
        else:
            return 0
    
    @staticmethod
    def _score_profitability(fund: FundamentalData) -> int:
        """
        Score profitability metrics (ROCE + ROE + Margin Trend).
        
        Maximum: 30 points (15 + 10 + 5)
        
        ROCE thresholds:
        >=25% → 15, 20-25% → 12, 15-20% → 8, 10-15% → 4, <10% → 0
        
        ROE thresholds:
        >=20% → 10, 15-20% → 8, 10-15% → 4, <10% → 0
        
        Margin trend:
        expanding → 5, flat → 3, shrinking → 0
        """
        roce_score = FundamentalAnalyzer._score_roce(fund.roce)
        roe_score = FundamentalAnalyzer._score_roe(fund.roe)
        margin_score = FundamentalAnalyzer._score_margin_trend(fund.margin_trend)
        
        return roce_score + roe_score + margin_score
    
    @staticmethod
    def _score_roce(roce: float) -> int:
        """
        Score Return on Capital Employed.
        
        >=25% → 15
        20–25% → 12
        15–20% → 8
        10–15% → 4
        <10% → 0
        """
        if roce >= 25:
            return 15
        elif roce >= 20:
            return 12
        elif roce >= 15:
            return 8
        elif roce >= 10:
            return 4
        else:
            return 0
    
    @staticmethod
    def _score_roe(roe: float) -> int:
        """
        Score Return on Equity.
        
        >=20% → 10
        15–20% → 8
        10–15% → 4
        <10% → 0
        """
        if roe >= 20:
            return 10
        elif roe >= 15:
            return 8
        elif roe >= 10:
            return 4
        else:
            return 0
    
    @staticmethod
    def _score_margin_trend(margin_trend: str) -> int:
        """
        Score margin trend direction.
        
        expanding → 5
        flat → 3
        shrinking → 0
        """
        trend = margin_trend.lower().strip()
        
        if trend == "expanding":
            return 5
        elif trend == "flat":
            return 3
        elif trend == "shrinking":
            return 0
        else:
            # Unknown value - default to flat
            return 3
    
    @staticmethod
    def _score_financial_strength(fund: FundamentalData) -> int:
        """
        Score financial strength metrics (D/E + Interest Coverage + OCF).
        
        Maximum: 25 points (10 + 5 + 10)
        
        Debt to Equity:
        <0.3 → 10, 0.3-0.6 → 7, 0.6-1.0 → 4, >1.0 → 0
        
        Interest Coverage:
        >10 → 5, 5-10 → 3, <5 → 0
        
        OCF vs Net Profit:
        OCF > NP → 10, OCF ≈ NP → 6, OCF < NP → 0
        """
        de_score = FundamentalAnalyzer._score_debt_to_equity(fund.debt_to_equity)
        ic_score = FundamentalAnalyzer._score_interest_coverage(fund.interest_coverage)
        ocf_score = FundamentalAnalyzer._score_ocf_vs_np(
            fund.operating_cash_flow, fund.net_profit
        )
        
        return de_score + ic_score + ocf_score
    
    @staticmethod
    def _score_debt_to_equity(de_ratio: float) -> int:
        """
        Score Debt-to-Equity ratio.
        
        <0.3 → 10
        0.3–0.6 → 7
        0.6–1.0 → 4
        >1.0 → 0
        """
        if de_ratio < 0.3:
            return 10
        elif de_ratio < 0.6:
            return 7
        elif de_ratio < 1.0:
            return 4
        else:
            return 0
    
    @staticmethod
    def _score_interest_coverage(ic_ratio: float) -> int:
        """
        Score Interest Coverage ratio.
        
        >10 → 5
        5–10 → 3
        <5 → 0
        """
        if ic_ratio > 10:
            return 5
        elif ic_ratio >= 5:
            return 3
        else:
            return 0
    
    @staticmethod
    def _score_ocf_vs_np(ocf: float, net_profit: float) -> int:
        """
        Score Operating Cash Flow vs Net Profit.
        
        OCF > NP → 10 (business generating more cash than accounting profit)
        OCF ≈ NP → 6 (roughly aligned, acceptable)
        OCF < NP → 0 (cash generation lagging profit - red flag)
        
        "Approximately equal" defined as: OCF is between 90-110% of NP
        """
        if net_profit <= 0:
            # Can't compare if no profit
            return 3  # Neutral
        
        ocf_to_np_ratio = ocf / net_profit
        
        if ocf_to_np_ratio > 1.0:
            # OCF > NP
            return 10
        elif ocf_to_np_ratio >= 0.9:
            # OCF ≈ NP (within 90-110% range)
            return 6
        else:
            # OCF < NP
            return 0
    
    @staticmethod
    def _score_valuation(fund: FundamentalData) -> int:
        """
        Score valuation metrics (P/E + PEG).
        
        Maximum: 15 points (10 + 5)
        Note: Valuation never reduces score - high valuations just don't add points.
        
        P/E vs Historical Median:
        <= median → 10
        <= 1.2× median → 6
        > 1.2× → 2
        
        PEG:
        <=1 → 5
        1–1.5 → 3
        >1.5 → 0
        """
        pe_score = FundamentalAnalyzer._score_pe(
            fund.pe_ratio, fund.historical_pe_median
        )
        peg_score = FundamentalAnalyzer._score_peg(fund.peg_ratio)
        
        # Valuation maxes at 15 (doesn't add to other 85)
        return min(15, pe_score + peg_score)
    
    @staticmethod
    def _score_pe(pe_ratio: float, historical_median: float) -> int:
        """
        Score P/E ratio relative to historical median.
        
        <= median → 10
        <= 1.2× median → 6
        > 1.2× → 2
        """
        if pe_ratio <= historical_median:
            return 10
        elif pe_ratio <= historical_median * 1.2:
            return 6
        else:
            return 2
    
    @staticmethod
    def _score_peg(peg_ratio: float) -> int:
        """
        Score PEG ratio.
        
        <=1 → 5
        1–1.5 → 3
        >1.5 → 0
        """
        if peg_ratio <= 1.0:
            return 5
        elif peg_ratio <= 1.5:
            return 3
        else:
            return 0
