"""
Fundamental Analysis Engine
Analyzes business quality, growth, stability, and valuation
"""

from typing import Dict, Tuple, Optional
from .data_models import FundamentalMetrics
from .constants import FUNDAMENTAL_THRESHOLDS as THRESHOLDS


class FundamentalAnalyzer:
    """
    Deterministic fundamental analysis based on financial metrics.
    Decision: IF the business is worth owning long-term.
    """
    
    def __init__(self):
        self.thresholds = THRESHOLDS
        self.rules_passed = []
        self.rules_failed = []
    
    def analyze(self, metrics: FundamentalMetrics) -> Tuple[bool, Dict]:
        """
        Comprehensive fundamental analysis.
        
        Args:
            metrics: FundamentalMetrics object
            
        Returns:
            (is_fundmentally_sound, analysis_details_dict)
        """
        self.rules_passed = []
        self.rules_failed = []
        
        # Rule 1: Profitability Check
        profitability_ok = self._check_profitability(metrics)
        
        # Rule 2: Growth Check (5-year CAGR)
        growth_ok = self._check_growth(metrics)
        
        # Rule 3: Financial Stability
        stability_ok = self._check_stability(metrics)
        
        # Rule 4: Valuation (not expensive)
        valuation_ok = self._check_valuation(metrics)
        
        # Conservative rule: ALL must pass for ACCUMULATE thesis
        fundamentally_sound = profitability_ok and growth_ok and stability_ok and valuation_ok
        
        return fundamentally_sound, {
            "profitability_ok": profitability_ok,
            "growth_ok": growth_ok,
            "stability_ok": stability_ok,
            "valuation_ok": valuation_ok,
            "rules_passed": self.rules_passed,
            "rules_failed": self.rules_failed,
            "metrics": {
                "net_profit_margin": metrics.net_profit_margin,
                "roe": metrics.roe,
                "roce": metrics.roce,
                "revenue_cagr_5yr": metrics.revenue_cagr_5yr,
                "eps_cagr_5yr": metrics.eps_cagr_5yr,
                "debt_to_equity": metrics.debt_to_equity,
                "current_ratio": metrics.current_ratio,
                "pe_ratio": metrics.pe_ratio,
                "pe_percentile": metrics.pe_percentile,
                "pb_ratio": metrics.pb_ratio,
            }
        }
    
    def _check_profitability(self, metrics: FundamentalMetrics) -> bool:
        """
        Rule: Business must be profitable.
        - Net Profit Margin >= 5%
        - ROE >= 10%
        - ROCE >= 12%
        """
        checks = {
            f"NPM >= {self.thresholds['min_profit_margin_pct']}%": 
                metrics.net_profit_margin >= self.thresholds['min_profit_margin_pct'],
            f"ROE >= {self.thresholds['min_roe_pct']}%": 
                metrics.roe >= self.thresholds['min_roe_pct'],
            f"ROCE >= {self.thresholds['min_roce_pct']}%": 
                metrics.roce >= self.thresholds['min_roce_pct'],
        }
        
        passed = all(checks.values())
        for rule, result in checks.items():
            if result:
                self.rules_passed.append(f"Profitability: {rule}")
            else:
                self.rules_failed.append(f"Profitability: {rule}")
        
        return passed
    
    def _check_growth(self, metrics: FundamentalMetrics) -> bool:
        """
        Rule: Business must have consistent long-term growth.
        - Revenue CAGR (5yr) >= 8%
        - EPS CAGR (5yr) >= 8%
        """
        checks = {
            f"Revenue CAGR (5yr) >= {self.thresholds['min_revenue_growth_5yr_pct']}%": 
                metrics.revenue_cagr_5yr >= self.thresholds['min_revenue_growth_5yr_pct'],
            f"EPS CAGR (5yr) >= {self.thresholds['min_eps_growth_5yr_pct']}%": 
                metrics.eps_cagr_5yr >= self.thresholds['min_eps_growth_5yr_pct'],
        }
        
        passed = all(checks.values())
        for rule, result in checks.items():
            if result:
                self.rules_passed.append(f"Growth: {rule}")
            else:
                self.rules_failed.append(f"Growth: {rule}")
        
        return passed
    
    def _check_stability(self, metrics: FundamentalMetrics) -> bool:
        """
        Rule: Balance sheet must be stable (low leverage, good liquidity).
        - Debt-to-Equity <= 1.5
        - Current Ratio >= 1.0
        - Debt Service Coverage >= 1.5x
        """
        checks = {
            f"D/E <= {self.thresholds['max_debt_to_equity']}": 
                metrics.debt_to_equity <= self.thresholds['max_debt_to_equity'],
            f"Current Ratio >= {self.thresholds['min_current_ratio']}": 
                metrics.current_ratio >= self.thresholds['min_current_ratio'],
            f"Debt Service Coverage >= {self.thresholds['min_debt_service_coverage']}x": 
                metrics.debt_service_coverage >= self.thresholds['min_debt_service_coverage'],
        }
        
        passed = all(checks.values())
        for rule, result in checks.items():
            if result:
                self.rules_passed.append(f"Stability: {rule}")
            else:
                self.rules_failed.append(f"Stability: {rule}")
        
        return passed
    
    def _check_valuation(self, metrics: FundamentalMetrics) -> bool:
        """
        Rule: Price must be reasonable relative to value.
        - PE Ratio <= 75th percentile (not expensive vs history)
        - PB Ratio <= 3.0
        - Prefer dividend payers (yield >= 1.5%)
        """
        checks = {
            f"PE Percentile <= {self.thresholds['max_pe_ratio_percentile']}": 
                metrics.pe_percentile <= self.thresholds['max_pe_ratio_percentile'],
            f"PB Ratio <= {self.thresholds['max_pb_ratio']}": 
                metrics.pb_ratio <= self.thresholds['max_pb_ratio'],
            f"Dividend Yield >= {self.thresholds['min_dividend_yield_pct']}% (preferred)": 
                metrics.dividend_yield >= self.thresholds['min_dividend_yield_pct'],
        }
        
        # All must pass: strict valuation discipline
        passed = all(checks.values())
        for rule, result in checks.items():
            if result:
                self.rules_passed.append(f"Valuation: {rule}")
            else:
                self.rules_failed.append(f"Valuation: {rule}")
        
        return passed
    
    def get_fundamental_score(self, metrics: FundamentalMetrics) -> float:
        """
        Score from 0-100 based on how strong fundamentals are.
        Not used for decision (binary), but for confidence ranking.
        """
        _, details = self.analyze(metrics)
        
        score = 0.0
        max_score = 100.0
        
        # Profitability: 25 points
        if details["profitability_ok"]:
            score += 25.0
        else:
            # Partial credit: count how many sub-rules pass
            npm_ok = metrics.net_profit_margin >= self.thresholds['min_profit_margin_pct']
            roe_ok = metrics.roe >= self.thresholds['min_roe_pct']
            roce_ok = metrics.roce >= self.thresholds['min_roce_pct']
            score += (sum([npm_ok, roe_ok, roce_ok]) / 3) * 25
        
        # Growth: 25 points
        if details["growth_ok"]:
            score += 25.0
        
        # Stability: 25 points
        if details["stability_ok"]:
            score += 25.0
        
        # Valuation: 25 points
        if details["valuation_ok"]:
            score += 25.0
        
        return score
